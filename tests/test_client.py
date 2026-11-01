"""Tests for SigtapClient."""

from __future__ import annotations

import datetime as dt
from unittest.mock import MagicMock

from sigtap_fetcher.client import SigtapClient


def test_list_remote_files() -> None:
    """Test parsing and filtering of remote FTP listings."""
    mock_ftp = MagicMock()
    mock_ftp.list_dir.return_value = [
        ("TabelaUnificada_200801.zip", 123456, dt.datetime(2008, 1, 15)),
        ("TabelaUnificada_201605_v1.zip", 234567, dt.datetime(2016, 5, 20)),
        ("TabelaUnificada_201605_v2.zip", 234599, dt.datetime(2016, 5, 25)),
        ("outros_documentos.pdf", 54321, dt.datetime(2020, 1, 1)),
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
