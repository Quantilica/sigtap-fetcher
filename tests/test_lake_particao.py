"""Partição ``ano=/mes=``: segunda execução, migração da pasta antiga e auditoria."""

from __future__ import annotations

import json
import shutil
import zipfile
from pathlib import Path

import pytest

pytest.importorskip("quantilica.analytics.lake")

import pyarrow.parquet as pq  # noqa: E402
from quantilica.analytics import lake_audit  # noqa: E402
from quantilica.analytics.lake import check_dataset, scan_dataset  # noqa: E402

import sigtap_fetcher.lake as lake_mod  # noqa: E402
from sigtap_fetcher.lake import converter  # noqa: E402

from .lake_fixtures import GOLDEN, build_raw, snapshot  # noqa: E402


def _legacy_convert(raw: Path, lake: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    """O conversor anterior: o mesmo código, com a pasta ``competencia=AAAAMM``."""
    with monkeypatch.context() as m:
        m.setattr(lake_mod, "PARTITION_KEYS", ["competencia"])
        m.setattr(lake_mod, "competencia_partitions", lambda c: {"competencia": c})
        m.setattr(lake_mod, "_remove_legacy_partition", lambda *a, **k: 0)
        res = converter.convert(raw, lake)
    # a simulação grava em competencia=, que o conversor novo relata como resíduo
    assert all("pasta do layout antigo" in e for e in res.errors)


def _parquets(lake: Path) -> list[Path]:
    return sorted((lake / "sigtap").rglob("*.parquet"))


@pytest.fixture
def raw(tmp_path: Path) -> Path:
    build_raw(tmp_path / "raw")
    return tmp_path / "raw"


def test_simulacao_do_conversor_antigo_bate_com_o_golden(
    raw: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """O auxiliar que recria o layout antigo é fiel: reproduz o golden commitado."""
    lake = tmp_path / "lake"
    _legacy_convert(raw, lake, monkeypatch)

    assert len(list((lake / "sigtap").rglob("competencia=*"))) == 18
    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))["lake"]
    assert json.loads(json.dumps(snapshot(lake), ensure_ascii=False)) == golden


def test_segunda_execucao_pula_tudo_sem_reescrever(raw: Path, tmp_path: Path) -> None:
    lake = tmp_path / "lake"
    primeira = converter.convert(raw, lake)
    assert not primeira.errors and primeira.skipped == 0
    n = primeira.converted
    antes = {p: (p.stat().st_mtime_ns, p.stat().st_ino) for p in _parquets(lake)}
    assert len(antes) == n

    segunda = converter.convert(raw, lake)

    assert not segunda.errors
    assert (segunda.converted, segunda.skipped) == (0, n)
    depois = {p: (p.stat().st_mtime_ns, p.stat().st_ino) for p in _parquets(lake)}
    assert depois == antes  # nenhum arquivo reescrito
    assert not list((lake / "sigtap").rglob(".tmp/*"))


