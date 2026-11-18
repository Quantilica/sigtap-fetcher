"""Conversor do lake do SIGTAP: um Parquet por tabela e por ano.

Cada tabela do ZIP mensal vira o membro de um grupo do ano
(``sigtap/<tabela>/ano=AAAA/<tabela>.parquet``), com a competência ``mes`` (texto
``MM``) como coluna do membro. Mês novo reescreve só o arquivo do ano; competência
em dia não abre o ZIP.
"""

from __future__ import annotations

import json
import logging
import zipfile
from contextlib import ExitStack
from dataclasses import dataclass
from pathlib import Path
from typing import Any

try:
    import polars as pl
    import pyarrow.parquet as pq
    from quantilica.analytics.fixed_width import FixedField, layout_from_datasus
    from quantilica.analytics.lake import (
        META_MEMBERS,
        ORIGIN_COLUMN,
        ConvertResult,
        GroupMember,
        LakeWriter,
        footer_from_metadata,
        member_matches,
        output_id,
        sha256_file,
    )
    from quantilica.core.lake import (
        DatasetDescriptor,
        composite_file_key,
        dataset_lock,
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
    """``(AAAAMM, versao)`` do nome do ZIP; ``None`` fora de ``COMPETENCIA_RE``."""
    match = COMPETENCIA_RE.search(path.name)
    if match is None:
        return None
    return match.group("competencia"), int(match.group("version") or 0)


class _Zip:
    """Um ZIP mensal do bruto. So e aberto quando alguma tabela precisa dele."""

    def __init__(self, path: Path, comp: str, ver: int) -> None:
        self.path = path
        self.comp = comp
        self.ver = ver
        self.key = composite_file_key(path)
        self.falha: str | None = None  # erro ao abrir, se houve
        self.tabelas: dict[str, str] = {}  # tabela -> nome do membro no ZIP
        self._layouts: dict[str, list[FixedField]] | None = None
        self._zf: zipfile.ZipFile | None = None
        self._sha256: str | None = None

    @property
    def sha256(self) -> str:
        if self._sha256 is None:
            self._sha256 = sha256_file(self.path)
        return self._sha256

    @property
    def layouts(self) -> dict[str, list[FixedField]]:
        """Layouts do ZIP; so os le (descomprime) quando alguem os pede."""
        assert self._zf is not None
        if self._layouts is None:
            self._layouts = _extract_layouts_from_zip(self._zf)
        return self._layouts

    def abrir(self, pilha: ExitStack) -> bool:
        """Le o diretorio central uma vez (fechado com ``pilha``).

        So a lista de membros: nada e descomprimido. ``False`` se nao abre.
        """
        if self._zf is not None:
            return True
        if self.falha is not None:
            return False
        try:
            zf = pilha.enter_context(zipfile.ZipFile(self.path, "r"))
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
    """Uma tabela de um ZIP, membro do grupo (tabela, ano).

    ``tipo``: ``dados`` (a gravar), ``atual`` (ja no arquivo do ano com o sha do ZIP;
    o ZIP nao e aberto), ``vazio`` (a tabela falta no ZIP ou nao tem linhas: membro de
    0 linhas, para o ZIP ficar em dia) e ``preservado`` (o ZIP falhou: as linhas que o
    arquivo ja tem dele ficam como estao).
    """

    zip: _Zip
    tipo: str
    layout: list[FixedField] | None = None
    entrada: dict[str, Any] | None = None  # entrada do arquivo do ano, se ja houver

    @property
    def linhas_no_arquivo(self) -> int:
        return int((self.entrada or {}).get("rows", 0))


def _entradas(arquivo: Path) -> dict[str, dict[str, Any]]:
    """``quantilica.members`` do arquivo do ano; vazio sem arquivo ou sem rodape."""
    try:
        meta = footer_from_metadata(pq.ParquetFile(arquivo).metadata)
        membros = json.loads(meta[META_MEMBERS])
    except Exception:
        return {}
    return {k: v for k, v in membros.items() if isinstance(v, dict)}


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

    def arquivo(self, tabela: str, ano: int) -> Path:
        return partition_dir(self.writer(tabela).dataset_dir, {"ano": ano}) / (
            f"{tabela}.parquet"
        )

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
            # Sem alvo nao se sabe quais tabelas ha: le-se o diretorio central de
            # todo ZIP (so a lista de membros). Tambem entram as tabelas que ja
            # tem arquivo do ano, para o que saiu de todos os ZIPs sair do arquivo.
            for z in zips:
                self._abrir(z, pilha, res)
            tabelas = {t for z in zips for t in z.tabelas}
            tabelas |= {
                t for t in self._tabelas_do_lake() if self.arquivo(t, ano).is_file()
            }
        else:
            tabelas = alvos
        for tabela in sorted(tabelas):
            self._grupo(tabela, ano, zips, pilha, res)

    def _tabelas_do_lake(self) -> list[str]:
        base = self.lake_dir / SOURCE_ID
        return (
            sorted(p.name for p in base.iterdir() if p.is_dir())
            if base.is_dir()
            else []
        )

    def sem_origem(self, anos_do_bruto: set[int], alvos: set[str] | None) -> None:
        """Apaga o arquivo de um ano em que nenhum ZIP do bruto resta.

        Sem ZIP nenhum no bruto (montagem fora do ar, pasta vazia) nada e apagado.
        """
        if not anos_do_bruto:
            return
        for tabela in sorted(alvos) if alvos is not None else self._tabelas_do_lake():
            base = self.writer(tabela).dataset_dir
            for pasta in sorted(base.glob("ano=*")) if base.is_dir() else []:
                try:
                    ano = int(pasta.name.split("=", 1)[1])
                except ValueError:
                    continue
                if ano not in anos_do_bruto:
                    self._remover(tabela, ano)

    def _remover(self, tabela: str, ano: int) -> None:
        """Apaga o arquivo do ano de uma tabela, se for um arquivo de grupo."""
        arquivo = self.arquivo(tabela, ano)
        with dataset_lock(self.writer(tabela).dataset_dir):
            if not _entradas(arquivo):
                return
            arquivo.unlink()
            logger.info(
                "sigtap: %s ano=%s sem ZIP de origem; arquivo removido", tabela, ano
            )
            try:
                arquivo.parent.rmdir()  # so se esvaziou
            except OSError:
                pass

    def _abrir(self, z: _Zip, pilha: ExitStack, res: ConvertResult) -> bool:
        ja_falhou = z.falha is not None
        if z.abrir(pilha):
            return True
        if not ja_falhou:
            res.errors.append(f"Erro em {z.path.name}: {z.falha}")
        return False

    def _ler_sha(self, z: _Zip, res: ConvertResult) -> bool:
        """Calcula o sha do ZIP; erro de leitura e falha so dele (uma vez)."""
        if z.falha is not None:
            return False
        try:
            _ = z.sha256
        except Exception as exc:
            z.falha = str(exc)
            res.errors.append(f"Erro em {z.path.name}: {z.falha}")
            return False
        return True

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
        arquivo = self.arquivo(tabela, ano)
        entradas = _entradas(arquivo)
        membros: list[_Membro] = []
        falhou = False

        def preservar(z: _Zip) -> None:
            # O ZIP nao pode ser lido: as linhas que o arquivo ja tem dele (a
            # entrada de mesma chave ou, se o ZIP foi regerado com outra versao, a
            # da mesma competencia) ficam como estao.
            for chave, entrada in entradas.items():
                if chave == z.key or entrada.get("mes") == z.comp[4:6]:
                    membros.append(
                        _Membro(z, "preservado", entrada=dict(entrada, chave=chave))
                    )
                    return

        for z in zips:
            # O ZIP em dia nao e aberto: o arquivo do ano ja o registra como
            # membro (inclusive o de 0 linhas, de tabela ausente ou vazia).
            if not self._ler_sha(z, res):
                falhou = True
                preservar(z)
                continue
            if not writer.force and member_matches(
                arquivo,
                tabela,
                z.key,
                z.sha256,
                layout_version=writer.descriptor.layout_version,
                contract_version=CONTRACT_VERSION,
                origin_outputs=saidas,
            ):
                membros.append(_Membro(z, "atual", entrada=entradas.get(z.key)))
                continue
            if not self._abrir(z, pilha, res):
                falhou = True
                preservar(z)
            elif tabela not in z.tabelas or z.tamanho(tabela) == 0:
                membros.append(_Membro(z, "vazio"))
            else:
                # Cada tabela tem o seu `<tabela>_layout.txt`. Sem ele a tabela nao
                # e convertida (nunca emprestar o layout de outra).
                layout, erro = self._layout(z, tabela, conferir=True)
                if erro:
                    res.errors.append(erro)
                    falhou = True
                    preservar(z)
                else:
                    membros.append(_Membro(z, "dados", layout))

        tem_dados = any(m.tipo == "dados" or m.linhas_no_arquivo > 0 for m in membros)
        if not tem_dados:
            # Nenhum ZIP do ano traz linhas da tabela: sem arquivo. Se algum ZIP
            # falhou, nao se sabe o que ele trazia e o arquivo fica como esta.
            if not falhou and arquivo.is_file():
                self._remover(tabela, ano)
            return

        grupo = [self._membro(m, tabela, saidas, pilha, arquivo) for m in membros]
        # So os membros com linhas entram na conta; os de 0 linhas e os preservados
        # (o ZIP falhou) nao sao conversao nem pulo.
        contaveis = {
            m.zip.key
            for m in membros
            if m.tipo == "dados" or (m.tipo == "atual" and m.linhas_no_arquivo > 0)
        }
        opcoes: dict[str, Any] = {
            "partitions": particoes,
            "contract_version": CONTRACT_VERSION,
        }
        try:
            if writer.is_current_group(tabela, grupo, **opcoes):
                res.skipped += len(contaveis)
                return
            out = writer.write_group(
                tabela,
                grupo,
                schema=self._schema(arquivo, membros, tabela, pilha, res),
                **opcoes,
            )
        except Exception as exc:
            res.errors.append(f"Erro em {SOURCE_ID}/{tabela} ano={ano}: {exc}")
            return
        res.converted += len(contaveis & set(out.written))
        res.skipped += len(contaveis & set(out.kept))

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
        self,
        m: _Membro,
        tabela: str,
        saidas: list[str],
        pilha: ExitStack,
        arquivo: Path,
    ) -> GroupMember:
        z = m.zip
        if m.tipo == "preservado":
            return self._preservado(m, saidas, arquivo)

        def dados() -> pl.DataFrame:
            if m.tipo == "vazio":
                return pl.DataFrame(schema=_frame_schema([]))
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

    def _preservado(self, m: _Membro, saidas: list[str], arquivo: Path) -> GroupMember:
        """Membro de um ZIP que falhou: fica o que o arquivo do ano ja tem dele.

        Com o mesmo sha, colunas e saidas da entrada, o grupo o considera em dia e
        copia as linhas, sem chamar ``data``. Com ``force`` o grupo chama ``data``,
        que devolve as mesmas linhas, lidas do arquivo. So nao da para preservar a
        entrada gravada com outro contrato (ou sem a declaracao de saidas): ai o
        grupo falha, com a causa.
        """
        z, entrada = m.zip, m.entrada
        assert entrada is not None
        chave = entrada["chave"]
        contrato = entrada.get("contract_version")
        if contrato != CONTRACT_VERSION or sorted(entrada.get("outputs") or []) != (
            sorted(saidas)
        ):

            def impossivel() -> pl.DataFrame:
                raise ValueError(
                    f"{z.path.name} nao pode ser lido ({z.falha}) e as linhas dele "
                    f"no arquivo do ano foram gravadas com outro contrato de "
                    f"conversao (versao {contrato}, a atual e {CONTRACT_VERSION}) "
                    "ou sem a declaracao de saidas: nao da para preserva-las; "
                    "corrija o ZIP"
                )

            dados = impossivel
        else:

            def antigas() -> pl.DataFrame:
                df = pl.read_parquet(arquivo, hive_partitioning=False)
                return df.filter(pl.col(ORIGIN_COLUMN) == chave).drop(
                    ORIGIN_COLUMN, "mes"
                )

            dados = antigas
        return GroupMember(
            src=z.path,
            data=dados,
            key=chave,
            columns={"mes": str(entrada.get("mes", z.comp[4:6]))},
            sha256=entrada.get("origin_sha256"),
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
        ano, sem abrir o ZIP deles. Coluna com tipo diferente entre dois layouts do
        ano e erro (promover calado, de inteiro a texto, perderia os zeros a
        esquerda): o grupo falha e os demais seguem.
        """
        schema: dict[str, Any] = {}
        origem: dict[str, str] = {}

        def somar(nome: str, tipo: Any, de: str) -> None:
            if nome in schema and schema[nome] != tipo:
                raise ValueError(
                    f"coluna {nome}: tipo {schema[nome]} em {origem[nome]} e {tipo} "
                    f"em {de}; o tipo de uma coluna nao pode mudar dentro do ano"
                )
            schema[nome] = tipo
            origem.setdefault(nome, de)

        try:
            # Com force todo membro e regravado e o tipo do arquivo antigo nao conta,
            # salvo se um membro preservado volta a ele pelas linhas do arquivo.
            preserva = any(m.tipo == "preservado" for m in membros)
            existente = (
                None if self.force and not preserva else pl.read_parquet_schema(arquivo)
            )
        except Exception:
            existente = None  # sem arquivo (ou ilegivel): nenhum membro esta nele
        for nome, tipo in (existente or {}).items():
            if nome not in (ORIGIN_COLUMN, "mes"):
                somar(nome, tipo, "o arquivo do ano")
        for m in membros:
            if m.tipo == "atual" and m.layout is None and existente is None:
                if self._abrir(m.zip, pilha, res):
                    m.layout, _ = self._layout(m.zip, tabela, conferir=False)
            if m.layout is not None:
                for nome, tipo in _frame_schema(m.layout).items():
                    somar(nome, tipo, m.zip.path.name)
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
            if achado is None:
                # Uma copia ou um nome improvisado duplicaria a competencia.
                res.errors.append(
                    f"{zpath.name}: nome fora do padrao "
                    "TabelaUnificada_AAAAMM[_vAAMMDDHHMM][@carimbo].zip; "
                    "nao convertido"
                )
                continue
            z = _Zip(zpath, *achado)
            por_ano.setdefault(int(z.comp[:4]), []).append(z)
        zip_comps = [(z.comp, z.path) for zs in por_ano.values() for z in zs]
        conversao = _Conversao(lake_dir, force, zip_comps)

        for ano in sorted(por_ano):
            zips = sorted(por_ano[ano], key=lambda z: (z.comp, z.path.name))
            # Os ZIPs do ano ficam abertos enquanto as tabelas do ano sao gravadas.
            with ExitStack() as pilha:
                conversao.ano(ano, zips, alvos, pilha, res)
        conversao.sem_origem(set(por_ano), alvos)
        return res


converter = SigtapLakeConverter()
