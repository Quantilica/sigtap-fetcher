"""O build do lake pula, sem abrir o ZIP, o que ja esta em dia."""

from __future__ import annotations

import builtins
import hashlib
import io
import json
import zipfile
from pathlib import Path

import pytest
import quantilica.core.manifests as manifests_mod

from sigtap_fetcher.lake import converter

_LAYOUT = "Coluna,Tamanho,Inicio,Fim,Tipo\nCO_GRUPO,2,1,2,VARCHAR2\n"
_LAYOUT_B = "Coluna,Tamanho,Inicio,Fim,Tipo\nCO_B,2,1,2,VARCHAR2\n"


def _zip(path: Path, tabelas: dict[str, str]) -> None:
    with zipfile.ZipFile(path, "w") as zf:
        for nome, layout in tabelas.items():
            zf.writestr(f"{nome}_layout.txt", layout)
            zf.writestr(f"{nome}.txt", b"01\n02\n")


def _bruto(tmp_path: Path) -> Path:
    raw = tmp_path / "raw"
    pasta = raw / "tabelas"
    pasta.mkdir(parents=True)
    # 202601 e 202602 tem as duas tabelas; 202512 (antigo) so tem tb_grupo.
    _zip(pasta / "TabelaUnificada_202512@20260101.zip", {"tb_grupo": _LAYOUT})
    for comp in ("202601", "202602"):
        _zip(
            pasta / f"TabelaUnificada_{comp}@20260301.zip",
            {"tb_grupo": _LAYOUT, "tb_b": _LAYOUT_B},
        )
    _sidecars(raw)
    return raw


def _sidecars(raiz: Path) -> None:
    """Sidecar ``.manifest.json`` com o sha256 de cada bruto, como o fetcher grava:
    o hash do bruto sai dele, sem ler o arquivo."""
    for f in sorted(raiz.rglob("*")):
        if f.is_file() and not f.name.endswith(".manifest.json"):
            Path(f"{f}.manifest.json").write_text(
                json.dumps(
                    {
                        "sha256": hashlib.sha256(f.read_bytes()).hexdigest(),
                        "size_bytes": f.stat().st_size,
                    }
                ),
                encoding="utf-8",
            )


