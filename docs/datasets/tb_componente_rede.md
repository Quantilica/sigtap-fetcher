---
dataset:
  id: tb_componente_rede
  fonte: sigtap
  titulo: "Componentes de rede (SIGTAP)"
  resumo: "Componentes das redes de atenção à saúde (por exemplo, 'Pré-natal', 'Sala de estabilização'), a que os procedimentos podem ser associados."
  orgao: Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde
  pagina_oficial: http://sigtap.datasus.gov.br/
  licenca: "Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos)."
  periodicidade: mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada)
  cobertura: {inicio: 2014-04, fim: em-curso}
  unidade: "um componente de rede vigente na competência"
  granularidade: {espacial: "nacional (sem recorte geográfico)", temporal: competência mensal}
  formato_bruto: "ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP"
  lake: {estado: convertido, particoes: [ano, mes], chave: [competencia, co_componente_rede], colunas: 5}
  unidades_de_medida:
    versao: "AAMMDDHHMM (identificador da publicação, sem unidade)"
  dados_pessoais: nenhum
  eras:
    - {desde: 2015-04, mudanca: "a tabela perde a coluna CO_REDE_ATENCAO"}
    - {desde: 2015-08, mudanca: "a tabela ganha a coluna CO_REDE_ATENCAO"}
  revisado_em: 2026-11-15
  versao_fetcher: 0.4.0
---

# Componentes de rede

## Resumo

Componentes das redes de atenção à saúde (por exemplo, 'Pré-natal', 'Sala de estabilização'), a que os procedimentos podem ser associados.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `sigtap/tb_componente_rede` |
| Órgão | Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde |
| Página oficial | http://sigtap.datasus.gov.br/ |
| Licença | Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos). |
| Periodicidade | mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada) |
| Cobertura | 2014-04 a em-curso |
| Unidade (uma linha) | um componente de rede vigente na competência |
| Granularidade | espacial: nacional (sem recorte geográfico); temporal: competência mensal |
| Formato bruto | ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP |
| Estado no lake | convertido |
| Partições | `ano`, `mes` |
| Chave | `competencia`, `co_componente_rede` |
| Colunas | 5 |
| Unidades de medida | `versao`: AAMMDDHHMM (identificador da publicação, sem unidade) |
| Dados pessoais | nenhum |
| Eras | 2015-04: a tabela perde a coluna CO_REDE_ATENCAO; 2015-08: a tabela ganha a coluna CO_REDE_ATENCAO |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.4.0 |

## Origem e coleta

