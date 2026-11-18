"""Conversor do lake do SIGTAP: um Parquet por tabela e por ano.

Cada tabela do ZIP mensal vira o membro de um grupo do ano
(``sigtap/<tabela>/ano=AAAA/<tabela>.parquet``), com a competência ``mes`` (texto
``MM``) como coluna do membro. Mês novo reescreve só o arquivo do ano; competência
em dia não abre o ZIP.
"""

from __future__ import annotations

import logging
import re
import zipfile
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import polars as pl
    from quantilica.analytics.fixed_width import FixedField, layout_from_datasus
    from quantilica.analytics.lake import (
        ORIGIN_COLUMN,
        ConvertResult,
        GroupMember,
        LakeWriter,
        output_id,
        sha256_file,
    )
    from quantilica.core.lake import (
        DatasetDescriptor,
        composite_file_key,
        partition_dir,
        partition_types_for,
        select_current,
    )
except ImportError as exc:
    raise ImportError(
        "sigtap_fetcher.lake requer o extra 'analysis': "
        "uv add 'sigtap-fetcher[analysis]' "
        "--index https://index.quantilica.com/simple/"
    ) from exc

from sigtap_fetcher.constants import (
    ALL_TABLES,
    COMPETENCIA_RE,
    MONEY_COLUMNS,
    PERCENT_COLUMNS,
)

logger = logging.getLogger(__name__)

SOURCE_ID = "sigtap"
PARTITION_KEYS = ["ano"]
# Sobe quando a decodificação de uma tabela muda: os membros gravados com outro
# valor são reconvertidos.
CONTRACT_VERSION = 1


def _extract_layouts_from_zip(zf: zipfile.ZipFile) -> dict[str, list[FixedField]]:
    """Extract table layouts from ZIP archive members."""
    layouts: dict[str, list[FixedField]] = {}
    names = zf.namelist()

    # Look for layout files
    layout_files = [n for n in names if "_layout" in n.lower() or "layout" in n.lower()]
    for lfile in layout_files:
        try:
            content = zf.read(lfile).decode("latin-1")
            fields = layout_from_datasus(content)
            if fields:
                # Associate layout with table name
                stem = Path(lfile).stem.lower()
                clean_name = (
                    stem.replace("_layout", "").replace("layout", "").strip("_")
                )
                if clean_name:
                    layouts[clean_name] = fields
                layouts[Path(lfile).stem.lower()] = fields
        except Exception:
            continue

    return layouts


def _month_index(comp: str) -> int:
    return int(comp[:4]) * 12 + int(comp[4:6])


def _layout_width(layout: list[FixedField]) -> int:
    return max(f.start + f.width - 1 for f in layout)


def _borrow_layout(
    table: str,
    comp: str,
    zip_comps: list[tuple[str, Path]],
    cache: dict[tuple[str, str], list[FixedField] | None],
) -> tuple[str, list[FixedField]] | None:
    """Layout de ``table`` da competencia mais proxima de ``comp`` que o traga.

    ZIPs antigos (201412 a 2015xx) nao trazem ``tb_regra_condicionada_layout.txt``.
    O layout da **mesma tabela** em outra competencia do lote e o fallback
    (empate de distancia: a competencia anterior). Nunca o layout de outra tabela.
    O chamador confere a largura contra os dados antes de usar.
    """
    candidates = sorted(
        (c for c in zip_comps if c[0] != comp),
        key=lambda c: (abs(_month_index(c[0]) - _month_index(comp)), c[0]),
    )
    for other_comp, zpath in candidates:
        key = (zpath.name, table)
        if key not in cache:
            try:
                with zipfile.ZipFile(zpath) as zf:
                    cache[key] = _extract_layouts_from_zip(zf).get(table)
            except (OSError, zipfile.BadZipFile):
                cache[key] = None
        if cache[key]:
            return other_comp, cache[key]  # type: ignore[return-value]
    return None


