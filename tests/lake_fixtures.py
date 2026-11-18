"""Brutos do SIGTAP e retrato do lake, para a prova de equivalência do conteúdo.

``build_raw`` copia os três ZIPs reais mínimos (200801, 201605 e 202610) e monta
mais dois sintéticos (202611, com acento Latin-1 e coluna esparsa, e 202612 com
uma tabela sem dado). ``snapshot`` descreve o lake por tabela e competência: número
de linhas, colunas com tipo e conteúdo ordenado, lendo cada Parquet direto (sem
hive). O arquivo do ano guarda várias competências; o retrato separa as linhas de
cada uma pela coluna ``mes``.
``golden/lake_por_competencia.json`` é o retrato do mesmo bruto gravado com um
Parquet por tabela e competência, gerado antes de o conversor passar a um Parquet
por tabela e ano; só o conteúdo importa, não a pasta.
"""

from __future__ import annotations

import shutil
import zipfile
from pathlib import Path
from typing import Any

FIXTURES = Path(__file__).parent / "fixtures"
GOLDEN = Path(__file__).parent / "golden" / "lake_por_competencia.json"

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


def snapshot(lake_dir: Path) -> dict[str, Any]:
    """Retrato do lake por tabela e competência (``AAAAMM``).

    Por competência: ``linhas``, ``colunas`` (nome e tipo, ordenadas por nome),
    ``conteudo`` (linhas ordenadas, nulo como texto vazio) e ``nao_nulas`` (colunas
    com algum valor). As colunas ``mes`` e ``_origem``, do arquivo do ano, ficam de
    fora; ``competencia`` é a de dados.
    """
    import polars as pl

    saida: dict[str, Any] = {}
    base = lake_dir / "sigtap"
    for tabela in sorted(p.name for p in base.iterdir() if p.is_dir()):
        periodos: dict[str, Any] = {}
        for arquivo in sorted((base / tabela).rglob("*.parquet")):
            ano = int(arquivo.parent.name.split("=", 1)[1])
            df = pl.read_parquet(arquivo, hive_partitioning=False)
            for mes in sorted(df["mes"].unique().to_list()):
                parte = df.filter(pl.col("mes") == mes).drop("mes", "_origem")
                parte = parte.select(sorted(parte.columns))
                comp = f"{ano:04d}{mes}"
                assert comp not in periodos, (tabela, comp)
                periodos[comp] = {
                    "linhas": parte.height,
                    "colunas": [[c, str(t)] for c, t in parte.schema.items()],
                    "nao_nulas": [
                        c for c in parte.columns if parte[c].null_count() < parte.height
                    ],
                    "conteudo": sorted(
                        ["" if v is None else str(v) for v in row]
                        for row in parte.rows()
                    ),
                }
        saida[tabela] = dict(sorted(periodos.items()))
    return saida


def parquets(lake_dir: Path) -> list[Path]:
    """Os Parquets do lake do SIGTAP, ordenados."""
    return sorted((lake_dir / "sigtap").rglob("*.parquet"))
