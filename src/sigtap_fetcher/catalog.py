"""Dataset catalog for sigtap-fetcher."""

from __future__ import annotations

import datetime as dt
from typing import Any

from .constants import FTP_DIR, FTP_HOST

__all__ = [
    "GROUPS",
    "GROUP_ALIASES",
    "list_datasets",
]


def _generate_competencias(start_year: int = 2008, start_month: int = 1) -> list[str]:
    """Generate list of competências from 2008-01 to current month."""
    now = dt.date.today()
    comps: list[str] = []
    y = start_year
    m = start_month
    while (y < now.year) or (y == now.year and m <= now.month):
        comps.append(f"{y}{m:02d}")
        m += 1
        if m > 12:
            m = 1
            y += 1
    return comps


ALL_COMPETENCIAS = _generate_competencias()

TABELAS_ENTRIES: list[dict[str, Any]] = [
    {
        "id": f"tabela_unificada_{comp}",
        "base_id": "TabelaUnificada",
        "name": f"Tabela Unificada SIGTAP — {comp[:4]}-{comp[4:]}",
        "url": f"ftp://{FTP_HOST}{FTP_DIR}/TabelaUnificada_{comp}.zip",
        "ext": "zip",
        "group": "tabelas",
        "competencia": comp,
    }
    for comp in ALL_COMPETENCIAS
]

RECENTES_ENTRIES = TABELAS_ENTRIES[-12:]

GROUPS: dict[str, dict[str, Any]] = {
    "tabelas": {
        "name": "Tabela Unificada Completa (2008–atual)",
        "entries": TABELAS_ENTRIES,
    },
    "recentes": {
        "name": "Últimos 12 Meses",
        "entries": RECENTES_ENTRIES,
    },
}

GROUP_ALIASES: dict[str, str] = {
    "padrao": "tabelas",
    "tudo": "tabelas",
    "ultimos": "recentes",
}


def list_datasets(group: str | None = None) -> list[dict[str, Any]]:
    """List datasets for a group or all groups."""
    if group is None:
        entries: list[dict[str, Any]] = []
        for g_data in GROUPS.values():
            entries.extend(g_data["entries"])
        return entries

    canon = GROUP_ALIASES.get(group, group)
    if canon not in GROUPS:
        raise ValueError(f"Grupo desconhecido: {group!r}")
    return list(GROUPS[canon]["entries"])