- O fetcher baixa, por FTP, o ZIP de cada competência do SIGTAP em `ftp2.datasus.gov.br`, pasta `/pub/sistemas/tup/downloads`. O nome na fonte é `TabelaUnificada_AAAAMM.zip` ou, quando o DATASUS regera a tabela, `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo é a data e a hora da geração.
- No bruto, o arquivo fica em `tabelas/` com o carimbo de data da versão baixada (`TabelaUnificada_AAAAMM_vAAMMDDHHMM@AAAAMMDD.zip`).
- Este dataset vem do membro `tb_componente_rede.txt` do ZIP (dados, uma linha por registro, largura fixa) e do layout `tb_componente_rede_layout.txt`, que dá nome, tamanho e posição de cada coluna. O ZIP traz ainda o layout reunido de todas as tabelas (`layout.txt`), a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' (dicionário oficial) e o `LEIA_ME.TXT` (histórico das mudanças da estrutura). O fetcher guarda o ZIP inteiro; o conversor lê só os membros `tb_*.txt` e `rl_*.txt` e os layouts.
- Conferido em 2026-11-15 pelo tamanho dos membros dos 227 ZIPs publicados (2008-01 a 2026-11, uma competência por mês, sem lacunas): `tb_componente_rede.txt` tem conteúdo em 2014-04, 2015-04 a 2026-11; não existe no ZIP em 2008-01 a 2014-03, 2014-05 a 2015-03.

## Conteúdo

- Unidade de análise: um componente de rede vigente na competência.
- Linhas por competência: 20 em 2014-04, 20 em 2026-11; entre as 141 competências convertidas para esta página, de 20 a 20. Cada competência traz a tabela inteira, não só o que mudou.
- Em 2026-11 são 20 componentes, o mesmo número em todas as competências com conteúdo (2014-04 e 2015-04 em diante).
- Esta tabela não consta da planilha oficial de layout: as descrições vêm dos nomes e dos valores observados. Não traz `dt_competencia`.
- Mudanças de estrutura (conferidas nos layouts dos ZIPs):
    - 2015-04: a tabela perde a coluna CO_REDE_ATENCAO.
    - 2015-08: a tabela ganha a coluna CO_REDE_ATENCAO.

## Variáveis

Esta tabela não consta da planilha oficial de layout do ZIP (que traz só as colunas até a versão de 2008-2014): as descrições vêm do nome das colunas e dos valores observados.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_componente_rede` | `CO_COMPONENTE_REDE` | texto | Código do componente de rede, no formato `NN.NN` (rede e componente) | `92.01` a `95.03` em 2026-11 | todo |
| `no_componente_rede` | `NO_COMPONENTE_REDE` | texto | Nome do componente de rede | — | todo |
| `co_rede_atencao` | `CO_REDE_ATENCAO` | texto | Rede de atenção a que o componente pertence; liga com `tb_rede_atencao` | `092` a `095` em 2026-11 | 2014-04; desde 2015-08 |
| `versao` | — (nome do ZIP) | inteiro | Versão da publicação: sufixo `_v` do nome do ZIP, no formato AAMMDDHHMM (data e hora em que o DATASUS gerou o arquivo); 0 quando o nome do ZIP não traz sufixo (competências de 2008-01 a 2009-04) | AAMMDDHHMM; 0 = sem sufixo | todo |
| `competencia` | — (conversor) | texto | Competência (AAAAMM) do ZIP de que a linha veio; igual a `ano` e `mes` juntos | AAAAMM | todo |

## No lake

- Dataset `sigtap/tb_componente_rede`, particionado por `ano` (inteiro) e `mes` (texto de 2 dígitos, `05`); um arquivo Parquet por ZIP de competência, em `ano=AAAA/mes=MM/`.
- O conversor lê cada linha de largura fixa com o layout do próprio ZIP, aparando espaços nas pontas; campo em branco vira nulo e texto é decodificado de ISO-8859-1 para UTF-8.
- Colunas numéricas viram inteiros ou decimais conforme o layout; valor que não converte vira nulo. Os valores `9999` que a fonte usa como 'não se aplica' ficam como estão.
- Linhas totalmente em branco são ignoradas. Se um ZIP traz mais de uma versão da mesma competência, só a de maior sufixo `_v` é convertida.
- As colunas `versao` (sufixo `_v` do ZIP) e `competencia` (AAAAMM, igual às pastas `ano=`/`mes=`) são acrescentadas pelo conversor.
- O layout desta tabela não tem `DT_COMPETENCIA`; a competência só consta da coluna `competencia` (e das pastas `ano=`/`mes=`).

## Cuidados de uso

- **Cada competência é uma fotografia completa, não um incremento.** Sem filtrar `competencia`, o mesmo registro aparece uma vez por competência (esta tabela soma 2.820 linhas nas 141 competências convertidas, contra 20 em 2026-11). Filtre uma competência ou compare competências explicitamente.
- `co_rede_atencao` é nulo nas competências de 2015-04 a 2015-07, em que o ZIP não trazia a coluna.
- Os nomes têm erros de grafia na fonte (por exemplo, 'Vigilâcia', 'Atiemnto').
- **Junte sempre pela mesma competência.** Códigos, nomes e valores mudam de uma competência para outra; unir tabelas de competências diferentes dá resultados que nunca existiram no SIGTAP.

## Exemplos

Procedimentos associados a cada componente de rede na competência mais recente.

```python
import duckdb

duckdb.sql("""
    SELECT c.co_componente_rede, c.no_componente_rede, count(x.co_procedimento) AS procedimentos
    FROM read_parquet('lake/sigtap/tb_componente_rede/**/*.parquet', hive_partitioning = true, union_by_name = true) c
    LEFT JOIN read_parquet('lake/sigtap/rl_procedimento_comp_rede/**/*.parquet', hive_partitioning = true, union_by_name = true) x
      ON x.competencia = c.competencia AND x.co_componente_rede = c.co_componente_rede
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
