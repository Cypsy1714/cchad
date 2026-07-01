from __future__ import annotations

import json

import pytest

from cchad.apply import (
    ApplyError,
    apply_selections,
    mcp_server_entry,
    remove_block,
    remove_from_disk,
    upsert_block,
)
from cchad.apply.atomic import Journal
from cchad.models import Kind, ManifestTool, Scope, Selection


def _select(catalog, package_id, scope):
    return Selection(package=catalog.get(package_id), scope=scope, reason="test")


def test_mcp_server_entry_command():
    assert mcp_server_entry("npx -y @upstash/context7-mcp") == {
        "command": "npx",
        "args": ["-y", "@upstash/context7-mcp"],
    }


def test_mcp_server_entry_http():
    assert mcp_server_entry("https://api.example.com/mcp") == {
        "type": "http",
        "url": "https://api.example.com/mcp",
    }


def test_apply_mcp_merges_and_backs_up(catalog, tmp_path, home):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".mcp.json").write_text(json.dumps({"mcpServers": {"keep": {"command": "x"}}, "z": 1}))
    journal = Journal()
    apply_selections(
        [_select(catalog, "context7", Scope.project)], repo_root=repo, home=home, journal=journal
    )
    data = json.loads((repo / ".mcp.json").read_text())
    assert data["z"] == 1  # unrelated keys preserved
    assert set(data["mcpServers"]) == {"keep", "context7"}
    assert (repo / ".mcp.json.bak").exists()


def test_apply_claude_md_is_idempotent(catalog, home):
    selections = [_select(catalog, "karpathy-claude-md", Scope.user)]
    apply_selections(selections, repo_root=None, home=home, journal=Journal())
    path = home / ".claude" / "CLAUDE.md"
    first = path.read_text()
    apply_selections(selections, repo_root=None, home=home, journal=Journal())
    second = path.read_text()
    assert first == second
    assert second.count("cchad:begin karpathy-claude-md") == 1


def test_apply_bundled_skill(catalog, tmp_path, home):
    repo = tmp_path / "repo"
    repo.mkdir()
    apply_selections(
        [_select(catalog, "react-patterns-skill", Scope.project)],
        repo_root=repo,
        home=home,
        journal=Journal(),
    )
    skill = repo / ".claude" / "skills" / "react-patterns-skill" / "SKILL.md"
    assert skill.exists()
    assert "React patterns" in skill.read_text()


def test_plugin_becomes_manual_step(catalog, home):
    result = apply_selections(
        [_select(catalog, "superpowers", Scope.user)], repo_root=None, home=home, journal=Journal()
    )
    assert result.written == []
    assert any("superpowers" in step for step in result.manual_steps)


def test_corrupt_mcp_json_raises(catalog, tmp_path, home):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".mcp.json").write_text("{ not valid json")
    with pytest.raises(ApplyError):
        apply_selections(
            [_select(catalog, "context7", Scope.project)],
            repo_root=repo,
            home=home,
            journal=Journal(),
        )


def test_rollback_removes_new_and_restores_modified(catalog, tmp_path, home):
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / ".mcp.json").write_text(json.dumps({"mcpServers": {"orig": {"command": "x"}}}))
    journal = Journal()
    apply_selections(
        [
            _select(catalog, "context7", Scope.project),
            _select(catalog, "react-patterns-skill", Scope.project),
        ],
        repo_root=repo,
        home=home,
        journal=journal,
    )
    skill = repo / ".claude" / "skills" / "react-patterns-skill" / "SKILL.md"
    assert skill.exists()
    journal.rollback()
    assert json.loads((repo / ".mcp.json").read_text())["mcpServers"] == {"orig": {"command": "x"}}
    assert not skill.exists()


def test_remove_from_disk(catalog, tmp_path, home):
    repo = tmp_path / "repo"
    repo.mkdir()
    apply_selections(
        [
            _select(catalog, "context7", Scope.project),
            _select(catalog, "react-patterns-skill", Scope.project),
        ],
        repo_root=repo,
        home=home,
        journal=Journal(),
    )
    tools = [
        ManifestTool(id="context7", kind=Kind.mcp, source="x", scope=Scope.project),
        ManifestTool(id="react-patterns-skill", kind=Kind.skill, source="x", scope=Scope.project),
    ]
    remove_from_disk(tools, repo_root=repo, home=home, journal=Journal())
    assert json.loads((repo / ".mcp.json").read_text())["mcpServers"] == {}
    assert not (repo / ".claude" / "skills" / "react-patterns-skill").exists()


def test_upsert_and_remove_block():
    text = upsert_block("", "demo", "hello")
    assert "cchad:begin demo" in text and "hello" in text
    text = upsert_block(text, "demo", "world")
    assert text.count("cchad:begin demo") == 1
    assert "world" in text and "hello" not in text
    assert "cchad:begin demo" not in remove_block(text, "demo")
