# SIGTAP — Tabela de Procedimentos, Medicamentos e OPM do SUS (`sigtap`)

O `sigtap-fetcher` coleta a Tabela Unificada de Procedimentos, Medicamentos e Órteses, Próteses e Materiais Especiais (OPM) do SUS, o SIGTAP, publicada pelo Departamento de Informática do SUS (DATASUS), do Ministério da Saúde. A tabela é a lista oficial do que o SUS pode pagar ou registrar, com código, nome, valores, regras de uso e vínculos com habilitações, CIDs, ocupações e instrumentos de registro. O fetcher converte cada tabela do ZIP mensal para o lake em Parquet particionado por ano da competência: um arquivo por tabela e ano (`ano=AAAA/<tabela>.parquet`), com as competências do ano distinguidas pela coluna `mes`.

O SIGTAP tem **41 datasets**, um por tabela do ZIP: as tabelas `tb_*` descrevem entidades (procedimento, CID, habilitação...) e as `rl_*` relacionam procedimentos a essas entidades. As descrições vêm da planilha oficial de layout que o próprio ZIP traz; onde ela não cobre a tabela, a página diz que a descrição é inferida.

## Classificação dos procedimentos

| Dataset | O que é | Linhas em 2026-11 | Desde | Página |
|---|---|---|---|---|
| `tb_forma_organizacao` | Formas de organização (nível 3 da classificação) | 424 | 2008-01 | [tb_forma_organizacao](datasets/tb_forma_organizacao.md) |
| `tb_grupo` | Grupos de procedimentos (nível 1 da classificação) | 9 | 2008-01 | [tb_grupo](datasets/tb_grupo.md) |
| `tb_sub_grupo` | Subgrupos de procedimentos (nível 2 da classificação) | 71 | 2008-01 | [tb_sub_grupo](datasets/tb_sub_grupo.md) |

## Procedimentos

| Dataset | O que é | Linhas em 2026-11 | Desde | Página |
|---|---|---|---|---|
| `tb_descricao` | Texto descritivo (até 4.000 caracteres) de cada procedimento: o que ele consiste, em que condições se aplica e orientações de registro. | 4.380 | 2009-10 | [tb_descricao](datasets/tb_descricao.md) |
| `tb_descricao_detalhe` | Texto longo (até 4.000 caracteres) que explica cada atributo de detalhe de `tb_detalhe`. | 61 | 2010-09 | [tb_descricao_detalhe](datasets/tb_descricao_detalhe.md) |
| `tb_detalhe` | Atributos de detalhe que se aplicam a procedimentos, como 'inclui valor da anestesia' ou 'admite longa permanência'. | 69 | 2008-01 | [tb_detalhe](datasets/tb_detalhe.md) |
| `tb_financiamento` | Tipos de financiamento dos procedimentos (atenção básica, média e alta complexidade, FAEC, vigilância em saúde e outros). | 7 | 2008-01 | [tb_financiamento](datasets/tb_financiamento.md) |
| `tb_modalidade` | Modalidades de atendimento em que um procedimento pode ser feito (ambulatorial, hospitalar, hospital-dia, atenção domiciliar). | 4 | 2008-01 | [tb_modalidade](datasets/tb_modalidade.md) |
| `tb_procedimento` | Procedimentos, medicamentos e OPM, com valores, limites e financiamento | 5.068 | 2008-01 | [tb_procedimento](datasets/tb_procedimento.md) |
| `tb_registro` | Instrumentos de registro dos procedimentos: o tipo de documento em que o procedimento é informado ao SUS (BPA, APAC, AIH, RAAS e outros). | 10 | 2008-01 | [tb_registro](datasets/tb_registro.md) |
| `tb_regra_condicionada` | Regras condicionadas de registro e pagamento de procedimentos: condições (por CID, por registro, por habilitação) que a regra impõe, com nome e texto de descrição. | 15 | 2012-11 | [tb_regra_condicionada](datasets/tb_regra_condicionada.md) |
| `tb_rubrica` | Rubricas de financiamento: o subtipo do financiamento, usado nos procedimentos de financiamento FAEC. | 46 | 2008-01 | [tb_rubrica](datasets/tb_rubrica.md) |
| `tb_sia_sih` | Tabela de procedimentos dos sistemas legados SIA (ambulatorial) e SIH (hospitalar) anteriores à Tabela Unificada, que deram origem aos procedimentos atuais. | 8.383 | 2008-01 | [tb_sia_sih](datasets/tb_sia_sih.md) |
| `tb_tipo_leito` | Classificação dos leitos hospitalares em que os procedimentos podem ser executados (cirúrgico, clínico, UTI e outros). | 41 | 2008-01 | [tb_tipo_leito](datasets/tb_tipo_leito.md) |

