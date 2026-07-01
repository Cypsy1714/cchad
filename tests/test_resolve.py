from __future__ import annotations

from cchad.models import BaseConfig, Config, Kind, Package, Policy, Scope, StackDescriptor
from cchad.resolve import resolve


def _ids(plan):
    return {s.package.id for s in plan.selections}


def _skips(plan):
    return {s.id: s.reason for s in plan.skips}


def test_base_only_on_empty_stack(catalog):
    plan = resolve(catalog, StackDescriptor(), Config())
    assert _ids(plan) == {
        "context7",
        "github-mcp",
        "chrome-devtools-mcp",
        "superpowers",
        "karpathy-claude-md",
    }
    assert not plan.skips


def test_rules_add_project_layer(catalog):
    stack = StackDescriptor(databases={"mongodb"}, frameworks={"react"})
    plan = resolve(catalog, stack, Config())
    assert {"mongodb-mcp", "react-patterns-skill"} <= _ids(plan)


def test_scopes_follow_default_scope(catalog):
    plan = resolve(catalog, StackDescriptor(databases={"mongodb"}), Config())
    scope = {s.package.id: s.scope for s in plan.selections}
    assert scope["github-mcp"] == Scope.user
    assert scope["context7"] == Scope.project
    assert scope["mongodb-mcp"] == Scope.project


def test_single_spine_drops_extras(catalog):
    catalog.packages["other-spine"] = Package(
        id="other-spine", kind=Kind.spine, name="Other", default_scope=Scope.user, priority=10
    )
    config = Config(base=BaseConfig(preset="recommended", enable=["other-spine"]))
    plan = resolve(catalog, StackDescriptor(), config)
    assert "superpowers" in _ids(plan)
    assert "other-spine" in _skips(plan)


def test_single_browser_keeps_policy_choice(catalog):
    config = Config(base=BaseConfig(preset="recommended", enable=["playwright-mcp"]))
    plan = resolve(catalog, StackDescriptor(), config)
    assert "chrome-devtools-mcp" in _ids(plan)
    assert "playwright-mcp" in _skips(plan)
    assert "browser" in _skips(plan)["playwright-mcp"]


def test_explicit_conflict_drops_lower_priority(catalog):
    catalog.packages["tool-a"] = Package(
        id="tool-a", kind=Kind.mcp, name="A", priority=100, conflicts_with=("tool-b",)
    )
    catalog.packages["tool-b"] = Package(id="tool-b", kind=Kind.mcp, name="B", priority=1)
    config = Config(base=BaseConfig(preset="minimal", enable=["tool-a", "tool-b"]))
    plan = resolve(catalog, StackDescriptor(), config)
    assert "tool-a" in _ids(plan)
    assert "tool-b" in _skips(plan)


def test_mcp_cap_drops_lowest_priority(catalog):
    config = Config(base=BaseConfig(preset="minimal"), policy=Policy(max_mcp_servers=1))
    plan = resolve(catalog, StackDescriptor(), config)
    # minimal has context7 (80) and github-mcp (70); cap keeps the higher one.
    assert "context7" in _ids(plan)
    assert "github-mcp" in _skips(plan)
    assert "cap" in _skips(plan)["github-mcp"]


def test_unknown_base_id_is_skipped(catalog):
    config = Config(base=BaseConfig(preset="minimal", enable=["ghost"]))
    plan = resolve(catalog, StackDescriptor(), config)
    assert _skips(plan).get("ghost") == "not found in catalog"


def test_resolution_is_deterministic(catalog):
    stack = StackDescriptor(databases={"mongodb", "postgres"}, frameworks={"react"})
    first = [s.package.id for s in resolve(catalog, stack, Config()).selections]
    second = [s.package.id for s in resolve(catalog, stack, Config()).selections]
    assert first == second


def test_language_skills_fire(catalog):
    stack = StackDescriptor(languages={"python", "go"})
    plan = resolve(catalog, stack, Config(base=BaseConfig(preset="minimal")))
    assert {"python-skill", "go-skill"} <= _ids(plan)


def test_javascript_skill_suppressed_by_typescript(catalog):
    minimal = Config(base=BaseConfig(preset="minimal"))
    ts = resolve(catalog, StackDescriptor(languages={"javascript", "typescript"}), minimal)
    js = resolve(catalog, StackDescriptor(languages={"javascript"}), minimal)
    assert "typescript-skill" in _ids(ts)
    assert "javascript-skill" not in _ids(ts)  # unless: [typescript]
    assert "javascript-skill" in _ids(js)
