---
dataset:
  id: rl_excecao_compatibilidade
  fonte: sigtap
  titulo: "Exceções de compatibilidade (SIGTAP)"
  resumo: "Exceções às relações de compatibilidade: um procedimento de restrição que nega a compatibilidade entre um principal e um compatível."
  orgao: Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde
  pagina_oficial: http://sigtap.datasus.gov.br/
  licenca: "Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos)."
  periodicidade: mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada)
  cobertura: {inicio: 2008-01, fim: em-curso}
  unidade: "uma exceção a uma relação de compatibilidade (restrição, principal e compatível)"
  granularidade: {espacial: "nacional (sem recorte geográfico)", temporal: competência mensal}
  formato_bruto: "ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP"
  lake: {estado: convertido, particoes: [ano, mes], chave: [competencia, co_procedimento_restricao, co_procedimento_principal, co_registro_principal, co_procedimento_compativel, co_registro_compativel], colunas: 9}
  unidades_de_medida:
    versao: "AAMMDDHHMM (identificador da publicação, sem unidade)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.4.0
---

# Exceções de compatibilidade

## Resumo

Exceções às relações de compatibilidade: um procedimento de restrição que nega a compatibilidade entre um principal e um compatível.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `sigtap/rl_excecao_compatibilidade` |
| Órgão | Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde |
| Página oficial | http://sigtap.datasus.gov.br/ |
| Licença | Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos). |
| Periodicidade | mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada) |
| Cobertura | 2008-01 a em-curso |
| Unidade (uma linha) | uma exceção a uma relação de compatibilidade (restrição, principal e compatível) |
| Granularidade | espacial: nacional (sem recorte geográfico); temporal: competência mensal |
| Formato bruto | ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP |
| Estado no lake | convertido |
| Partições | `ano`, `mes` |
| Chave | `competencia`, `co_procedimento_restricao`, `co_procedimento_principal`, `co_registro_principal`, `co_procedimento_compativel`, `co_registro_compativel` |
| Colunas | 9 |
| Unidades de medida | `versao`: AAMMDDHHMM (identificador da publicação, sem unidade) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.4.0 |

## Origem e coleta

- O fetcher baixa, por FTP, o ZIP de cada competência do SIGTAP em `ftp2.datasus.gov.br`, pasta `/pub/sistemas/tup/downloads`. O nome na fonte é `TabelaUnificada_AAAAMM.zip` ou, quando o DATASUS regera a tabela, `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo é a data e a hora da geração.
- No bruto, o arquivo fica em `tabelas/` com o carimbo de data da versão baixada (`TabelaUnificada_AAAAMM_vAAMMDDHHMM@AAAAMMDD.zip`).
- Este dataset vem do membro `rl_excecao_compatibilidade.txt` do ZIP (dados, uma linha por registro, largura fixa) e do layout `rl_excecao_compatibilidade_layout.txt`, que dá nome, tamanho e posição de cada coluna. O ZIP traz ainda o layout reunido de todas as tabelas (`layout.txt`), a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' (dicionário oficial) e o `LEIA_ME.TXT` (histórico das mudanças da estrutura). O fetcher guarda o ZIP inteiro; o conversor lê só os membros `tb_*.txt` e `rl_*.txt` e os layouts.
- Conferido em 2026-11-15 pelo tamanho dos membros dos 227 ZIPs publicados (2008-01 a 2026-11, uma competência por mês, sem lacunas), `rl_excecao_compatibilidade.txt` existe e tem conteúdo em todos.

## Conteúdo

- Unidade de análise: uma exceção a uma relação de compatibilidade (restrição, principal e compatível).
- Linhas por competência: 5 em 2008-01, 5 em 2026-11; entre as 227 competências convertidas para esta página, de 3 a 5. Cada competência traz a tabela inteira, não só o que mudou.
- Tabela muito pequena: de 3 a 5 linhas por competência (5 em 2026-11, todas com o mesmo par principal–compatível).

## Variáveis

As descrições seguem a planilha oficial de layout do ZIP ('DATASUS - Tabela de Procedimentos - Lay-out.xls'), conferidas contra os valores observados em 2026-11. Onde os dados diferem da planilha, isso está dito na coluna 'Unidade / códigos'.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_procedimento_restricao` | `CO_PROCEDIMENTO_RESTRICAO` | texto | Procedimento que nega a compatibilidade definida para o par abaixo | — | todo |
| `co_procedimento_principal` | `CO_PROCEDIMENTO_PRINCIPAL` | texto | Procedimento principal da restrição | — | todo |
| `co_registro_principal` | `CO_REGISTRO_PRINCIPAL` | texto | Instrumento de registro do procedimento principal; liga com `tb_registro` | — | todo |
| `co_procedimento_compativel` | `CO_PROCEDIMENTO_COMPATIVEL` | texto | Procedimento secundário da restrição | — | todo |
| `co_registro_compativel` | `CO_REGISTRO_COMPATIVEL` | texto | Instrumento de registro do procedimento secundário; liga com `tb_registro` | — | todo |
| `tp_compatibilidade` | `TP_COMPATIBILIDADE` | texto | Tipo da relação negada | `2` incompatível/excludente (única observada) | todo |
| `dt_competencia` | `DT_COMPETENCIA` | texto | Competência de validade do registro (AAAAMM). Igual à coluna `competencia` em todas as linhas conferidas | AAAAMM | todo |
| `versao` | — (nome do ZIP) | inteiro | Versão da publicação: sufixo `_v` do nome do ZIP, no formato AAMMDDHHMM (data e hora em que o DATASUS gerou o arquivo); 0 quando o nome do ZIP não traz sufixo (competências de 2008-01 a 2009-04) | AAMMDDHHMM; 0 = sem sufixo | todo |
| `competencia` | — (conversor) | texto | Competência (AAAAMM) do ZIP de que a linha veio; igual a `ano` e `mes` juntos | AAAAMM | todo |

