---
dataset:
  id: tb_rede_atencao
  fonte: sigtap
  titulo: "Redes de atenção (SIGTAP)"
  resumo: "Redes temáticas de atenção à saúde (Rede Cegonha, Urgência e Emergência, Psicossocial e outras) a que os componentes de rede pertencem."
  orgao: Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde
  pagina_oficial: http://sigtap.datasus.gov.br/
  licenca: "Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos)."
  periodicidade: mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada)
  cobertura: {inicio: 2014-04, fim: em-curso}
  unidade: "uma rede de atenção vigente na competência"
  granularidade: {espacial: "nacional (sem recorte geográfico)", temporal: competência mensal}
  formato_bruto: "ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP"
  lake: {estado: convertido, particoes: [ano, mes], chave: [competencia, co_rede_atencao], colunas: 4}
  unidades_de_medida:
    versao: "AAMMDDHHMM (identificador da publicação, sem unidade)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.4.0
---

# Redes de atenção

## Resumo

Redes temáticas de atenção à saúde (Rede Cegonha, Urgência e Emergência, Psicossocial e outras) a que os componentes de rede pertencem.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `sigtap/tb_rede_atencao` |
| Órgão | Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde |
| Página oficial | http://sigtap.datasus.gov.br/ |
| Licença | Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos). |
| Periodicidade | mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada) |
| Cobertura | 2014-04 a em-curso |
| Unidade (uma linha) | uma rede de atenção vigente na competência |
| Granularidade | espacial: nacional (sem recorte geográfico); temporal: competência mensal |
| Formato bruto | ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP |
| Estado no lake | convertido |
| Partições | `ano`, `mes` |
| Chave | `competencia`, `co_rede_atencao` |
| Colunas | 4 |
| Unidades de medida | `versao`: AAMMDDHHMM (identificador da publicação, sem unidade) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.4.0 |

## Origem e coleta

- O fetcher baixa, por FTP, o ZIP de cada competência do SIGTAP em `ftp2.datasus.gov.br`, pasta `/pub/sistemas/tup/downloads`. O nome na fonte é `TabelaUnificada_AAAAMM.zip` ou, quando o DATASUS regera a tabela, `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo é a data e a hora da geração.
- No bruto, o arquivo fica em `tabelas/` com o carimbo de data da versão baixada (`TabelaUnificada_AAAAMM_vAAMMDDHHMM@AAAAMMDD.zip`).
- Este dataset vem do membro `tb_rede_atencao.txt` do ZIP (dados, uma linha por registro, largura fixa) e do layout `tb_rede_atencao_layout.txt`, que dá nome, tamanho e posição de cada coluna. O ZIP traz ainda o layout reunido de todas as tabelas (`layout.txt`), a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' (dicionário oficial) e o `LEIA_ME.TXT` (histórico das mudanças da estrutura). O fetcher guarda o ZIP inteiro; o conversor lê só os membros `tb_*.txt` e `rl_*.txt` e os layouts.
- Conferido em 2026-11-15 pelo tamanho dos membros dos 227 ZIPs publicados (2008-01 a 2026-11, uma competência por mês, sem lacunas): `tb_rede_atencao.txt` tem conteúdo em 2014-04, 2015-04 a 2026-11; não existe no ZIP em 2008-01 a 2014-03, 2014-05 a 2015-03.

## Conteúdo

- Unidade de análise: uma rede de atenção vigente na competência.
- Linhas por competência: 4 em 2014-04, 5 em 2026-11; entre as 141 competências convertidas para esta página, de 4 a 5. Cada competência traz a tabela inteira, não só o que mudou.
- Em 2026-11 são cinco redes: `092` Cegonha, `093` Urgência e Emergência, `094` Psicossocial, `095` Cuidados à Pessoa com Deficiência e `096` Atenção Especializada à Saúde da População Trans (quatro redes em 2020-01).
- Esta tabela não consta da planilha oficial de layout: as descrições vêm dos nomes e dos valores observados. Não traz `dt_competencia`.

## Variáveis

Esta tabela não consta da planilha oficial de layout do ZIP (que traz só as colunas até a versão de 2008-2014): as descrições vêm do nome das colunas e dos valores observados.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_rede_atencao` | `CO_REDE_ATENCAO` | texto | Código da rede de atenção (3 dígitos) | `092` a `096` em 2026-11 | todo |
| `no_rede_atencao` | `NO_REDE_ATENCAO` | texto | Nome da rede de atenção | — | todo |
| `versao` | — (nome do ZIP) | inteiro | Versão da publicação: sufixo `_v` do nome do ZIP, no formato AAMMDDHHMM (data e hora em que o DATASUS gerou o arquivo); 0 quando o nome do ZIP não traz sufixo (competências de 2008-01 a 2009-04) | AAMMDDHHMM; 0 = sem sufixo | todo |
| `competencia` | — (conversor) | texto | Competência (AAAAMM) do ZIP de que a linha veio; igual a `ano` e `mes` juntos | AAAAMM | todo |

