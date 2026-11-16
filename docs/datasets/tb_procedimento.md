---
dataset:
  id: tb_procedimento
  fonte: sigtap
  titulo: "Procedimentos (SIGTAP)"
  resumo: "A tabela central do SIGTAP: um registro por procedimento, medicamento ou órtese, prótese e material especial vigente na competência, com nome, complexidade, sexo e idade permitidos, limites de execução, valores pagos (hospitalar, ambulatorial e profissional) e financiamento."
  orgao: Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde
  pagina_oficial: http://sigtap.datasus.gov.br/
  licenca: "Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos)."
  periodicidade: mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada)
  cobertura: {inicio: 2008-01, fim: em-curso}
  unidade: "um procedimento vigente na competência"
  granularidade: {espacial: "nacional (sem recorte geográfico)", temporal: competência mensal}
  formato_bruto: "ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP"
  lake: {estado: convertido, particoes: [competencia], chave: [competencia, co_procedimento], colunas: 17}
  unidades_de_medida:
    qt_maxima_execucao: "execuções (9999 = não se aplica)"
    qt_dias_permanencia: "dias (9999 = não se aplica)"
    qt_pontos: "pontos"
    vl_idade_minima: "meses (9999 = não se aplica)"
    vl_idade_maxima: "meses (9999 = não se aplica)"
    vl_sh: "R$"
    vl_sa: "R$"
    vl_sp: "R$"
    qt_tempo_permanencia: "unidade não informada pela fonte (9999 = não se aplica)"
    versao: "AAMMDDHHMM (identificador da publicação, sem unidade)"
  dados_pessoais: nenhum
  eras:
    - {desde: 2012-09, mudanca: "a tabela ganha a coluna QT_TEMPO_PERMANENCIA"}
    - {desde: 2025-06, mudanca: "larguras do arquivo mudam: VL_SH 10→12; VL_SA 10→12; VL_SP 10→12"}
  revisado_em: 2026-11-15
  versao_fetcher: 0.4.0
---

# Procedimentos

## Resumo

A tabela central do SIGTAP: um registro por procedimento, medicamento ou órtese, prótese e material especial vigente na competência, com nome, complexidade, sexo e idade permitidos, limites de execução, valores pagos (hospitalar, ambulatorial e profissional) e financiamento.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `sigtap/tb_procedimento` |
| Órgão | Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde |
| Página oficial | http://sigtap.datasus.gov.br/ |
| Licença | Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos). |
| Periodicidade | mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada) |
| Cobertura | 2008-01 a em-curso |
| Unidade (uma linha) | um procedimento vigente na competência |
| Granularidade | espacial: nacional (sem recorte geográfico); temporal: competência mensal |
| Formato bruto | ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP |
| Estado no lake | convertido |
| Partições | `competencia` |
| Chave | `competencia`, `co_procedimento` |
| Colunas | 17 |
| Unidades de medida | `qt_maxima_execucao`: execuções (9999 = não se aplica); `qt_dias_permanencia`: dias (9999 = não se aplica); `qt_pontos`: pontos; `vl_idade_minima`: meses (9999 = não se aplica); `vl_idade_maxima`: meses (9999 = não se aplica); `vl_sh`: R$; `vl_sa`: R$; `vl_sp`: R$; `qt_tempo_permanencia`: unidade não informada pela fonte (9999 = não se aplica); `versao`: AAMMDDHHMM (identificador da publicação, sem unidade) |
| Dados pessoais | nenhum |
| Eras | 2012-09: a tabela ganha a coluna QT_TEMPO_PERMANENCIA; 2025-06: larguras do arquivo mudam: VL_SH 10→12; VL_SA 10→12; VL_SP 10→12 |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.4.0 |

## Origem e coleta

