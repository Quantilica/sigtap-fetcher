# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Adicionado
- O fetcher declara os fatos da fonte (`FetcherInfo`: id canônico, apelidos, órgão, licença, página e cadência) para o registro de fetchers da Quantilica.

### Alterado
- Requer `quantilica-core>=0.19.0` (e `quantilica-cli>=0.17.0` como host).

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

