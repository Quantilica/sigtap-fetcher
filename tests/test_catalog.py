"""Tests for sigtap-fetcher catalog."""

from __future__ import annotations

import pytest

from sigtap_fetcher import catalog
from sigtap_fetcher.catalog import GROUP_ALIASES, GROUPS, list_datasets

FAKE_REMOTE = [
    {
        "filename": "TabelaUnificada_202501.zip",
        "competencia": "202501",
        "version": 0,
        "size": 1,
        "mtime": None,
        "path": "/pub/sistemas/tup/downloads/TabelaUnificada_202501.zip",
    },
    {
        "filename": "TabelaUnificada_202502_v2502131336.zip",
        "competencia": "202502",
        "version": 2502131336,
        "size": 2,
        "mtime": None,
        "path": "/pub/sistemas/tup/downloads/TabelaUnificada_202502_v2502131336.zip",
    },
    {
        "filename": "TabelaUnificada_202502_v2504011200.zip",
        "competencia": "202502",
        "version": 2504011200,
        "size": 3,
        "mtime": None,
        "path": "/pub/sistemas/tup/downloads/TabelaUnificada_202502_v2504011200.zip",
    },
]


@pytest.fixture(autouse=True)
def clear_cache(monkeypatch: pytest.MonkeyPatch) -> None:
    """Isola cada teste do cache de listagem e da rede."""
    monkeypatch.setattr(catalog, "_REMOTE_CACHE", None)
    monkeypatch.setattr(
        "sigtap_fetcher.client.SigtapClient.list_remote_files",
        lambda self: list(FAKE_REMOTE),
    )


def test_one_entry_per_competencia_with_latest_version() -> None:
    """Cada competência expõe só a versão mais recente do FTP."""
    datasets = list_datasets()
    assert [d["competencia"] for d in datasets] == ["202501", "202502"]
    latest = datasets[1]
    assert latest["remote_filename"] == "TabelaUnificada_202502_v2504011200.zip"
    assert latest["url"].endswith("TabelaUnificada_202502_v2504011200.zip")
    assert latest["web_url"].startswith("ftp://")


def test_list_datasets_by_group() -> None:
    """Grupos e aliases válidos devolvem a mesma lista; inválido levanta erro."""
    for group in GROUPS:
        assert isinstance(list_datasets(group), list)

    for alias in GROUP_ALIASES:
        assert isinstance(list_datasets(alias), list)

    with pytest.raises(ValueError, match="Grupo desconhecido"):
        list_datasets("grupo_inexistente_xyz")
