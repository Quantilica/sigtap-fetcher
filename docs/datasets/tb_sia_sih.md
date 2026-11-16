---
dataset:
  id: tb_sia_sih
  fonte: sigtap
  titulo: "Procedimentos antigos do SIA e do SIH (SIGTAP)"
  resumo: "Tabela de procedimentos dos sistemas legados SIA (ambulatorial) e SIH (hospitalar) anteriores à Tabela Unificada, que deram origem aos procedimentos atuais."
  orgao: Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde
  pagina_oficial: http://sigtap.datasus.gov.br/
  licenca: "Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos)."
  periodicidade: mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada)
  cobertura: {inicio: 2008-01, fim: em-curso}
  unidade: "um procedimento do SIA ou do SIH (código e tipo) da tabela anterior à unificação"
  granularidade: {espacial: "nacional (sem recorte geográfico)", temporal: competência mensal}
  formato_bruto: "ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP"
  lake: {estado: convertido, particoes: [ano, mes], chave: [competencia, co_procedimento_sia_sih, tp_procedimento], colunas: 6}
  unidades_de_medida:
    versao: "AAMMDDHHMM (identificador da publicação, sem unidade)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.4.0
---

# Procedimentos antigos do SIA e do SIH

## Resumo

Tabela de procedimentos dos sistemas legados SIA (ambulatorial) e SIH (hospitalar) anteriores à Tabela Unificada, que deram origem aos procedimentos atuais.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `sigtap/tb_sia_sih` |
| Órgão | Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde |
| Página oficial | http://sigtap.datasus.gov.br/ |
| Licença | Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos). |
| Periodicidade | mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada) |
| Cobertura | 2008-01 a em-curso |
| Unidade (uma linha) | um procedimento do SIA ou do SIH (código e tipo) da tabela anterior à unificação |
| Granularidade | espacial: nacional (sem recorte geográfico); temporal: competência mensal |
| Formato bruto | ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP |
| Estado no lake | convertido |
| Partições | `ano`, `mes` |
| Chave | `competencia`, `co_procedimento_sia_sih`, `tp_procedimento` |
| Colunas | 6 |
| Unidades de medida | `versao`: AAMMDDHHMM (identificador da publicação, sem unidade) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.4.0 |

## Origem e coleta

- O fetcher baixa, por FTP, o ZIP de cada competência do SIGTAP em `ftp2.datasus.gov.br`, pasta `/pub/sistemas/tup/downloads`. O nome na fonte é `TabelaUnificada_AAAAMM.zip` ou, quando o DATASUS regera a tabela, `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo é a data e a hora da geração.
- No bruto, o arquivo fica em `tabelas/` com o carimbo de data da versão baixada (`TabelaUnificada_AAAAMM_vAAMMDDHHMM@AAAAMMDD.zip`).
- Este dataset vem do membro `tb_sia_sih.txt` do ZIP (dados, uma linha por registro, largura fixa) e do layout `tb_sia_sih_layout.txt`, que dá nome, tamanho e posição de cada coluna. O ZIP traz ainda o layout reunido de todas as tabelas (`layout.txt`), a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' (dicionário oficial) e o `LEIA_ME.TXT` (histórico das mudanças da estrutura). O fetcher guarda o ZIP inteiro; o conversor lê só os membros `tb_*.txt` e `rl_*.txt` e os layouts.
- Conferido em 2026-11-15 pelo tamanho dos membros dos 227 ZIPs publicados (2008-01 a 2026-11, uma competência por mês, sem lacunas), `tb_sia_sih.txt` existe e tem conteúdo em todos.

## Conteúdo

- Unidade de análise: um procedimento do SIA ou do SIH (código e tipo) da tabela anterior à unificação.
- Linhas por competência: 8.383 em 2008-01, 8.383 em 2026-11; entre as 227 competências convertidas para esta página, de 8.383 a 8.383. Cada competência traz a tabela inteira, não só o que mudou.
- Tabela de referência estática: tem 8.383 linhas em todas as competências conferidas (2008-01 a 2026-11); 5.644 são hospitalares e 2.739 ambulatoriais.
- É a ponte entre a Tabela Unificada atual e os códigos antigos; `rl_procedimento_sia_sih` faz a ligação.

## Variáveis

As descrições seguem a planilha oficial de layout do ZIP ('DATASUS - Tabela de Procedimentos - Lay-out.xls'), conferidas contra os valores observados em 2026-11. Onde os dados diferem da planilha, isso está dito na coluna 'Unidade / códigos'.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_procedimento_sia_sih` | `CO_PROCEDIMENTO_SIA_SIH` | texto | Código do procedimento no SIA ou no SIH (8 posições, na numeração anterior à Tabela Unificada) | — | todo |
| `no_procedimento_sia_sih` | `NO_PROCEDIMENTO_SIA_SIH` | texto | Nome do procedimento no SIA ou no SIH | — | todo |
| `tp_procedimento` | `TP_PROCEDIMENTO` | texto | Tipo do procedimento de origem | `A` ambulatorial (SIA); `H` hospitalar (SIH) | todo |
| `dt_competencia` | `DT_COMPETENCIA` | texto | Competência de validade do registro (AAAAMM). Igual à coluna `competencia` em todas as linhas conferidas | AAAAMM | todo |
| `versao` | — (nome do ZIP) | inteiro | Versão da publicação: sufixo `_v` do nome do ZIP, no formato AAMMDDHHMM (data e hora em que o DATASUS gerou o arquivo); 0 quando o nome do ZIP não traz sufixo (competências de 2008-01 a 2009-04) | AAMMDDHHMM; 0 = sem sufixo | todo |
| `competencia` | — (conversor) | texto | Competência (AAAAMM) do ZIP de que a linha veio; igual a `ano` e `mes` juntos | AAAAMM | todo |

