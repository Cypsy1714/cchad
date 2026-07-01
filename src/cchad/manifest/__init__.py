"""Read, write, and diff the committed lockfile ``auto_plugins_mcps.md``.

The file is YAML frontmatter (what apply/sync read) followed by a human-readable
body (what reviewers read in a PR). Rendering is pure so it is easy to test.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from cchad.models import Kind, Manifest, ManifestTool, Plan, Scope, Selection, Skip

__all__ = [
    "ManifestError",
    "ManifestDiff",
    "render",
    "render_doc",
    "tool_from_selection",
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


def tool_from_selection(selection: Selection) -> ManifestTool:
    return ManifestTool(
        id=selection.package.id,
        kind=selection.package.kind,
        source=selection.package.source,
        scope=selection.scope,
        version_pin="latest",
    )


def render(plan: Plan, *, version: str, generated: str) -> str:
    """Render a plan's project layer into a manifest document."""
    project = plan.for_scope(Scope.project)
    return render_doc(
        version=version,
        generated=generated,
        stack=plan.stack.sorted_signals(),
        tools=[tool_from_selection(s) for s in project],
        skipped=plan.skips,
        descriptions={s.package.id: s.package.description for s in project},
    )


def render_doc(
    *,
    version: str,
    generated: str,
    stack: list[str],
    tools: list[ManifestTool],
    skipped: list[Skip],
    descriptions: dict[str, str] | None = None,
) -> str:
    """Render a manifest document from explicit tools (used by add/remove too)."""
    frontmatter = {
        "cchad_version": version,
        "generated": generated,
        "stack": list(stack),
        "tools": [
            {
                "id": tool.id,
                "kind": tool.kind.value,
                "source": tool.source,
                "scope": tool.scope.value,
                "version_pin": tool.version_pin,
            }
            for tool in tools
        ],
        "skipped": [{"id": skip.id, "reason": skip.reason} for skip in skipped],
    }
    front = yaml.safe_dump(frontmatter, sort_keys=False, default_flow_style=False).strip()
    body = _render_body(stack, tools, skipped, descriptions or {})
    return f"---\n{front}\n---\n\n{body}\n"


def _render_body(
    stack: list[str],
    tools: list[ManifestTool],
    skipped: list[Skip],
    descriptions: dict[str, str],
) -> str:
    lines = ["# Claude Code setup for this repo", ""]
    if stack:
        lines += [f"Detected stack: {', '.join(stack)}.", ""]

    lines += ["## Installed", ""]
    if tools:
        for tool in tools:
            description = descriptions.get(tool.id, "")
            suffix = f" — {description}" if description else ""
            lines.append(f"- **{tool.id}** ({tool.kind.value}){suffix}")
    else:
        lines.append("- _Nothing project-specific was needed._")
    lines.append("")

    if skipped:
        lines += ["## Deliberately skipped", ""]
        for skip in skipped:
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
