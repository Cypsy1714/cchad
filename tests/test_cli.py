from __future__ import annotations

import json

from typer.testing import CliRunner

from cchad import __version__
from cchad.cli import app

runner = CliRunner()


def _repo(tmp_path, monkeypatch, **deps):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "package.json").write_text(json.dumps({"dependencies": deps}))
    monkeypatch.chdir(repo)
    return repo


def test_version():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_plan_json(isolated_home, tmp_path, monkeypatch):
    _repo(tmp_path, monkeypatch, react="^18", mongoose="^8")
    result = runner.invoke(app, ["plan", "--json"])
    assert result.exit_code == 0
    payload = json.loads(result.output)
    ids = {item["id"] for item in payload["add"]}
    assert {"mongodb-mcp", "react-patterns-skill"} <= ids


def test_init_writes_and_is_idempotent(isolated_home, tmp_path, monkeypatch):
    repo = _repo(tmp_path, monkeypatch, react="^18", mongoose="^8")
    result = runner.invoke(app, ["init", "--yes"])
    assert result.exit_code == 0
    assert (repo / "auto_plugins_mcps.md").exists()
    assert (repo / ".mcp.json").exists()

    again = runner.invoke(app, ["plan"])
    assert again.exit_code == 0
    assert "up to date" in again.output


def test_setup_writes_config(isolated_home):
    result = runner.invoke(app, ["setup", "--preset", "minimal", "--yes"])
    assert result.exit_code == 0
    config = isolated_home / ".config" / "cchad" / "config.toml"
    assert config.exists()
    assert "minimal" in config.read_text()


def test_rollback_undoes_init(isolated_home, tmp_path, monkeypatch):
    repo = _repo(tmp_path, monkeypatch, react="^18")
    runner.invoke(app, ["init", "--yes"])
    assert (repo / ".mcp.json").exists()
    result = runner.invoke(app, ["rollback"])
    assert result.exit_code == 0
    assert not (repo / ".mcp.json").exists()


def test_unknown_add_errors(isolated_home, tmp_path, monkeypatch):
    _repo(tmp_path, monkeypatch, react="^18")
    runner.invoke(app, ["init", "--yes"])
    result = runner.invoke(app, ["add", "no-such-package"])
    assert result.exit_code == 1
