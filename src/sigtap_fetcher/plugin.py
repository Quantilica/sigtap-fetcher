"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from quantilica.cli.sdk import CheckPlanItem, FetcherApp, make_resolve_groups
from quantilica.core.ftp import FtpClient
from quantilica.core.sync import FreshnessPolicy

from .catalog import GROUP_ALIASES, GROUPS, list_datasets
from .constants import FTP_HOST
from .storage import DataRepository

resolve_groups = make_resolve_groups(
    GROUPS, {alias: [canon] for alias, canon in GROUP_ALIASES.items()}
)


def path_builder(
    output_dir: Path, entry: dict[str, Any], last_modified: dt.date | None
) -> Path:
    """Build local storage path for a dataset entry."""
    return DataRepository(output_dir).path_for_entry(entry, last_modified=last_modified)


fetcher = FetcherApp(
    name="sigtap",
    help="Tabela Unificada de Procedimentos, Medicamentos e OPM do SUS (SIGTAP).",
    groups_dict=GROUPS,
    aliases_dict=GROUP_ALIASES,
    list_datasets=list_datasets,
    path_builder=path_builder,
    default_output=Path("/data/sigtap"),
    client=FtpClient(FTP_HOST),
    freshness_policy=FreshnessPolicy.REMOTE_ONLY,
)


def _sigtap_check_entry(entry: dict[str, Any], output_dir: Path) -> CheckPlanItem:
    """Veredito de frescor para uma competência do SIGTAP, sem baixar.

    O probe genérico do SDK usa ``HEAD`` HTTP, que o ``FtpClient`` não
    implementa. Como cada competência tem URL fixa e imutável no FTP, o
    critério honesto é local: arquivo carimbado já presente → ``skip``,
    senão ``download``.
    """
    dataset = str(entry.get("group") or "tabelas")
    eid = str(entry.get("id", "unknown"))
    local = path_builder(output_dir, entry, None)
    exists = local.exists()
    return CheckPlanItem(
        dataset=dataset,
        id=eid,
        url=str(entry.get("url", "")),
        partition=str(entry.get("competencia")) if entry.get("competencia") else None,
        local_path=str(local),
        remote_etag=None,
        remote_last_modified=None,
        remote_size=None,
        local_exists=exists,
        action="skip-up-to-date" if exists else "download",
        reason="local-exists" if exists else "not-present",
        entry=dict(entry),
    )


fetcher.check_entry = _sigtap_check_entry  # type: ignore[method-assign]


def convert(
    input_dir: Path,
    lake_dir: Path,
    *,
    dataset: list[str] | None = None,
    force: bool = False,
) -> Any:
    """Converte acervo bruto do SIGTAP para o lake Hive (Parquet)."""
    try:
        from sigtap_fetcher import lake
    except ImportError as exc:
        raise RuntimeError(
            "Conversão para o lake requer o extra 'analysis'. "
            "Instale com: quantilica install sigtap --extra analysis"
        ) from exc
    return lake.converter.convert(input_dir, lake_dir, datasets=dataset, force=force)


fetcher.command_convert(convert)
fetcher.command_pipeline(convert)

app = fetcher.app