@pytest.fixture
def bruto_lido(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Registra todo ``open``/``io.open``/``Path.open`` de arquivo do bruto (menos o
    sidecar, lido de propósito) e todo hash do bruto feito lendo o arquivo."""
    vistas: list[str] = []
    original_open = builtins.open
    original_io_open = io.open
    original_path_open = Path.open
    original_hash = manifests_mod.sha256_file

    def do_bruto(arquivo) -> bool:  # noqa: ANN001
        nome = str(arquivo)
        return "/raw/" in nome and not nome.endswith(".manifest.json")

    def open_espia(file, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if do_bruto(file):
            vistas.append(f"open:{Path(file).name}")
        return original_open(file, *args, **kwargs)

    def io_open_espia(file, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if do_bruto(file):
            vistas.append(f"io.open:{Path(file).name}")
        return original_io_open(file, *args, **kwargs)

    def path_open_espia(self, *args, **kwargs):  # noqa: ANN001, ANN002, ANN003, ANN202
        if do_bruto(self):
            vistas.append(f"Path.open:{self.name}")
        return original_path_open(self, *args, **kwargs)

    def hash_espia(*args, **kwargs):  # noqa: ANN002, ANN003, ANN202
        vistas.append("hash")
        return original_hash(*args, **kwargs)

    monkeypatch.setattr(builtins, "open", open_espia)
    monkeypatch.setattr(io, "open", io_open_espia)
    monkeypatch.setattr(Path, "open", path_open_espia)
    monkeypatch.setattr(manifests_mod, "sha256_file", hash_espia)
    return vistas


@pytest.fixture
def aberturas(monkeypatch: pytest.MonkeyPatch) -> list[str]:
    """Registra cada ``zipfile.ZipFile`` aberto em modo de leitura."""
    abertos: list[str] = []
    original = zipfile.ZipFile

    def espia(file, mode="r", *args, **kwargs):  # noqa: ANN001, ANN002, ANN003
        if mode == "r":
            abertos.append(Path(file).name)
        return original(file, mode, *args, **kwargs)

    monkeypatch.setattr(zipfile, "ZipFile", espia)
    return abertos


def test_segunda_rodada_por_tabela_nao_abre_zip(
    tmp_path: Path, aberturas: list[str], bruto_lido: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    res = converter.convert(raw, lake, datasets=["tb_b"])
    assert not res.errors
    assert res.converted == 2 and res.skipped == 0
    # 3 zips: o de 202512 nao tem tb_b, mas e aberto para descobrir isso
    assert len(aberturas) == 3

    aberturas.clear()
    bruto_lido.clear()
    res2 = converter.convert(raw, lake, datasets=["tb_b"])
    assert res2.converted == 0 and res2.skipped == 2
    assert not res2.errors
    # so o ZIP sem a tabela e reaberto; os dois em dia nao
    assert aberturas == ["TabelaUnificada_202512@20260101.zip"]
    assert "hash" not in bruto_lido
    assert all("202512" in v for v in bruto_lido)


def test_tabela_presente_em_todos_os_zips_nao_abre_nenhum(
    tmp_path: Path, aberturas: list[str], bruto_lido: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    res = converter.convert(raw, lake, datasets=["tb_grupo"])
    assert res.converted == 3

    aberturas.clear()
    bruto_lido.clear()
    res2 = converter.convert(raw, lake, datasets=["tb_grupo"])
    assert (res2.converted, res2.skipped, res2.errors) == (0, 3, [])
    assert aberturas == []
    assert bruto_lido == []


def test_varias_tabelas_alvo_so_pula_se_todas_em_dia(
    tmp_path: Path, aberturas: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["tb_grupo"])

    aberturas.clear()
    res = converter.convert(raw, lake, datasets=["tb_grupo", "tb_b"])
    # tb_grupo em dia (3 pulos); tb_b converte nos 2 zips que a tem
    assert (res.converted, res.skipped, res.errors) == (2, 3, [])
    assert len(aberturas) == 3  # nenhum zip tinha ambas em dia

    aberturas.clear()
    res2 = converter.convert(raw, lake, datasets=["tb_grupo", "tb_b"])
    assert (res2.converted, res2.skipped) == (0, 5)
    assert aberturas == ["TabelaUnificada_202512@20260101.zip"]


def test_force_abre_e_reconverte(tmp_path: Path, aberturas: list[str]) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["tb_grupo"])

    aberturas.clear()
    res = converter.convert(raw, lake, datasets=["tb_grupo"], force=True)
    assert (res.converted, res.skipped) == (3, 0)
    assert len(aberturas) == 3


def test_zip_novo_e_aberto_e_os_demais_nao(
    tmp_path: Path, aberturas: list[str], bruto_lido: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["tb_grupo"])
    _zip(
        raw / "tabelas" / "TabelaUnificada_202603@20260401.zip",
        {"tb_grupo": _LAYOUT},
    )
    _sidecars(raw)

    aberturas.clear()
    bruto_lido.clear()
    res = converter.convert(raw, lake, datasets=["tb_grupo"])
    assert (res.converted, res.skipped, res.errors) == (1, 3, [])
    assert aberturas == ["TabelaUnificada_202603@20260401.zip"]
    assert "hash" not in bruto_lido
    assert all("202603" in v for v in bruto_lido)


def test_sem_datasets_continua_abrindo_todos(
    tmp_path: Path, aberturas: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake)

    aberturas.clear()
    res = converter.convert(raw, lake)
    assert (res.converted, res.skipped) == (0, 5)
    assert len(aberturas) == 3


def test_pasta_legada_com_zip_pulado_nao_diz_tabela_fora_do_zip(
    tmp_path: Path, aberturas: list[str]
) -> None:
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["tb_grupo"])
    # pasta do layout antigo com um arquivo alheio: nao e apagada
    legado = lake / "sigtap" / "tb_grupo" / "competencia=202601"
    legado.mkdir()
    (legado / "nota.txt").write_text("alheio")

    aberturas.clear()
    res = converter.convert(raw, lake, datasets=["tb_grupo"])
    assert aberturas == []
    assert res.converted == 0 and res.skipped == 3
    assert len(res.errors) == 1
    assert "nao e Parquet deste dataset" in res.errors[0]
    assert "nao esta no ZIP" not in res.errors[0]


def test_sem_sidecar_o_espiao_de_hash_dispara(
    tmp_path: Path, aberturas: list[str], bruto_lido: list[str]
) -> None:
    # Prova de que o espião funciona: sem sidecar o bruto é hasheado lendo-o.
    raw, lake = _bruto(tmp_path), tmp_path / "lake"
    converter.convert(raw, lake, datasets=["tb_grupo"])
    for sidecar in raw.rglob("*.manifest.json"):
        sidecar.unlink()
    bruto_lido.clear()
    converter.convert(raw, lake, datasets=["tb_grupo"])
    assert "hash" in bruto_lido
