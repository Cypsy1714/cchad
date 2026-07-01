from __future__ import annotations

import pytest

from cchad.manifest import (
    ManifestError,
    diff_plan,
    parse_manifest,
    read_manifest,
    render,
)
from cchad.models import Config, Scope, StackDescriptor
from cchad.resolve import resolve


def _plan(catalog):
    stack = StackDescriptor(databases={"mongodb"}, frameworks={"react"})
    return resolve(catalog, stack, Config())


def test_render_then_parse_round_trips(catalog):
    plan = _plan(catalog)
    text = render(plan, version="0.1.0", generated="2026-07-01")
    manifest = parse_manifest(text)
    assert manifest.cchad_version == "0.1.0"
    assert "mongodb" in manifest.stack
    tool_ids = {t.id for t in manifest.tools}
    project_ids = {s.package.id for s in plan.for_scope(Scope.project)}
    assert tool_ids == project_ids
    assert all(t.scope == Scope.project for t in manifest.tools)


def test_diff_reports_no_changes_against_own_manifest(catalog):
    plan = _plan(catalog)
    manifest = parse_manifest(render(plan, version="0.1.0", generated="2026-07-01"))
    diff = diff_plan(plan, manifest)
    assert not diff.has_changes
    assert diff.unchanged


def test_diff_detects_added_and_removed(catalog):
    plan = _plan(catalog)
    manifest = parse_manifest(render(plan, version="0.1.0", generated="2026-07-01"))
    manifest.tools = [t for t in manifest.tools if t.id != "mongodb-mcp"]
    diff = diff_plan(plan, manifest)
    assert "mongodb-mcp" in diff.added


def test_parse_requires_frontmatter():
    with pytest.raises(ManifestError):
        parse_manifest("# just a heading\n")


def test_read_manifest_missing_returns_none(tmp_path):
    assert read_manifest(tmp_path / "auto_plugins_mcps.md") is None


def test_body_lists_installed_and_skipped(catalog):
    text = render(_plan(catalog), version="0.1.0", generated="2026-07-01")
    assert "## Installed" in text
    assert "mongodb-mcp" in text
