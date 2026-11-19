# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [0.6.0] - 2026-11-19

### Alterado

- **Quebra de layout no lake: um Parquet por tabela e por ano.** Antes, cada tabela tinha um Parquet por competência (`sigtap/<tabela>/ano=AAAA/mes=MM/TabelaUnificada_AAAAMM.parquet`, 8.378 arquivos de cerca de 28 KB). Agora há um por tabela e ano, com as linhas de todas as competências do ano:
  - antes: `ano=2026/mes=10/TabelaUnificada_202610.parquet`;
  - depois: `ano=2026/tb_grupo.parquet`.
  - A partição passa a ser só `ano` (inteiro). `mes` (texto de 2 dígitos) deixa de ser pasta e vira coluna do arquivo, ao lado de `competencia` (AAAAMM, como antes) e de `_origem` (chave do ZIP de origem da linha); `WHERE competencia = '202610'` e `WHERE ano = 2026 AND mes = '10'` continuam valendo. A ordem das linhas dentro do arquivo não é garantida: filtre por `mes` ou `competencia`.
  - Cada competência é um membro do grupo do ano (`LakeWriter.write_group`): competência nova, ou ZIP regerado com outro hash, reescreve só o arquivo do ano dela, e a que está em dia não é decodificada. Na conversão de uma tabela que o ZIP traz, o ZIP em dia nem é aberto; um build sem `datasets`, ou de uma tabela ausente em alguns anos, ainda lê o diretório central dos ZIPs desses anos (só a lista de membros, nada é descomprimido).
  - Tabela ausente de um ZIP, ou vazia nele, num ano em que a tabela tem dados, entra no arquivo como membro de 0 linhas: o ZIP fica em dia e deixa de ser lido a cada build. Num ano sem dado da tabela em nenhum ZIP não há arquivo; ali só se lê a lista de membros do ZIP (diretório central), sem descompactar nada.
  - ZIP que sai do bruto sai do arquivo do ano, e o arquivo de um ano sem nenhum ZIP de origem no bruto é apagado (nada é apagado se o bruto não tem ZIP algum, se há ZIP com nome fora do padrão, nem num ano em que algum ZIP falhou). Competência regerada sem a tabela perde as linhas antigas dela.
  - Uma competência que passa a falhar (ZIP ilegível, tabela sem layout) mantém no arquivo as linhas que já tinha (da mesma chave ou da mesma competência numa versão anterior), sem duplicar, e o erro continua em `ConvertResult.errors` a cada build; vale também com `force` e quando o ZIP não pode nem ser lido para calcular o hash. Só as linhas gravadas com outro contrato de conversão, ou sem os nulos por membro, não podem ser preservadas com exatidão: o grupo (tabela e ano) falha, com a causa, e é preciso reconverter.
  - ZIP com nome fora de `TabelaUnificada_AAAAMM[_vAAMMDDHHMM][@carimbo].zip` (uma cópia, por exemplo) não é convertido e vira erro em `ConvertResult.errors` a cada build, em vez de duplicar a competência.
  - O esquema do arquivo é a união das colunas das competências que ficam no ano (a coluna que só um membro removido trazia sai do arquivo, sem decodificar os membros mantidos, e o tipo dele não conflita mais; o layout de `tb_cid`, `tb_componente_rede` e `tb_procedimento` ganha coluna no meio de um ano): a competência que não traz a coluna a recebe nula. Coluna cujo tipo muda entre layouts do mesmo ano é erro daquele grupo (tabela e ano), sem travar os demais.
  - Cada membro do arquivo do ano registra, em `quantilica.members`, os nulos exatos de cada coluna que ele tinha (`null_counts`), para o perfil do lake continuar mensal (`granularidade: mensal`, períodos `AAAA-MM`, linhas e nulos por competência) mesmo com a partição por ano; competências sem linhas não aparecem no perfil. Arquivo gravado antes disso é regravado uma vez, sem que os ZIPs em dia deixem de ser pulados depois.
  - A conversão não apaga os Parquets do layout anterior (`ano=AAAA/mes=MM/`): quem tem um lake já convertido precisa removê-los uma vez, e regerar os esquemas de `docs/` depois da reconversão.
- Exige `quantilica-analytics>=0.15.0` no extra `analysis` (grupos que declaram as saídas de cada ZIP).
- Documentação dos dados: partição `ano`, colunas `mes` e `_origem` no dicionário das 40 tabelas convertidas e esquemas regerados.
- CI e infraestrutura alinhados ao template (fetcher-template v0.2.1).

### Corrigido

