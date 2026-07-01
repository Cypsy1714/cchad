"""Well-known filesystem locations. Only the CLI resolves these; the core
functions always take explicit paths so they stay easy to test.
"""

from __future__ import annotations

import os
from pathlib import Path

MANIFEST_NAME = "auto_plugins_mcps.md"


def user_home() -> Path:
    return Path.home()


def config_dir() -> Path:
    base = os.environ.get("XDG_CONFIG_HOME")
    root = Path(base) if base else user_home() / ".config"
    return root / "cchad"


def config_path() -> Path:
    return config_dir() / "config.toml"


def journal_path() -> Path:
    return config_dir() / "rollback.json"


def manifest_path(repo_root: Path | str) -> Path:
    return Path(repo_root) / MANIFEST_NAME