def test_migracao_da_pasta_antiga_sem_duplicar_linhas(
    raw: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lake = tmp_path / "lake"
    _legacy_convert(raw, lake, monkeypatch)
    antigos = _parquets(lake)
    assert antigos and all("competencia=" in str(p) for p in antigos)
    tabelas = sorted(p.name for p in (lake / "sigtap").iterdir())
    linhas_antes = {
        t: scan_dataset(lake / "sigtap" / t).collect().height for t in tabelas
    }

    res = converter.convert(raw, lake)

    assert not res.errors
    assert (res.converted, res.skipped) == (len(antigos), 0)
    novos = _parquets(lake)
    assert len(novos) == len(antigos)
    assert not any("competencia=" in str(p) for p in novos)
    assert not list((lake / "sigtap").rglob("competencia=*"))  # pastas antigas somem
    for tabela, linhas in linhas_antes.items():
        df = scan_dataset(lake / "sigtap" / tabela).collect()
        assert df.height == linhas, tabela  # nenhuma linha duplicada
        assert check_dataset(lake / "sigtap" / tabela) == []
    # Idempotente: a passada seguinte não mexe em nada.
    assert converter.convert(raw, lake).skipped == len(novos)


def test_migracao_nao_apaga_o_que_nao_e_do_dataset(
    raw: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lake = tmp_path / "lake"
    _legacy_convert(raw, lake, monkeypatch)
    pasta = lake / "sigtap" / "tb_grupo" / "competencia=202610"
    # Parquet de outro dataset (rodapé de tb_cid) na pasta antiga: não é apagado.
    outro = lake / "sigtap" / "tb_grupo" / "competencia=202610" / "alheio.parquet"
    shutil.copy2(
        lake
        / "sigtap"
        / "tb_procedimento"
        / "competencia=202610"
        / "TabelaUnificada_202610.parquet",
        outro,
    )

    res = converter.convert(raw, lake)

    # a pasta com o arquivo alheio fica e é relatada, com o caminho
    assert len(res.errors) == 1 and str(pasta) in res.errors[0]
    assert outro.exists()  # rodapé de tb_procedimento: não é de tb_grupo
    assert not (pasta / "TabelaUnificada_202610.parquet").exists()
    assert (
        lake / "sigtap/tb_grupo/ano=2026/mes=10/TabelaUnificada_202610.parquet"
    ).exists()


def test_migracao_retoma_depois_de_queda_entre_publicar_e_apagar(
    raw: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Nova partição publicada, pasta antiga ainda lá: a próxima passada pula a
    conversão e só limpa o antigo."""
    lake = tmp_path / "lake"
    converter.convert(raw, lake)
    novo = _parquets(lake)
    # Recria uma pasta antiga com o mesmo conteúdo (a queda ocorreu antes do rm).
    alvo = lake / "sigtap/tb_grupo/ano=2026/mes=10/TabelaUnificada_202610.parquet"
    velho = lake / "sigtap/tb_grupo/competencia=202610/TabelaUnificada_202610.parquet"
    velho.parent.mkdir(parents=True)
    shutil.copy2(alvo, velho)

    res = converter.convert(raw, lake)

    assert (res.converted, res.skipped) == (0, len(novo))
    assert not velho.exists() and not velho.parent.exists()


def test_auditoria_do_lake_particionado(raw: Path, tmp_path: Path) -> None:
    # O lake_audit espera <fonte>/<pasta>/<arquivo> sob o diretório de entrada.
    entrada = tmp_path / "entrada"
    shutil.copytree(raw, entrada / "sigtap")
    lake = tmp_path / "lake"
    res = converter.convert(entrada / "sigtap", lake)
    assert not res.errors

    report = lake_audit(lake, input_dir=entrada, converters={}, rehash=True)

    assert report.ok, report.to_text()


def test_auditoria_do_lake_migrado(
    raw: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    entrada = tmp_path / "entrada"
    shutil.copytree(raw, entrada / "sigtap")
    lake = tmp_path / "lake"
    _legacy_convert(entrada / "sigtap", lake, monkeypatch)
    converter.convert(entrada / "sigtap", lake)

    report = lake_audit(lake, input_dir=entrada, converters={}, rehash=True)

    assert report.ok, report.to_text()


def test_rodape_da_particao_nova(raw: Path, tmp_path: Path) -> None:
    converter.convert(raw, tmp_path / "lake")
    arquivo = (
        tmp_path / "lake/sigtap/tb_grupo/ano=2026/mes=11/"
        "TabelaUnificada_202611_v2611011000.parquet"
    )
    meta = pq.ParquetFile(arquivo).metadata.metadata
    assert meta[b"quantilica.dataset_id"] == b"tb_grupo"
    assert "competencia" in pq.ParquetFile(arquivo).schema_arrow.names


def test_pasta_antiga_de_competencia_fora_da_visao_e_erro_e_nao_e_apagada(
    raw: Path, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    lake = tmp_path / "lake"
    _legacy_convert(raw, lake, monkeypatch)
    # A competência 200801 sai do bruto antes da reconversão.
    for z in raw.glob("tabelas/TabelaUnificada_200801*.zip"):
        z.unlink()

    res = converter.convert(raw, lake)

    antigas = sorted((lake / "sigtap").glob("*/competencia=200801"))
    assert len(antigas) == 5  # as 5 tabelas da fixture
    assert all(list(p.glob("*.parquet")) for p in antigas)  # nada foi apagado
    assert len(res.errors) == 5
    for pasta in antigas:
        erro = next(e for e in res.errors if str(pasta) in e)
        assert "fora do bruto visto" in erro and f"sigtap/{pasta.parent.name}" in erro
    # as demais competências migraram normalmente
    assert not list((lake / "sigtap").glob("*/competencia=2026*"))
    assert not list((lake / "sigtap").glob("*/competencia=201605"))


def test_pasta_antiga_de_tabela_sem_layout_e_relatada(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    from .test_lake import _zip

    raw = tmp_path / "raw" / "tabelas"
    raw.mkdir(parents=True)
    layout = "Coluna,Tamanho,Inicio,Fim,Tipo\nCO_A,2,1,2,VARCHAR2\n"
    zip_path = raw / "TabelaUnificada_202610@20261101.zip"
    _zip(zip_path, {"tb_grupo": (layout, "01\n"), "tb_vazia": (layout, "")})
    lake = tmp_path / "lake"
    _legacy_convert(tmp_path / "raw", lake, monkeypatch)
    # Reconversão com um ZIP em que tb_grupo perdeu o layout e a tabela vazia segue
    # vazia: as pastas antigas ficam, com o motivo.
    with zipfile.ZipFile(zip_path, "w") as zf:
        zf.writestr("tb_grupo.txt", b"01\n")
        zf.writestr("tb_vazia_layout.txt", layout)
        zf.writestr("tb_vazia.txt", b"")

    res = converter.convert(tmp_path / "raw", lake)

    por_tabela = {
        t: [e for e in res.errors if f"sigtap/{t}:" in e] for t in ("tb_grupo",)
    }
    assert any("sem arquivo de layout" in e for e in por_tabela["tb_grupo"])
    assert (lake / "sigtap/tb_grupo/competencia=202610").is_dir()
