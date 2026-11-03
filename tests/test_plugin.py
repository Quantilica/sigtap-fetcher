"""Tests for sigtap-fetcher Typer plugin."""

from __future__ import annotations

import pytest
from typer.testing import CliRunner

from sigtap_fetcher import catalog
from sigtap_fetcher.plugin import app


@pytest.fixture(autouse=True)
def fake_listing(monkeypatch: pytest.MonkeyPatch) -> None:
    """Evita rede: injeta uma listagem mínima no catálogo."""
    monkeypatch.setattr(
        catalog,
        "_REMOTE_CACHE",
        [
            {
                "id": "tabela_unificada_202501",
                "base_id": "TabelaUnificada",
                "name": "Tabela Unificada SIGTAP — 2025-01",
                "url": "/pub/sistemas/tup/downloads/TabelaUnificada_202501.zip",
                "ext": "zip",
                "group": "tabelas",
                "competencia": "202501",
                "version": None,
            }
        ],
    )


def test_cli_list() -> None:
    """Test quantilica sigtap list."""
    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "tabelas" in result.output
    assert "tabela_unificada" in result.output


def _entry(comp: str, version: int | None = None) -> dict:
    return {
        "id": f"tabela_unificada_{comp}",
        "base_id": "TabelaUnificada",
        "url": f"/pub/sistemas/tup/downloads/TabelaUnificada_{comp}.zip",
        "ext": "zip",
        "group": "tabelas",
        "competencia": comp,
        "version": version,
    }


def _touch(tmp_path, name: str):
    d = tmp_path / "tabelas"
    d.mkdir(exist_ok=True)
    (d / name).write_bytes(b"zip")
    return d / name


def test_check_matches_by_competencia_ignoring_stamp(tmp_path) -> None:
    """Regressão A5: arquivo carimbado ontem virava `download/not-present`."""
    from sigtap_fetcher.plugin import _sigtap_check_entry

    local = _touch(tmp_path, "TabelaUnificada_202501_v2504011200@20200101.zip")
    item = _sigtap_check_entry(_entry("202501", 2504011200), tmp_path)
    assert item.action == "skip-up-to-date"
    assert item.local_exists is True
    assert item.local_path == str(local)


def test_check_new_version_suffix_is_a_new_version(tmp_path) -> None:
    from sigtap_fetcher.plugin import _sigtap_check_entry

    _touch(tmp_path, "TabelaUnificada_202501_v2504011200@20250401.zip")
    item = _sigtap_check_entry(_entry("202501", 2602261200), tmp_path)
    assert item.action == "download"
    assert item.reason == "new-version"


def test_check_unversioned_and_missing(tmp_path) -> None:
    from sigtap_fetcher.plugin import _sigtap_check_entry

    _touch(tmp_path, "TabelaUnificada_200801@20200101.zip")
    assert _sigtap_check_entry(_entry("200801"), tmp_path).action == "skip-up-to-date"
    missing = _sigtap_check_entry(_entry("200802"), tmp_path)
    assert (missing.action, missing.reason) == ("download", "not-present")


def test_check_does_not_mix_competencias(tmp_path) -> None:
    from sigtap_fetcher.plugin import _sigtap_check_entry

    _touch(tmp_path, "TabelaUnificada_202502@20250401.zip")
    assert _sigtap_check_entry(_entry("202501"), tmp_path).action == "download"
