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
