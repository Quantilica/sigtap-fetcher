---
dataset:
  id: tb_cid
  fonte: sigtap
  titulo: "CID-10 (SIGTAP)"
  resumo: "Classificação Internacional de Doenças (CID-10) como usada pelo SIGTAP, com o tipo de agravo, o sexo de aplicação e, para câncer, se o código admite estadiamento."
  orgao: Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde
  pagina_oficial: http://sigtap.datasus.gov.br/
  licenca: "Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos)."
  periodicidade: mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada)
  cobertura: {inicio: 2008-01, fim: em-curso}
  unidade: "um código da CID-10 (categoria de três caracteres ou subcategoria de quatro) vigente na competência"
  granularidade: {espacial: "nacional (sem recorte geográfico)", temporal: competência mensal}
  formato_bruto: "ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP"
  lake: {estado: convertido, particoes: [competencia], chave: [competencia, co_cid], colunas: 7}
  unidades_de_medida:
    vl_campos_irradiados: "campos"
    versao: "AAMMDDHHMM (identificador da publicação, sem unidade)"
  dados_pessoais: nenhum
  eras:
    - {desde: 2011-04, mudanca: "a tabela ganha as colunas TP_ESTADIO, VL_CAMPOS_IRRADIADOS"}
  revisado_em: 2026-11-15
  versao_fetcher: 0.4.0
---

# CID-10

## Resumo

Classificação Internacional de Doenças (CID-10) como usada pelo SIGTAP, com o tipo de agravo, o sexo de aplicação e, para câncer, se o código admite estadiamento.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `sigtap/tb_cid` |
| Órgão | Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde |
| Página oficial | http://sigtap.datasus.gov.br/ |
| Licença | Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos). |
| Periodicidade | mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada) |
| Cobertura | 2008-01 a em-curso |
| Unidade (uma linha) | um código da CID-10 (categoria de três caracteres ou subcategoria de quatro) vigente na competência |
| Granularidade | espacial: nacional (sem recorte geográfico); temporal: competência mensal |
| Formato bruto | ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP |
| Estado no lake | convertido |
| Partições | `competencia` |
| Chave | `competencia`, `co_cid` |
| Colunas | 7 |
| Unidades de medida | `vl_campos_irradiados`: campos; `versao`: AAMMDDHHMM (identificador da publicação, sem unidade) |
| Dados pessoais | nenhum |
| Eras | 2011-04: a tabela ganha as colunas TP_ESTADIO, VL_CAMPOS_IRRADIADOS |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.4.0 |

## Origem e coleta

- O fetcher baixa, por FTP, o ZIP de cada competência do SIGTAP em `ftp2.datasus.gov.br`, pasta `/pub/sistemas/tup/downloads`. O nome na fonte é `TabelaUnificada_AAAAMM.zip` ou, quando o DATASUS regera a tabela, `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo é a data e a hora da geração.
- No bruto, o arquivo fica em `tabelas/` com o carimbo de data da versão baixada (`TabelaUnificada_AAAAMM_vAAMMDDHHMM@AAAAMMDD.zip`).
- Este dataset vem do membro `tb_cid.txt` do ZIP (dados, uma linha por registro, largura fixa) e do layout `tb_cid_layout.txt`, que dá nome, tamanho e posição de cada coluna. O ZIP traz ainda o layout reunido de todas as tabelas (`layout.txt`), a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' (dicionário oficial) e o `LEIA_ME.TXT` (histórico das mudanças da estrutura). O fetcher guarda o ZIP inteiro; o conversor lê só os membros `tb_*.txt` e `rl_*.txt` e os layouts.
- Conferido em 2026-11-15 pelo tamanho dos membros dos 227 ZIPs publicados (2008-01 a 2026-11, uma competência por mês, sem lacunas), `tb_cid.txt` existe e tem conteúdo em todos.

## Conteúdo

- Unidade de análise: um código da CID-10 (categoria de três caracteres ou subcategoria de quatro) vigente na competência.
- Linhas por competência: 12.422 em 2008-01, 14.246 em 2026-11; entre as 227 competências convertidas para esta página, de 12.422 a 14.246. Cada competência traz a tabela inteira, não só o que mudou.
- Em 2026-11 são 14.246 códigos (12.422 em 2008-01); 101 com agravo de bloqueio, 338 com agravo de notificação, 390 estadiáveis.
- Esta tabela não traz `dt_competencia`: o ZIP deixou de gravar a data nesta tabela desde 2007-11 (LEIA_ME).
- Mudanças de estrutura (conferidas nos layouts dos ZIPs):
    - 2011-04: a tabela ganha as colunas TP_ESTADIO, VL_CAMPOS_IRRADIADOS.

## Variáveis

As descrições seguem a planilha oficial de layout do ZIP ('DATASUS - Tabela de Procedimentos - Lay-out.xls'), conferidas contra os valores observados em 2026-11. Onde os dados diferem da planilha, isso está dito na coluna 'Unidade / códigos'.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_cid` | `CO_CID` | texto | Código da CID-10 sem ponto (3 ou 4 caracteres) | — | todo |
| `no_cid` | `NO_CID` | texto | Nome da doença | — | todo |
| `tp_agravo` | `TP_AGRAVO` | texto | Tipo de agravo a ser notificado | `0` sem agravo; `1` agravo de notificação; `2` agravo de bloqueio | todo |
| `tp_sexo` | `TP_SEXO` | texto | Sexo a que o código se aplica | `I` indiferente (em 2026-11, todas as linhas) | todo |
| `tp_estadio` | `TP_ESTADIO` | texto | Se o CID é estadiável (câncer) | `S` sim; `N` não | desde 2011-04 |
| `vl_campos_irradiados` | `VL_CAMPOS_IRRADIADOS` | inteiro | Quantidade de campos irradiados associada ao código (radioterapia) | 0 a 144 em 2026-11 | desde 2011-04 |
| `versao` | — (nome do ZIP) | inteiro | Versão da publicação: sufixo `_v` do nome do ZIP, no formato AAMMDDHHMM (data e hora em que o DATASUS gerou o arquivo); 0 quando o nome do ZIP não traz sufixo (competências de 2008-01 a 2009-04) | AAMMDDHHMM; 0 = sem sufixo | todo |
| `competencia` | — (partição) | texto | Competência (AAAAMM) do ZIP de que a linha veio | AAAAMM | todo |

