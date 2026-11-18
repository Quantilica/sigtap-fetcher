---
dataset:
  id: tb_financiamento
  fonte: sigtap
  titulo: "Tipos de financiamento (SIGTAP)"
  resumo: "Tipos de financiamento dos procedimentos (atenção básica, média e alta complexidade, FAEC, vigilância em saúde e outros)."
  orgao: Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde
  pagina_oficial: http://sigtap.datasus.gov.br/
  licenca: "Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos)."
  periodicidade: mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada)
  cobertura: {inicio: 2008-01, fim: em-curso}
  unidade: "um tipo de financiamento vigente na competência"
  granularidade: {espacial: "nacional (sem recorte geográfico)", temporal: competência mensal}
  formato_bruto: "ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP"
  lake: {estado: convertido, particoes: [ano], chave: [competencia, co_financiamento], colunas: 7}
  unidades_de_medida:
    versao: "AAMMDDHHMM (identificador da publicação, sem unidade)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.4.0
---

# Tipos de financiamento

## Resumo

Tipos de financiamento dos procedimentos (atenção básica, média e alta complexidade, FAEC, vigilância em saúde e outros).

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `sigtap/tb_financiamento` |
| Órgão | Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde |
| Página oficial | http://sigtap.datasus.gov.br/ |
| Licença | Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos). |
| Periodicidade | mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada) |
| Cobertura | 2008-01 a em-curso |
| Unidade (uma linha) | um tipo de financiamento vigente na competência |
| Granularidade | espacial: nacional (sem recorte geográfico); temporal: competência mensal |
| Formato bruto | ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | `competencia`, `co_financiamento` |
| Colunas | 7 |
| Unidades de medida | `versao`: AAMMDDHHMM (identificador da publicação, sem unidade) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.4.0 |

## Origem e coleta

- O fetcher baixa, por FTP, o ZIP de cada competência do SIGTAP em `ftp2.datasus.gov.br`, pasta `/pub/sistemas/tup/downloads`. O nome na fonte é `TabelaUnificada_AAAAMM.zip` ou, quando o DATASUS regera a tabela, `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo é a data e a hora da geração.
- No bruto, o arquivo fica em `tabelas/` com o carimbo de data da versão baixada (`TabelaUnificada_AAAAMM_vAAMMDDHHMM@AAAAMMDD.zip`).
- Este dataset vem do membro `tb_financiamento.txt` do ZIP (dados, uma linha por registro, largura fixa) e do layout `tb_financiamento_layout.txt`, que dá nome, tamanho e posição de cada coluna. O ZIP traz ainda o layout reunido de todas as tabelas (`layout.txt`), a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' (dicionário oficial) e o `LEIA_ME.TXT` (histórico das mudanças da estrutura). O fetcher guarda o ZIP inteiro; o conversor lê só os membros `tb_*.txt` e `rl_*.txt` e os layouts.
- Conferido em 2026-11-15 pelo tamanho dos membros dos 227 ZIPs publicados (2008-01 a 2026-11, uma competência por mês, sem lacunas), `tb_financiamento.txt` existe e tem conteúdo em todos.

## Conteúdo

- Unidade de análise: um tipo de financiamento vigente na competência.
- Linhas por competência: 6 em 2008-01, 7 em 2026-11; entre as 227 competências convertidas para esta página, de 6 a 7. Cada competência traz a tabela inteira, não só o que mudou.
- Em 2026-11 são sete tipos: `01` Atenção Básica (PAB), `02` Assistência Farmacêutica, `04` Fundo de Ações Estratégicas e Compensações (FAEC), `05` Incentivo - MAC, `06` Média e Alta Complexidade (MAC), `07` Vigilância em Saúde e `08` Gestão do SUS. O código `03` não existe nas competências conferidas.
- Eram seis tipos em 2008-01; o `08` Gestão do SUS aparece a partir de 2012-01.

## Variáveis

As descrições seguem a planilha oficial de layout do ZIP ('DATASUS - Tabela de Procedimentos - Lay-out.xls'), conferidas contra os valores observados em 2026-11. Onde os dados diferem da planilha, isso está dito na coluna 'Unidade / códigos'.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_financiamento` | `CO_FINANCIAMENTO` | texto | Código do tipo de financiamento (2 dígitos) | `01`, `02`, `04` a `08` | todo |
| `no_financiamento` | `NO_FINANCIAMENTO` | texto | Nome do tipo de financiamento | — | todo |
| `dt_competencia` | `DT_COMPETENCIA` | texto | Competência de validade do registro (AAAAMM). Igual à coluna `competencia` em todas as linhas conferidas | AAAAMM | todo |
| `versao` | — (nome do ZIP) | inteiro | Versão da publicação: sufixo `_v` do nome do ZIP, no formato AAMMDDHHMM (data e hora em que o DATASUS gerou o arquivo); 0 quando o nome do ZIP não traz sufixo (competências de 2008-01 a 2009-04) | AAMMDDHHMM; 0 = sem sufixo | todo |
| `competencia` | — (conversor) | texto | Competência (AAAAMM) do ZIP de que a linha veio; igual a `ano` e `mes` juntos | AAAAMM | todo |
| `mes` | — (conversor) | texto | Mês da competência (`MM`, texto de 2 dígitos), gravado pelo conversor; com `ano` (a partição) dá a competência | 01 a 12 | todo |
| `_origem` | — (conversor) | texto | Chave do ZIP de origem da linha: o nome do ZIP sem a extensão e sem o carimbo `@AAAAMMDD` (por exemplo `TabelaUnificada_202610_v2610271043`), gravada pelo conversor | texto | todo |