## No lake

- Dataset `sigtap/tb_sia_sih`, particionado por `ano` (inteiro) e `mes` (texto de 2 dígitos, `05`); um arquivo Parquet por ZIP de competência, em `ano=AAAA/mes=MM/`.
- O conversor lê cada linha de largura fixa com o layout do próprio ZIP, aparando espaços nas pontas; campo em branco vira nulo e texto é decodificado de ISO-8859-1 para UTF-8.
- Colunas numéricas viram inteiros ou decimais conforme o layout; valor que não converte vira nulo. Os valores `9999` que a fonte usa como 'não se aplica' ficam como estão.
- Linhas totalmente em branco são ignoradas. Se um ZIP traz mais de uma versão da mesma competência, só a de maior sufixo `_v` é convertida.
- As colunas `versao` (sufixo `_v` do ZIP) e `competencia` (AAAAMM, igual às pastas `ano=`/`mes=`) são acrescentadas pelo conversor.
- `dt_competencia` é a coluna do arquivo, mantida como texto.

## Cuidados de uso

- **Cada competência é uma fotografia completa, não um incremento.** Sem filtrar `competencia`, o mesmo registro aparece uma vez por competência (esta tabela soma 1.902.941 linhas nas 227 competências convertidas, contra 8.383 em 2026-11). Filtre uma competência ou compare competências explicitamente.
- O código antigo sozinho não é único: o mesmo `co_procedimento_sia_sih` aparece como ambulatorial e como hospitalar em 90 códigos, em todas as competências conferidas; use `co_procedimento_sia_sih` e `tp_procedimento` juntos.
- **Junte sempre pela mesma competência.** Códigos, nomes e valores mudam de uma competência para outra; unir tabelas de competências diferentes dá resultados que nunca existiram no SIGTAP.

## Exemplos

Procedimentos antigos por tipo e quantos têm correspondente na tabela atual.

```python
import duckdb

duckdb.sql("""
    SELECT s.tp_procedimento, count(*) AS antigos, count(DISTINCT r.co_procedimento_sia_sih) AS com_correspondente
    FROM read_parquet('lake/sigtap/tb_sia_sih/**/*.parquet', hive_partitioning = true, union_by_name = true) s
    LEFT JOIN read_parquet('lake/sigtap/rl_procedimento_sia_sih/**/*.parquet', hive_partitioning = true, union_by_name = true) r
      ON r.competencia = s.competencia
     AND r.co_procedimento_sia_sih = s.co_procedimento_sia_sih AND r.tp_procedimento = s.tp_procedimento
    WHERE s.competencia = '202611'
    GROUP BY 1
""").show()
```

## Referências

- SIGTAP (Sistema de Gerenciamento da Tabela de Procedimentos, Medicamentos e OPM do SUS): http://sigtap.datasus.gov.br/
- Arquivos de exportação do SIGTAP (FTP do DATASUS): ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/
- Dentro de cada ZIP: a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' e o `LEIA_ME.TXT`.
- Notas técnicas da CGSI/DATASUS sobre cada competência: ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/notastecnicas/
