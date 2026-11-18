"""Um Parquet por tabela e ano: pulo, reescrita só do ano afetado e auditoria."""

from __future__ import annotations

import hashlib
import json
import shutil
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")

import polars as pl  # noqa: E402
import pyarrow.parquet as pq  # noqa: E402
from quantilica.analytics import lake_audit  # noqa: E402
from quantilica.analytics.lake import LakeWriter, check_dataset, output_id  # noqa: E402
from quantilica.core.lake import DatasetDescriptor  # noqa: E402

from sigtap_fetcher.lake import CONTRACT_VERSION, converter  # noqa: E402

from .lake_fixtures import build_raw, parquets  # noqa: E402

_L2 = "Coluna,Tamanho,Inicio,Fim,Tipo\nCO_A,2,1,2,VARCHAR2\nCO_B,2,3,4,VARCHAR2\n"
_L3 = _L2 + "CO_C,2,5,6,VARCHAR2\n"


def _zip(path: Path, tabelas: dict[str, tuple[str, str]]) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for nome, (layout, dados) in tabelas.items():
            if layout:
                zf.writestr(f"{nome}_layout.txt", layout)
            zf.writestr(f"{nome}.txt", dados.encode("latin-1"))


def _sidecars(raiz: Path) -> None:
    """Sidecar com o sha256 de cada bruto, como o fetcher grava."""
    for f in sorted(raiz.rglob("*.zip")):
        Path(f"{f}.manifest.json").write_text(
            json.dumps(
                {
                    "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
                    "size_bytes": f.stat().st_size,
                }
            ),
            encoding="utf-8",
        )


def _zip_do_mes(raw: Path, comp: str, tabelas: dict[str, tuple[str, str]]) -> Path:
    destino = raw / "tabelas" / f"TabelaUnificada_{comp}@20261101.zip"
    destino.parent.mkdir(parents=True, exist_ok=True)
    _zip(destino, tabelas)
    _sidecars(raw)
    return destino


def _carimbos(lake: Path) -> dict[Path, tuple[int, int]]:
    return {p: (p.stat().st_mtime_ns, p.stat().st_ino) for p in parquets(lake)}


def _arquivo(lake: Path, tabela: str, ano: int) -> Path:
    return lake / "sigtap" / tabela / f"ano={ano}" / f"{tabela}.parquet"


@pytest.fixture
def raw(tmp_path: Path) -> Path:
    build_raw(tmp_path / "raw")
    _sidecars(tmp_path / "raw")
    return tmp_path / "raw"


def test_segunda_execucao_nao_escreve_nem_abre_zip(
    raw: Path, tmp_path: Path, aberturas: list[str]
) -> None:
    lake = tmp_path / "lake"
    primeira = converter.convert(raw, lake)
    assert not primeira.errors and primeira.skipped == 0
    antes = _carimbos(lake)
    assert len(antes) == 15

    aberturas.clear()
    segunda = converter.convert(raw, lake)

    assert not segunda.errors
    assert (segunda.converted, segunda.skipped) == (0, primeira.converted)
    assert _carimbos(lake) == antes  # nenhum arquivo reescrito
    assert not list((lake / "sigtap").rglob(".tmp/*"))


def test_por_tabela_com_a_tabela_em_todos_os_zips_nao_abre_nenhum(
    raw: Path, tmp_path: Path, aberturas: list[str]
) -> None:
    lake = tmp_path / "lake"
    converter.convert(raw, lake, datasets=["tb_grupo"])
    antes = _carimbos(lake)
    assert len(antes) == 3  # 2008, 2016 e 2026

    aberturas.clear()
    res = converter.convert(raw, lake, datasets=["tb_grupo"])

    assert (res.converted, res.skipped, res.errors) == (0, 5, [])
    assert aberturas == []
    assert _carimbos(lake) == antes