- O fetcher baixa, por FTP, o ZIP de cada competência do SIGTAP em `ftp2.datasus.gov.br`, pasta `/pub/sistemas/tup/downloads`. O nome na fonte é `TabelaUnificada_AAAAMM.zip` ou, quando o DATASUS regera a tabela, `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo é a data e a hora da geração.
- No bruto, o arquivo fica em `tabelas/` com o carimbo de data da versão baixada (`TabelaUnificada_AAAAMM_vAAMMDDHHMM@AAAAMMDD.zip`).
- Este dataset vem do membro `tb_procedimento.txt` do ZIP (dados, uma linha por registro, largura fixa) e do layout `tb_procedimento_layout.txt`, que dá nome, tamanho e posição de cada coluna. O ZIP traz ainda o layout reunido de todas as tabelas (`layout.txt`), a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' (dicionário oficial) e o `LEIA_ME.TXT` (histórico das mudanças da estrutura). O fetcher guarda o ZIP inteiro; o conversor lê só os membros `tb_*.txt` e `rl_*.txt` e os layouts.
- Conferido em 2026-11-15 pelo tamanho dos membros dos 227 ZIPs publicados (2008-01 a 2026-11, uma competência por mês, sem lacunas), `tb_procedimento.txt` existe e tem conteúdo em todos.

## Conteúdo

- Unidade de análise: um procedimento vigente na competência.
- Linhas por competência: 4.190 em 2008-01, 5.068 em 2026-11; entre as 227 competências convertidas para esta página, de 4.190 a 5.068. Cada competência traz a tabela inteira, não só o que mudou.
- Cobre procedimentos de todos os nove grupos da classificação, inclusive medicamentos (grupo `06`) e órteses, próteses e materiais especiais (grupo `07`).
- `co_rubrica` só vem preenchido nos procedimentos de financiamento `04` (FAEC): nas 227 competências, nenhuma linha de outro financiamento tem rubrica, e os dois primeiros dígitos da rubrica repetem o financiamento. Em 34 linhas de FAEC (somadas as competências) a rubrica vem nula.
- Os valores `vl_sh`, `vl_sa` e `vl_sp` são os valores que o SUS paga naquela competência, por componente (hospitalar, ambulatorial, profissional); a fonte não define a soma dos três como valor único.
- Mudanças de estrutura (conferidas nos layouts dos ZIPs):
    - 2012-09: a tabela ganha a coluna QT_TEMPO_PERMANENCIA.
    - 2025-06: larguras do arquivo mudam: VL_SH 10→12; VL_SA 10→12; VL_SP 10→12.

## Variáveis

As descrições seguem a planilha oficial de layout do ZIP ('DATASUS - Tabela de Procedimentos - Lay-out.xls'), conferidas contra os valores observados em 2026-11. Onde os dados diferem da planilha, isso está dito na coluna 'Unidade / códigos'.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_procedimento` | `CO_PROCEDIMENTO` | texto | Código do procedimento, 10 dígitos: os seis primeiros dão grupo (2), subgrupo (2) e forma de organização (2); os quatro últimos identificam o procedimento dentro da forma de organização | — | todo |
| `no_procedimento` | `NO_PROCEDIMENTO` | texto | Nome descritivo do procedimento (até 250 caracteres) | — | todo |
| `tp_complexidade` | `TP_COMPLEXIDADE` | texto | Complexidade do procedimento | `0` não se aplica; `1` atenção básica; `2` média complexidade; `3` alta complexidade | todo |
| `tp_sexo` | `TP_SEXO` | texto | Sexo a que o procedimento se aplica | `M` masculino; `F` feminino; `I` indiferente (ambos); `N` não se aplica | todo |
| `qt_maxima_execucao` | `QT_MAXIMA_EXECUCAO` | inteiro | Número máximo de execuções permitidas do procedimento | 9999 = não se aplica | todo |
| `qt_dias_permanencia` | `QT_DIAS_PERMANENCIA` | inteiro | Número máximo de dias de internação possíveis | 9999 = não se aplica | todo |
| `qt_pontos` | `QT_PONTOS` | inteiro | Quantidade de pontos do procedimento | 0 = sem pontos | todo |
| `vl_idade_minima` | `VL_IDADE_MINIMA` | inteiro | Idade mínima para usar o procedimento, em meses | 9999 = não se aplica | todo |
| `vl_idade_maxima` | `VL_IDADE_MAXIMA` | inteiro | Idade máxima para usar o procedimento, em meses | 9999 = não se aplica; o valor 1571 (130 anos e 11 meses) aparece como teto de idade | todo |
| `vl_sh` | `VL_SH` | decimal | Valor do serviço hospitalar (SH) do procedimento, em reais; a fonte grava centavos sem separador e o conversor divide por 100 | R$ | todo |
| `vl_sa` | `VL_SA` | decimal | Valor do serviço ambulatorial (SA) do procedimento, em reais (mesma escala de `vl_sh`) | R$ | todo |
| `vl_sp` | `VL_SP` | decimal | Valor do serviço profissional (SP) do procedimento, em reais (mesma escala de `vl_sh`) | R$ | todo |
| `co_financiamento` | `CO_FINANCIAMENTO` | texto | Tipo de financiamento do procedimento; liga com `tb_financiamento` | `01`, `02`, `04` a `08` (ver `tb_financiamento`) | todo |
| `co_rubrica` | `CO_RUBRICA` | texto | Rubrica do procedimento (financiamento + subtipo); nula quando o procedimento não tem rubrica. Liga com `tb_rubrica` | 6 dígitos; os dois primeiros repetem `co_financiamento` | todo |
| `qt_tempo_permanencia` | `QT_TEMPO_PERMANENCIA` | inteiro | Tempo de permanência do procedimento; a fonte não descreve a coluna (ausente da planilha oficial) | 9999 = não se aplica | desde 2012-09 |
| `dt_competencia` | `DT_COMPETENCIA` | texto | Competência de validade do registro (AAAAMM). Igual à partição `competencia` em todas as linhas conferidas | AAAAMM | todo |
| `versao` | — (nome do ZIP) | inteiro | Versão da publicação: sufixo `_v` do nome do ZIP, no formato AAMMDDHHMM (data e hora em que o DATASUS gerou o arquivo); 0 quando o nome do ZIP não traz sufixo (competências de 2008-01 a 2009-04) | AAMMDDHHMM; 0 = sem sufixo | todo |
| `competencia` | — (partição) | texto | Competência (AAAAMM) do ZIP de que a linha veio | AAAAMM | todo |

