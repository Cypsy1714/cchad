from __future__ import annotations

import json

import pytest

from cchad.sync import SyncError, sync

MANIFEST = """---
cchad_version: 0.1.0
generated: 2026-07-01
stack: [react, mongodb]
tools:
- id: context7
  kind: mcp
  source: npx -y @upstash/context7-mcp
  scope: project
- id: react-patterns-skill
  kind: skill
  source: bundled:react-patterns-skill
  scope: project
skipped: []
---

body
"""


def test_sync_reproduces_config(catalog, tmp_path, home):
    repo = tmp_path / "clone"
    repo.mkdir()
    (repo / "auto_plugins_mcps.md").write_text(MANIFEST)
    result, _ = sync(repo, catalog, home=home)
    data = json.loads((repo / ".mcp.json").read_text())
    assert "context7" in data["mcpServers"]
    assert (repo / ".claude" / "skills" / "react-patterns-skill" / "SKILL.md").exists()
    assert result.written


def test_sync_without_manifest_raises(catalog, tmp_path, home):
    with pytest.raises(SyncError):
        sync(tmp_path / "empty", catalog, home=home)


def test_sync_reconstructs_unknown_tool(catalog, tmp_path, home):
    repo = tmp_path / "clone"
    repo.mkdir()
    (repo / "auto_plugins_mcps.md").write_text(
        "---\n"
        "cchad_version: 0.1.0\n"
        "generated: 2026-07-01\n"
        "stack: []\n"
        "tools:\n"
        "- id: mystery-mcp\n"
        "  kind: mcp\n"
        "  source: npx -y mystery\n"
        "  scope: project\n"
        "skipped: []\n"
        "---\n\nbody\n"
    )
    sync(repo, catalog, home=home)
    data = json.loads((repo / ".mcp.json").read_text())
    assert data["mcpServers"]["mystery-mcp"] == {"command": "npx", "args": ["-y", "mystery"]}
