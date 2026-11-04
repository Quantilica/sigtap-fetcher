"""Constants and configuration for sigtap-fetcher."""

from __future__ import annotations

import re

FTP_HOST = "ftp2.datasus.gov.br"
FTP_DIR = "/pub/sistemas/tup/downloads"

COMPETENCIA_RE = re.compile(
    r"^TabelaUnificada_(?P<competencia>\d{6})(?:_v(?P<version>\d+))?(?:@.*)?(?:\.zip)?$",
    re.IGNORECASE,
)

# As 41 tabelas (tb_*/rl_*) do ZIP de 2026-10, cada uma com `<tabela>_layout.txt`
# (sondado no FTP em 2026-11-03). Eras antigas trazem um subconjunto.
ALL_TABLES = [
    "rl_excecao_compatibilidade",
    "rl_procedimento_cid",
    "rl_procedimento_comp_rede",
    "rl_procedimento_compativel",
    "rl_procedimento_detalhe",
    "rl_procedimento_habilitacao",
    "rl_procedimento_incremento",
    "rl_procedimento_leito",
    "rl_procedimento_modalidade",
    "rl_procedimento_ocupacao",
    "rl_procedimento_origem",
    "rl_procedimento_registro",
    "rl_procedimento_regra_cond",
    "rl_procedimento_renases",
    "rl_procedimento_servico",
    "rl_procedimento_sia_sih",
    "rl_procedimento_tuss",
    "tb_cid",
    "tb_componente_rede",
    "tb_descricao",
    "tb_descricao_detalhe",
    "tb_detalhe",
    "tb_financiamento",
    "tb_forma_organizacao",
    "tb_grupo",
    "tb_grupo_habilitacao",
    "tb_habilitacao",
    "tb_modalidade",
    "tb_ocupacao",
    "tb_procedimento",
    "tb_rede_atencao",
    "tb_registro",
    "tb_regra_condicionada",
    "tb_renases",
    "tb_rubrica",
    "tb_servico",
    "tb_servico_classificacao",
    "tb_sia_sih",
    "tb_sub_grupo",
    "tb_tipo_leito",
    "tb_tuss",
]

# Mantido por compatibilidade: antes era a lista (incompleta) usada pelo lake.
CORE_TABLES = ALL_TABLES

# Unicas colunas monetarias (centavos, sem separador decimal). Os demais `VL_*`
# do SIGTAP sao idade em meses, contagem ou percentual: inteiros, nao dinheiro.
MONEY_COLUMNS = frozenset({"vl_sh", "vl_sa", "vl_sp"})

# Percentuais de incremento (`rl_procedimento_incremento`): duas casas implicitas
# (`2000` = 20,00 %). O layout so informa a largura; a escala vem da distribuicao
# dos valores publicados (2000, 3500, 5000, 8000, 10000).
PERCENT_COLUMNS = frozenset(
    {"vl_percentual_sh", "vl_percentual_sa", "vl_percentual_sp"}
)
