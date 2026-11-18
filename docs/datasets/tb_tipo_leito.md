---
dataset:
  id: tb_tipo_leito
  fonte: sigtap
  titulo: "Tipos de leito (SIGTAP)"
  resumo: "Classificação dos leitos hospitalares em que os procedimentos podem ser executados (cirúrgico, clínico, UTI e outros)."
  orgao: Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde
  pagina_oficial: http://sigtap.datasus.gov.br/
  licenca: "Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos)."
  periodicidade: mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada)
  cobertura: {inicio: 2008-01, fim: em-curso}
  unidade: "um tipo de leito vigente na competência"
  granularidade: {espacial: "nacional (sem recorte geográfico)", temporal: competência mensal}
  formato_bruto: "ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP"
  lake: {estado: convertido, particoes: [ano], chave: [competencia, co_tipo_leito], colunas: 7}
  unidades_de_medida:
    versao: "AAMMDDHHMM (identificador da publicação, sem unidade)"
  dados_pessoais: nenhum
  eras:
    - {desde: 2020-06, mudanca: "larguras do arquivo mudam: NO_TIPO_LEITO 60→100"}
    - {desde: 2020-07, mudanca: "larguras do arquivo mudam: NO_TIPO_LEITO 100→60"}
  revisado_em: 2026-11-15
  versao_fetcher: 0.4.0
---

# Tipos de leito

## Resumo

Classificação dos leitos hospitalares em que os procedimentos podem ser executados (cirúrgico, clínico, UTI e outros).

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `sigtap/tb_tipo_leito` |
| Órgão | Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde |
| Página oficial | http://sigtap.datasus.gov.br/ |
| Licença | Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos). |
| Periodicidade | mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada) |
| Cobertura | 2008-01 a em-curso |
| Unidade (uma linha) | um tipo de leito vigente na competência |
| Granularidade | espacial: nacional (sem recorte geográfico); temporal: competência mensal |
| Formato bruto | ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | `competencia`, `co_tipo_leito` |
| Colunas | 7 |
| Unidades de medida | `versao`: AAMMDDHHMM (identificador da publicação, sem unidade) |
| Dados pessoais | nenhum |
| Eras | 2020-06: larguras do arquivo mudam: NO_TIPO_LEITO 60→100; 2020-07: larguras do arquivo mudam: NO_TIPO_LEITO 100→60 |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.4.0 |

## Origem e coleta

- O fetcher baixa, por FTP, o ZIP de cada competência do SIGTAP em `ftp2.datasus.gov.br`, pasta `/pub/sistemas/tup/downloads`. O nome na fonte é `TabelaUnificada_AAAAMM.zip` ou, quando o DATASUS regera a tabela, `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo é a data e a hora da geração.
- No bruto, o arquivo fica em `tabelas/` com o carimbo de data da versão baixada (`TabelaUnificada_AAAAMM_vAAMMDDHHMM@AAAAMMDD.zip`).
- Este dataset vem do membro `tb_tipo_leito.txt` do ZIP (dados, uma linha por registro, largura fixa) e do layout `tb_tipo_leito_layout.txt`, que dá nome, tamanho e posição de cada coluna. O ZIP traz ainda o layout reunido de todas as tabelas (`layout.txt`), a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' (dicionário oficial) e o `LEIA_ME.TXT` (histórico das mudanças da estrutura). O fetcher guarda o ZIP inteiro; o conversor lê só os membros `tb_*.txt` e `rl_*.txt` e os layouts.
- Conferido em 2026-11-15 pelo tamanho dos membros dos 227 ZIPs publicados (2008-01 a 2026-11, uma competência por mês, sem lacunas), `tb_tipo_leito.txt` existe e tem conteúdo em todos.

## Conteúdo

- Unidade de análise: um tipo de leito vigente na competência.
- Linhas por competência: 26 em 2008-01, 41 em 2026-11; entre as 227 competências convertidas para esta página, de 26 a 41. Cada competência traz a tabela inteira, não só o que mudou.
- Em 2026-11 há 41 tipos de leito; o total cresce de 26 em 2008-01 a 41 em 2026-11, com a entrada de leitos de UTI, unidades de cuidados intermediários, queimados e saúde mental.
- Os códigos `51` e `52` são leitos de UTI II para síndrome respiratória aguda grave (SRAG) por COVID-19.
- Mudanças de estrutura (conferidas nos layouts dos ZIPs):
    - 2020-06: larguras do arquivo mudam: NO_TIPO_LEITO 60→100.
    - 2020-07: larguras do arquivo mudam: NO_TIPO_LEITO 100→60.

## Variáveis

As descrições seguem a planilha oficial de layout do ZIP ('DATASUS - Tabela de Procedimentos - Lay-out.xls'), conferidas contra os valores observados em 2026-11. Onde os dados diferem da planilha, isso está dito na coluna 'Unidade / códigos'.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_tipo_leito` | `CO_TIPO_LEITO` | texto | Código da classificação de leito (2 dígitos) | `01` a `14`, `17`, `51`, `52`, `65`, `74` a `96` em 2026-11 | todo |
| `no_tipo_leito` | `NO_TIPO_LEITO` | texto | Nome da classificação de leito | — | todo |
| `dt_competencia` | `DT_COMPETENCIA` | texto | Competência de validade do registro (AAAAMM). Igual à coluna `competencia` em todas as linhas conferidas | AAAAMM | todo |
| `versao` | — (nome do ZIP) | inteiro | Versão da publicação: sufixo `_v` do nome do ZIP, no formato AAMMDDHHMM (data e hora em que o DATASUS gerou o arquivo); 0 quando o nome do ZIP não traz sufixo (competências de 2008-01 a 2009-04) | AAMMDDHHMM; 0 = sem sufixo | todo |
| `competencia` | — (conversor) | texto | Competência (AAAAMM) do ZIP de que a linha veio; igual a `ano` e `mes` juntos | AAAAMM | todo |
| `mes` | — (conversor) | texto | Mês da competência (`MM`, texto de 2 dígitos), gravado pelo conversor; com `ano` (a partição) dá a competência | 01 a 12 | todo |
| `_origem` | — (conversor) | texto | Chave do ZIP de origem da linha: o nome do ZIP sem a extensão e sem o carimbo `@AAAAMMDD` (por exemplo `TabelaUnificada_202610_v2610271043`), gravada pelo conversor | texto | todo |

