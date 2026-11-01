"""Constants and configuration for sigtap-fetcher."""

from __future__ import annotations

import re

FTP_HOST = "ftp2.datasus.gov.br"
FTP_DIR = "/pub/sistemas/tup/downloads"

COMPETENCIA_RE = re.compile(
    r"^TabelaUnificada_(?P<competencia>\d{6})(?:_v(?P<version>\d+))?(?:@.*)?(?:\.zip)?$",
    re.IGNORECASE,
)

# Canonical list of prominent SIGTAP tables
CORE_TABLES = [
    "tb_procedimento",
    "tb_grupo",
    "tb_subgrupo",
    "tb_forma_organizacao",
    "tb_rubrica",
    "tb_modalidade",
    "tb_registro",
    "tb_tipo_leito",
    "tb_financiamento",
    "rl_procedimento_ocupacao",
    "rl_procedimento_compativel",
    "rl_procedimento_habilitacao",
    "rl_procedimento_modalidade",
    "rl_procedimento_registro",
    "rl_procedimento_regra_cond",
    "rl_procedimento_servico",
]
