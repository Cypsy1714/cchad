"""Read, write, and diff the committed lockfile ``auto_plugins_mcps.md``.

The file is YAML frontmatter (what apply/sync read) followed by a human-readable
body (what reviewers read in a PR). Rendering is pure so it is easy to test.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from cchad.models import Kind, Manifest, ManifestTool, Plan, Scope, Skip

__all__ = [
    "ManifestError",
    "ManifestDiff",
    "render",
    "parse_manifest",
    "read_manifest",
    "diff_plan",
]

_FRONTMATTER_RE = re.compile(r"^---\n(?P<front>.*?)\n---\n?(?P<body>.*)$", re.DOTALL)


class ManifestError(Exception):
    pass


@dataclass
class ManifestDiff:
    added: list[str] = field(default_factory=list)
    removed: list[str] = field(default_factory=list)
    changed: list[str] = field(default_factory=list)
    unchanged: list[str] = field(default_factory=list)

    @property
    def has_changes(self) -> bool:
        return bool(self.added or self.removed or self.changed)


def render(plan: Plan, *, version: str, generated: str) -> str:
    """Render a plan's project layer into a manifest document."""
    tools = [
        {
            "id": selection.package.id,
            "kind": selection.package.kind.value,
            "source": selection.package.source,
            "scope": selection.scope.value,
            "version_pin": "latest",
        }
        for selection in plan.for_scope(Scope.project)
    ]
    frontmatter = {
        "cchad_version": version,
        "generated": generated,
        "stack": plan.stack.sorted_signals(),
        "tools": tools,
        "skipped": [{"id": skip.id, "reason": skip.reason} for skip in plan.skips],
    }
    front = yaml.safe_dump(frontmatter, sort_keys=False, default_flow_style=False).strip()
    return f"---\n{front}\n---\n\n{_render_body(plan)}\n"


def _render_body(plan: Plan) -> str:
    lines = ["# Claude Code setup for this repo", ""]
    signals = plan.stack.sorted_signals()
    if signals:
        lines += [f"Detected stack: {', '.join(signals)}.", ""]

    installed = plan.for_scope(Scope.project)
    lines += ["## Installed", ""]
    if installed:
        for selection in installed:
            package = selection.package
            lines.append(f"- **{package.id}** ({package.kind.value}) — {package.description}")
    else:
        lines.append("- _Nothing project-specific was needed._")
    lines.append("")

    if plan.skips:
        lines += ["## Deliberately skipped", ""]
        for skip in plan.skips:
            lines.append(f"- **{skip.id}** — {skip.reason}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def parse_manifest(text: str) -> Manifest:
    match = _FRONTMATTER_RE.match(text)
    if not match:
        raise ManifestError("manifest is missing its --- frontmatter --- block")
    try:
        front = yaml.safe_load(match.group("front")) or {}
    except yaml.YAMLError as exc:
        raise ManifestError(f"could not parse manifest frontmatter: {exc}") from exc

    tools = [
        ManifestTool(
            id=raw["id"],
            kind=Kind(raw.get("kind", "mcp")),
            source=raw.get("source", ""),
            scope=Scope(raw.get("scope", "project")),
            version_pin=raw.get("version_pin", "latest"),
        )
        for raw in front.get("tools", []) or []
    ]
    skipped = [
        Skip(id=raw["id"], reason=raw.get("reason", "")) for raw in front.get("skipped", []) or []
    ]
    return Manifest(
        cchad_version=str(front.get("cchad_version", "")),
        generated=str(front.get("generated", "")),
        stack=list(front.get("stack", []) or []),
        tools=tools,
        skipped=skipped,
        body=match.group("body").strip(),
    )


def read_manifest(path: Path) -> Manifest | None:
    path = Path(path)
    if not path.is_file():
        return None
    return parse_manifest(path.read_text(encoding="utf-8"))


def diff_plan(plan: Plan, manifest: Manifest | None) -> ManifestDiff:
    """Compare a plan's project layer against a committed manifest."""
    plan_tools = {s.package.id: s for s in plan.for_scope(Scope.project)}
    manifest_tools = {t.id: t for t in manifest.tools} if manifest else {}

    diff = ManifestDiff()
    for package_id, selection in plan_tools.items():
        existing = manifest_tools.get(package_id)
        if existing is None:
            diff.added.append(package_id)
        elif existing.source != selection.package.source:
            diff.changed.append(package_id)
        else:
            diff.unchanged.append(package_id)
    for package_id in manifest_tools:
        if package_id not in plan_tools:
            diff.removed.append(package_id)

    for bucket in (diff.added, diff.removed, diff.changed, diff.unchanged):
        bucket.sort()
    return diff