_DTYPES: dict[str, Any] = {"str": pl.Utf8, "int": pl.Int64, "decimal": pl.Float64}


def _effective_kind(f: FixedField) -> tuple[str, int]:
    """Tipo e escala efetivos: ``vl_sh/sa/sp`` sao dinheiro (centavos).

    A heuristica generica trata todo ``vl_*`` como decimal; no SIGTAP ``vl_idade_*``
    (meses) e ``vl_campos_irradiados`` (contagem) sao inteiros e ``vl_percentual_*``
    e percentual com duas casas (pontos percentuais: 20.0 = 20 %).
    """
    if f.name in PERCENT_COLUMNS:
        return "decimal", 2
    if f.kind == "decimal" and f.name not in MONEY_COLUMNS:
        return "int", 0
    return f.kind, f.scale


def _is_table_member(name: str) -> bool:
    """``tb_*.txt`` / ``rl_*.txt`` de dados (nao layout, LEIA_ME, layout.txt)."""
    stem = Path(name).stem.lower()
    return (
        name.lower().endswith(".txt")
        and stem.startswith(("tb_", "rl_"))
        and not stem.endswith("_layout")
    )


def _current_by_competencia(zips: list[Path]) -> list[Path]:
    """Uma versao por competencia: a de maior sufixo ``_v`` (depois, a mais nova).

    ``select_current`` agrupa pela chave inteira (``..._202610_v2610271043``) e,
    portanto, manteria duas versoes regeradas da mesma competencia.
    """
    best: dict[str, tuple[int, Path]] = {}
    sem_competencia: list[Path] = []
    for z in select_current(zips):
        m = COMPETENCIA_RE.search(z.name)
        if not m:
            sem_competencia.append(z)
            continue
        ver = int(m.group("version") or 0)
        cur = best.get(m.group("competencia"))
        # empate de versao: o nome com carimbo @ maior (mais novo) vence
        if cur is None or (ver, z.name) > (cur[0], cur[1].name):
            best[m.group("competencia")] = (ver, z)
    return sorted([v[1] for v in best.values()] + sem_competencia)


def parse_fixed_width_lines(
    lines: list[str], layout: list[FixedField], comp: str, ver: int
) -> pl.DataFrame:
    """Parse raw fixed-width lines into a Polars DataFrame using layout definition."""
    kinds = [(f, *_effective_kind(f)) for f in layout]
    rows: list[dict[str, Any]] = []
    for line in lines:
        if not line.strip():
            continue
        row: dict[str, Any] = {"competencia": comp, "versao": ver}
        for f, kind, scale in kinds:
            # start is 1-based index
            s_idx = f.start - 1
            e_idx = s_idx + f.width
            raw_val = line[s_idx:e_idx].strip() if s_idx < len(line) else ""
            if not raw_val:
                row[f.name] = None
            elif kind == "int":
                try:
                    row[f.name] = int(raw_val)
                except ValueError:
                    row[f.name] = None
            elif kind == "decimal":
                try:
                    num = float(raw_val)
                    row[f.name] = num / (10**scale) if scale > 0 else num
                except ValueError:
                    row[f.name] = None
            else:
                row[f.name] = raw_val
        rows.append(row)

    schema = _frame_schema(layout)
    if not rows:
        return pl.DataFrame(schema=schema)
    return pl.DataFrame(rows, schema=schema, infer_schema_length=None)


def _frame_schema(layout: list[FixedField]) -> dict[str, Any]:
    """Schema explicito das colunas de uma tabela.

    A inferencia olha so as primeiras linhas e uma coluna vazia nelas virava Null,
    quebrando no primeiro valor de texto.
    """
    schema: dict[str, Any] = {"competencia": pl.Utf8, "versao": pl.Int64}
    schema.update({f.name: _DTYPES[_effective_kind(f)[0]] for f in layout})
    return schema