## No lake

- Dataset `sigtap/tb_rede_atencao`, particionado por `ano` (inteiro) e `mes` (texto de 2 dígitos, `05`); um arquivo Parquet por ZIP de competência, em `ano=AAAA/mes=MM/`.
- O conversor lê cada linha de largura fixa com o layout do próprio ZIP, aparando espaços nas pontas; campo em branco vira nulo e texto é decodificado de ISO-8859-1 para UTF-8.
- Colunas numéricas viram inteiros ou decimais conforme o layout; valor que não converte vira nulo. Os valores `9999` que a fonte usa como 'não se aplica' ficam como estão.
- Linhas totalmente em branco são ignoradas. Se um ZIP traz mais de uma versão da mesma competência, só a de maior sufixo `_v` é convertida.
- As colunas `versao` (sufixo `_v` do ZIP) e `competencia` (AAAAMM, igual às pastas `ano=`/`mes=`) são acrescentadas pelo conversor.
- O layout desta tabela não tem `DT_COMPETENCIA`; a competência só consta da coluna `competencia` (e das pastas `ano=`/`mes=`).

## Cuidados de uso

- **Cada competência é uma fotografia completa, não um incremento.** Sem filtrar `competencia`, o mesmo registro aparece uma vez por competência (esta tabela soma 599 linhas nas 141 competências convertidas, contra 5 em 2026-11). Filtre uma competência ou compare competências explicitamente.
- Os nomes têm erros de grafia na fonte (por exemplo, 'Cuidados á Pessoa com Deficiêcia').
- **Junte sempre pela mesma competência.** Códigos, nomes e valores mudam de uma competência para outra; unir tabelas de competências diferentes dá resultados que nunca existiram no SIGTAP.

## Exemplos

Componentes de rede por rede de atenção na competência mais recente.

```python
import duckdb

duckdb.sql("""
    SELECT r.co_rede_atencao, r.no_rede_atencao, count(*) AS componentes
    FROM read_parquet('lake/sigtap/tb_componente_rede/**/*.parquet', hive_partitioning = true, union_by_name = true) c
    JOIN read_parquet('lake/sigtap/tb_rede_atencao/**/*.parquet', hive_partitioning = true, union_by_name = true) r
      ON r.competencia = c.competencia AND r.co_rede_atencao = c.co_rede_atencao
    WHERE c.competencia = '202611'
    GROUP BY 1, 2
    ORDER BY 1
""").show()
```

## Referências

- SIGTAP (Sistema de Gerenciamento da Tabela de Procedimentos, Medicamentos e OPM do SUS): http://sigtap.datasus.gov.br/
- Arquivos de exportação do SIGTAP (FTP do DATASUS): ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/
- Dentro de cada ZIP: a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' e o `LEIA_ME.TXT`.
- Notas técnicas da CGSI/DATASUS sobre cada competência: ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/notastecnicas/
