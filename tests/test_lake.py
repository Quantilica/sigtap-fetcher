"""Tests for SIGTAP lake conversion."""

from __future__ import annotations

import shutil
from pathlib import Path

import polars as pl
from quantilica.analytics.lake import check_dataset

from sigtap_fetcher.lake import converter

FIXTURES_DIR = Path(__file__).parent / "fixtures"


def test_converter_metadata() -> None:
    """Test converter datasets."""
    assert converter.source_id == "sigtap"
    assert "tb_procedimento" in converter.datasets()
    assert "tb_grupo" in converter.datasets()


def test_convert_sigtap_zip_fixtures(tmp_path: Path) -> None:
    """Test converting real minimal SIGTAP ZIP fixtures into Hive Parquet Lake."""
    raw_dir = tmp_path / "raw" / "tabelas"
    raw_dir.mkdir(parents=True)
    lake_dir = tmp_path / "lake"
    lake_dir.mkdir(parents=True)

    # Copy the 3 competence ZIPs
    comps = ["200801", "201605", "202610"]
    for comp in comps:
        src = FIXTURES_DIR / f"TabelaUnificada_{comp}.zip"
        assert src.is_file()
        shutil.copy2(src, raw_dir / f"TabelaUnificada_{comp}@20261101.zip")

    # Run conversion
    res = converter.convert(tmp_path / "raw", lake_dir)
    assert not res.errors, f"Errors: {res.errors}"
    assert res.converted >= 15  # 5 tables x 3 competences
    assert res.skipped == 0

    # Verify check_dataset passes on tb_procedimento and tb_grupo
    for t_name in (
        "tb_procedimento",
        "tb_grupo",
        "tb_subgrupo",
        "tb_forma_organizacao",
        "tb_rubrica",
    ):
        ds_dir = lake_dir / "sigtap" / t_name
        assert ds_dir.is_dir()
        errors = check_dataset(ds_dir)
        assert not errors, f"check_dataset failed for {t_name}: {errors}"

    # Verify centavos conversion on tb_procedimento: 1000 cents must be 10.00
    df_proc = pl.read_parquet(lake_dir / "sigtap" / "tb_procedimento/**/*.parquet")
    assert "vl_sh" in df_proc.columns
    # 0000001000 / 100 = 10.0
    val_10 = df_proc.filter(pl.col("co_procedimento") == "0101010010")["vl_sh"][0]
    assert val_10 == 10.0

    # Second conversion skips current files
    res2 = converter.convert(tmp_path / "raw", lake_dir)
    assert not res2.errors
    assert res2.skipped >= 15


def test_table_without_layout_is_an_error_not_first_table_layout(
    tmp_path: Path,
) -> None:
    """Regressão A5: sem `*_layout`, a tabela usava o layout da primeira tabela."""
    import zipfile

    raw = tmp_path / "raw" / "tabelas"
    raw.mkdir(parents=True)
    with zipfile.ZipFile(raw / "TabelaUnificada_202610@20261101.zip", "w") as zf:
        zf.writestr(
            "tb_grupo_layout.txt", "CO_GRUPO,2,1,2,CHAR\nNO_GRUPO,10,3,12,CHAR\n"
        )
        zf.writestr("tb_grupo.txt", "01ACOES     \n")
        # tb_subgrupo sem tb_subgrupo_layout.txt
        zf.writestr("tb_subgrupo.txt", "0101ABCDEFGH\n")
    lake = tmp_path / "lake"
    res = converter.convert(tmp_path / "raw", lake)

    assert res.converted == 1  # só tb_grupo
    assert len(res.errors) == 1
    assert "tb_subgrupo" in res.errors[0] and "layout" in res.errors[0]
    assert not (lake / "sigtap" / "tb_subgrupo").exists()
