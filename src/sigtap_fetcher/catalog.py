"""Dataset catalog for sigtap-fetcher.

O catálogo do SIGTAP é **descoberto no FTP** a cada processo, não gerado por
aritmética de competências: desde 2025 o DATASUS publica os arquivos com sufixo
de versão (``TabelaUnificada_202605_v2610231231.zip``), e meses recentes não
existem com o nome "liso". Descobrir a listagem real evita 100 % de erros de
download por nome inexistente.

Para cada competência vale o arquivo de maior versão; versões anteriores
permanecem no FTP e não são baixadas.
"""

from __future__ import annotations

import datetime as dt
from typing import Any

from .constants import FTP_DIR

__all__ = [
    "GROUPS",
    "GROUP_ALIASES",
    "list_datasets",
]


def _remote_date(remote: dict[str, Any]) -> str | None:
    """Data estável da publicação (``AAAA-MM-DD``) do arquivo remoto.

    Prefere o sufixo ``_v<yymmddHHMM>`` do nome: o ``LIST`` de arquivos
    recentes vem sem ano e a inferência poderia virar na passagem do ano. Sem
    sufixo válido, usa a data do ``mtime`` da listagem.
    """
    version = str(int(remote.get("version") or 0))
    if len(version) == 10:
        try:
            return dt.date(
                2000 + int(version[:2]), int(version[2:4]), int(version[4:6])
            ).isoformat()
        except ValueError:
            pass
    mtime = remote.get("mtime")
    if isinstance(mtime, dt.datetime):
        return mtime.date().isoformat()
    if isinstance(mtime, dt.date):
        return mtime.isoformat()
    if isinstance(mtime, str) and len(mtime) >= 10:
        try:
            return dt.date.fromisoformat(mtime[:10]).isoformat()
        except ValueError:
            return None
    return None


# Preenchido sob demanda por `_remote_entries()` (uma listagem FTP por processo).
_REMOTE_CACHE: list[dict[str, Any]] | None = None


def _remote_entries() -> list[dict[str, Any]]:
    """Descobre as competências disponíveis no FTP e mantém a última versão."""
    global _REMOTE_CACHE
    if _REMOTE_CACHE is not None:
        return _REMOTE_CACHE

    from .client import SigtapClient

    client = SigtapClient()
    latest: dict[str, dict[str, Any]] = {}
    for remote in client.list_remote_files():
        comp = str(remote.get("competencia") or "")
        version = int(remote.get("version") or 0)
        current = latest.get(comp)
        if current is None or version > int(current.get("version") or 0):
            latest[comp] = remote

    entries: list[dict[str, Any]] = []
    for comp in sorted(latest):
        remote = latest[comp]
        version = int(remote.get("version") or 0)
        entries.append(
            {
                "id": f"tabela_unificada_{comp}",
                "base_id": "TabelaUnificada",
                "name": f"Tabela Unificada SIGTAP — {comp[:4]}-{comp[4:]}",
                "url": f"{FTP_DIR}/{remote['filename']}",
                "web_url": f"ftp://{client.host}{FTP_DIR}/{remote['filename']}",
                "ext": "zip",
                "group": "tabelas",
                "competencia": comp,
                "partition": comp,
                "version": version or None,
                "remote_filename": remote["filename"],
                "remote_size": remote.get("size"),
                "remote_date": _remote_date(remote),
            }
        )

    _REMOTE_CACHE = entries
    return entries


GROUPS: dict[str, dict[str, Any]] = {
    "tabelas": {
        "name": "Tabela Unificada Completa (2008–atual)",
        "entries": [],
    },
}

GROUP_ALIASES: dict[str, str] = {
    "padrao": "tabelas",
    "tudo": "tabelas",
}


def list_datasets(group: str | None = None) -> list[dict[str, Any]]:
    """Lista competências reais do FTP, opcionalmente filtradas por grupo."""
    entries = _remote_entries()
    if group is None:
        return list(entries)

    canon = GROUP_ALIASES.get(group, group)
    if canon not in GROUPS:
        raise ValueError(f"Grupo desconhecido: {group!r}")
    return list(entries)