def _competencia_e_versao(path: Path) -> tuple[str, int] | None:
    """``(AAAAMM, versao)`` do nome do ZIP; ``None`` sem competencia reconhecivel."""
    match = COMPETENCIA_RE.search(path.name)
    if match:
        return match.group("competencia"), int(match.group("version") or 0)
    m_comp = re.search(r"\b(20\d{4})\b", path.stem)
    return (m_comp.group(1), 0) if m_comp else None


class _Zip:
    """Um ZIP mensal do bruto. So e aberto quando alguma tabela precisa dele."""

    def __init__(self, path: Path, comp: str, ver: int) -> None:
        self.path = path
        self.comp = comp
        self.ver = ver
        self.key = composite_file_key(path)
        self.falha: str | None = None  # erro ao abrir, se houve
        self.tabelas: dict[str, str] = {}  # tabela -> nome do membro no ZIP
        self.layouts: dict[str, list[FixedField]] = {}
        self._zf: zipfile.ZipFile | None = None
        self._sha256: str | None = None

    @property
    def sha256(self) -> str:
        if self._sha256 is None:
            self._sha256 = sha256_file(self.path)
        return self._sha256

    def abrir(self, pilha: ExitStack) -> bool:
        """Abre o ZIP uma vez (fechado com ``pilha``); ``False`` se nao abre."""
        if self._zf is not None:
            return True
        if self.falha is not None:
            return False
        try:
            zf = pilha.enter_context(zipfile.ZipFile(self.path, "r"))
            self.layouts = _extract_layouts_from_zip(zf)
            self.tabelas = {
                Path(n).stem.lower(): n for n in zf.namelist() if _is_table_member(n)
            }
        except Exception as exc:
            self.falha = str(exc)
            return False
        self._zf = zf
        return True

    def tamanho(self, tabela: str) -> int:
        assert self._zf is not None
        return self._zf.getinfo(self.tabelas[tabela]).file_size

    def linhas(self, tabela: str) -> list[str]:
        assert self._zf is not None
        return self._zf.read(self.tabelas[tabela]).decode("latin-1").splitlines()


@dataclass
class _Membro:
    """Uma tabela de um ZIP, membro do grupo (tabela, ano)."""

    zip: _Zip
    # None para o membro em dia (o ZIP nao foi aberto para resolver o layout).
    layout: list[FixedField] | None = None