- Conversão do lake: com `datasets=[...]` e sem `force`, o ZIP cujas tabelas-alvo já estão em dia deixa de ser aberto (nem os arquivos de layout nem a lista de membros são lidos). Antes, cada tarefa por tabela abria todos os ZIPs antes de verificar o Parquet, o que em disco lento levava minutos por tabela sem nada a converter. As contagens de `converted` e `skipped` não mudam; o ZIP em que a tabela falta, o ZIP novo, `force` e a conversão sem `datasets` seguem abrindo o ZIP como antes.

## [0.5.0] - 2026-11-16
### Alterado
- **Quebra de layout no lake: a competência passa a `ano=AAAA/mes=MM/`.** Cada tabela continua com um Parquet por competência, com o mesmo conteúdo, mas a pasta muda. Antes e depois, em `sigtap/<tabela>/`:
  - antes: `competencia=202610/TabelaUnificada_202610.parquet`;
  - depois: `ano=2026/mes=10/TabelaUnificada_202610.parquet`.
  - A coluna `competencia` (AAAAMM, texto) deixa de ser a pasta e passa a ser coluna de dados, com os mesmos valores, de modo que `WHERE competencia = '202610'` continua valendo; `ano` (inteiro) e `mes` (texto de 2 dígitos) vêm das pastas. Não há o que agrupar: o número de arquivos não muda.
  - Na reconversão a pasta antiga `competencia=AAAAMM/` de cada tabela é apagada sozinha depois que a nova é publicada (só os Parquets deste dataset; qualquer outro arquivo fica e a pasta só some se esvaziar). Rodar a conversão de novo sobre um lake já migrado não reescreve nada.
  - Toda pasta `competencia=*` que sobrar ao fim de `convert` (competência fora do bruto visto, tabela sem layout, tabela vazia, ZIP com falha, ou arquivo alheio dentro dela) é listada em `ConvertResult.errors`, com o caminho e o motivo provável; nada além do que a migração substitui é apagado.
- Exige `quantilica-analytics>=0.12.0` no extra `analysis`.
- Documentação dos dados: partições `ano` e `mes`, `competencia` como coluna do conversor, esquemas com a coluna `competencia` (regerar os esquemas do lake depois da reconversão).

### Adicionado
- Testes de equivalência da partição: o conteúdo do lake (linhas, colunas e tipos, linhas ordenadas por tabela e competência) é igual ao do conversor da pasta `competencia=` (`tests/golden/lake_antes_da_particao.json`, gerado antes da mudança), mais segunda execução sem reescrita, migração da pasta antiga sem linhas duplicadas, `lake_audit` limpo e `profile_from_lake` com período mensal.
- Testes: identidade do registro conferida.
- Documentação dos dados em `docs/`, conforme a norma de documentação dos dados: página da fonte, página e esquema de referência para cada um dos 41 datasets (o esquema de `rl_procedimento_tuss` não existe porque a fonte publica a tabela vazia), com o dicionário de todas as variáveis. Um teste a verifica.

### Corrigido
- CI: o pyproject declara o PyPI antes do índice Quantilica (`[[tool.uv.index]]`), e o workflow perde `--index` e `--index-strategy`. Com a estratégia padrão `first-index`, o `uv sync` só consulta o índice para o que não está no PyPI (`quantilica-analytics`) e deixa de receber o 503 intermitente que o GitHub Pages devolve a caminhos inexistentes.

## [0.4.0] - 2026-11-14

### Adicionado
- O fetcher declara os fatos da fonte (`FetcherInfo`: id canônico, apelidos, órgão, licença, página e cadência) para o registro de fetchers da Quantilica.

### Alterado
- Requer `quantilica-core>=0.19.0` (e `quantilica-cli>=0.17.0` como host).
- `FetcherInfo.licenca` passa a declarar a licença da fonte: Sem licença declarada; dados públicos pela Lei 12.527/2011 (LAI) e Decreto 8.777/2016.

## [0.3.0] - 2026-11-05

### Corrigido
- O arquivo baixado passa a ter nome estável: o carimbo `@AAAAMMDD` é a data de publicação no servidor (sufixo `_v` do nome ou data da listagem), não mais o dia do download. Antes, cada execução gerava um nome novo e baixava de novo todas as competências já obtidas. Na primeira execução após esta mudança, as competências são baixadas uma vez com o novo nome.

### Alterado
- A listagem do catálogo passa a informar o tamanho (`remote_size`) e a data de publicação (`remote_date`) de cada competência, e o `check` preenche o tamanho remoto no plano.
- A chave do arquivo bruto no lake passa a ser montada com `composite_file_key` do `quantilica-core` (nome do arquivo e, quando houver, o membro do ZIP), sem mudar as partições.

