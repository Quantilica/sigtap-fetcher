"""Tests for SigtapClient."""

from __future__ import annotations

from unittest.mock import MagicMock

from sigtap_fetcher.client import SigtapClient


def test_list_remote_files() -> None:
    """Test parsing and filtering of remote FTP listings."""
    mock_ftp = MagicMock()
    mock_ftp.list_files.return_value = [
        {
            "name": "TabelaUnificada_200801.zip",
            "is_dir": False,
            "full_path": "/pub/sistemas/tup/downloads/TabelaUnificada_200801.zip",
        },
        {
            "name": "TabelaUnificada_201605_v1.zip",
            "is_dir": False,
            "full_path": "/pub/sistemas/tup/downloads/TabelaUnificada_201605_v1.zip",
        },
        {
            "name": "TabelaUnificada_201605_v2.zip",
            "is_dir": False,
            "full_path": "/pub/sistemas/tup/downloads/TabelaUnificada_201605_v2.zip",
        },
        {
            "name": "outros_documentos.pdf",
            "is_dir": False,
            "full_path": "/pub/sistemas/tup/downloads/outros_documentos.pdf",
        },
        {
            "name": "downloads",
            "is_dir": True,
            "full_path": "/pub/sistemas/tup/downloads/downloads",
        },
    ]

    client = SigtapClient(client=mock_ftp)
    files = client.list_remote_files()
    assert len(files) == 3
    assert files[0]["competencia"] == "200801"
    assert files[0]["version"] == 0
    assert files[1]["competencia"] == "201605"
    assert files[1]["version"] == 1
    assert files[2]["competencia"] == "201605"
    assert files[2]["version"] == 2
    assert files[0]["path"].endswith("TabelaUnificada_200801.zip")
