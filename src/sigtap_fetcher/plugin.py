"""Typer plugin for quantilica-cli integration."""

from __future__ import annotations

import datetime as dt
from pathlib import Path
from typing import Any

from quantilica.cli.sdk import CheckPlanItem, FetcherApp, make_resolve_groups
from quantilica.core.ftp import FtpClient
from quantilica.core.registry import FetcherInfo
from quantilica.core.sync import FreshnessPolicy

from .catalog import GROUP_ALIASES, GROUPS, list_datasets
from .constants import COMPETENCIA_RE, FTP_HOST
from .storage import DataRepository

# O SDK espera ``alias -> lista de grupos``; passar a string crua faria
# ``list("teses")`` virar ['t', 'e', 's', ...] ("Grupo desconhecido: 't'").
ALIASES: dict[str, list[str]] = {
    alias: [canon] for alias, canon in GROUP_ALIASES.items()
}
resolve_groups = make_resolve_groups(GROUPS, ALIASES)


def path_builder(
    output_dir: Path, entry: dict[str, Any], last_modified: dt.date | None
) -> Path:
    """Build local storage path for a dataset entry."""
    return DataRepository(output_dir).path_for_entry(entry, last_modified=last_modified)


fetcher = FetcherApp(
    name="sigtap",
    help="Tabela Unificada de Procedimentos, Medicamentos e OPM do SUS (SIGTAP).",
    info=FetcherInfo(
        id="sigtap",
        nome="SIGTAP - Tabela de Procedimentos, Medicamentos e OPM do SUS",
        aliases=("datasus-sigtap",),
        orgao=(
            "Departamento de Informática do Sistema Único de Saúde (DATASUS), "
            "Ministério da Saúde"
        ),
        licenca=(
            "Sem licença declarada; dados públicos pela Lei 12.527/2011 (LAI) "
            "e Decreto 8.777/2016"
        ),
        homepage="http://sigtap.datasus.gov.br/",
        cadencia="monthly",
        dominio="saude",
    ),
    groups_dict=GROUPS,
    aliases_dict=ALIASES,
    list_datasets=list_datasets,
    path_builder=path_builder,
    default_output=Path("/data/sigtap"),
    client=FtpClient(FTP_HOST),
    freshness_policy=FreshnessPolicy.HEAD_OR_MANIFEST,
)


def _local_files_for_competencia(
    output_dir: Path, entry: dict[str, Any]
) -> list[tuple[Path, int | None]]:
    """Arquivos locais da competência do ``entry`` com a versão (sufixo ``v``).

    Casa por competência (AAAAMM) ignorando o carimbo ``@AAAAMMDD``, que muda a
    cada download e não identifica a publicação.
    """
    group = str(entry.get("group") or "tabelas")
    comp = str(entry.get("competencia") or "")
    folder = output_dir / group
    found: list[tuple[Path, int | None]] = []
    if not comp or not folder.is_dir():
        return found
    for path in sorted(folder.glob("*.zip")):
        match = COMPETENCIA_RE.match(path.name)
        if match and match.group("competencia") == comp:
            version = match.group("version")
            found.append((path, int(version) if version else None))
    return found


def _sigtap_check_entry(entry: dict[str, Any], output_dir: Path) -> CheckPlanItem:
    """Veredito de frescor para uma competência do SIGTAP, sem baixar.

    O probe genérico do SDK usa ``HEAD`` HTTP, que o ``FtpClient`` não
    implementa. O critério honesto é local e por competência: existe arquivo da
    mesma competência **e** da mesma versão (sufixo ``v``) → ``skip``; sufixo
    diferente é versão nova (o DATASUS regera competências passadas em lote) →
    ``download``; nenhum arquivo → ``download``. O carimbo ``@AAAAMMDD`` do nome
    local é ignorado. Havendo ``remote_date`` na entry, o ``local_path`` é sempre o
    caminho estável (carimbo = data de publicação remota), igual ao do download.
    """
    dataset = str(entry.get("group") or "tabelas")
    eid = str(entry.get("id", "unknown"))
    raw_version = entry.get("version")
    version = int(raw_version) if raw_version else None
    local_files = _local_files_for_competencia(output_dir, entry)
    current = [p for p, v in local_files if v == version]
    exists = bool(current)
    stable = path_builder(output_dir, entry, None) if entry.get("remote_date") else None
    if exists:
        local = stable or current[-1]
        reason = "local-exists"
    else:
        local = path_builder(output_dir, entry, None)
        reason = "new-version" if local_files else "not-present"
    return CheckPlanItem(
        dataset=dataset,
        id=eid,
        url=str(entry.get("url", "")),
        partition=str(entry.get("competencia")) if entry.get("competencia") else None,
        local_path=str(local),
        remote_etag=None,
        remote_last_modified=None,
        remote_size=entry.get("remote_size"),
        local_exists=exists,
        action="skip-up-to-date" if exists else "download",
        reason=reason,
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
        raise ImportError(
            "Conversão para o lake requer o extra 'analysis'. "
            "Instale com: quantilica install sigtap --extra analysis"
        ) from exc
    return lake.converter.convert(input_dir, lake_dir, datasets=dataset, force=force)


fetcher.command_convert(convert)
fetcher.command_pipeline(convert)

app = fetcher.app
