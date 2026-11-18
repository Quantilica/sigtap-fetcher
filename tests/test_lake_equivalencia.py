"""Prova de equivalência: o arquivo do ano tem as mesmas linhas de cada competência.

``golden/lake_por_competencia.json`` é o retrato (linhas, colunas e tipos, conteúdo
ordenado) do mesmo bruto gravado com um Parquet por tabela e competência. Aqui o
conversor lê os mesmos brutos, grava um Parquet por tabela e ano e o retrato de cada
competência, separada pela coluna ``mes``, tem de coincidir; só a pasta muda.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")

from sigtap_fetcher.lake import converter  # noqa: E402

from .lake_fixtures import GOLDEN, build_raw, parquets, snapshot  # noqa: E402


def _golden() -> dict:
    return json.loads(GOLDEN.read_text(encoding="utf-8"))["lake"]


def test_conteudo_de_cada_competencia_igual_ao_do_golden(tmp_path: Path) -> None:
    build_raw(tmp_path / "raw")
    res = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert not res.errors

    atual = snapshot(tmp_path / "lake")
    golden = _golden()

    assert sorted(atual) == sorted(golden)
    for tabela, esperado in golden.items():
        obtido = atual[tabela]
        assert sorted(obtido) == sorted(esperado["periodos"]), tabela
        for comp, dados in esperado["periodos"].items():
            lido = obtido[comp]
            assert lido["linhas"] == dados["linhas"], (tabela, comp)
            # As colunas da competência, com os mesmos tipos; as que só outro mês
            # do ano traz (o esquema do arquivo é a união) vêm nulas.
            for coluna in dados["colunas"]:
                assert coluna in lido["colunas"], (tabela, comp, coluna)
            nomes = [c for c, _ in dados["colunas"]]
            extras = {c for c, _ in lido["colunas"]} - set(nomes)
            assert not extras & set(lido["nao_nulas"]), (tabela, comp, extras)
            posicao = {c: i for i, (c, _) in enumerate(lido["colunas"])}
            projetado = sorted(
                [row[posicao[c]] for c in nomes] for row in lido["conteudo"]
            )
            assert projetado == dados["conteudo"], (tabela, comp)


def test_um_parquet_por_tabela_e_ano(tmp_path: Path) -> None:
    build_raw(tmp_path / "raw")
    converter.convert(tmp_path / "raw", tmp_path / "lake")

    lake = tmp_path / "lake" / "sigtap"
    esperado = {
        f"{tabela}/ano={comp[:4]}/{tabela}.parquet"
        for tabela, dados in _golden().items()
        for comp in dados["periodos"]
    }
    obtido = {str(p.relative_to(lake)) for p in parquets(tmp_path / "lake")}
    assert obtido == esperado
    # 5 tabelas em 3 anos (2008, 2016 e 2026, que junta 3 competências): 15 arquivos.
    assert len(obtido) == 15
    assert not list(lake.rglob("mes=*"))


def test_ano_e_mes_continuam_visiveis_na_consulta(tmp_path: Path) -> None:
    """A partição é só ``ano``; ``mes`` é coluna do arquivo e ``competencia``
    (AAAAMM) concorda com as duas."""
    import polars as pl
    from quantilica.analytics.lake import scan_dataset

    build_raw(tmp_path / "raw")
    converter.convert(tmp_path / "raw", tmp_path / "lake")
    df = scan_dataset(tmp_path / "lake" / "sigtap" / "tb_grupo").collect()

    assert {"competencia", "ano", "mes"} <= set(df.columns)
    esperado = df["ano"].cast(pl.String) + df["mes"]
    assert (df["competencia"] == esperado).all()
    assert sorted(df["mes"].unique().to_list()) == ["01", "05", "10", "11", "12"]
    assert df.filter(pl.col("mes") == "12").height == 1


def test_lake_profile_devolve_periodo_anual_das_tabelas(tmp_path: Path) -> None:
    """A partição é o ano: o perfil lê o período da pasta e o devolve por ano."""
    pytest.importorskip("pyarrow")
    from quantilica.core.lake_profile import profile_from_lake

    build_raw(tmp_path / "raw")
    converter.convert(tmp_path / "raw", tmp_path / "lake")

    perfil = profile_from_lake(tmp_path / "lake", "sigtap", "tb_grupo")

    doc = perfil.perfil
    assert doc["granularidade"] == "anual"
    assert doc["periodos"] == ["2008", "2016", "2026"]
    assert doc["linhas"] == [2, 2, 11]
    assert "versao" in doc["colunas"]
    assert "mes" not in doc["colunas"]
