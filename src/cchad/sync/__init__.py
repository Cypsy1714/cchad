"""Rebuild a repo's local Claude Code config from its committed manifest.

sync is how a teammate onboards: it reads ``auto_plugins_mcps.md`` and applies
exactly what it records — no re-detection, no re-resolution. The manifest is the
source of truth. Where the local catalog knows a tool (by id) its richer
definition is used, so bundled skills and CLAUDE.md blocks install fully.
"""

from __future__ import annotations

from pathlib import Path

from cchad.apply import ApplyResult, apply_selections
from cchad.apply.atomic import Journal
from cchad.catalog import Catalog
from cchad.manifest import read_manifest
from cchad.models import InstallMethod, Kind, ManifestTool, Package, Scope, Selection


class SyncError(Exception):
    pass


def _install_method_for(tool: ManifestTool) -> InstallMethod:
    if tool.source.startswith("plugin:") or tool.kind == Kind.spine:
        return InstallMethod.plugin
    if tool.kind == Kind.claude_md:
        return InstallMethod.claude_md_block
    if tool.kind == Kind.skill:
        return InstallMethod.skill_dir
    return InstallMethod.mcp_json


def _package_for(tool: ManifestTool, catalog: Catalog) -> Package:
    known = catalog.get(tool.id)
    if known is not None:
        return known
    return Package(
        id=tool.id,
        kind=tool.kind,
        name=tool.id,
        source=tool.source,
        install_method=_install_method_for(tool),
        default_scope=tool.scope,
    )


def sync(
    repo_root: Path,
    catalog: Catalog,
    *,
    home: Path,
    journal: Journal | None = None,
) -> tuple[ApplyResult, Journal]:
    """Apply the committed manifest at ``repo_root`` to local disk."""
    repo_root = Path(repo_root)
    manifest = read_manifest(repo_root / "auto_plugins_mcps.md")
    if manifest is None:
        raise SyncError("no auto_plugins_mcps.md found — nothing to sync")

    journal = journal or Journal()
    selections = [
        Selection(
            package=_package_for(tool, catalog),
            scope=tool.scope or Scope.project,
            reason="from manifest",
        )
        for tool in manifest.tools
    ]
    result = apply_selections(selections, repo_root=repo_root, home=home, journal=journal)
    return result, journal
