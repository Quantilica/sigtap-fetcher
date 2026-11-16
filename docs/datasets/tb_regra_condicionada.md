---
dataset:
  id: tb_regra_condicionada
  fonte: sigtap
  titulo: "Regras condicionadas (SIGTAP)"
  resumo: "Regras condicionadas de registro e pagamento de procedimentos: condições (por CID, por registro, por habilitação) que a regra impõe, com nome e texto de descrição."
  orgao: Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde
  pagina_oficial: http://sigtap.datasus.gov.br/
  licenca: "Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos)."
  periodicidade: mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada)
  cobertura: {inicio: 2012-11, fim: em-curso}
  unidade: "uma regra condicionada vigente na competência"
  granularidade: {espacial: "nacional (sem recorte geográfico)", temporal: competência mensal}
  formato_bruto: "ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP"
  lake: {estado: convertido, particoes: [ano, mes], chave: [competencia, co_regra_condicionada], colunas: 5}
  unidades_de_medida:
    versao: "AAMMDDHHMM (identificador da publicação, sem unidade)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.4.0
---

# Regras condicionadas

## Resumo

Regras condicionadas de registro e pagamento de procedimentos: condições (por CID, por registro, por habilitação) que a regra impõe, com nome e texto de descrição.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `sigtap/tb_regra_condicionada` |
| Órgão | Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde |
| Página oficial | http://sigtap.datasus.gov.br/ |
| Licença | Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos). |
| Periodicidade | mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada) |
| Cobertura | 2012-11 a em-curso |
| Unidade (uma linha) | uma regra condicionada vigente na competência |
| Granularidade | espacial: nacional (sem recorte geográfico); temporal: competência mensal |
| Formato bruto | ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP |
| Estado no lake | convertido |
| Partições | `ano`, `mes` |
| Chave | `competencia`, `co_regra_condicionada` |
| Colunas | 5 |
| Unidades de medida | `versao`: AAMMDDHHMM (identificador da publicação, sem unidade) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.4.0 |

## Origem e coleta

- O fetcher baixa, por FTP, o ZIP de cada competência do SIGTAP em `ftp2.datasus.gov.br`, pasta `/pub/sistemas/tup/downloads`. O nome na fonte é `TabelaUnificada_AAAAMM.zip` ou, quando o DATASUS regera a tabela, `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo é a data e a hora da geração.
- No bruto, o arquivo fica em `tabelas/` com o carimbo de data da versão baixada (`TabelaUnificada_AAAAMM_vAAMMDDHHMM@AAAAMMDD.zip`).
- Este dataset vem do membro `tb_regra_condicionada.txt` do ZIP (dados, uma linha por registro, largura fixa) e do layout `tb_regra_condicionada_layout.txt`, que dá nome, tamanho e posição de cada coluna. O ZIP traz ainda o layout reunido de todas as tabelas (`layout.txt`), a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' (dicionário oficial) e o `LEIA_ME.TXT` (histórico das mudanças da estrutura). O fetcher guarda o ZIP inteiro; o conversor lê só os membros `tb_*.txt` e `rl_*.txt` e os layouts.
- Conferido em 2026-11-15 pelo tamanho dos membros dos 227 ZIPs publicados (2008-01 a 2026-11, uma competência por mês, sem lacunas): `tb_regra_condicionada.txt` tem conteúdo em 2012-11 a 2026-11; não existe no ZIP em 2008-01 a 2012-10.

## Conteúdo

- Unidade de análise: uma regra condicionada vigente na competência.
- Linhas por competência: 2 em 2012-11, 15 em 2026-11; entre as 169 competências convertidas para esta página, de 2 a 15. Cada competência traz a tabela inteira, não só o que mudou.
- A tabela existe desde 2012-11, com duas regras; em 2026-11 são 15. `rl_procedimento_regra_cond` diz a quais procedimentos cada uma se aplica.

## Variáveis

As descrições seguem a planilha oficial de layout do ZIP ('DATASUS - Tabela de Procedimentos - Lay-out.xls'), conferidas contra os valores observados em 2026-11. Onde os dados diferem da planilha, isso está dito na coluna 'Unidade / códigos'.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_regra_condicionada` | `CO_REGRA_CONDICIONADA` | texto | Código da regra condicionada (4 dígitos) | — | todo |
| `no_regra_condicionada` | `NO_REGRA_CONDICIONADA` | texto | Nome da regra condicionada, em caixa alta | — | todo |
| `ds_regra_condicionada` | `DS_REGRA_CONDICIONADA` | texto | Descrição da regra condicionada (até 4.000 caracteres); nula na regra `PROJ` em 17 competências, de 2013-06 a 2014-11 | — | todo |
| `versao` | — (nome do ZIP) | inteiro | Versão da publicação: sufixo `_v` do nome do ZIP, no formato AAMMDDHHMM (data e hora em que o DATASUS gerou o arquivo); 0 quando o nome do ZIP não traz sufixo (competências de 2008-01 a 2009-04) | AAMMDDHHMM; 0 = sem sufixo | todo |
| `competencia` | — (conversor) | texto | Competência (AAAAMM) do ZIP de que a linha veio; igual a `ano` e `mes` juntos | AAAAMM | todo |

