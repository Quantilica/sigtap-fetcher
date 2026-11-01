# sigtap-fetcher

[![CI](https://github.com/Quantilica/sigtap-fetcher/actions/workflows/test.yml/badge.svg)](https://github.com/Quantilica/sigtap-fetcher/actions/workflows/test.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

Coletor e conversor Lake Hive para dados abertos de **Tabela Unificada de Procedimentos do SUS (SIGTAP)** (`sigtap`), parte do ecossistema [Quantilica](https://quantilica.com).

## Instalação

### Via CLI Quantilica (recomendado)

```bash
quantilica install sigtap
```

Para instalar com suporte à conversão Parquet Lake:

```bash
quantilica install sigtap --extra analysis
```

### Como biblioteca Python

```bash
uv add sigtap-fetcher --index https://index.quantilica.com/simple/
```

Com o extra de análise analítica:

```bash
uv add 'sigtap-fetcher[analysis]' --index https://index.quantilica.com/simple/
```

## Uso via CLI

```bash
# Listar conjuntos disponíveis
quantilica sigtap list

# Verificar novos arquivos e frescor
quantilica sigtap check

# Sincronizar arquivos para o diretório local bruto
quantilica sigtap sync -o /data/sigtap

# Converter acervo bruto para o Universal Hive Parquet Lake
quantilica sigtap convert /data/sigtap /data/lake
```

## Licença

Distribuído sob licença MIT. Consulte [LICENSE](LICENSE) para mais detalhes.
