"""Tests for sigtap-fetcher Typer plugin."""

from typer.testing import CliRunner

from sigtap_fetcher.plugin import app


def test_cli_list() -> None:
    """Test quantilica sigtap list."""
    runner = CliRunner()
    result = runner.invoke(app, ["list"])
    assert result.exit_code == 0
    assert "tabelas" in result.output
    assert "tabela_unificada" in result.output
