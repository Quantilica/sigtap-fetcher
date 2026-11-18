---
dataset:
  id: rl_procedimento_tuss
  fonte: sigtap
  titulo: "Procedimento × TUSS (vazia na fonte) (SIGTAP)"
  resumo: "Relação que ligaria cada procedimento do SIGTAP aos códigos da TUSS. Nas competências conferidas, o arquivo tem zero bytes."
  orgao: Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde
  pagina_oficial: http://sigtap.datasus.gov.br/
  licenca: "Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos)."
  periodicidade: mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada)
  cobertura: {inicio: 2014-04, fim: em-curso}
  unidade: "um vínculo entre um procedimento e um código TUSS (não há linhas publicadas)"
  granularidade: {espacial: "nacional (sem recorte geográfico)", temporal: competência mensal}
  formato_bruto: "ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP"
  lake: {estado: so-bruto, particoes: [], chave: [], colunas: null}
  unidades_de_medida:
    versao: "AAMMDDHHMM (identificador da publicação, sem unidade)"
  dados_pessoais: nenhum
  eras: []
  revisado_em: 2026-11-15
  versao_fetcher: 0.4.0
---

# Procedimento × TUSS (vazia na fonte)

## Resumo

Relação que ligaria cada procedimento do SIGTAP aos códigos da TUSS. Nas competências conferidas, o arquivo tem zero bytes.

## Ficha técnica

<!-- gerado:ficha -->

| Campo | Valor |
|---|---|
| Dataset | `sigtap/rl_procedimento_tuss` |
| Órgão | Departamento de Informática do Sistema Único de Saúde (DATASUS), Ministério da Saúde |
| Página oficial | http://sigtap.datasus.gov.br/ |
| Licença | Sem licença declarada pela fonte; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016 (política de dados abertos). |
| Periodicidade | mensal (uma tabela por competência; o DATASUS pode regerar uma competência depois de publicada) |
| Cobertura | 2014-04 a em-curso |
| Unidade (uma linha) | um vínculo entre um procedimento e um código TUSS (não há linhas publicadas) |
| Granularidade | espacial: nacional (sem recorte geográfico); temporal: competência mensal |
| Formato bruto | ZIP mensal com arquivos TXT de largura fixa, ISO-8859-1, sem separador, um arquivo por tabela; o layout vem em arquivos de texto no próprio ZIP |
| Estado no lake | so-bruto |
| Partições | — |
| Chave | — |
| Colunas | — |
| Unidades de medida | `versao`: AAMMDDHHMM (identificador da publicação, sem unidade) |
| Dados pessoais | nenhum |
| Eras | nenhuma |
| Revisado em | 2026-11-15 |
| Versão do fetcher | 0.4.0 |

## Origem e coleta