## No lake

- Dataset `sigtap/rl_excecao_compatibilidade`, particionado por `ano` (inteiro) e `mes` (texto de 2 dígitos, `05`); um arquivo Parquet por ZIP de competência, em `ano=AAAA/mes=MM/`.
- O conversor lê cada linha de largura fixa com o layout do próprio ZIP, aparando espaços nas pontas; campo em branco vira nulo e texto é decodificado de ISO-8859-1 para UTF-8.
- Colunas numéricas viram inteiros ou decimais conforme o layout; valor que não converte vira nulo. Os valores `9999` que a fonte usa como 'não se aplica' ficam como estão.
- Linhas totalmente em branco são ignoradas. Se um ZIP traz mais de uma versão da mesma competência, só a de maior sufixo `_v` é convertida.
- As colunas `versao` (sufixo `_v` do ZIP) e `competencia` (AAAAMM, igual às pastas `ano=`/`mes=`) são acrescentadas pelo conversor.
- `dt_competencia` é a coluna do arquivo, mantida como texto.

## Cuidados de uso

- **Cada competência é uma fotografia completa, não um incremento.** Sem filtrar `competencia`, o mesmo registro aparece uma vez por competência (esta tabela soma 1.128 linhas nas 227 competências convertidas, contra 5 em 2026-11). Filtre uma competência ou compare competências explicitamente.
- Cada linha nega, para um procedimento de restrição, o par principal–compatível; o tipo observado é sempre `2`.
- **Junte sempre pela mesma competência.** Códigos, nomes e valores mudam de uma competência para outra; unir tabelas de competências diferentes dá resultados que nunca existiram no SIGTAP.

## Exemplos

As exceções da competência mais recente.

```python
import duckdb

duckdb.sql("""
    SELECT *
    FROM read_parquet('lake/sigtap/rl_excecao_compatibilidade/**/*.parquet', hive_partitioning = true, union_by_name = true)
    WHERE competencia = '202611'
""").show()
```

## Referências

- SIGTAP (Sistema de Gerenciamento da Tabela de Procedimentos, Medicamentos e OPM do SUS): http://sigtap.datasus.gov.br/
- Arquivos de exportação do SIGTAP (FTP do DATASUS): ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/
- Dentro de cada ZIP: a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' e o `LEIA_ME.TXT`.
- Notas técnicas da CGSI/DATASUS sobre cada competência: ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/notastecnicas/
