"""FTP client for DATASUS SIGTAP archives."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from quantilica.core.ftp import FtpClient

from .constants import COMPETENCIA_RE, FTP_DIR, FTP_HOST


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
                results.append(
                    {
                        "filename": name,
                        "competencia": comp,
                        "version": ver,
                        "size": item.get("size"),
                        "mtime": item.get("mtime"),
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