## No lake

- Dataset `sigtap/tb_tipo_leito`, particionado por `ano` (inteiro); um arquivo Parquet por ano, `ano=AAAA/<tabela>.parquet`, com as linhas de todas as competências do ano. A competência de cada linha está em `competencia` (AAAAMM) e em `mes` (texto de 2 dígitos, `05`).
- O conversor lê cada linha de largura fixa com o layout do próprio ZIP, aparando espaços nas pontas; campo em branco vira nulo e texto é decodificado de ISO-8859-1 para UTF-8.
- Colunas numéricas viram inteiros ou decimais conforme o layout; valor que não converte vira nulo. Os valores `9999` que a fonte usa como 'não se aplica' ficam como estão.
- Linhas totalmente em branco são ignoradas. Se um ZIP traz mais de uma versão da mesma competência, só a de maior sufixo `_v` é convertida.
- As colunas `versao` (sufixo `_v` do ZIP), `competencia` (AAAAMM, igual a `ano` e `mes` juntos), `mes` e `_origem` são acrescentadas pelo conversor.
- `dt_competencia` é a coluna do arquivo, mantida como texto.

## Cuidados de uso

- **Cada competência é uma fotografia completa, não um incremento.** Sem filtrar `competencia`, o mesmo registro aparece uma vez por competência (esta tabela soma 8.141 linhas nas 227 competências convertidas, contra 41 em 2026-11). Filtre uma competência ou compare competências explicitamente.
- O nome de um mesmo código pode mudar de sentido ao longo do tempo: em 2008-01 o `74` é 'UTI I', o `75` 'UTI Adulto II' e o `79` 'UTI Infantil III'; em 2026-11 são 'UTI-PED TIPO II', 'UTI-A TIPO II' e 'UTI-PED TIPO III'. Não compare tipos de UTI entre eras só pelo código.
- **Junte sempre pela mesma competência.** Códigos, nomes e valores mudam de uma competência para outra; unir tabelas de competências diferentes dá resultados que nunca existiram no SIGTAP.

## Exemplos

Procedimentos por tipo de leito na competência mais recente.

```python
import duckdb

duckdb.sql("""
    SELECT l.co_tipo_leito, l.no_tipo_leito, count(*) AS procedimentos
    FROM read_parquet('lake/sigtap/rl_procedimento_leito/**/*.parquet', hive_partitioning = true, union_by_name = true) x
    JOIN read_parquet('lake/sigtap/tb_tipo_leito/**/*.parquet', hive_partitioning = true, union_by_name = true) l
      ON l.competencia = x.competencia AND l.co_tipo_leito = x.co_tipo_leito
    WHERE x.competencia = '202611'
    GROUP BY 1, 2
    ORDER BY 3 DESC
    LIMIT 10
""").show()
```

## Referências

- SIGTAP (Sistema de Gerenciamento da Tabela de Procedimentos, Medicamentos e OPM do SUS): http://sigtap.datasus.gov.br/
- Arquivos de exportação do SIGTAP (FTP do DATASUS): ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/
- Dentro de cada ZIP: a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' e o `LEIA_ME.TXT`.
- Notas técnicas da CGSI/DATASUS sobre cada competência: ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/notastecnicas/