## No lake

- Dataset `sigtap/tb_procedimento`, particionado por `competencia` (AAAAMM, texto); um arquivo Parquet por ZIP de competência.
- O conversor lê cada linha de largura fixa com o layout do próprio ZIP, aparando espaços nas pontas; campo em branco vira nulo e texto é decodificado de ISO-8859-1 para UTF-8.
- Colunas numéricas viram inteiros ou decimais conforme o layout; valor que não converte vira nulo. Os valores `9999` que a fonte usa como 'não se aplica' ficam como estão.
- Linhas totalmente em branco são ignoradas. Se um ZIP traz mais de uma versão da mesma competência, só a de maior sufixo `_v` é convertida.
- As colunas `versao` (sufixo `_v` do ZIP) e a partição `competencia` são acrescentadas pelo conversor.
- `dt_competencia` é a coluna do arquivo, mantida como texto.
- Os valores `vl_sh`, `vl_sa` e `vl_sp` são lidos como centavos e divididos por 100.
- As colunas `vl_idade_minima`, `vl_idade_maxima` e `qt_*` são inteiros; o conversor os lê como inteiros mesmo quando o layout automático as trataria como decimais.

## Cuidados de uso

- **Cada competência é uma fotografia completa, não um incremento.** Sem filtrar `competencia`, o mesmo registro aparece uma vez por competência (esta tabela soma 1.035.134 linhas nas 227 competências convertidas, contra 5.068 em 2026-11). Filtre uma competência ou compare competências explicitamente.
- **A fonte usa 9999 como 'não se aplica'** em `qt_maxima_execucao`, `qt_dias_permanencia`, `vl_idade_minima`, `vl_idade_maxima` e `qt_tempo_permanencia`; o conversor preserva o 9999. Em 2026-11, 1.444 procedimentos têm `qt_maxima_execucao` 9999, 3.351 têm `qt_dias_permanencia` 9999 e 5.065 de 5.068 têm `qt_tempo_permanencia` 9999. Trate 9999 como ausência antes de calcular médias ou limites.
- **Idade em meses.** Desde 2007 a fonte grava a idade em meses, não em anos (LEIA_ME do ZIP). Em 2026-11, `vl_idade_maxima` é 1571 em 4.092 procedimentos e 9999 em 595; a planilha oficial só prevê valores de 0 a 1331 e 9999.
- **Valores zerados são comuns.** Em 2026-11, 2.569 procedimentos têm `vl_sh` igual a zero, 2.961 têm `vl_sa` zero, 3.235 têm `vl_sp` zero e 902 têm os três zerados (por exemplo, procedimentos de registro sem pagamento direto).
- **Valor e nome são da competência.** O mesmo código muda de valor e de nome ao longo do tempo; para séries de preço, junte sempre por `competencia`. O nome mais antigo pode estar em caixa alta sem acento, o recente em caixa mista.
- **Sexo.** `tp_sexo` traz `A` em uma linha de 2008-01 (procedimento `0702050369`), valor que a planilha oficial não prevê. Em 2026-11 só há `F`, `I`, `M` e `N`.
- **Junte sempre pela mesma competência.** Códigos, nomes e valores mudam de uma competência para outra; unir tabelas de competências diferentes dá resultados que nunca existiram no SIGTAP.

## Exemplos

Valor ambulatorial médio (SA) dos procedimentos de média e alta complexidade com valor, por grupo, na competência mais recente.

```python
import duckdb

duckdb.sql("""
    SELECT substr(co_procedimento, 1, 2) AS grupo, count(*) AS procedimentos,
           round(avg(vl_sa), 2) AS vl_sa_medio
    FROM read_parquet('lake/sigtap/tb_procedimento/**/*.parquet', hive_partitioning = true, union_by_name = true)
    WHERE competencia = '202611' AND tp_complexidade IN ('2', '3') AND vl_sa > 0
    GROUP BY 1
    ORDER BY 1
""").show()
```

## Referências

- SIGTAP (Sistema de Gerenciamento da Tabela de Procedimentos, Medicamentos e OPM do SUS): http://sigtap.datasus.gov.br/
- Arquivos de exportação do SIGTAP (FTP do DATASUS): ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/
- Dentro de cada ZIP: a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' e o `LEIA_ME.TXT`.
- Notas técnicas da CGSI/DATASUS sobre cada competência: ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/notastecnicas/