class _Conversao:
    """Uma execucao de ``convert``: escritores por tabela e caches da rodada."""

    def __init__(
        self, lake_dir: Path, force: bool, zip_comps: list[tuple[str, Path]]
    ) -> None:
        self.lake_dir = lake_dir
        self.force = force
        self.zip_comps = zip_comps
        self.writers: dict[str, LakeWriter] = {}
        self.emprestados: dict[tuple[str, str], list[FixedField] | None] = {}

    def writer(self, tabela: str) -> LakeWriter:
        if tabela not in self.writers:
            self.writers[tabela] = LakeWriter(
                self.lake_dir / SOURCE_ID / tabela,
                DatasetDescriptor(
                    source_id=SOURCE_ID,
                    dataset_id=tabela,
                    alias=tabela,
                    partition_keys=PARTITION_KEYS,
                    partition_types=partition_types_for(PARTITION_KEYS),
                ),
                force=self.force,
            )
        return self.writers[tabela]

    def ano(
        self,
        ano: int,
        zips: list[_Zip],
        alvos: set[str] | None,
        pilha: ExitStack,
        res: ConvertResult,
    ) -> None:
        """Converte as tabelas dos ZIPs de um ano, um arquivo por tabela."""
        if alvos is None:
            # Sem alvo nao se sabe quais tabelas ha: todo ZIP e aberto.
            for z in zips:
                self._abrir(z, pilha, res)
            tabelas = sorted({t for z in zips for t in z.tabelas})
        else:
            tabelas = sorted(alvos)
        for tabela in tabelas:
            self._grupo(tabela, ano, zips, pilha, res)

    def _abrir(self, z: _Zip, pilha: ExitStack, res: ConvertResult) -> bool:
        ja_falhou = z.falha is not None
        if z.abrir(pilha):
            return True
        if not ja_falhou:
            res.errors.append(f"Erro em {z.path.name}: {z.falha}")
        return False

    def _grupo(
        self,
        tabela: str,
        ano: int,
        zips: list[_Zip],
        pilha: ExitStack,
        res: ConvertResult,
    ) -> None:
        writer = self.writer(tabela)
        particoes = {"ano": ano}
        saidas = [output_id(particoes, tabela)]
        membros: list[_Membro] = []
        erro_de_membro = False
        for z in zips:
            # O ZIP em dia nao e aberto: o arquivo do ano ja o registra como
            # membro. Tabela sem membro (ausente do ZIP ou nao convertida) nao
            # esta em dia e o ZIP e aberto.
            if writer.is_current_member(
                z.path,
                group_key=tabela,
                partitions=particoes,
                member_key=z.key,
                contract_version=CONTRACT_VERSION,
                origin_outputs=saidas,
            ):
                membros.append(_Membro(z))
                continue
            if not self._abrir(z, pilha, res) or tabela not in z.tabelas:
                continue
            # Cada tabela tem o seu `<tabela>_layout.txt`. Sem ele a tabela nao e
            # convertida (nunca emprestar o layout de outra).
            layout, erro = self._layout(z, tabela, conferir=True)
            if erro:
                res.errors.append(erro)
                erro_de_membro = True
            elif z.tamanho(tabela) == 0:
                logger.info(
                    "sigtap: %s %s vazia no ZIP; nada a converter", z.comp, tabela
                )
            else:
                membros.append(_Membro(z, layout))
        if not membros:
            return
        # Membro que nao pode ser lido nao deve apagar as linhas que o arquivo do
        # ano ja tem dele: sem prune o que nao esta na lista fica como esta.
        prune = not (erro_de_membro or any(z.falha is not None for z in zips))
        grupo = [self._membro(m, tabela, saidas, pilha) for m in membros]
        arquivo = partition_dir(writer.dataset_dir, particoes) / f"{tabela}.parquet"
        opcoes: dict[str, Any] = {
            "partitions": particoes,
            "contract_version": CONTRACT_VERSION,
            "prune": prune,
        }
        try:
            if writer.is_current_group(tabela, grupo, **opcoes):
                res.skipped += len(grupo)
                return
            out = writer.write_group(
                tabela,
                grupo,
                sort_by=["mes"],
                schema=self._schema(arquivo, membros, tabela, pilha, res),
                **opcoes,
            )
        except Exception as exc:
            res.errors.append(f"Erro em {SOURCE_ID}/{tabela} ano={ano}: {exc}")
            return
        res.converted += len(out.written)
        res.skipped += len(out.kept)

    def _layout(
        self, z: _Zip, tabela: str, *, conferir: bool
    ) -> tuple[list[FixedField] | None, str | None]:
        """Layout da tabela no ZIP, ou o da mesma tabela na competencia mais proxima.

        ``conferir`` valida o layout emprestado contra a largura dos dados (le a
        tabela); sem ele so se descobre qual layout seria usado.
        """
        layout = z.layouts.get(tabela)
        if layout:
            return layout, None
        # Fallback explicito: layout da MESMA tabela na competencia mais proxima
        # (nunca o de outra tabela), aceito so se a largura bate com a dos dados.
        emprestado = _borrow_layout(tabela, z.comp, self.zip_comps, self.emprestados)
        if emprestado is None:
            return None, (
                f"{z.path.name}: {tabela} sem arquivo de layout "
                f"({tabela}_layout.txt) nem em outra competencia; "
                "tabela nao convertida"
            )
        src_comp, layout = emprestado
        if conferir:
            largura = max((len(x.rstrip("\r\n")) for x in z.linhas(tabela)), default=0)
            if largura != _layout_width(layout):
                return None, (
                    f"{z.path.name}: {tabela} sem layout; o de {src_comp} e "
                    f"incompativel (largura {_layout_width(layout)} contra "
                    f"{largura} nos dados); tabela nao convertida"
                )
            logger.warning(
                "sigtap: %s %s sem layout no ZIP; usando o de %s",
                z.comp,
                tabela,
                src_comp,
            )
        return layout, None

    def _membro(
        self, m: _Membro, tabela: str, saidas: list[str], pilha: ExitStack
    ) -> GroupMember:
        z = m.zip

        def dados() -> pl.DataFrame:
            # So chamada para o membro a gravar; o ZIP ja esta aberto, salvo se o
            # arquivo do ano nao confirmou um membro dado como em dia.
            if not z.abrir(pilha):
                raise OSError(f"{z.path.name}: {z.falha}")
            layout = m.layout
            if layout is None:
                layout, erro = self._layout(z, tabela, conferir=True)
                if layout is None:
                    raise ValueError(erro)
            return parse_fixed_width_lines(z.linhas(tabela), layout, z.comp, z.ver)

        return GroupMember(
            src=z.path,
            data=dados,
            key=z.key,
            columns={"mes": z.comp[4:6]},
            sha256=z.sha256,
            origin_outputs=saidas,
        )

    def _schema(
        self,
        arquivo: Path,
        membros: list[_Membro],
        tabela: str,
        pilha: ExitStack,
        res: ConvertResult,
    ) -> dict[str, Any]:
        """Uniao das colunas do arquivo do ano e dos membros a gravar.

        O layout de uma tabela ganha colunas no meio do ano (``tb_cid`` em 2011,
        por exemplo) e o grupo tem um esquema so: o membro que nao traz a coluna a
        recebe nula. As colunas dos membros em dia saem do rodape do arquivo do
        ano, sem abrir o ZIP deles.
        """
        schema: dict[str, Any] = {}
        try:
            existente = pl.read_parquet_schema(arquivo)
        except Exception:
            existente = None  # sem arquivo (ou ilegivel): nenhum membro esta nele
        for nome, tipo in (existente or {}).items():
            if nome not in (ORIGIN_COLUMN, "mes"):
                schema[nome] = tipo
        for m in membros:
            if m.layout is None and existente is None:
                if self._abrir(m.zip, pilha, res):
                    m.layout, _ = self._layout(m.zip, tabela, conferir=False)
            for nome, tipo in _frame_schema(m.layout or []).items():
                schema[nome] = tipo
        return schema


