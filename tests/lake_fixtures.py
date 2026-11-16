"""Brutos do SIGTAP e retrato do lake, para a prova de equivalência da partição.

``build_raw`` copia os três ZIPs reais mínimos (200801, 201605 e 202610) e monta
mais dois sintéticos (202611, com acento Latin-1 e coluna esparsa, e 202612 com
uma tabela sem dado). ``snapshot`` descreve o lake por tabela e competência: número
de linhas, colunas com tipo e conteúdo ordenado, lendo cada Parquet direto (sem
hive), de modo que o mesmo retrato vale para as duas pastas (``competencia=AAAAMM``
e ``ano=AAAA/mes=MM``). A coluna ``competencia`` é de dados no layout novo e da
pasta no antigo; o retrato a trata igual nos dois.
``golden/lake_antes_da_particao.json`` foi gerado pelo conversor da pasta
``competencia=``, antes da mudança:

    uv run --no-sync python -m tests.lake_fixtures --escrever-golden
"""

from __future__ import annotations

import json
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from typing import Any

FIXTURES = Path(__file__).parent / "fixtures"
GOLDEN = Path(__file__).parent / "golden" / "lake_antes_da_particao.json"

REAIS = ("200801", "201605", "202610")

_LAYOUT_GRUPO = (
    "Coluna,Tamanho,Inicio,Fim,Tipo\n"
    "CO_GRUPO,2,1,2,VARCHAR2\nNO_GRUPO,20,3,22,VARCHAR2\nNU_OPC,4,23,26,VARCHAR2\n"
)
_LAYOUT_VALOR = (
    "Coluna,Tamanho,Inicio,Fim,Tipo\n"
    "CO_P,4,1,4,VARCHAR2\nVL_SH,8,5,12,NUMBER\nVL_IDADE_MINIMA,4,13,16,NUMBER\n"
)


def _zip_sintetico(path: Path, tabelas: dict[str, tuple[str, str]]) -> None:
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("LEIA_ME.TXT", "leia-me")
        for nome, (layout, dados) in tabelas.items():
            zf.writestr(f"{nome}_layout.txt", layout)
            zf.writestr(f"{nome}.txt", dados.encode("latin-1"))


def build_raw(root: Path) -> list[Path]:
    """Cria ``root/tabelas/*.zip`` e devolve os caminhos."""
    pasta = root / "tabelas"
    pasta.mkdir(parents=True, exist_ok=True)
    caminhos = []
    for comp in REAIS:
        destino = pasta / f"TabelaUnificada_{comp}@20261101.zip"
        shutil.copy2(FIXTURES / f"TabelaUnificada_{comp}.zip", destino)
        caminhos.append(destino)
    # Acento Latin-1 e coluna esparsa (NU_OPC vazio nas primeiras linhas).
    grupos = "".join(
        f"{i:02d}{('AÇÃO ' + str(i)).ljust(20)}{'' if i < 5 else '9000'.ljust(4)}\n"
        for i in range(1, 9)
    )
    valores = "0001" + "00001000" + "0012\n" + "0002" + "00002550" + "0024\n"
    sint1 = pasta / "TabelaUnificada_202611_v2611011000@20261102.zip"
    _zip_sintetico(
        sint1,
        {
            "tb_grupo": (_LAYOUT_GRUPO, grupos),
            "tb_procedimento": (_LAYOUT_VALOR, valores),
        },
    )
    # Dois meses depois, a mesma tabela com outra linha (outro mês, mesmo ano).
    sint2 = pasta / "TabelaUnificada_202612@20261201.zip"
    _zip_sintetico(sint2, {"tb_grupo": (_LAYOUT_GRUPO, "01CAMPO DE DEZEMBRO     \n")})
    return [*caminhos, sint1, sint2]


def _competencia_do_caminho(path: Path, dataset_dir: Path) -> str:
    """``AAAAMM`` da pasta: ``competencia=AAAAMM`` ou ``ano=AAAA/mes=MM``."""
    chaves = dict(
        p.split("=", 1) for p in path.relative_to(dataset_dir).parts[:-1] if "=" in p
    )
    if "competencia" in chaves:
        return chaves["competencia"]
    return f"{int(chaves['ano']):04d}{int(chaves['mes']):02d}"


def snapshot(lake_dir: Path) -> dict[str, Any]:
    """Retrato do lake por tabela e competência, sem depender da pasta."""
    import polars as pl

    saida: dict[str, Any] = {}
    base = lake_dir / "sigtap"
    for tabela in sorted(p.name for p in base.iterdir() if p.is_dir()):
        dataset_dir = base / tabela
        periodos: dict[str, Any] = {}
        colunas: dict[str, str] = {}
        for arquivo in sorted(dataset_dir.rglob("*.parquet")):
            comp = _competencia_do_caminho(arquivo, dataset_dir)
            df = pl.read_parquet(arquivo, hive_partitioning=False)
            if "competencia" not in df.columns:
                df = df.with_columns(pl.lit(comp).alias("competencia"))
            df = df.select(sorted(df.columns))
            assert comp not in periodos, (tabela, comp)  # um Parquet por competência
            periodos[comp] = {
                "linhas": df.height,
                "colunas": [[c, str(t)] for c, t in df.schema.items()],
                "conteudo": sorted(
                    ["" if v is None else str(v) for v in row] for row in df.rows()
                ),
            }
            colunas.update({c: str(t) for c, t in df.schema.items()})
        saida[tabela] = {
            "colunas": sorted(colunas.items()),
            "periodos": dict(sorted(periodos.items())),
        }
    return saida


def contagem_de_arquivos(lake_dir: Path) -> dict[str, dict[str, int]]:
    """Parquets por tabela e competência (``AAAAMM``)."""
    base = lake_dir / "sigtap"
    saida: dict[str, dict[str, int]] = {}
    for tabela in sorted(p.name for p in base.iterdir() if p.is_dir()):
        comps: dict[str, int] = {}
        for arquivo in sorted((base / tabela).rglob("*.parquet")):
            comp = _competencia_do_caminho(arquivo, base / tabela)
            comps[comp] = comps.get(comp, 0) + 1
        saida[tabela] = comps
    return saida


def _escrever_golden() -> None:
    from sigtap_fetcher.lake import converter

    with tempfile.TemporaryDirectory(prefix="sigtap-golden-") as tmp:
        raiz = Path(tmp)
        build_raw(raiz / "raw")
        resultado = converter.convert(raiz / "raw", raiz / "lake")
        assert not resultado.errors, resultado.errors
        GOLDEN.parent.mkdir(parents=True, exist_ok=True)
        GOLDEN.write_text(
            json.dumps(
                {
                    "contagem_de_arquivos": contagem_de_arquivos(raiz / "lake"),
                    "lake": snapshot(raiz / "lake"),
                },
                ensure_ascii=False,
                indent=1,
                sort_keys=True,
            )
            + "\n",
            encoding="utf-8",
        )
    print(f"golden escrito em {GOLDEN}")


if __name__ == "__main__":
    if "--escrever-golden" not in sys.argv:
        raise SystemExit(__doc__)
    _escrever_golden()
