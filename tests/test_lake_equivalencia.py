"""Prova de equivalência: o lake tem o mesmo conteúdo antes e depois da partição.

``golden/lake_antes_da_particao.json`` foi gerado pelo conversor que gravava em
``competencia=AAAAMM/`` (commit anterior à mudança). Aqui o conversor atual lê os
mesmos brutos e o retrato do lake, por tabela e competência (linhas, colunas e
tipos, conteúdo ordenado), tem de ser idêntico; só a pasta muda.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")

from sigtap_fetcher.lake import converter  # noqa: E402

from .lake_fixtures import (  # noqa: E402
    GOLDEN,
    build_raw,
    contagem_de_arquivos,
    snapshot,
)


def _golden() -> dict:
    return json.loads(GOLDEN.read_text(encoding="utf-8"))


def _viaje_json(obj: dict) -> dict:
    return json.loads(json.dumps(obj, ensure_ascii=False))


def test_conteudo_do_lake_igual_ao_do_conversor_anterior(tmp_path: Path) -> None:
    build_raw(tmp_path / "raw")
    res = converter.convert(tmp_path / "raw", tmp_path / "lake")
    assert not res.errors

    atual = _viaje_json(snapshot(tmp_path / "lake"))
    golden = _golden()["lake"]

    assert sorted(atual) == sorted(golden)
    for tabela, esperado in golden.items():
        obtido = atual[tabela]
        assert obtido["colunas"] == esperado["colunas"], tabela
        assert sorted(obtido["periodos"]) == sorted(esperado["periodos"]), tabela
        for comp, dados in esperado["periodos"].items():
            lido = obtido["periodos"][comp]
            assert lido["linhas"] == dados["linhas"], (tabela, comp)
            assert lido["colunas"] == dados["colunas"], (tabela, comp)
            assert lido["conteudo"] == dados["conteudo"], (tabela, comp)


def test_pastas_ano_mes_e_um_parquet_por_tabela_e_competencia(tmp_path: Path) -> None:
    build_raw(tmp_path / "raw")
    converter.convert(tmp_path / "raw", tmp_path / "lake")

    depois = contagem_de_arquivos(tmp_path / "lake")
    antes = _golden()["contagem_de_arquivos"]

    # Mesma contagem de arquivos: um por tabela e competência (não há o que agrupar).
    assert depois == antes
    assert sum(sum(c.values()) for c in antes.values()) == 18
    lake = tmp_path / "lake" / "sigtap"
    assert not list(lake.rglob("competencia=*"))
    arquivo = (
        lake / "tb_grupo" / "ano=2026" / "mes=10" / "TabelaUnificada_202610.parquet"
    )
    assert arquivo.is_file()
    assert (lake / "tb_grupo" / "ano=2008" / "mes=01").is_dir()


def test_competencia_continua_como_coluna_de_dados(tmp_path: Path) -> None:
    """Só a pasta muda: ``competencia`` (AAAAMM) segue nas linhas, ao lado de
    ``ano`` e ``mes`` (partição), e concorda com elas."""
    import polars as pl
    from quantilica.analytics.lake import scan_dataset

    build_raw(tmp_path / "raw")
    converter.convert(tmp_path / "raw", tmp_path / "lake")
    df = scan_dataset(tmp_path / "lake" / "sigtap" / "tb_grupo").collect()

    assert {"competencia", "ano", "mes"} <= set(df.columns)
    esperado = df["ano"].cast(pl.String) + df["mes"]
    assert (df["competencia"] == esperado).all()


def test_lake_profile_devolve_periodo_mensal_das_tabelas(tmp_path: Path) -> None:
    pytest.importorskip("pyarrow")
    from quantilica.core.lake_profile import profile_from_lake

    build_raw(tmp_path / "raw")
    converter.convert(tmp_path / "raw", tmp_path / "lake")

    perfil = profile_from_lake(tmp_path / "lake", "sigtap", "tb_grupo")

    doc = perfil.perfil
    assert doc["granularidade"] == "mensal"
    assert doc["periodos"] == [
        "2008-01",
        "2016-05",
        "2026-10",
        "2026-11",
        "2026-12",
    ]
    assert doc["linhas"] == [2, 2, 2, 8, 1]
    assert "versao" in doc["colunas"]
