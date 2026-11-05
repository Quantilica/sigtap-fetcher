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


def test_path_for_entry_stable_with_remote_date(monkeypatch) -> None:
    """Com remote_date o caminho não muda de um dia para o outro."""
    repo = DataRepository(Path("/tmp/test"))
    entry = {
        "group": "tabelas",
        "ext": "zip",
        "base_id": "TabelaUnificada",
        "competencia": "202610",
        "version": 2610271043,
        "remote_date": "2026-10-27",
    }
    first = repo.path_for_entry(entry, last_modified=None)

    class _Later(dt.date):
        @classmethod
        def today(cls):
            return cls(2030, 1, 1)

    monkeypatch.setattr("sigtap_fetcher.storage.dt.date", _Later)
    second = repo.path_for_entry(entry, last_modified=None)
    assert first == second
    assert first.name == "TabelaUnificada_202610_v2610271043@20261027.zip"


def test_remote_date_beats_last_modified_and_bad_value_falls_back() -> None:
    repo = DataRepository(Path("/tmp/test"))
    base = {"base_id": "TabelaUnificada", "competencia": "202501"}
    p = repo.path_for_entry(
        {**base, "remote_date": "2025-02-03"}, last_modified=dt.date(2025, 9, 9)
    )
    assert p.name == "TabelaUnificada_202501@20250203.zip"
    p = repo.path_for_entry(
        {**base, "remote_date": "lixo"}, last_modified=dt.date(2025, 9, 9)
    )
    assert p.name == "TabelaUnificada_202501@20250909.zip"
