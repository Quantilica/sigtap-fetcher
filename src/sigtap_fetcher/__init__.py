"""Coletor e conversor Lake Hive do SIGTAP (SUS)."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("sigtap-fetcher")
except PackageNotFoundError:
    __version__ = "0.0.0"

__all__ = ["__version__"]