## Atributos clínicos e de habilitação

| Dataset | O que é | Linhas em 2026-11 | Desde | Página |
|---|---|---|---|---|
| `tb_cid` | Classificação Internacional de Doenças (CID-10) como usada pelo SIGTAP, com o tipo de agravo, o sexo de aplicação e, para câncer, se o código admite estadiamento. | 14.246 | 2008-01 | [tb_cid](datasets/tb_cid.md) |
| `tb_grupo_habilitacao` | Grupos de habilitações exigidas em conjunto: um procedimento ligado a um grupo exige do estabelecimento todas as habilitações do grupo (por exemplo, `0801 e 0803`). | 31 | 2008-01 | [tb_grupo_habilitacao](datasets/tb_grupo_habilitacao.md) |
| `tb_habilitacao` | Habilitações do CNES que um estabelecimento precisa ter para executar ou receber incremento em um procedimento. | 376 | 2008-01 | [tb_habilitacao](datasets/tb_habilitacao.md) |
| `tb_ocupacao` | Ocupações da Classificação Brasileira de Ocupações (CBO-2002) usadas pelo SIGTAP para indicar os profissionais que podem executar um procedimento. | 2.719 | 2008-01 | [tb_ocupacao](datasets/tb_ocupacao.md) |
| `tb_servico` | Serviços especializados do CNES que um estabelecimento precisa ter para executar um procedimento. | 75 | 2008-01 | [tb_servico](datasets/tb_servico.md) |
| `tb_servico_classificacao` | Classificações de cada serviço especializado: o detalhamento do serviço (por exemplo, um tipo de atenção dentro do serviço). | 436 | 2008-01 | [tb_servico_classificacao](datasets/tb_servico_classificacao.md) |

## Rede, RENASES e TUSS

| Dataset | O que é | Linhas em 2026-11 | Desde | Página |
|---|---|---|---|---|
| `tb_componente_rede` | Componentes das redes de atenção à saúde (por exemplo, 'Pré-natal', 'Sala de estabilização'), a que os procedimentos podem ser associados. | 20 | 2014-04 | [tb_componente_rede](datasets/tb_componente_rede.md) |
| `tb_rede_atencao` | Redes temáticas de atenção à saúde (Rede Cegonha, Urgência e Emergência, Psicossocial e outras) a que os componentes de rede pertencem. | 5 | 2014-04 | [tb_rede_atencao](datasets/tb_rede_atencao.md) |
| `tb_renases` | Relação Nacional de Ações e Serviços de Saúde (RENASES): lista das ações e serviços de saúde que o SUS oferece, a que os procedimentos são associados. | 201 | 2014-04 | [tb_renases](datasets/tb_renases.md) |
| `tb_tuss` | Terminologia Unificada da Saúde Suplementar (TUSS), a terminologia de procedimentos da saúde suplementar, que o SIGTAP traz para permitir a correspondência com os procedimentos do SUS. | 5.766 | 2014-04 | [tb_tuss](datasets/tb_tuss.md) |

## Relações entre procedimentos e atributos