- O fetcher baixa, por FTP, o ZIP de cada competência do SIGTAP em `ftp2.datasus.gov.br`, pasta `/pub/sistemas/tup/downloads`. O nome na fonte é `TabelaUnificada_AAAAMM.zip` ou, quando o DATASUS regera a tabela, `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo é a data e a hora da geração.
- No bruto, o arquivo fica em `tabelas/` com o carimbo de data da versão baixada (`TabelaUnificada_AAAAMM_vAAMMDDHHMM@AAAAMMDD.zip`).
- Este dataset vem do membro `rl_procedimento_tuss.txt` do ZIP (dados, uma linha por registro, largura fixa) e do layout `rl_procedimento_tuss_layout.txt`, que dá nome, tamanho e posição de cada coluna. O ZIP traz ainda o layout reunido de todas as tabelas (`layout.txt`), a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' (dicionário oficial) e o `LEIA_ME.TXT` (histórico das mudanças da estrutura). O fetcher guarda o ZIP inteiro; o conversor lê só os membros `tb_*.txt` e `rl_*.txt` e os layouts.
- Conferido em 2026-11-15 pelo tamanho dos membros dos 227 ZIPs publicados (2008-01 a 2026-11, uma competência por mês, sem lacunas): `rl_procedimento_tuss.txt` não tem conteúdo em nenhuma competência; o arquivo existe, mas está vazio, em 2014-04, 2015-08 a 2026-11; não existe no ZIP em 2008-01 a 2014-03, 2014-05 a 2015-07.

## Conteúdo

- Unidade de análise: um vínculo entre um procedimento e um código TUSS (não há linhas publicadas).
- O arquivo `rl_procedimento_tuss.txt` está presente em 137 ZIPs (2014-04 e 2015-08 a 2026-11) e tem zero bytes em todos (conferido pelo tamanho dos membros dos 227 ZIPs). O layout declara `CO_PROCEDIMENTO` (10) e `CO_TUSS` (10). O layout existe: `CO_PROCEDIMENTO` (10) e `CO_TUSS` (10).

## Variáveis

Esta tabela não consta da planilha oficial de layout do ZIP (que traz só as colunas até a versão de 2008-2014): as descrições vêm do nome das colunas e dos valores observados.

| Coluna no lake | Na fonte | Tipo | Descrição | Unidade / códigos | Período |
|---|---|---|---|---|---|
| `co_procedimento` | `CO_PROCEDIMENTO` | texto | Código do procedimento, 10 dígitos: os seis primeiros dão grupo (2), subgrupo (2) e forma de organização (2); os quatro últimos identificam o procedimento dentro da forma de organização | — | todo |
| `co_tuss` | `CO_TUSS` | texto | Código TUSS; ligaria com `tb_tuss` | — | todo |
| `versao` | — (nome do ZIP) | inteiro | Versão da publicação: sufixo `_v` do nome do ZIP, no formato AAMMDDHHMM (data e hora em que o DATASUS gerou o arquivo); 0 quando o nome do ZIP não traz sufixo (competências de 2008-01 a 2009-04) | AAMMDDHHMM; 0 = sem sufixo | todo |
| `competencia` | — (conversor) | texto | Competência (AAAAMM) do ZIP de que a linha veio; igual a `ano` e `mes` juntos | AAAAMM | todo |

## No lake

- Sem dataset no lake: o conversor não grava Parquet para arquivo sem linhas, então `sigtap/rl_procedimento_tuss` não existe (estado `so-bruto`: só o ZIP bruto traz o arquivo, vazio).
- Se a fonte passar a preencher a tabela, o conversor a grava como as demais relações, particionada por `ano`, com as colunas `co_procedimento`, `co_tuss`, `versao`, `competencia`, `mes` e `_origem`.
- O conversor lê cada linha de largura fixa com o layout do próprio ZIP, aparando espaços nas pontas; campo em branco vira nulo e texto é decodificado de ISO-8859-1 para UTF-8.
- Colunas numéricas viram inteiros ou decimais conforme o layout; valor que não converte vira nulo. Os valores `9999` que a fonte usa como 'não se aplica' ficam como estão.
- Linhas totalmente em branco são ignoradas. Se um ZIP traz mais de uma versão da mesma competência, só a de maior sufixo `_v` é convertida.
- As colunas `versao` (sufixo `_v` do ZIP), `competencia` (AAAAMM, igual a `ano` e `mes` juntos), `mes` e `_origem` são acrescentadas pelo conversor.
- O layout desta tabela não tem `DT_COMPETENCIA`; a competência só consta da coluna `competencia` (e de `ano` e `mes`).

## Cuidados de uso

- O conversor ignora arquivos sem linhas: o dataset não tem Parquet no lake. A página existe para registrar que a fonte declara a tabela e não a preenche.
- **Junte sempre pela mesma competência.** Códigos, nomes e valores mudam de uma competência para outra; unir tabelas de competências diferentes dá resultados que nunca existiram no SIGTAP.

## Exemplos

Não há consulta ao lake; para conferir, liste o tamanho do membro no ZIP.

```bash
unzip -l TabelaUnificada_202611_v2611051737.zip | grep rl_procedimento_tuss
```

## Referências

- SIGTAP (Sistema de Gerenciamento da Tabela de Procedimentos, Medicamentos e OPM do SUS): http://sigtap.datasus.gov.br/
- Arquivos de exportação do SIGTAP (FTP do DATASUS): ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/
- Dentro de cada ZIP: a planilha 'DATASUS - Tabela de Procedimentos - Lay-out.xls' e o `LEIA_ME.TXT`.
- Notas técnicas da CGSI/DATASUS sobre cada competência: ftp://ftp2.datasus.gov.br/pub/sistemas/tup/downloads/notastecnicas/
