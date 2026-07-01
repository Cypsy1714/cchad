from __future__ import annotations

from cchad.catalog import Rule, load_catalog
from cchad.models import Kind


def test_shipped_catalog_has_expected_content(catalog):
    assert "context7" in catalog.packages
    assert catalog.get("superpowers").kind == Kind.spine
    assert set(catalog.presets) == {"minimal", "recommended", "full"}
    assert "context7" in catalog.expand_preset("recommended")
    assert len(catalog.rules) >= 5


def test_rule_matches_requires_all_signals():
    rule = Rule(when=("react", "vite"), recommend=("x",))
    assert rule.matches({"react", "vite", "typescript"})
    assert not rule.matches({"react"})


def test_user_source_overrides_by_id(tmp_path):
    override = tmp_path / "extra.yaml"
    override.write_text(
        "packages:\n"
        "  - id: context7\n"
        "    kind: mcp\n"
        "    name: My Context7\n"
        "    source: npx -y custom\n"
        "presets:\n"
        "  team: [context7]\n"
        "rules:\n"
        "  - when: [svelte]\n"
        "    recommend: [context7]\n"
    )
    catalog = load_catalog(sources=[str(override)])
    assert catalog.get("context7").name == "My Context7"
    assert catalog.expand_preset("team") == ["context7"]
    assert any(r.when == ("svelte",) for r in catalog.rules)


def test_unknown_source_warns_without_crashing():
    warnings: list[str] = []
    catalog = load_catalog(sources=["/no/such/file.yaml"], warn=warnings.append)
    assert catalog.get("context7") is not None  # shipped catalog still loads
    assert warnings and "not found" in warnings[0]


def test_invalid_package_in_source_is_skipped(tmp_path):
    bad = tmp_path / "bad.yaml"
    bad.write_text("packages:\n  - id: broken\n    kind: not-a-kind\n")
    warnings: list[str] = []
    catalog = load_catalog(sources=[str(bad)], warn=warnings.append)
    assert catalog.get("broken") is None
    assert warnings
