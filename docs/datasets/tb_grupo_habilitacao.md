---
dataset:
  id: tb_grupo_habilitacao
  fonte: sigtap
  titulo: "Grupos de habilitação (SIGTAP)"
  resumo: "Grupos de habilitações exigidas em conjunto: um procedimento ligado a um grupo exige do estabelecimento todas as habilitações do grupo (por exemplo, `0801 e 0803`)."
  orgao: Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde
  pagina_oficial: http://sigtap.datasus.gov.br/
  licenca: "Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos)."
  periodicidade: mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada)
  cobertura: {inicio: 2008-01, fim: em-curso}
  unidade: "um grupo de habilitações vigente na competência"
  granularidade: {espacial: "nacional (sem recorte geográfico)", temporal: competência mensal}
  formato_bruto: "ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP"
  lake: {estado: convertido, particoes: [competencia], chave: [competencia, nu_grupo_habilitacao], colunas: 4}
  unidades_de_medida:
    versao: "AAMMDDHHMM (identificador da publicação, sem unidade)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.4.0
---

# Grupos de habilitação

## Resumo

Grupos de habilitações exigidas em conjunto: um procedimento ligado a um grupo exige do estabelecimento todas as habilitações do grupo (por exemplo, `0801 e 0803`).

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `sigtap/tb_grupo_habilitacao` |
| Órgão | Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde |
| Página oficial | http://sigtap.datasus.gov.br/ |
| Licença | Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos). |
| Periodicidade | mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada) |
| Cobertura | 2008-01 a em-curso |
| Unidade (uma linha) | um grupo de habilitações vigente na competência |
| Granularidade | espacial: nacional (sem recorte geográfico); temporal: competência mensal |
| Formato bruto | ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP |
| Estado no lake | convertido |
| Partições | `competencia` |
| Chave | `competencia`, `nu_grupo_habilitacao` |
| Colunas | 4 |
| Unidades de medida | `versao`: AAMMDDHHMM (identificador da publicação, sem unidade) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.4.0 |

## Origem e coleta

