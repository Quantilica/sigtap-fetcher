---
dataset:
  id: tb_renases
  fonte: sigtap
  titulo: "RENASES (SIGTAP)"
  resumo: "Relação Nacional de Ações e Serviços de Saúde (RENASES): lista das ações e serviços de saúde que o SUS oferece, a que os procedimentos são associados."
  orgao: Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde
  pagina_oficial: http://sigtap.datasus.gov.br/
  licenca: "Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos)."
  periodicidade: mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada)
  cobertura: {inicio: 2014-04, fim: em-curso}
  unidade: "uma ação ou serviço da RENASES vigente na competência"
  granularidade: {espacial: "nacional (sem recorte geográfico)", temporal: competência mensal}
  formato_bruto: "ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP"
  lake: {estado: convertido, particoes: [ano], chave: [competencia, co_renases], colunas: 6}
  unidades_de_medida:
    versao: "AAMMDDHHMM (identificador da publicação, sem unidade)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.4.0
---

# RENASES

## Resumo

Relação Nacional de Ações e Serviços de Saúde (RENASES): lista das ações e serviços de saúde que o SUS oferece, a que os procedimentos são associados.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `sigtap/tb_renases` |
| Órgão | Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde |
| Página oficial | http://sigtap.datasus.gov.br/ |
| Licença | Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos). |
| Periodicidade | mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada) |
| Cobertura | 2014-04 a em-curso |
| Unidade (uma linha) | uma ação ou serviço da RENASES vigente na competência |
| Granularidade | espacial: nacional (sem recorte geográfico); temporal: competência mensal |
| Formato bruto | ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP |
| Estado no lake | convertido |
| Partições | `ano` |
| Chave | `competencia`, `co_renases` |
| Colunas | 6 |
| Unidades de medida | `versao`: AAMMDDHHMM (identificador da publicação, sem unidade) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.4.0 |

## Origem e coleta

- O fetcher baixa, por FTP, o ZIP de cada competência do SIGTAP em `ftp2.datasus.gov.br`, pasta `/pub/sistemas/tup/downloads`. O nome na fonte é `TabelaUnificada_AAAAMM.zip` ou, quando o DATASUS regera a tabela, `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo é a data e a hora da geração.
- No bruto, o arquivo fica em `tabelas/` com o carimbo de data da versão baixada (`TabelaUnificada_AAAAMM_vAAMMDDHHMM@AAAAMMDD.zip`).
- Este dataset vem do membro `tb_renases.txt` do ZIP (dados, uma linha por registro, largura fixa) e do layout `tb_renases_layout.txt`, que dá nome, tamanho e posição de cada coluna. O ZIP traz ainda o layout reunido de todas as tabelas (`layout.txt`), a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' (dicionário oficial) e o `LEIA_ME.TXT` (histórico das mudanças da estrutura). O fetcher guarda o ZIP inteiro; o conversor lê só os membros `tb_*.txt` e `rl_*.txt` e os layouts.
- Conferido em 2026-11-15 pelo tamanho dos membros dos 227 ZIPs publicados (2008-01 a 2026-11, uma competência por mês, sem lacunas): `tb_renases.txt` tem conteúdo em 2014-04, 2015-04 a 2026-11; não existe no ZIP em 2008-01 a 2014-03, 2014-05 a 2015-03.

## Conteúdo

- Unidade de análise: uma ação ou serviço da RENASES vigente na competência.
- Linhas por competência: 201 em 2014-04, 201 em 2026-11; entre as 141 competências convertidas para esta página, de 201 a 201. Cada competência traz a tabela inteira, não só o que mudou.
- Em 2026-11 são 201 itens, o mesmo número em todas as competências com conteúdo (2014-04 e 2015-04 em diante).
- Esta tabela não consta da planilha oficial de layout: as descrições vêm dos nomes e dos valores observados. Não traz `dt_competencia`.

## Variáveis

Esta tabela não consta da planilha oficial de layout do ZIP (que traz só as colunas até a versão de 2008-2014): as descrições vêm do nome das colunas e dos valores observados.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_renases` | `CO_RENASES` | texto | Código da ação ou serviço da RENASES (3 dígitos) | `001` a `201` em 2026-11 | todo |
| `no_renases` | `NO_RENASES` | texto | Nome da ação ou serviço da RENASES | — | todo |
| `versao` | — (nome do ZIP) | inteiro | Versão da publicação: sufixo `_v` do nome do ZIP, no formato AAMMDDHHMM (data e hora em que o DATASUS gerou o arquivo); 0 quando o nome do ZIP não traz sufixo (competências de 2008-01 a 2009-04) | AAMMDDHHMM; 0 = sem sufixo | todo |
| `competencia` | — (conversor) | texto | Competência (AAAAMM) do ZIP de que a linha veio; igual a `ano` e `mes` juntos | AAAAMM | todo |
| `mes` | — (conversor) | texto | Mês da competência (`MM`, texto de 2 dígitos), gravado pelo conversor; com `ano` (a partição) dá a competência | 01 a 12 | todo |
| `_origem` | — (conversor) | texto | Chave do ZIP de origem da linha: o nome do ZIP sem a extensão e sem o carimbo `@AAAAMMDD` (por exemplo `TabelaUnificada_202610_v2610271043`), gravada pelo conversor | texto | todo |

