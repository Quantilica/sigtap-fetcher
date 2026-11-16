---
dataset:
  id: tb_forma_organizacao
  fonte: sigtap
  titulo: "Formas de organização (SIGTAP)"
  resumo: "Terceiro nível da classificação dos procedimentos: as formas de organização de cada subgrupo, identificadas pelos seis primeiros dígitos do código do procedimento."
  orgao: Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde
  pagina_oficial: http://sigtap.datasus.gov.br/
  licenca: "Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos)."
  periodicidade: mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada)
  cobertura: {inicio: 2008-01, fim: em-curso}
  unidade: "uma forma de organização (grupo, subgrupo e forma) vigente na competência"
  granularidade: {espacial: "nacional (sem recorte geográfico)", temporal: competência mensal}
  formato_bruto: "ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP"
  lake: {estado: convertido, particoes: [competencia], chave: [competencia, co_grupo, co_sub_grupo, co_forma_organizacao], colunas: 6}
  unidades_de_medida:
    versao: "AAMMDDHHMM (identificador da publicação, sem unidade)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.4.0
---

# Formas de organização

## Resumo

Terceiro nível da classificação dos procedimentos: as formas de organização de cada subgrupo, identificadas pelos seis primeiros dígitos do código do procedimento.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `sigtap/tb_forma_organizacao` |
| Órgão | Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde |
| Página oficial | http://sigtap.datasus.gov.br/ |
| Licença | Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos). |
| Periodicidade | mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada) |
| Cobertura | 2008-01 a em-curso |
| Unidade (uma linha) | uma forma de organização (grupo, subgrupo e forma) vigente na competência |
| Granularidade | espacial: nacional (sem recorte geográfico); temporal: competência mensal |
| Formato bruto | ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP |
| Estado no lake | convertido |
| Partições | `competencia` |
| Chave | `competencia`, `co_grupo`, `co_sub_grupo`, `co_forma_organizacao` |
| Colunas | 6 |
| Unidades de medida | `versao`: AAMMDDHHMM (identificador da publicação, sem unidade) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.4.0 |

## Origem e coleta

- O fetcher baixa, por FTP, o ZIP de cada competência do SIGTAP em `ftp2.datasus.gov.br`, pasta `/pub/sistemas/tup/downloads`. O nome na fonte é `TabelaUnificada_AAAAMM.zip` ou, quando o DATASUS regera a tabela, `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo é a data e a hora da geração.
- No bruto, o arquivo fica em `tabelas/` com o carimbo de data da versão baixada (`TabelaUnificada_AAAAMM_vAAMMDDHHMM@AAAAMMDD.zip`).
- Este dataset vem do membro `tb_forma_organizacao.txt` do ZIP (dados, uma linha por registro, largura fixa) e do layout `tb_forma_organizacao_layout.txt`, que dá nome, tamanho e posição de cada coluna. O ZIP traz ainda o layout reunido de todas as tabelas (`layout.txt`), a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' (dicionário oficial) e o `LEIA_ME.TXT` (histórico das mudanças da estrutura). O fetcher guarda o ZIP inteiro; o conversor lê só os membros `tb_*.txt` e `rl_*.txt` e os layouts.
- Conferido em 2026-11-15 pelo tamanho dos membros dos 227 ZIPs publicados (2008-01 a 2026-11, uma competência por mês, sem lacunas), `tb_forma_organizacao.txt` existe e tem conteúdo em todos.

## Conteúdo

- Unidade de análise: uma forma de organização (grupo, subgrupo e forma) vigente na competência.
- Linhas por competência: 301 em 2008-01, 424 em 2026-11; entre as 227 competências convertidas para esta página, de 301 a 424. Cada competência traz a tabela inteira, não só o que mudou.
- O código completo da forma é `co_grupo` + `co_sub_grupo` + `co_forma_organizacao`, igual aos seis primeiros dígitos de `co_procedimento`. Em 2026-11, os 368 prefixos de seis dígitos presentes em `tb_procedimento` têm forma de organização cadastrada.

## Variáveis

As descrições seguem a planilha oficial de layout do ZIP ('DATASUS - Tabela de Procedimentos - Lay-out.xls'), conferidas contra os valores observados em 2026-11. Onde os dados diferem da planilha, isso está dito na coluna 'Unidade / códigos'.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_grupo` | `CO_GRUPO` | texto | Código do grupo dos procedimentos | 01 a 09 | todo |
| `co_sub_grupo` | `CO_SUB_GRUPO` | texto | Código do subgrupo dentro do grupo (2 dígitos) | — | todo |
| `co_forma_organizacao` | `CO_FORMA_ORGANIZACAO` | texto | Código da forma de organização dentro do subgrupo (2 dígitos); só identifica a forma junto com grupo e subgrupo | — | todo |
| `no_forma_organizacao` | `NO_FORMA_ORGANIZACAO` | texto | Nome da forma de organização dos procedimentos | — | todo |
| `dt_competencia` | `DT_COMPETENCIA` | texto | Competência de validade do registro (AAAAMM). Igual à partição `competencia` em todas as linhas conferidas | AAAAMM | todo |
| `versao` | — (nome do ZIP) | inteiro | Versão da publicação: sufixo `_v` do nome do ZIP, no formato AAMMDDHHMM (data e hora em que o DATASUS gerou o arquivo); 0 quando o nome do ZIP não traz sufixo (competências de 2008-01 a 2009-04) | AAMMDDHHMM; 0 = sem sufixo | todo |
| `competencia` | — (partição) | texto | Competência (AAAAMM) do ZIP de que a linha veio | AAAAMM | todo |