## [0.2.2] - 2026-11-04

### Corrigido
- `lake`: ZIPs antigos (201412 a 2015xx) sem `tb_regra_condicionada_layout.txt` voltam a ser convertidos: o layout é o da mesma tabela na competência mais próxima do lote (empate: a anterior), com aviso no log e só se a largura bater com a dos dados; senão a tabela continua contada como erro. Nunca se usa o layout de outra tabela.

## [0.2.1] - 2026-11-04

### Corrigido
- `lake`: `vl_percentual_sh/sa/sp` (`rl_procedimento_incremento`) voltam a ter duas casas decimais (`2000` = 20,0 %); a 0.2.0 os lia como inteiros. Reconverter `rl_procedimento_incremento` com `--force`. `vl_idade_*` e `vl_campos_irradiados` continuam inteiros.
- Sem o extra `analysis`, o comando `convert` termina com código 1 e a instrução de instalação (`quantilica install sigtap --extra analysis`), sem traceback.

## [0.2.0] - 2026-11-04

### Corrigido
- `lake`: o `convert` mantinha duas versoes da mesma competencia (`select_current` agrupa pela chave inteira, que inclui `_v<timestamp>`); agora so a de maior `_v` entra por competencia.
- `lake`: `datasets()` devolvia 16 `CORE_TABLES` (uma, `tb_subgrupo`, nem existe: o nome real e `tb_sub_grupo`). Agora sao as 41 tabelas `tb_*`/`rl_*` do ZIP de 2026-10 (`ALL_TABLES`, sondadas no FTP; o plano falava em 42). Todas tem `<tabela>_layout.txt` e convertem sem parser novo; `rl_procedimento_tuss` vem vazia na fonte.
- `lake`: `LEIA_ME.TXT` e o `layout.txt` consolidado eram tratados como tabelas (erro / dataset-lixo); so `tb_*`/`rl_*` sao convertidas.
- `lake`: schema explicito no DataFrame (coluna vazia nas primeiras linhas virava `Null` e quebrava, p.ex. `rl_procedimento_habilitacao`).
- `lake`: so `vl_sh/vl_sa/vl_sp` sao dinheiro (centavos /100); `vl_idade_*`, `vl_campos_irradiados` e `vl_percentual_*` eram divididos por 100 por engano e agora sao inteiros. Reconverter `tb_procedimento`, `tb_cid` e `rl_procedimento_incremento` com `--force`.
- Política de frescor volta a F1 (`HEAD_OR_MANIFEST`): `REMOTE_ONLY` (F3, para fontes sem validadores) causava re-download diário de fontes com Last-Modified/ETag, porque descartava o Last-Modified e o nome do arquivo caía em `@hoje`.
- Aliases de grupo (`sync padrao` etc.): o `FetcherApp` recebia `alias -> str` e o
  SDK fazia `list("teses")`, resolvendo para `['t', 'e', 's', ...]` ("Grupo
  desconhecido: 't'"). O plugin agora passa `alias -> [grupo]`.
- `check`: o veredito casa a entrada por competência (AAAAMM) e versão (sufixo
  `v`), ignorando o carimbo `@AAAAMMDD` do nome local. Antes o carimbo de hoje
  era usado na busca e todo arquivo baixado em outro dia virava
  `download/not-present` (redownload diário). Sufixo `v` novo é versão nova
  (`download/new-version`).
- `lake`: tabela sem `<tabela>_layout.txt` no ZIP não é mais convertida com o
  layout da primeira tabela; entra em `errors` com o nome da tabela e do ZIP.
- Marcador pytest `network` registrado (fora do `pytest -q` padrão).
- `sync`/`check` do SIGTAP agora baixam de verdade: o catálogo era gerado por
  aritmética de competências com `ftp://` e nomes "lisos", que o cliente HTTP
  recusava e que não existem desde 2025 (`_v<timestamp>`). O catálogo passa a
  descobrir a listagem real do FTP e a usar a versão mais recente por
  competência, com `FtpClient` no `FetcherApp` e veredito de frescor local.
- `SigtapClient` usa `FtpClient.list_files` (não o inexistente `list_dir`) e
  repassa `source_id`/`dataset_id`/`producer` ao manifesto.

## [0.1.0] - 2026-11-01

### Adicionado
- Versão inicial do pacote `sigtap-fetcher` (`quantilica sigtap`).
- Suporte a `list`, `check`, `sync` e verificação de frescor via SDK `FetcherApp`.

- Conversor Universal Hive Parquet Lake com `DatasetSpec` em `lake.py`.