## No lake

- Dataset `sigtap/tb_regra_condicionada`, particionado por `ano` (inteiro) e `mes` (texto de 2 dígitos, `05`); um arquivo Parquet por ZIP de competência, em `ano=AAAA/mes=MM/`.
- O conversor lê cada linha de largura fixa com o layout do próprio ZIP, aparando espaços nas pontas; campo em branco vira nulo e texto é decodificado de ISO-8859-1 para UTF-8.
- Colunas numéricas viram inteiros ou decimais conforme o layout; valor que não converte vira nulo. Os valores `9999` que a fonte usa como 'não se aplica' ficam como estão.
- Linhas totalmente em branco são ignoradas. Se um ZIP traz mais de uma versão da mesma competência, só a de maior sufixo `_v` é convertida.
- As colunas `versao` (sufixo `_v` do ZIP) e `competencia` (AAAAMM, igual às pastas `ano=`/`mes=`) são acrescentadas pelo conversor.
- O layout desta tabela não tem `DT_COMPETENCIA`; a competência só consta da coluna `competencia` (e das pastas `ano=`/`mes=`).

## Cuidados de uso

- **Cada competência é uma fotografia completa, não um incremento.** Sem filtrar `competencia`, o mesmo registro aparece uma vez por competência (esta tabela soma 1.613 linhas nas 169 competências convertidas, contra 15 em 2026-11). Filtre uma competência ou compare competências explicitamente.
- Em 2014-12 e em competências de 2015 o ZIP traz o layout desta tabela com o nome de coluna `REPLACE(DS_REGRA_CONDICIONADA,CHR(10),NULL)`, que o conversor não reconhece; ele usa então o layout de outra competência e confere a largura (nenhuma linha se perde: ver `No lake`).
- **Junte sempre pela mesma competência.** Códigos, nomes e valores mudam de uma competência para outra; unir tabelas de competências diferentes dá resultados que nunca existiram no SIGTAP.

## Exemplos

Regras condicionadas da competência mais recente e a quantidade de procedimentos a que se aplicam.

```python
import duckdb

duckdb.sql("""
    SELECT r.co_regra_condicionada, r.no_regra_condicionada, count(x.co_procedimento) AS procedimentos
    FROM read_parquet('lake/sigtap/tb_regra_condicionada/**/*.parquet', hive_partitioning = true, union_by_name = true) r
    LEFT JOIN read_parquet('lake/sigtap/rl_procedimento_regra_cond/**/*.parquet', hive_partitioning = true, union_by_name = true) x
      ON x.competencia = r.competencia AND x.co_regra_condicionada = r.co_regra_condicionada
    WHERE r.competencia = '202611'
    GROUP BY 1, 2
    ORDER BY 1
""").show()
```

## Referências

- SIGTAP (Sistema de Gerenciamento da Tabela de Procedimentos, Medicamentos e OPM do SUS): http://sigtap.datasus.gov.br/
- Arquivos de exportação do SIGTAP (FTP do DATASUS): ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/
- Dentro de cada ZIP: a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' e o `LEIA_ME.TXT`.
- Notas técnicas da CGSI/DATASUS sobre cada competência: ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/notastecnicas/
