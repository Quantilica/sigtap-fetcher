"""Universal Hive Parquet Lake converter for sigtap-fetcher."""

from __future__ import annotations

import logging
import re
import zipfile
from pathlib import Path
from typing import Any

try:
    import polars as pl
    from quantilica.analytics.fixed_width import FixedField, layout_from_datasus
    from quantilica.analytics.lake import ConvertResult, LakeWriter
    from quantilica.core.lake import (
        DatasetDescriptor,
        composite_file_key,
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

    # Schema explicito: a inferencia olha so as primeiras linhas e uma coluna vazia
    # nelas virava Null, quebrando no primeiro valor de texto.
    schema = {"competencia": pl.Utf8, "versao": pl.Int64}
    schema.update({f.name: _DTYPES[kind] for f, kind, _ in kinds})
    if not rows:
        return pl.DataFrame(schema=schema)
    return pl.DataFrame(rows, schema=schema, infer_schema_length=None)


class SigtapLakeConverter:
    """Universal Hive Parquet Lake converter for SIGTAP."""

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
        target_datasets = set(datasets) if datasets else None

        tabelas_dir = input_dir / "tabelas"
        if not tabelas_dir.is_dir():
            tabelas_dir = input_dir

        zip_files = _current_by_competencia(list(tabelas_dir.glob("*.zip")))
        writers: dict[str, LakeWriter] = {}

        def get_writer(table_name: str) -> LakeWriter:
            if table_name not in writers:
                writers[table_name] = LakeWriter(
                    lake_dir / SOURCE_ID / table_name,
                    DatasetDescriptor(
                        source_id=SOURCE_ID,
                        dataset_id=table_name,
                        alias=table_name,
                        partition_keys=["competencia"],
                        partition_types=partition_types_for(["competencia"]),
                    ),
                    force=force,
                )
            return writers[table_name]

        zip_comps: list[tuple[str, Path]] = []
        for z in zip_files:
            m_z = COMPETENCIA_RE.search(z.name) or re.search(r"\b(20\d{4})\b", z.stem)
            if m_z:
                zip_comps.append((m_z.group(m_z.lastindex or 0), z))
        borrowed_cache: dict[tuple[str, str], list[FixedField] | None] = {}

        for zpath in zip_files:
            match = COMPETENCIA_RE.search(zpath.name)
            if not match:
                # Try finding 6-digit year-month in stem
                m_comp = re.search(r"\b(20\d{4})\b", zpath.stem)
                if m_comp:
                    comp = m_comp.group(1)
                    ver = 0
                else:
                    continue
            else:
                comp = match.group("competencia")
                ver = int(match.group("version") or 0)

            try:
                with zipfile.ZipFile(zpath, "r") as zf:
                    layouts = _extract_layouts_from_zip(zf)
                    names = zf.namelist()
                    data_files = [n for n in names if _is_table_member(n)]

                    for dfile in data_files:
                        table_name = Path(dfile).stem.lower()
                        if target_datasets and table_name not in target_datasets:
                            continue

                        writer = get_writer(table_name)
                        # Sem membro (a tabela e o dataset): igual a file_key(zpath).
                        file_key_name = composite_file_key(zpath)
                        if not force and writer.is_current(
                            zpath,
                            partitions={"competencia": comp},
                            file_key_name=file_key_name,
                        ):
                            res.skipped += 1
                            continue

                        # Cada tabela tem o seu `<tabela>_layout.txt`. Sem ele a
                        # tabela nao e convertida (nunca emprestar o layout de outra).
                        content = zf.read(dfile).decode("latin-1")
                        lines = content.splitlines()
                        layout = layouts.get(table_name)
                        if not layout:
                            # Fallback explicito: layout da MESMA tabela na
                            # competencia mais proxima (nunca o de outra tabela),
                            # aceito so se a largura bate com a dos dados.
                            borrowed = _borrow_layout(
                                table_name, comp, zip_comps, borrowed_cache
                            )
                            if borrowed is None:
                                res.errors.append(
                                    f"{zpath.name}: {table_name} sem arquivo de "
                                    f"layout ({table_name}_layout.txt) nem em outra "
                                    "competencia; tabela nao convertida"
                                )
                                continue
                            src_comp, layout = borrowed
                            width = max(
                                (len(x.rstrip("\r\n")) for x in lines), default=0
                            )
                            if width != _layout_width(layout):
                                res.errors.append(
                                    f"{zpath.name}: {table_name} sem layout; o de "
                                    f"{src_comp} e incompativel (largura "
                                    f"{_layout_width(layout)} contra {width} nos "
                                    "dados); tabela nao convertida"
                                )
                                continue
                            logger.warning(
                                "sigtap: %s %s sem layout no ZIP; usando o de %s",
                                comp,
                                table_name,
                                src_comp,
                            )
                        df = parse_fixed_width_lines(lines, layout, comp, ver)
                        if df.height > 0:
                            writer.write_polars(
                                df,
                                zpath,
                                partitions={"competencia": comp},
                                file_key_name=file_key_name,
                            )
                            res.converted += 1
            except Exception as exc:
                res.errors.append(f"Erro em {zpath.name}: {exc}")

        return res


converter = SigtapLakeConverter()
