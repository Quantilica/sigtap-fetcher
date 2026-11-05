"""FTP client for DATASUS SIGTAP archives."""

from __future__ import annotations

import datetime as dt
import re
from pathlib import Path
from typing import Any

from quantilica.core.ftp import FtpClient

from .constants import COMPETENCIA_RE, FTP_DIR, FTP_HOST

_LIST_RE = re.compile(
    r"^\S+\s+\d+\s+\S+\s+\S+\s+(?P<size>\d+)\s+"
    r"(?P<mon>[A-Za-z]{3})\s+(?P<day>\d{1,2})\s+(?P<year>\d{4}|\d{1,2}:\d{2})\s+"
)
_MONTHS = {
    m: i
    for i, m in enumerate(
        "jan feb mar apr may jun jul aug sep oct nov dec".split(), start=1
    )
}


def parse_list_line(
    raw: str, today: dt.date | None = None
) -> tuple[int | None, dt.date | None]:
    """Extrai ``(tamanho, data)`` de uma linha ``LIST`` no formato POSIX.

    Linhas recentes trazem ``hh:mm`` no lugar do ano; o ano é inferido como o
    mais recente que não fica no futuro.
    """
    match = _LIST_RE.match(raw or "")
    if not match:
        return None, None
    size = int(match.group("size"))
    month = _MONTHS.get(match.group("mon").lower())
    if month is None:
        return size, None
    today = today or dt.date.today()
    day = int(match.group("day"))
    year_s = match.group("year")
    try:
        if ":" in year_s:
            date = dt.date(today.year, month, day)
            if date > today:
                date = dt.date(today.year - 1, month, day)
        else:
            date = dt.date(int(year_s), month, day)
    except ValueError:
        return size, None
    return size, date


class SigtapClient:
    """Client for discovering and downloading SIGTAP archives from DATASUS FTP."""

    def __init__(
        self,
        host: str = FTP_HOST,
        ftp_dir: str = FTP_DIR,
        client: FtpClient | None = None,
    ) -> None:
        self.host = host
        self.ftp_dir = ftp_dir
        self.client = client or FtpClient(host)

    def list_remote_files(self) -> list[dict[str, Any]]:
        """List all TabelaUnificada archives on FTP server."""
        entries = self.client.list_files(self.ftp_dir)
        results: list[dict[str, Any]] = []
        for item in entries:
            if item.get("is_dir"):
                continue
            name = str(item.get("name", ""))
            match = COMPETENCIA_RE.match(name)
            if match:
                comp = match.group("competencia")
                ver = int(match.group("version") or 0)
                size = item.get("size")
                mtime = item.get("mtime")
                if size is None or mtime is None:
                    raw_size, raw_date = parse_list_line(str(item.get("raw") or ""))
                    size = raw_size if size is None else size
                    mtime = raw_date if mtime is None else mtime
                results.append(
                    {
                        "filename": name,
                        "competencia": comp,
                        "version": ver,
                        "size": size,
                        "mtime": mtime,
                        "path": item.get("full_path") or f"{self.ftp_dir}/{name}",
                    }
                )
        return results

    def download_file(self, remote_filename: str, destination: Path) -> Path:
        """Download single archive with manifest."""
        remote_path = f"{self.ftp_dir}/{remote_filename}"
        return self.client.download_with_manifest(
            remote_path,
            destination,
            source_id="sigtap",
            dataset_id="tabelas",
            producer="sigtap-fetcher",
        )
