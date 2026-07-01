from __future__ import annotations

import json
from collections.abc import Callable
from pathlib import Path

import pytest

from cchad.catalog import Catalog, load_catalog


@pytest.fixture
def catalog() -> Catalog:
    """A fresh shipped catalog per test (safe to mutate)."""
    return load_catalog()


@pytest.fixture
def make_repo(tmp_path: Path) -> Callable[..., Path]:
    """Build a repo directory from name -> content pairs (dicts become JSON)."""

    def _make(**files: object) -> Path:
        root = tmp_path / "repo"
        root.mkdir(exist_ok=True)
        for name, content in files.items():
            path = root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            if isinstance(content, (dict, list)):
                content = json.dumps(content)
            path.write_text(str(content), encoding="utf-8")
        return root

    return _make


@pytest.fixture
def home(tmp_path: Path) -> Path:
    path = tmp_path / "home"
    path.mkdir()
    return path


@pytest.fixture
def isolated_home(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect HOME and XDG_CONFIG_HOME so CLI runs never touch the real home."""
    path = tmp_path / "userhome"
    (path / ".config").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(path))
    monkeypatch.setenv("XDG_CONFIG_HOME", str(path / ".config"))
    return path
