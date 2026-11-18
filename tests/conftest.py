"""Pytest configuration and fixtures for sigtap-fetcher."""

from __future__ import annotations

import builtins
import io
import zipfile
from pathlib import Path

import pytest
import quantilica.core.manifests as manifests_mod


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
