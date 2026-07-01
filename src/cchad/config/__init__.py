"""Read and write ~/.config/cchad/config.toml — the user's base choices and
policy. A missing file simply yields the default Config.
"""

from __future__ import annotations

import tomllib
from pathlib import Path
from typing import Any

import tomli_w

from cchad.apply.atomic import atomic_write_text
from cchad.models import BaseConfig, Config, Policy
from cchad.paths import config_path


def load_config(path: Path | None = None) -> Config:
    path = path or config_path()
    if not path.is_file():
        return Config()
    data = tomllib.loads(path.read_text(encoding="utf-8"))
    return _config_from_dict(data)


def save_config(config: Config, path: Path | None = None) -> None:
    path = path or config_path()
    atomic_write_text(path, tomli_w.dumps(_config_to_dict(config)))


def _config_from_dict(data: dict[str, Any]) -> Config:
    base = data.get("base", {}) or {}
    policy = data.get("policy", {}) or {}
    catalog = data.get("catalog", {}) or {}
    return Config(
        base=BaseConfig(
            preset=base.get("preset", "recommended"),
            enable=list(base.get("enable", [])),
            disable=list(base.get("disable", [])),
        ),
        policy=Policy(
            max_mcp_servers=int(policy.get("max_mcp_servers", 5)),
            browser=policy.get("browser", "chrome-devtools-mcp"),
            spine=policy.get("spine", "superpowers"),
        ),
        catalog_sources=list(catalog.get("sources", [])),
    )


def _config_to_dict(config: Config) -> dict[str, Any]:
    policy: dict[str, Any] = {"max_mcp_servers": config.policy.max_mcp_servers}
    if config.policy.browser is not None:
        policy["browser"] = config.policy.browser
    if config.policy.spine is not None:
        policy["spine"] = config.policy.spine
    return {
        "base": {
            "preset": config.base.preset,
            "enable": config.base.enable,
            "disable": config.base.disable,
        },
        "policy": policy,
        "catalog": {"sources": config.catalog_sources},
    }
