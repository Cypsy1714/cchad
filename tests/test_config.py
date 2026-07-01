from __future__ import annotations

from cchad.config import load_config, save_config
from cchad.models import BaseConfig, Config, Policy


def test_missing_config_returns_defaults(tmp_path):
    config = load_config(tmp_path / "config.toml")
    assert config.base.preset == "recommended"
    assert config.policy.max_mcp_servers == 5


def test_save_then_load_round_trips(tmp_path):
    path = tmp_path / "config.toml"
    config = Config(
        base=BaseConfig(preset="full", enable=["playwright-mcp"], disable=["chrome-devtools-mcp"]),
        policy=Policy(max_mcp_servers=3, browser="playwright-mcp", spine="superpowers"),
        catalog_sources=["~/team.yaml"],
    )
    save_config(config, path)
    loaded = load_config(path)
    assert loaded.base.preset == "full"
    assert loaded.base.enable == ["playwright-mcp"]
    assert loaded.base.disable == ["chrome-devtools-mcp"]
    assert loaded.policy.max_mcp_servers == 3
    assert loaded.policy.browser == "playwright-mcp"
    assert loaded.catalog_sources == ["~/team.yaml"]


def test_save_omits_none_policy_values(tmp_path):
    path = tmp_path / "config.toml"
    save_config(Config(policy=Policy(browser=None, spine=None)), path)
    text = path.read_text()
    assert "browser" not in text
    assert "spine" not in text
