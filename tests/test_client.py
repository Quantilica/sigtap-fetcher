"""Tests for SigtapClient."""

from __future__ import annotations

import datetime as dt
from unittest.mock import MagicMock

from sigtap_fetcher.client import SigtapClient, parse_list_line


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


def test_parse_list_line_size_and_dates() -> None:
    today = dt.date(2026, 11, 5)
    old = "-rwxrwxr-x 1 ftp ftp 806021 Jan 08  2009 TabelaUnificada_200801.zip"
    recent = "-rwxr-xr-x 1 ftp ftp 23061985 Oct 27 10:43 TabelaUnificada_202610.zip"
    future = "-rwxr-xr-x    1 ftp      ftp       10 Dec 30 10:43 x.zip"
    assert parse_list_line(old, today) == (806021, dt.date(2009, 1, 8))
    assert parse_list_line(recent, today) == (23061985, dt.date(2026, 10, 27))
    assert parse_list_line(future, today) == (10, dt.date(2025, 12, 30))
    assert parse_list_line("lixo", today) == (None, None)


def test_list_remote_files_reads_size_and_mtime_from_raw() -> None:
    mock_ftp = MagicMock()
    mock_ftp.list_files.return_value = [
        {
            "name": "TabelaUnificada_200801.zip",
            "is_dir": False,
            "raw": "-rwxrwxr-x 1 ftp ftp 806021 Jan 08  2009 x.zip",
        }
    ]
    (f,) = SigtapClient(client=mock_ftp).list_remote_files()
    assert f["size"] == 806021
    assert f["mtime"] == dt.date(2009, 1, 8)