## No lake

- Dataset `sigtap/tb_financiamento`, particionado por `ano` (inteiro); um arquivo Parquet por ano, `ano=AAAA/<tabela>.parquet`, com as linhas de todas as competências do ano. A competência de cada linha está em `competencia` (AAAAMM) e em `mes` (texto de 2 dígitos, `05`).
- O conversor lê cada linha de largura fixa com o layout do próprio ZIP, aparando espaços nas pontas; campo em branco vira nulo e texto é decodificado de ISO-8859-1 para UTF-8.
- Colunas numéricas viram inteiros ou decimais conforme o layout; valor que não converte vira nulo. Os valores `9999` que a fonte usa como 'não se aplica' ficam como estão.
- Linhas totalmente em branco são ignoradas. Se um ZIP traz mais de uma versão da mesma competência, só a de maior sufixo `_v` é convertida.
- As colunas `versao` (sufixo `_v` do ZIP), `competencia` (AAAAMM, igual a `ano` e `mes` juntos), `mes` e `_origem` são acrescentadas pelo conversor.
- `dt_competencia` é a coluna do arquivo, mantida como texto.

## Cuidados de uso

- **Cada competência é uma fotografia completa, não um incremento.** Sem filtrar `competencia`, o mesmo registro aparece uma vez por competência (esta tabela soma 1.541 linhas nas 227 competências convertidas, contra 7 em 2026-11). Filtre uma competência ou compare competências explicitamente.
- A planilha oficial do ZIP lista os tipos com numeração antiga (por exemplo, `03` FAEC); os códigos e nomes publicados nos dados são os que valem.
- **Junte sempre pela mesma competência.** Códigos, nomes e valores mudam de uma competência para outra; unir tabelas de competências diferentes dá resultados que nunca existiram no SIGTAP.

## Exemplos

Quantidade de procedimentos por tipo de financiamento na competência mais recente.

```python
import duckdb

duckdb.sql("""
    SELECT f.co_financiamento, f.no_financiamento, count(*) AS procedimentos
    FROM read_parquet('lake/sigtap/tb_procedimento/**/*.parquet', hive_partitioning = true, union_by_name = true) p
    JOIN read_parquet('lake/sigtap/tb_financiamento/**/*.parquet', hive_partitioning = true, union_by_name = true) f
      ON f.competencia = p.competencia AND f.co_financiamento = p.co_financiamento
    WHERE p.competencia = '202611'
    GROUP BY 1, 2
    ORDER BY 1
""").show()
```

## Referências

- SIGTAP (Sistema de Gerenciamento da Tabela de Procedimentos, Medicamentos e OPM do SUS): http://sigtap.datasus.gov.br/
- Arquivos de exportação do SIGTAP (FTP do DATASUS): ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/
- Dentro de cada ZIP: a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' e o `LEIA_ME.TXT`.
- Notas técnicas da CGSI/DATASUS sobre cada competência: ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/notastecnicas/
