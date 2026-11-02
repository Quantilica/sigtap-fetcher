# Changelog

Todas as alterações notáveis neste projeto serão documentadas neste arquivo.

O formato é baseado em [Keep a Changelog](https://keepachangelog.com/pt-BR/1.1.0/),
e este projeto adere ao [Versionamento Semântico](https://semver.org/lang/pt-BR/).

## [Não lançado]

### Corrigido
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