## No lake

- Dataset `sigtap/tb_renases`, particionado por `ano` (inteiro); um arquivo Parquet por ano, `ano=AAAA/<tabela>.parquet`, com as linhas de todas as competências do ano. A competência de cada linha está em `competencia` (AAAAMM) e em `mes` (texto de 2 dígitos, `05`).
- O conversor lê cada linha de largura fixa com o layout do próprio ZIP, aparando espaços nas pontas; campo em branco vira nulo e texto é decodificado de ISO-8859-1 para UTF-8.
- Colunas numéricas viram inteiros ou decimais conforme o layout; valor que não converte vira nulo. Os valores `9999` que a fonte usa como 'não se aplica' ficam como estão.
- Linhas totalmente em branco são ignoradas. Se um ZIP traz mais de uma versão da mesma competência, só a de maior sufixo `_v` é convertida.
- As colunas `versao` (sufixo `_v` do ZIP), `competencia` (AAAAMM, igual a `ano` e `mes` juntos), `mes` e `_origem` são acrescentadas pelo conversor.
- O layout desta tabela não tem `DT_COMPETENCIA`; a competência só consta da coluna `competencia` (e de `ano` e `mes`).

## Cuidados de uso

- **Cada competência é uma fotografia completa, não um incremento.** Sem filtrar `competencia`, o mesmo registro aparece uma vez por competência (esta tabela soma 28.341 linhas nas 141 competências convertidas, contra 201 em 2026-11). Filtre uma competência ou compare competências explicitamente.
- Os itens da RENASES não substituem a classificação por grupo, subgrupo e forma de organização; um procedimento pode estar ligado a vários itens (`rl_procedimento_renases`).
- **Junte sempre pela mesma competência.** Códigos, nomes e valores mudam de uma competência para outra; unir tabelas de competências diferentes dá resultados que nunca existiram no SIGTAP.

## Exemplos

Itens da RENASES com mais procedimentos associados na competência mais recente.

```python
import duckdb

duckdb.sql("""
    SELECT r.co_renases, r.no_renases, count(DISTINCT x.co_procedimento) AS procedimentos
    FROM read_parquet('lake/sigtap/rl_procedimento_renases/**/*.parquet', hive_partitioning = true, union_by_name = true) x
    JOIN read_parquet('lake/sigtap/tb_renases/**/*.parquet', hive_partitioning = true, union_by_name = true) r
      ON r.competencia = x.competencia AND r.co_renases = x.co_renases
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
