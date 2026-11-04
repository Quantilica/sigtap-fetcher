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


def _zip(path: Path, tabelas: dict[str, tuple[str, str]], extra: dict | None = None):
    import zipfile

    with zipfile.ZipFile(path, "w") as zf:
        for nome, (layout, dados) in tabelas.items():
            zf.writestr(f"{nome}_layout.txt", layout)
            zf.writestr(f"{nome}.txt", dados.encode("latin-1"))
        for nome, conteudo in (extra or {}).items():
            zf.writestr(nome, conteudo)


_GRUPO = ("Coluna,Tamanho,Inicio,Fim,Tipo\nCO_GRUPO,2,1,2,VARCHAR2\n", "01\n02\n")


def test_so_a_versao_vigente_de_cada_competencia(tmp_path: Path) -> None:
    """select_current agrupava por chave com `_v`: duas versoes da mesma
    competencia viravam duas partidas vigentes."""
    raw = tmp_path / "raw" / "tabelas"
    raw.mkdir(parents=True)
    velha = raw / "TabelaUnificada_202610_v2610011000@20261002.zip"
    nova = raw / "TabelaUnificada_202610_v2610271043@20261028.zip"
    _zip(
        velha,
        {
            "tb_grupo": (
                "Coluna,Tamanho,Inicio,Fim,Tipo\nCO_GRUPO,2,1,2,VARCHAR2\n",
                "01\n",
            )
        },
    )
    _zip(nova, {"tb_grupo": _GRUPO})
    lake = tmp_path / "lake"
    res = converter.convert(tmp_path / "raw", lake)
    assert not res.errors
    assert res.converted == 1  # so a versao vigente
    df = pl.read_parquet(lake / "sigtap" / "tb_grupo" / "**" / "*.parquet")
    assert df["versao"].unique().to_list() == [2610271043]
    assert df.height == 2


def test_coluna_esparsa_nao_quebra_a_inferencia(tmp_path: Path) -> None:
    """Coluna vazia nas primeiras 100 linhas virava tipo Null e quebrava no 1o
    valor texto (rl_procedimento_habilitacao no SIGTAP real)."""
    layout = (
        "Coluna,Tamanho,Inicio,Fim,Tipo\nCO_A,2,1,2,VARCHAR2\nNU_B,4,3,6,VARCHAR2\n"
    )
    linhas = "".join(f"{i % 90 + 10:02d}    \n" for i in range(150)) + "990001\n"
    raw = tmp_path / "raw" / "tabelas"
    raw.mkdir(parents=True)
    _zip(
        raw / "TabelaUnificada_202610_v2610271043@20261028.zip",
        {"rl_x": (layout, linhas)},
    )
    lake = tmp_path / "lake"
    res = converter.convert(tmp_path / "raw", lake)
    assert not res.errors, res.errors
    df = pl.read_parquet(lake / "sigtap" / "rl_x" / "**" / "*.parquet")
    assert df.height == 151
    assert df["nu_b"].null_count() == 150
    assert "0001" in df["nu_b"].to_list()


def test_arquivos_auxiliares_do_zip_nao_viram_tabela(tmp_path: Path) -> None:
    """LEIA_ME.TXT e o layout.txt consolidado nao sao tabelas."""
    raw = tmp_path / "raw" / "tabelas"
    raw.mkdir(parents=True)
    _zip(
        raw / "TabelaUnificada_202610_v2610271043@20261028.zip",
        {"tb_grupo": _GRUPO},
        {
            "LEIA_ME.TXT": "leia-me",
            "layout.txt": (
                "tb_grupo\nColuna,Tamanho,Inicio,Fim,Tipo\nCO_GRUPO,2,1,2,VARCHAR2\n"
            ),
        },
    )
    lake = tmp_path / "lake"
    res = converter.convert(tmp_path / "raw", lake)
    assert not res.errors, res.errors
    assert sorted(p.name for p in (lake / "sigtap").iterdir()) == ["tb_grupo"]


def test_idade_e_contagem_nao_dividem_por_100(tmp_path: Path) -> None:
    layout = (
        "Coluna,Tamanho,Inicio,Fim,Tipo\n"
        "CO_P,2,1,2,VARCHAR2\nVL_IDADE_MINIMA,4,3,6,NUMBER\n"
        "VL_SH,6,7,12,NUMBER\n"
    )
    raw = tmp_path / "raw" / "tabelas"
    raw.mkdir(parents=True)
    _zip(
        raw / "TabelaUnificada_202610_v2610271043@20261028.zip",
        {"tb_procedimento": (layout, "010012001000\n")},
    )
    lake = tmp_path / "lake"
    res = converter.convert(tmp_path / "raw", lake)
    assert not res.errors, res.errors
    df = pl.read_parquet(lake / "sigtap" / "tb_procedimento" / "**" / "*.parquet")
    assert df["vl_idade_minima"][0] == 12  # meses, nao centavos
    assert df["vl_sh"][0] == 10.0  # centavos


def test_datasets_cobre_as_41_tabelas_reais() -> None:
    from sigtap_fetcher.constants import ALL_TABLES

    assert len(ALL_TABLES) == 41 == len(set(ALL_TABLES))
    assert set(converter.datasets()) == set(ALL_TABLES)
    assert "tb_sub_grupo" in ALL_TABLES and "rl_procedimento_cid" in ALL_TABLES