def test_competencia_nova_reescreve_so_o_arquivo_do_ano(
    raw: Path, tmp_path: Path, aberturas: list[str]
) -> None:
    lake = tmp_path / "lake"
    converter.convert(raw, lake, datasets=["tb_grupo"])
    antes = _carimbos(lake)
    _zip_do_mes(raw, "202701", {"tb_grupo": (_L2, "01AA\n")})
    # 202612 é regerado, com outro sha, e o arquivo de 2026 é reescrito.
    _zip(
        raw / "tabelas" / "TabelaUnificada_202612@20261201.zip",
        {"tb_grupo": (_L2, "01ZZ\n")},
    )
    _sidecars(raw)

    aberturas.clear()
    res = converter.convert(raw, lake, datasets=["tb_grupo"])

    assert (res.converted, res.skipped, res.errors) == (2, 4, [])
    # Só os dois ZIPs que mudaram são abertos; os do mesmo ano em dia, não.
    assert sorted(aberturas) == [
        "TabelaUnificada_202612@20261201.zip",
        "TabelaUnificada_202701@20261101.zip",
    ]
    depois = _carimbos(lake)
    assert len(depois) == 4  # o arquivo de 2027 é novo
    for ano in (2008, 2016):
        arq = _arquivo(lake, "tb_grupo", ano)
        assert depois[arq] == antes[arq]  # outros anos intocados
    arq26 = _arquivo(lake, "tb_grupo", 2026)
    assert depois[arq26] != antes[arq26]
    df = pl.read_parquet(arq26, hive_partitioning=False)
    assert sorted(df["mes"].unique().to_list()) == ["10", "11", "12"]
    assert df.filter(pl.col("mes") == "12")["co_a"].to_list() == ["01"]
    assert df.filter(pl.col("mes") == "12")["co_b"].to_list() == ["ZZ"]