## No lake

- Dataset `sigtap/tb_cid`, particionado por `competencia` (AAAAMM, texto); um arquivo Parquet por ZIP de competência.
- O conversor lê cada linha de largura fixa com o layout do próprio ZIP, aparando espaços nas pontas; campo em branco vira nulo e texto é decodificado de ISO-8859-1 para UTF-8.
- Colunas numéricas viram inteiros ou decimais conforme o layout; valor que não converte vira nulo. Os valores `9999` que a fonte usa como 'não se aplica' ficam como estão.
- Linhas totalmente em branco são ignoradas. Se um ZIP traz mais de uma versão da mesma competência, só a de maior sufixo `_v` é convertida.
- As colunas `versao` (sufixo `_v` do ZIP) e a partição `competencia` são acrescentadas pelo conversor.
- O layout desta tabela não tem `DT_COMPETENCIA`; a competência só consta da partição.

## Cuidados de uso

- **Cada competência é uma fotografia completa, não um incremento.** Sem filtrar `competencia`, o mesmo registro aparece uma vez por competência (esta tabela soma 2.995.633 linhas nas 227 competências convertidas, contra 14.246 em 2026-11). Filtre uma competência ou compare competências explicitamente.
- O código não tem o ponto da CID-10 impresso (`A000`, não `A00.0`).
- As colunas `tp_estadio` e `vl_campos_irradiados` ficam nulas nas competências anteriores a 2011-04.
- Em 2014-04, `co_cid` não é único: `A778`, `A779` e `Y090` aparecem duas vezes, com linhas diferentes (14.233 linhas na competência). Nas outras 226 competências a chave é única.
- **Junte sempre pela mesma competência.** Códigos, nomes e valores mudam de uma competência para outra; unir tabelas de competências diferentes dá resultados que nunca existiram no SIGTAP.

## Exemplos

Quantidade de CIDs por tipo de agravo na competência mais recente.

```python
import duckdb

duckdb.sql("""
    SELECT tp_agravo, count(*) AS cids
    FROM read_parquet('lake/sigtap/tb_cid/**/*.parquet', hive_partitioning = true, union_by_name = true)
    WHERE competencia = '202611'
    GROUP BY 1
    ORDER BY 1
""").show()
```

## Referências

- SIGTAP (Sistema de Gerenciamento da Tabela de Procedimentos, Medicamentos e OPM do SUS): http://sigtap.datasus.gov.br/
- Arquivos de exportação do SIGTAP (FTP do DATASUS): ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/
- Dentro de cada ZIP: a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' e o `LEIA_ME.TXT`.
- Notas técnicas da CGSI/DATASUS sobre cada competência: ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/notastecnicas/