## No lake

- Dataset `sigtap/tb_forma_organizacao`, particionado por `competencia` (AAAAMM, texto); um arquivo Parquet por ZIP de competência.
- O conversor lê cada linha de largura fixa com o layout do próprio ZIP, aparando espaços nas pontas; campo em branco vira nulo e texto é decodificado de ISO-8859-1 para UTF-8.
- Colunas numéricas viram inteiros ou decimais conforme o layout; valor que não converte vira nulo. Os valores `9999` que a fonte usa como 'não se aplica' ficam como estão.
- Linhas totalmente em branco são ignoradas. Se um ZIP traz mais de uma versão da mesma competência, só a de maior sufixo `_v` é convertida.
- As colunas `versao` (sufixo `_v` do ZIP) e a partição `competencia` são acrescentadas pelo conversor.
- `dt_competencia` é a coluna do arquivo, mantida como texto.

## Cuidados de uso

- **Cada competência é uma fotografia completa, não um incremento.** Sem filtrar `competencia`, o mesmo registro aparece uma vez por competência (esta tabela soma 85.800 linhas nas 227 competências convertidas, contra 424 em 2026-11). Filtre uma competência ou compare competências explicitamente.
- O nome vem em caixa mista e, em algumas formas recentes, termina com ponto final; não use o nome como chave.
- **Junte sempre pela mesma competência.** Códigos, nomes e valores mudam de uma competência para outra; unir tabelas de competências diferentes dá resultados que nunca existiram no SIGTAP.

## Exemplos

As formas de organização com mais procedimentos na competência mais recente.

```python
import duckdb

duckdb.sql("""
    SELECT f.co_grupo || f.co_sub_grupo || f.co_forma_organizacao AS forma,
           f.no_forma_organizacao, count(*) AS procedimentos
    FROM read_parquet('lake/sigtap/tb_procedimento/**/*.parquet', hive_partitioning = true, union_by_name = true) p
    JOIN read_parquet('lake/sigtap/tb_forma_organizacao/**/*.parquet', hive_partitioning = true, union_by_name = true) f
      ON f.competencia = p.competencia
     AND f.co_grupo || f.co_sub_grupo || f.co_forma_organizacao = substr(p.co_procedimento, 1, 6)
    WHERE p.competencia = '202611'
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
