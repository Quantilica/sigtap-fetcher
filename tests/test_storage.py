"""Tests for sigtap-fetcher storage path management."""

from __future__ import annotations

import datetime as dt
from pathlib import Path

from sigtap_fetcher.storage import DataRepository


def test_path_for_entry_with_last_modified() -> None:
    """When last_modified is provided, filename gets @YYYYMMDD stamp."""
    repo = DataRepository(Path("/tmp/test"))
    entry = {
        "group": "tabelas",
        "ext": "zip",
        "base_id": "TabelaUnificada",
        "competencia": "202501",
    }
    path = repo.path_for_entry(entry, last_modified=dt.date(2025, 3, 15))
    assert path.name == "TabelaUnificada_202501@20250315.zip"


def test_path_for_entry_fallback_timestamp() -> None:
    """When last_modified=None, filename gets today's @YYYYMMDD stamp."""
    repo = DataRepository(Path("/tmp/test"))
    entry = {
        "group": "tabelas",
        "ext": "zip",
        "base_id": "TabelaUnificada",
        "competencia": "202501",
    }
    path = repo.path_for_entry(entry, last_modified=None)
    today = dt.date.today()
    expected = f"TabelaUnificada_202501@{today:%Y%m%d}.zip"
    assert path.name == expected


def test_path_for_entry_without_competencia() -> None:
    """When no competencia, filename uses base_id with fallback timestamp."""
    repo = DataRepository(Path("/tmp/test"))
    entry = {
        "group": "tabelas",
        "ext": "zip",
        "base_id": "TabelaUnificada",
    }
    path = repo.path_for_entry(entry, last_modified=None)
    today = dt.date.today()
    expected = f"TabelaUnificada@{today:%Y%m%d}.zip"
    assert path.name == expected


def test_path_for_entry_with_version() -> None:
    """When version is present, partition includes _v{version}."""
    repo = DataRepository(Path("/tmp/test"))
    entry = {
        "group": "tabelas",
        "ext": "zip",
        "base_id": "TabelaUnificada",
        "competencia": "202502",
        "version": 2504011200,
    }
    path = repo.path_for_entry(entry, last_modified=dt.date(2025, 4, 1))
    assert path.name == "TabelaUnificada_202502_v2504011200@20250401.zip"