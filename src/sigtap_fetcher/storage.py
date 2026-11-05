"""Storage path management for sigtap-fetcher."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from quantilica.core.storage import (
    BaseDataRepository,
    build_stamped_filename,
    stamp_filename,
)


class DataRepository(BaseDataRepository):
    """Manages local storage for sigtap-fetcher files."""

    def __init__(self, root: Path | str) -> None:
        super().__init__(root)

    @staticmethod
    def _remote_date(entry: dict[str, Any]) -> dt.date | None:
        raw = entry.get("remote_date")
        if not raw:
            return None
        try:
            return dt.date.fromisoformat(str(raw)[:10])
        except ValueError:
            return None

    def path_for_entry(
        self,
        entry: dict[str, Any],
        *,
        last_modified: dt.date | None = None,
    ) -> Path:
        """Compute the local path for a dataset entry."""
        group = entry.get("group", "tabelas")
        ext = entry.get("ext", "zip")
        base_id = entry.get("base_id", entry.get("id", "tabela_unificada"))
        comp = entry.get("competencia")
        ver = entry.get("version")

        # Carimbo estável: a data da publicação remota viaja na entry; sem ela,
        # vale o Last-Modified e, por último, o dia de hoje.
        timestamp = self._remote_date(entry) or last_modified or dt.date.today()

        if comp is not None:
            partition = str(comp)
            if ver:
                partition = f"{partition}_v{ver}"
            filename = build_stamped_filename(
                base_id, partition, ext=ext, timestamp=timestamp
            )
        else:
            filename = stamp_filename(base_id, ext, timestamp)

        return self.storage.path_for(f"{group}/{filename}")