class SigtapLakeConverter:
    """Conversor do lake do SIGTAP."""

    source_id = SOURCE_ID

    def datasets(self) -> list[str]:
        return list(ALL_TABLES)

    def convert(
        self,
        input_dir: Path,
        lake_dir: Path,
        *,
        datasets: list[str] | None = None,
        force: bool = False,
    ) -> ConvertResult:
        res = ConvertResult()
        alvos = set(datasets) if datasets else None

        tabelas_dir = input_dir / "tabelas"
        if not tabelas_dir.is_dir():
            tabelas_dir = input_dir

        por_ano: dict[int, list[_Zip]] = {}
        for zpath in _current_by_competencia(list(tabelas_dir.glob("*.zip"))):
            achado = _competencia_e_versao(zpath)
            if achado:
                z = _Zip(zpath, *achado)
                por_ano.setdefault(int(z.comp[:4]), []).append(z)
        zip_comps = [(z.comp, z.path) for zs in por_ano.values() for z in zs]
        conversao = _Conversao(lake_dir, force, zip_comps)

        for ano in sorted(por_ano):
            zips = sorted(por_ano[ano], key=lambda z: (z.comp, z.path.name))
            # Os ZIPs do ano ficam abertos enquanto as tabelas do ano sao gravadas.
            with ExitStack() as pilha:
                conversao.ano(ano, zips, alvos, pilha, res)
        return res


converter = SigtapLakeConverter()