- O fetcher baixa, por FTP, o ZIP de cada competência do SIGTAP em `ftp2.datasus.gov.br`, pasta `/pub/sistemas/tup/downloads`. O nome na fonte é `TabelaUnificada_AAAAMM.zip` ou, quando o DATASUS regera a tabela, `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo é a data e a hora da geração.
- No bruto, o arquivo fica em `tabelas/` com o carimbo de data da versão baixada (`TabelaUnificada_AAAAMM_vAAMMDDHHMM@AAAAMMDD.zip`).
- Este dataset vem do membro `tb_grupo_habilitacao.txt` do ZIP (dados, uma linha por registro, largura fixa) e do layout `tb_grupo_habilitacao_layout.txt`, que dá nome, tamanho e posição de cada coluna. O ZIP traz ainda o layout reunido de todas as tabelas (`layout.txt`), a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' (dicionário oficial) e o `LEIA_ME.TXT` (histórico das mudanças da estrutura). O fetcher guarda o ZIP inteiro; o conversor lê só os membros `tb_*.txt` e `rl_*.txt` e os layouts.
- Conferido em 2026-11-15 pelo tamanho dos membros dos 227 ZIPs publicados (2008-01 a 2026-11, uma competência por mês, sem lacunas), `tb_grupo_habilitacao.txt` existe e tem conteúdo em todos.

## Conteúdo

- Unidade de análise: um grupo de habilitações vigente na competência.
- Linhas por competência: 10 em 2008-01, 31 em 2026-11; entre as 227 competências convertidas para esta página, de 10 a 31. Cada competência traz a tabela inteira, não só o que mudou.
- Em 2026-11 são 31 grupos (10 em 2008-01). O grupo foi criado em 2008-03 porque a habilitação do procedimento pode exigir várias habilitações em conjunto, e não só uma (LEIA_ME).
- Esta tabela não traz `dt_competencia`.

## Variáveis

As descrições seguem a planilha oficial de layout do ZIP ('DATASUS - Tabela de Procedimentos - Lay-out.xls'), conferidas contra os valores observados em 2026-11. Onde os dados diferem da planilha, isso está dito na coluna 'Unidade / códigos'.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `nu_grupo_habilitacao` | `NU_GRUPO_HABILITACAO` | texto | Número do grupo de habilitação (4 dígitos) | — | todo |
| `no_grupo_habilitacao` | `NO_GRUPO_HABILITACAO` | texto | Nome curto do grupo (até 20 caracteres), normalmente as habilitações que o compõem, como `0801 e 0803` | — | todo |
| `ds_grupo_habilitacao` | `DS_GRUPO_HABILITACAO` | texto | Descrição longa do grupo (até 250 caracteres) | — | todo |
| `versao` | — (nome do ZIP) | inteiro | Versão da publicação: sufixo `_v` do nome do ZIP, no formato AAMMDDHHMM (data e hora em que o DATASUS gerou o arquivo); 0 quando o nome do ZIP não traz sufixo (competências de 2008-01 a 2009-04) | AAMMDDHHMM; 0 = sem sufixo | todo |
| `competencia` | — (partição) | texto | Competência (AAAAMM) do ZIP de que a linha veio | AAAAMM | todo |

## No lake

- Dataset `sigtap/tb_grupo_habilitacao`, particionado por `competencia` (AAAAMM, texto); um arquivo Parquet por ZIP de competência.
- O conversor lê cada linha de largura fixa com o layout do próprio ZIP, aparando espaços nas pontas; campo em branco vira nulo e texto é decodificado de ISO-8859-1 para UTF-8.
- Colunas numéricas viram inteiros ou decimais conforme o layout; valor que não converte vira nulo. Os valores `9999` que a fonte usa como 'não se aplica' ficam como estão.
- Linhas totalmente em branco são ignoradas. Se um ZIP traz mais de uma versão da mesma competência, só a de maior sufixo `_v` é convertida.
- As colunas `versao` (sufixo `_v` do ZIP) e a partição `competencia` são acrescentadas pelo conversor.
- O layout desta tabela não tem `DT_COMPETENCIA`; a competência só consta da partição.

## Cuidados de uso

- **Cada competência é uma fotografia completa, não um incremento.** Sem filtrar `competencia`, o mesmo registro aparece uma vez por competência (esta tabela soma 4.960 linhas nas 227 competências convertidas, contra 31 em 2026-11). Filtre uma competência ou compare competências explicitamente.
- Há registros de teste na fonte: em 2026-11 os grupos `0174` e `0175` se chamam 'Teste' e o `0176` tem nome e descrição 'h'. Não use a descrição como texto de apresentação sem revisar.
- **Junte sempre pela mesma competência.** Códigos, nomes e valores mudam de uma competência para outra; unir tabelas de competências diferentes dá resultados que nunca existiram no SIGTAP.

## Exemplos

Grupos de habilitação da competência mais recente e quantos procedimentos usam cada um.

```python
import duckdb

duckdb.sql("""
    SELECT g.nu_grupo_habilitacao, g.no_grupo_habilitacao, count(DISTINCT x.co_procedimento) AS procedimentos
    FROM read_parquet('lake/sigtap/tb_grupo_habilitacao/**/*.parquet', hive_partitioning = true, union_by_name = true) g
    LEFT JOIN read_parquet('lake/sigtap/rl_procedimento_habilitacao/**/*.parquet', hive_partitioning = true, union_by_name = true) x
      ON x.competencia = g.competencia AND x.nu_grupo_habilitacao = g.nu_grupo_habilitacao
    WHERE g.competencia = '202611'
    GROUP BY 1, 2
    ORDER BY 3 DESC
""").show()
```

## Referências

- SIGTAP (Sistema de Gerenciamento da Tabela de Procedimentos, Medicamentos e OPM do SUS): http://sigtap.datasus.gov.br/
- Arquivos de exportação do SIGTAP (FTP do DATASUS): ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/
- Dentro de cada ZIP: a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' e o `LEIA_ME.TXT`.
- Notas técnicas da CGSI/DATASUS sobre cada competência: ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/notastecnicas/