| Dataset | O que é | Linhas em 2026-11 | Desde | Página |
|---|---|---|---|---|
| `rl_excecao_compatibilidade` | Exceções às relações de compatibilidade: um procedimento de restrição que nega a compatibilidade entre um principal e um compatível. | 5 | 2008-01 | [rl_excecao_compatibilidade](datasets/rl_excecao_compatibilidade.md) |
| `rl_procedimento_cid` | Liga cada procedimento aos CIDs com que ele pode ser solicitado, e indica se o CID pode ser o diagnóstico principal. | 82.494 | 2008-01 | [rl_procedimento_cid](datasets/rl_procedimento_cid.md) |
| `rl_procedimento_comp_rede` | Liga cada procedimento aos componentes de rede de atenção à saúde a que ele pertence. | 4 | 2015-08 | [rl_procedimento_comp_rede](datasets/rl_procedimento_comp_rede.md) |
| `rl_procedimento_compativel` | Pares de procedimentos que podem ou não ser registrados juntos (compatibilidade, incompatibilidade, concomitância), com a quantidade permitida. | 12.765 | 2008-01 | [rl_procedimento_compativel](datasets/rl_procedimento_compativel.md) |
| `rl_procedimento_detalhe` | Liga cada procedimento aos atributos de detalhe (`tb_detalhe`) que se aplicam a ele. | 10.750 | 2008-01 | [rl_procedimento_detalhe](datasets/rl_procedimento_detalhe.md) |
| `rl_procedimento_habilitacao` | Liga cada procedimento às habilitações do CNES exigidas do estabelecimento, isoladamente ou em grupo. | 11.635 | 2008-01 | [rl_procedimento_habilitacao](datasets/rl_procedimento_habilitacao.md) |
| `rl_procedimento_incremento` | Percentuais de incremento sobre os valores hospitalar, ambulatorial e profissional que um procedimento recebe quando o estabelecimento tem uma habilitação. | 2.710 | 2008-01 | [rl_procedimento_incremento](datasets/rl_procedimento_incremento.md) |
| `rl_procedimento_leito` | Liga cada procedimento hospitalar aos tipos de leito em que ele pode ser feito. | 4.124 | 2008-01 | [rl_procedimento_leito](datasets/rl_procedimento_leito.md) |
| `rl_procedimento_modalidade` | Liga cada procedimento às modalidades de atendimento em que ele pode ser feito. | 8.131 | 2008-01 | [rl_procedimento_modalidade](datasets/rl_procedimento_modalidade.md) |
| `rl_procedimento_ocupacao` | Liga cada procedimento às ocupações da CBO autorizadas a executá-lo. | 195.396 | 2008-01 | [rl_procedimento_ocupacao](datasets/rl_procedimento_ocupacao.md) |
| `rl_procedimento_origem` | Liga um procedimento novo ao procedimento da Tabela Unificada de que ele foi derivado (por exemplo, quando um procedimento é desdobrado em vários). | 4 | 2008-03 | [rl_procedimento_origem](datasets/rl_procedimento_origem.md) |
| `rl_procedimento_registro` | Liga cada procedimento aos instrumentos de registro em que ele pode ser informado (BPA, AIH, APAC, RAAS, e-SUS APS). | 7.838 | 2008-01 | [rl_procedimento_registro](datasets/rl_procedimento_registro.md) |
| `rl_procedimento_regra_cond` | Liga cada procedimento às regras condicionadas (`tb_regra_condicionada`) que se aplicam a ele. | 3.909 | 2012-11 | [rl_procedimento_regra_cond](datasets/rl_procedimento_regra_cond.md) |
| `rl_procedimento_renases` | Liga cada procedimento aos itens da RENASES (`tb_renases`) a que ele corresponde. | 5.455 | 2014-04 | [rl_procedimento_renases](datasets/rl_procedimento_renases.md) |
| `rl_procedimento_servico` | Liga cada procedimento aos serviços especializados (e à classificação dentro do serviço) exigidos do estabelecimento. | 4.163 | 2008-01 | [rl_procedimento_servico](datasets/rl_procedimento_servico.md) |
| `rl_procedimento_sia_sih` | Liga cada procedimento da Tabela Unificada aos procedimentos antigos do SIA ou do SIH de que ele se originou. | 5.380 | 2008-01 | [rl_procedimento_sia_sih](datasets/rl_procedimento_sia_sih.md) |
| `rl_procedimento_tuss` | Relação que ligaria cada procedimento do SIGTAP aos códigos da TUSS. Nas competências conferidas, o arquivo tem zero bytes. | 0 (vazia na fonte) | 2014-04 | [rl_procedimento_tuss](datasets/rl_procedimento_tuss.md) |

## Como o SIGTAP publica

