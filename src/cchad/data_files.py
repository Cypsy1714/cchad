"""Locate files that ship inside the package (catalog, presets, rules, blocks,
skills). cchad is installed unzipped, so the data directory sits next to the
package modules on disk.
"""

from __future__ import annotations

from pathlib import Path

import cchad

DATA_DIR = Path(cchad.__file__).resolve().parent / "data"


def data_path(*parts: str) -> Path:
    """Return the on-disk path of a shipped data file or directory."""
    return DATA_DIR.joinpath(*parts)


def data_text(*parts: str) -> str:
    """Read a shipped data file as UTF-8 text."""
    return data_path(*parts).read_text(encoding="utf-8")
