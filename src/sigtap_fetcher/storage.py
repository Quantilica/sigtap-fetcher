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

        if comp is not None:
            partition = str(comp)
            if ver:
                partition = f"{partition}_v{ver}"
            filename = build_stamped_filename(
                base_id, partition, ext=ext, timestamp=last_modified
            )
        else:
            filename = stamp_filename(base_id, ext, last_modified)

        return self.storage.path_for(f"{group}/{filename}")
