"""Turn resolved selections into real files on disk.

Routing by install method and scope:
  mcp_json        project -> <repo>/.mcp.json          user -> ~/.claude.json
  claude_md_block project -> <repo>/CLAUDE.md          user -> ~/.claude/CLAUDE.md
  skill_dir       project -> <repo>/.claude/skills/    user -> ~/.claude/skills/
  plugin          not written automatically -> reported as a manual step

Plugins are never auto-installed: cchad only writes config and never runs an
untrusted install script. The caller gets the exact command to run instead.
"""

from __future__ import annotations

import json
import shlex
from dataclasses import dataclass, field
from pathlib import Path

from cchad.data_files import data_path, data_text
from cchad.models import InstallMethod, Package, Scope, Selection

from .atomic import Journal

__all__ = ["ApplyError", "ApplyResult", "apply_selections", "mcp_server_entry"]


class ApplyError(Exception):
    """Raised when apply cannot safely proceed (e.g. corrupt existing config)."""


@dataclass
class ApplyResult:
    written: list[str] = field(default_factory=list)
    manual_steps: list[str] = field(default_factory=list)


def mcp_server_entry(source: str) -> dict:
    """Convert a catalog source string into a .mcp.json server entry."""
    source = source.strip()
    if source.startswith(("http://", "https://")):
        return {"type": "http", "url": source}
    parts = shlex.split(source)
    if not parts:
        raise ApplyError(f"empty MCP source: {source!r}")
    return {"command": parts[0], "args": parts[1:]}


def _mcp_json_path(scope: Scope, repo_root: Path | None, home: Path) -> Path | None:
    if scope == Scope.project:
        return repo_root / ".mcp.json" if repo_root else None
    return home / ".claude.json"


def _claude_md_path(scope: Scope, repo_root: Path | None, home: Path) -> Path | None:
    if scope == Scope.project:
        return repo_root / "CLAUDE.md" if repo_root else None
    return home / ".claude" / "CLAUDE.md"


def _skills_root(scope: Scope, repo_root: Path | None, home: Path) -> Path | None:
    if scope == Scope.project:
        return repo_root / ".claude" / "skills" if repo_root else None
    return home / ".claude" / "skills"


def _read_json(path: Path) -> dict:
    if not path.exists():
        return {}
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ApplyError(f"{path} is not valid JSON; fix or remove it and retry ({exc})") from exc
    if not isinstance(data, dict):
        raise ApplyError(f"{path} must contain a JSON object")
    return data


def _write_mcp_json(path: Path, selections: list[Selection], journal: Journal) -> None:
    data = _read_json(path)
    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        servers = {}
    for selection in selections:
        servers[selection.package.id] = mcp_server_entry(selection.package.source)
    data["mcpServers"] = servers
    journal.write_text(path, json.dumps(data, indent=2) + "\n")


def _block_markers(block_id: str) -> tuple[str, str]:
    return f"<!-- cchad:begin {block_id} -->", f"<!-- cchad:end {block_id} -->"


def upsert_block(text: str, block_id: str, content: str) -> str:
    """Insert or replace an id-fenced block, leaving the rest of the file intact."""
    begin, end = _block_markers(block_id)
    block = f"{begin}\n{content.strip()}\n{end}"
    start = text.find(begin)
    stop = text.find(end)
    if start != -1 and stop != -1 and stop > start:
        return text[:start] + block + text[stop + len(end) :]
    prefix = "" if not text else text.rstrip("\n") + "\n\n"
    return f"{prefix}{block}\n"


def _claude_md_content(package: Package) -> str:
    if package.source.startswith("bundled:"):
        name = package.source.split(":", 1)[1]
        return data_text("blocks", f"{name}.md")
    return f"## {package.name}\n\n{package.description}\n"


def _write_claude_md(path: Path, selections: list[Selection], journal: Journal) -> None:
    text = path.read_text(encoding="utf-8") if path.exists() else ""
    for selection in selections:
        text = upsert_block(text, selection.package.id, _claude_md_content(selection.package))
    journal.write_text(path, text)


def _skill_stub(package: Package) -> str:
    return (
        f"---\nname: {package.id}\ndescription: {package.description}\n---\n\n"
        f"# {package.name}\n\n{package.description}\n\n"
        f"> Installed by cchad. Populate this skill from its source: {package.source}\n"
    )


def _write_skill(root: Path, package: Package, journal: Journal) -> list[str]:
    target_dir = root / package.id
    written: list[str] = []
    if package.source.startswith("bundled:"):
        name = package.source.split(":", 1)[1]
        source_dir = data_path("skills", name)
        for source_file in sorted(source_dir.rglob("*")):
            if source_file.is_file():
                dest = target_dir / source_file.relative_to(source_dir)
                journal.write_text(dest, source_file.read_text(encoding="utf-8"))
                written.append(str(dest))
    else:
        dest = target_dir / "SKILL.md"
        journal.write_text(dest, _skill_stub(package))
        written.append(str(dest))
    return written


def _plugin_step(package: Package) -> str:
    source = package.source
    if source.startswith("plugin:"):
        body = source[len("plugin:") :]
        if "@" in body:
            name, marketplace = body.split("@", 1)
            return (
                f"Install the '{name}' plugin: add the '{marketplace}' marketplace, "
                f"then run /plugin install {name}@{marketplace}"
            )
        return f"Install the '{body}' plugin via /plugin install {body}"
    return f"Install plugin from source: {source}"


def apply_selections(
    selections: list[Selection],
    *,
    repo_root: Path | None,
    home: Path,
    journal: Journal,
) -> ApplyResult:
    """Write every selection to its target, recording changes in ``journal``."""
    result = ApplyResult()

    mcp: dict[Scope, list[Selection]] = {}
    claude_md: dict[Scope, list[Selection]] = {}
    skills: list[Selection] = []

    for selection in selections:
        method = selection.package.install_method
        if method == InstallMethod.mcp_json:
            mcp.setdefault(selection.scope, []).append(selection)
        elif method == InstallMethod.claude_md_block:
            claude_md.setdefault(selection.scope, []).append(selection)
        elif method == InstallMethod.skill_dir:
            skills.append(selection)
        elif method == InstallMethod.plugin:
            result.manual_steps.append(_plugin_step(selection.package))

    for scope, group in mcp.items():
        path = _mcp_json_path(scope, repo_root, home)
        if path is None:
            continue
        _write_mcp_json(path, group, journal)
        result.written.append(str(path))

    for scope, group in claude_md.items():
        path = _claude_md_path(scope, repo_root, home)
        if path is None:
            continue
        _write_claude_md(path, group, journal)
        result.written.append(str(path))

    for selection in skills:
        root = _skills_root(selection.scope, repo_root, home)
        if root is None:
            continue
        result.written.extend(_write_skill(root, selection.package, journal))

    return result