def test_competencia_com_sha_alterado_troca_so_as_linhas_dela(
    tmp_path: Path, aberturas: list[str]
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    for comp, dados in (("202601", "01AA\n"), ("202602", "02BB\n")):
        _zip_do_mes(raw, comp, {"tb_x": (_L2, dados)})
    _zip_do_mes(raw, "202501", {"tb_x": (_L2, "09ZZ\n")})
    converter.convert(raw, lake, datasets=["tb_x"])
    antes = _carimbos(lake)

    _zip_do_mes(raw, "202602", {"tb_x": (_L2, "02BB\n03CC\n")})
    aberturas.clear()
    res = converter.convert(raw, lake, datasets=["tb_x"])

    assert (res.converted, res.skipped, res.errors) == (1, 2, [])
    assert aberturas == ["TabelaUnificada_202602@20261101.zip"]
    depois = _carimbos(lake)
    assert depois[_arquivo(lake, "tb_x", 2025)] == antes[_arquivo(lake, "tb_x", 2025)]
    assert depois[_arquivo(lake, "tb_x", 2026)] != antes[_arquivo(lake, "tb_x", 2026)]
    df = pl.read_parquet(_arquivo(lake, "tb_x", 2026), hive_partitioning=False)
    por_mes = {m: sorted(g["co_a"].to_list()) for (m,), g in df.group_by("mes")}
    assert por_mes == {"01": ["01"], "02": ["02", "03"]}


def test_coluna_nova_no_meio_do_ano_nao_abre_os_zips_em_dia(
    tmp_path: Path, aberturas: list[str]
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _zip_do_mes(raw, "202601", {"tb_x": (_L2, "01AA\n")})
    _zip_do_mes(raw, "202602", {"tb_x": (_L2, "02BB\n")})
    converter.convert(raw, lake, datasets=["tb_x"])

    _zip_do_mes(raw, "202603", {"tb_x": (_L3, "03CCdd\n")})  # CO_C nasce em março
    aberturas.clear()
    res = converter.convert(raw, lake, datasets=["tb_x"])

    assert (res.converted, res.skipped, res.errors) == (1, 2, [])
    assert aberturas == ["TabelaUnificada_202603@20261101.zip"]
    df = pl.read_parquet(_arquivo(lake, "tb_x", 2026), hive_partitioning=False)
    assert df.schema["co_c"] == pl.String
    assert {m: g["co_c"].to_list() for (m,), g in df.group_by("mes")} == {
        "01": [None],
        "02": [None],
        "03": ["dd"],
    }
    # E o ano seguinte, já com a coluna, reconverte sem nova diferença de esquema.
    assert converter.convert(raw, lake, datasets=["tb_x"]).skipped == 3


def test_zip_que_sai_do_bruto_sai_do_arquivo_do_ano(tmp_path: Path) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _zip_do_mes(raw, "202601", {"tb_x": (_L2, "01AA\n")})
    saindo = _zip_do_mes(raw, "202602", {"tb_x": (_L2, "02BB\n")})
    converter.convert(raw, lake)

    saindo.unlink()
    res = converter.convert(raw, lake)

    assert not res.errors and res.converted == 0
    df = pl.read_parquet(_arquivo(lake, "tb_x", 2026), hive_partitioning=False)
    assert df["mes"].to_list() == ["01"]


def test_membro_que_passa_a_falhar_nao_apaga_as_linhas_do_arquivo(
    tmp_path: Path,
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _zip_do_mes(raw, "202601", {"tb_x": (_L2, "01AA\n")})
    ruim = _zip_do_mes(raw, "202602", {"tb_x": (_L2, "02BB\n")})
    converter.convert(raw, lake)

    # A competência é regerada sem o layout e nenhuma outra o traz da tabela
    # com a mesma largura: o erro é do ZIP, e as linhas que o arquivo já tem ficam.
    ruim.unlink()
    _zip_do_mes(raw, "202602", {"tb_x": ("", "02BBXX\n")})
    res = converter.convert(raw, lake)

    assert res.converted == 0
    assert len(res.errors) == 1 and "tb_x" in res.errors[0]
    df = pl.read_parquet(_arquivo(lake, "tb_x", 2026), hive_partitioning=False)
    assert sorted(df["mes"].to_list()) == ["01", "02"]


def test_erro_deterministico_volta_a_cada_execucao(tmp_path: Path) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _zip_do_mes(raw, "202601", {"tb_ok": (_L2, "01AA\n"), "tb_sem": ("", "01AA\n")})
    _zip_do_mes(raw, "202602", {"tb_ok": (_L2, "02BB\n")})

    primeira = converter.convert(raw, lake)
    segunda = converter.convert(raw, lake)

    assert primeira.errors == segunda.errors
    assert len(segunda.errors) == 1 and "tb_sem" in segunda.errors[0]
    assert (primeira.converted, segunda.converted, segunda.skipped) == (2, 0, 2)
    assert not (lake / "sigtap" / "tb_sem").exists()


def test_tabela_vazia_no_zip_nao_gera_arquivo_nem_erro(tmp_path: Path) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _zip_do_mes(raw, "202601", {"tb_ok": (_L2, "01AA\n"), "tb_vazia": (_L2, "")})

    res = converter.convert(raw, lake)

    assert res.errors == [] and res.converted == 1
    assert not (lake / "sigtap" / "tb_vazia").exists()


def test_force_reconverte_todos_os_membros(raw: Path, tmp_path: Path) -> None:
    lake = tmp_path / "lake"
    primeira = converter.convert(raw, lake)

    res = converter.convert(raw, lake, force=True)

    assert (res.converted, res.skipped, res.errors) == (primeira.converted, 0, [])


def test_rodape_do_arquivo_do_ano(raw: Path, tmp_path: Path) -> None:
    converter.convert(raw, tmp_path / "lake")
    arquivo = _arquivo(tmp_path / "lake", "tb_grupo", 2026)

    meta = pq.ParquetFile(arquivo).metadata.metadata
    membros = json.loads(meta[b"quantilica.members"])

    assert meta[b"quantilica.dataset_id"] == b"tb_grupo"
    assert sorted(membros) == [
        "TabelaUnificada_202610",
        "TabelaUnificada_202611_v2611011000",
        "TabelaUnificada_202612",
    ]
    assert membros["TabelaUnificada_202612"]["mes"] == "12"
    descritor = json.loads(
        (tmp_path / "lake/sigtap/tb_grupo/_dataset.json").read_text(encoding="utf-8")
    )
    assert descritor["partition_keys"] == ["ano"]


def test_origem_completa_para_o_zip_em_cada_tabela(raw: Path, tmp_path: Path) -> None:
    """O ZIP declara a saída que gera em cada tabela: ``origin_complete`` diz que
    está inteiro no lake sem abrir o bruto."""
    lake = tmp_path / "lake"
    converter.convert(raw, lake)
    zip_2026 = raw / "tabelas" / "TabelaUnificada_202612@20261201.zip"

    def writer(tabela: str) -> LakeWriter:
        return LakeWriter(
            lake / "sigtap" / tabela,
            DatasetDescriptor(
                source_id="sigtap",
                dataset_id=tabela,
                alias=tabela,
                partition_keys=["ano"],
                partition_types={"ano": "int"},
            ),
        )

    grupo = writer("tb_grupo")
    assert grupo.origin_complete(zip_2026, contract_version=CONTRACT_VERSION)
    assert grupo.origin_outputs(zip_2026, contract_version=CONTRACT_VERSION) == [
        output_id({"ano": 2026}, "tb_grupo")
    ]
    # tb_procedimento não está nesse ZIP, mas 2026 tem a tabela em outros: o ZIP
    # consta como membro de 0 linhas e está inteiro no lake.
    assert writer("tb_procedimento").origin_complete(
        zip_2026, contract_version=CONTRACT_VERSION
    )


def test_auditoria_do_lake_por_ano(raw: Path, tmp_path: Path) -> None:
    # O lake_audit espera <fonte>/<pasta>/<arquivo> sob o diretório de entrada.
    entrada = tmp_path / "entrada"
    shutil.copytree(raw, entrada / "sigtap")
    lake = tmp_path / "lake"
    res = converter.convert(entrada / "sigtap", lake)
    assert not res.errors

    report = lake_audit(lake, input_dir=entrada, converters={}, rehash=True)

    assert report.ok, report.to_text()
    for tabela in (p.name for p in (lake / "sigtap").iterdir()):
        assert check_dataset(lake / "sigtap" / tabela) == []


# --- tabela ausente ou vazia num ZIP: o ZIP fica em dia sem ser decodificado -----


def _bruto_com_lacunas(raw: Path) -> None:
    """2026: tb_y so em 202601 (ausente em 202602, vazia em 202603); 2025 sem tb_y."""
    _zip_do_mes(raw, "202512", {"tb_x": (_L2, "09ZZ\n")})
    _zip_do_mes(raw, "202601", {"tb_x": (_L2, "01AA\n"), "tb_y": (_L2, "01YY\n")})
    _zip_do_mes(raw, "202602", {"tb_x": (_L2, "02BB\n")})
    _zip_do_mes(raw, "202603", {"tb_x": (_L2, "03CC\n"), "tb_y": (_L2, "")})


def test_tabela_ausente_ou_vazia_vira_membro_sem_linhas(tmp_path: Path) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _bruto_com_lacunas(raw)

    res = converter.convert(raw, lake)

    assert res.errors == []
    arquivo = _arquivo(lake, "tb_y", 2026)
    df = pl.read_parquet(arquivo, hive_partitioning=False)
    assert df["mes"].to_list() == ["01"] and df["co_a"].to_list() == ["01"]
    membros = json.loads(
        pq.ParquetFile(arquivo).metadata.metadata[b"quantilica.members"]
    )
    assert {m["mes"]: m["rows"] for m in membros.values()} == {
        "01": 1,
        "02": 0,
        "03": 0,
    }
    # Sem dado em nenhum ZIP do ano, nao ha arquivo (nem vazio).
    assert not _arquivo(lake, "tb_y", 2025).exists()
    # Os membros sem linha nao entram na conta de convertidos.
    assert res.converted == 4 + 1


def test_segundo_build_sem_mudanca_nao_decodifica_membro(
    tmp_path: Path, aberturas: list[str], decodificados: list[str]
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _bruto_com_lacunas(raw)
    converter.convert(raw, lake)

    aberturas.clear()
    decodificados.clear()
    res = converter.convert(raw, lake)

    assert (res.errors, res.converted) == ([], 0)
    assert decodificados == []  # nenhum membro (nem layout) descomprimido
    # Por tabela: tb_y em 2026 esta em dia com o ZIP sem a tabela; so o ano sem
    # dado de tb_y le o diretorio central.
    aberturas.clear()
    converter.convert(raw, lake, datasets=["tb_y"])
    assert aberturas == ["TabelaUnificada_202512@20261101.zip"]
    assert decodificados == []


def test_ano_sem_dado_da_tabela_em_nenhum_zip_nao_cria_arquivo(
    tmp_path: Path, decodificados: list[str]
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _zip_do_mes(raw, "202601", {"tb_vazia": (_L2, ""), "tb_x": (_L2, "01AA\n")})

    converter.convert(raw, lake)
    decodificados.clear()
    converter.convert(raw, lake)

    assert not (lake / "sigtap" / "tb_vazia").exists()
    assert decodificados == []


# --- membro que falha: preservado, sem duplicar nem apagar -----------------------


def test_zip_ilegivel_preserva_as_linhas_e_nova_versao_nao_duplica(
    tmp_path: Path,
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    ruim = _zip_do_mes(raw, "202601", {"tb_x": (_L2, "01AA\n")})
    velho = _zip_do_mes(raw, "202602", {"tb_x": (_L2, "02BB\n")})
    converter.convert(raw, lake)

    ruim.write_bytes(b"nao e zip")  # 202601 passa a ser ilegivel (outro sha)
    velho.unlink()
    nova = raw / "tabelas" / "TabelaUnificada_202602_v2602021200@20261101.zip"
    _zip(nova, {"tb_x": (_L2, "02BB\n04DD\n")})
    _sidecars(raw)
    res = converter.convert(raw, lake)

    assert len(res.errors) == 1 and "202601" in res.errors[0]
    df = pl.read_parquet(_arquivo(lake, "tb_x", 2026), hive_partitioning=False)
    por_mes = {m: sorted(g["co_a"].to_list()) for (m,), g in df.group_by("mes")}
    assert por_mes == {"01": ["01"], "02": ["02", "04"]}  # sem duplicar o 02
    # O erro volta a cada build e o arquivo segue igual.
    res2 = converter.convert(raw, lake)
    assert res2.errors == res.errors
    assert (
        pl.read_parquet(_arquivo(lake, "tb_x", 2026), hive_partitioning=False).height
        == 3
    )


def test_competencia_regerada_sem_layout_mantem_as_linhas_da_versao_anterior(
    tmp_path: Path,
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _zip_do_mes(raw, "202601", {"tb_x": (_L2, "01AA\n")})
    _zip_do_mes(raw, "202602", {"tb_x": (_L2, "02BB\n")})
    converter.convert(raw, lake)

    (raw / "tabelas" / "TabelaUnificada_202602@20261101.zip").unlink()
    nova = raw / "tabelas" / "TabelaUnificada_202602_v2602021200@20261101.zip"
    _zip(nova, {"tb_x": ("", "02BBXX\n")})  # sem layout e de outra largura
    _sidecars(raw)
    res = converter.convert(raw, lake)

    assert len(res.errors) == 1 and "tb_x" in res.errors[0]
    df = pl.read_parquet(_arquivo(lake, "tb_x", 2026), hive_partitioning=False)
    assert sorted(df["mes"].to_list()) == ["01", "02"]
    assert df.filter(pl.col("mes") == "02")["co_b"].to_list() == ["BB"]


# --- ano sem origem: o arquivo sai ----------------------------------------------


def test_ano_cujo_unico_zip_saiu_do_bruto_perde_o_arquivo(tmp_path: Path) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    saindo = _zip_do_mes(raw, "202512", {"tb_x": (_L2, "09ZZ\n")})
    _zip_do_mes(raw, "202601", {"tb_x": (_L2, "01AA\n")})
    converter.convert(raw, lake)
    assert _arquivo(lake, "tb_x", 2025).is_file()

    saindo.unlink()
    res = converter.convert(raw, lake, datasets=["tb_x"])

    assert res.errors == []
    assert not _arquivo(lake, "tb_x", 2025).exists()
    assert _arquivo(lake, "tb_x", 2026).is_file()


def test_bruto_sem_nenhum_zip_nao_apaga_o_lake(tmp_path: Path) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _zip_do_mes(raw, "202601", {"tb_x": (_L2, "01AA\n")})
    converter.convert(raw, lake)

    shutil.rmtree(raw)  # bruto ausente (montagem fora do ar, por exemplo)
    (raw / "tabelas").mkdir(parents=True)
    converter.convert(raw, lake, datasets=["tb_x"])

    assert _arquivo(lake, "tb_x", 2026).is_file()


def test_ano_com_zip_ilegivel_nao_perde_o_arquivo(tmp_path: Path) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    ruim = _zip_do_mes(raw, "202601", {"tb_x": (_L2, "01AA\n")})
    converter.convert(raw, lake)

    ruim.write_bytes(b"nao e zip")
    _sidecars(raw)
    res = converter.convert(raw, lake, datasets=["tb_x"])

    assert len(res.errors) == 1
    assert _arquivo(lake, "tb_x", 2026).is_file()


def test_competencia_regerada_sem_a_tabela_perde_as_linhas_antigas(
    tmp_path: Path,
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _zip_do_mes(raw, "202601", {"tb_x": (_L2, "01AA\n")})
    _zip_do_mes(raw, "202602", {"tb_x": (_L2, "02BB\n"), "tb_z": (_L2, "02ZZ\n")})
    converter.convert(raw, lake)

    # 202602 e regerado sem tb_x (e sem nenhuma linha dela) e 202601 continua.
    _zip_do_mes(raw, "202602", {"tb_z": (_L2, "02ZZ\n")})
    res = converter.convert(raw, lake)

    assert res.errors == []
    df = pl.read_parquet(_arquivo(lake, "tb_x", 2026), hive_partitioning=False)
    assert df["mes"].to_list() == ["01"]
    # E se era o unico ZIP com dado da tabela no ano, o arquivo sai.
    _zip_do_mes(raw, "202601", {"tb_z": (_L2, "01ZZ\n")})
    converter.convert(raw, lake)
    assert not _arquivo(lake, "tb_x", 2026).exists()


# --- hash, tipo e ordem ---------------------------------------------------------


def test_sha_do_zip_e_calculado_uma_vez_e_nao_por_tabela(
    tmp_path: Path, bruto_lido: list[str]
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    tabelas = {f"tb_{c}": (_L2, "01AA\n") for c in "abcd"}
    _zip_do_mes(raw, "202601", tabelas)
    _zip_do_mes(raw, "202602", tabelas)
    converter.convert(raw, lake)
    for sidecar in raw.rglob("*.manifest.json"):
        sidecar.unlink()  # sem sidecar o hash le o bruto

    bruto_lido.clear()
    converter.convert(raw, lake)

    assert bruto_lido.count("hash") == 2  # um por ZIP, nao 2 x 4 tabelas


def test_tipo_que_muda_entre_layouts_do_ano_e_erro_do_grupo(tmp_path: Path) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    numerico = "Coluna,Tamanho,Inicio,Fim,Tipo\nCO_A,2,1,2,NUMBER\n"
    # int em janeiro e texto em fevereiro: promover calado perderia o zero de "01".
    _zip_do_mes(raw, "202601", {"tb_x": (numerico, "01\n"), "tb_ok": (_L2, "01AA\n")})
    _zip_do_mes(raw, "202602", {"tb_x": (_L2, "AABB\n"), "tb_ok": (_L2, "02BB\n")})

    res = converter.convert(raw, lake)

    assert len(res.errors) == 1
    assert "tb_x" in res.errors[0] and "co_a" in res.errors[0]
    assert not _arquivo(lake, "tb_x", 2026).exists()
    assert _arquivo(lake, "tb_ok", 2026).is_file()  # os outros grupos seguem


def test_membros_vao_ao_grupo_em_ordem_de_competencia_sem_sort_by(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    for comp in ("202603", "202601", "202602"):
        _zip_do_mes(raw, comp, {"tb_x": (_L2, f"{comp[-2:]}AA\n")})
    chamadas: list[dict] = []
    original = LakeWriter.write_group

    def espia(self, group_key, members, **kwargs):  # noqa: ANN001, ANN202
        chamadas.append({"chaves": [m.key for m in members], **kwargs})
        return original(self, group_key, members, **kwargs)

    monkeypatch.setattr(LakeWriter, "write_group", espia)
    converter.convert(raw, lake)

    (chamada,) = chamadas
    assert chamada["chaves"] == [
        "TabelaUnificada_202601",
        "TabelaUnificada_202602",
        "TabelaUnificada_202603",
    ]
    assert not chamada.get("sort_by")
    assert chamada.get("prune", True) is True


# --- ZIP que nao se le: falha so dele ---------------------------------------------


def test_erro_ao_calcular_o_sha_de_um_zip_nao_aborta_o_convert(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import sigtap_fetcher.lake as lake_mod

    raw, lake = tmp_path / "raw", tmp_path / "lake"
    _zip_do_mes(raw, "202601", {"tb_x": (_L2, "01AA\n"), "tb_y": (_L2, "01AA\n")})
    _zip_do_mes(raw, "202602", {"tb_x": (_L2, "02BB\n"), "tb_y": (_L2, "02BB\n")})
    _zip_do_mes(raw, "202512", {"tb_x": (_L2, "09ZZ\n"), "tb_y": (_L2, "09ZZ\n")})
    converter.convert(raw, lake)

    original = lake_mod.sha256_file

    def sha(path):  # noqa: ANN001, ANN202
        if "202602" in Path(path).name:
            raise OSError("Could not read file for checksum")
        return original(path)

    monkeypatch.setattr(lake_mod, "sha256_file", sha)
    res = converter.convert(raw, lake)  # nao levanta

    assert len(res.errors) == 1 and "202602" in res.errors[0]  # uma vez por ZIP
    for tabela in ("tb_x", "tb_y"):
        df = pl.read_parquet(_arquivo(lake, tabela, 2026), hive_partitioning=False)
        assert sorted(df["mes"].to_list()) == ["01", "02"]  # linhas preservadas
        assert _arquivo(lake, tabela, 2025).is_file()  # outros anos seguem


# --- force e membro preservado -----------------------------------------------------


def test_force_com_zip_ilegivel_preserva_as_linhas_dele(tmp_path: Path) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    ruim = _zip_do_mes(raw, "202601", {"tb_x": (_L3, "01AAbbcc\n")})
    _zip_do_mes(raw, "202602", {"tb_x": (_L2, "02BB\n")})
    converter.convert(raw, lake)

    ruim.write_bytes(b"nao e zip")
    _sidecars(raw)
    res = converter.convert(raw, lake, force=True)

    assert len(res.errors) == 1 and "202601" in res.errors[0]
    df = pl.read_parquet(_arquivo(lake, "tb_x", 2026), hive_partitioning=False)
    por_mes = {m: g for (m,), g in df.group_by("mes")}
    assert por_mes["01"]["co_c"].to_list() == ["bb"]  # as linhas antigas, intactas
    assert por_mes["02"]["co_a"].to_list() == ["02"]


def test_preservar_com_contrato_antigo_falha_dizendo_a_causa(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    import sigtap_fetcher.lake as lake_mod

    raw, lake = tmp_path / "raw", tmp_path / "lake"
    ruim = _zip_do_mes(raw, "202601", {"tb_x": (_L2, "01AA\n")})
    _zip_do_mes(raw, "202602", {"tb_x": (_L2, "02BB\n")})
    with monkeypatch.context() as m:
        m.setattr(lake_mod, "CONTRACT_VERSION", CONTRACT_VERSION - 1)
        converter.convert(raw, lake)

    ruim.write_bytes(b"nao e zip")
    _sidecars(raw)
    res = converter.convert(raw, lake)

    grupo = [e for e in res.errors if "tb_x" in e and "ano=2026" in e]
    assert len(grupo) == 1
    assert "contrato" in grupo[0] and "202601" in grupo[0]
    assert "em dia" not in grupo[0]


# --- nome de ZIP fora do padrao ---------------------------------------------------


def test_zip_com_nome_fora_do_padrao_e_erro_e_nao_duplica_o_mes(
    tmp_path: Path,
) -> None:
    raw, lake = tmp_path / "raw", tmp_path / "lake"
    original = _zip_do_mes(raw, "202610", {"tb_x": (_L2, "10AA\n")})
    copia = original.with_name("copia 202610.zip")
    shutil.copy2(original, copia)
    _sidecars(raw)

    primeira = converter.convert(raw, lake)
    segunda = converter.convert(raw, lake)

    assert len(primeira.errors) == 1 and "copia 202610.zip" in primeira.errors[0]
    assert segunda.errors == primeira.errors  # determinístico
    df = pl.read_parquet(_arquivo(lake, "tb_x", 2026), hive_partitioning=False)
    assert df["mes"].to_list() == ["10"]  # um mes so, sem duplicar