- A fonte publica um ZIP por competência (mês), de 2008-01 a 2026-11 (227 ZIPs conferidos em 2026-11-15, sem lacunas), no FTP do DATASUS. O nome é `TabelaUnificada_AAAAMM.zip` ou `TabelaUnificada_AAAAMM_vAAMMDDHHMM.zip`; o sufixo `_v` existe desde 2009-05 e marca a data e a hora em que o DATASUS gerou o arquivo.
- Cada ZIP é uma fotografia completa de todas as tabelas na competência. Não há incrementos: a tabela de uma competência substitui a anterior, e o histórico de valores só existe porque o fetcher guarda um ZIP por competência.
- Os dados são arquivos de texto de largura fixa em ISO-8859-1, sem separador; cada tabela tem um arquivo `<tabela>.txt` e um `<tabela>_layout.txt` com nome, tamanho e posição das colunas.
- Dentro do ZIP há também o `layout.txt` (todos os layouts), uma planilha de layout com a descrição das colunas e o `LEIA_ME.TXT`, que registra, de 2007 a 2008, as mudanças de estrutura da exportação.
- As notas técnicas mensais da CGSI/DATASUS, que explicam as mudanças de conteúdo de cada competência (novos procedimentos, valores, regras), ficam em `notastecnicas/` no mesmo FTP.
- A fonte não traz licença; a base legal é a de dados públicos (Lei 12.527/2011, LAI, e Decreto 8.777/2016).
- O fetcher guarda cada ZIP com o carimbo de data da versão baixada. Se o DATASUS regera uma competência, o conversor usa só a versão de maior sufixo `_v`.

## Como as tabelas se relacionam

- O código do procedimento tem 10 dígitos: os dois primeiros são o grupo (`tb_grupo`), os quatro primeiros o grupo e o subgrupo (`tb_sub_grupo`) e os seis primeiros o grupo, o subgrupo e a forma de organização (`tb_forma_organizacao`). Conferido em 2026-11: todos os procedimentos de `tb_procedimento` têm subgrupo e forma de organização cadastrados.
- As tabelas `rl_procedimento_*` ligam `co_procedimento` a uma entidade (CID, ocupação, habilitação, instrumento de registro, modalidade, leito, serviço, detalhe, regra condicionada, componente de rede, RENASES, TUSS e procedimentos antigos do SIA e do SIH). Em 2026-11 nenhuma relação aponta para procedimento ou entidade inexistente.
- Os valores (`vl_sh`, `vl_sa`, `vl_sp`) estão em `tb_procedimento`; os incrementos percentuais por habilitação estão em `rl_procedimento_incremento`.
- Toda junção deve usar a mesma `competencia` nas duas tabelas.

## Quebras que valem para mais de um dataset

| Desde | Mudança | Afeta |
|---|---|---|
| 2007-11 | Idades mínima e máxima passam de anos para meses; `DT_COMPETENCIA` sai das tabelas `tb_cid` e `tb_ocupacao`; as relações de OPM migram para `rl_procedimento_compativel` | `tb_procedimento`, `tb_cid`, `tb_ocupacao`, `rl_procedimento_compativel` |
| 2008-01 | `CO_RUBRICA` muda de composição (dois dígitos de financiamento mais quatro de subtipo); `TB_SIA_AIH` passa a `TB_SIA_SIH` | `tb_procedimento`, `tb_rubrica`, `tb_sia_sih`, `rl_procedimento_sia_sih` |
| 2009-05 | Os nomes dos ZIPs passam a ter o sufixo `_v` de versão | todos |
| 2012-09 | `tb_procedimento` ganha `QT_TEMPO_PERMANENCIA` | `tb_procedimento` |
| 2014-04; 2015-04 a 2015-08 | As tabelas de rede de atenção, RENASES e TUSS e as relações correspondentes aparecem em 2014-04 (competência isolada) e voltam a ser publicadas a partir de 2015-04 (as relações, a partir de 2015-08) | `tb_rede_atencao`, `tb_componente_rede`, `tb_renases`, `tb_tuss`, `rl_procedimento_comp_rede`, `rl_procedimento_renases`, `rl_procedimento_tuss` |
| 2025-06 | `VL_SH`, `VL_SA` e `VL_SP` passam de 10 para 12 posições no arquivo; a escala não muda | `tb_procedimento` |

As datas acima vêm do `LEIA_ME.TXT` (2007-2008) e dos layouts dos ZIPs (demais); cada página de dataset detalha as mudanças que lhe dizem respeito.
