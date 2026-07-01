"""The resolver: turn a catalog + detected stack + config into a Plan.

This is the deconfliction algorithm. It is deterministic — same inputs always
produce the same Plan — and every drop carries a human-readable reason.

Order of operations (see docs/deconfliction.md):
  1. base set   = expand(preset) + enable - disable
  2. project set = union of rule recommendations for the detected stack
  3. candidates  = base + project, each tagged with a scope
  4. single spine    (only one workflow spine survives)
  5. single browser  (only one browser MCP survives)
  6. conflicts       (drop anything that conflicts with a kept package)
  7. cap             (limit MCP servers to policy.max_mcp_servers)
"""

from __future__ import annotations

from dataclasses import dataclass

from cchad.catalog import Catalog
from cchad.models import (
    Config,
    Kind,
    Package,
    Plan,
    Scope,
    Selection,
    Skip,
    StackDescriptor,
)


@dataclass
class _Candidate:
    package: Package
    scope: Scope
    reason: str
    from_base: bool


def _sort_key(candidate: _Candidate) -> tuple[int, str]:
    # Higher priority first; ties broken by id for full determinism.
    return (-candidate.package.priority, candidate.package.id)


def _base_ids(catalog: Catalog, config: Config) -> dict[str, str]:
    """Return {id: reason} for the base layer, honoring enable/disable."""
    reasons: dict[str, str] = {}
    for package_id in catalog.expand_preset(config.base.preset):
        reasons[package_id] = f"base preset '{config.base.preset}'"
    for package_id in config.base.enable:
        reasons[package_id] = "base (enabled in config)"
    for package_id in config.base.disable:
        reasons.pop(package_id, None)
    return reasons


def _project_ids(catalog: Catalog, descriptor: StackDescriptor) -> dict[str, str]:
    """Return {id: reason} for packages recommended by matching rules."""
    signals = descriptor.signals
    reasons: dict[str, str] = {}
    for rule in catalog.rules:
        if not rule.matches(signals):
            continue
        label = "+".join(rule.when)
        for package_id in rule.recommend:
            reasons.setdefault(package_id, f"stack match: {label}")
    return reasons


def _pick_preferred(group: list[_Candidate], preferred_id: str | None) -> _Candidate:
    for candidate in group:
        if candidate.package.id == preferred_id:
            return candidate
    return sorted(group, key=_sort_key)[0]


def resolve(catalog: Catalog, descriptor: StackDescriptor, config: Config) -> Plan:
    """Resolve the full plan of packages to add and packages skipped, with reasons."""
    skips: list[Skip] = []
    candidates: dict[str, _Candidate] = {}

    base = _base_ids(catalog, config)
    project = _project_ids(catalog, descriptor)

    for package_id, reason in {**project, **base}.items():
        package = catalog.get(package_id)
        if package is None:
            skips.append(Skip(id=package_id, reason="not found in catalog"))
            continue
        candidates[package_id] = _Candidate(
            package=package,
            scope=package.default_scope,
            reason=base.get(package_id, reason),
            from_base=package_id in base,
        )

    def drop(candidate: _Candidate, reason: str) -> None:
        candidates.pop(candidate.package.id, None)
        skips.append(Skip(id=candidate.package.id, reason=reason, package=candidate.package))

    # 4. Single workflow spine.
    spines = [c for c in candidates.values() if c.package.kind == Kind.spine]
    if len(spines) > 1:
        keep = _pick_preferred(spines, config.policy.spine)
        for candidate in spines:
            if candidate is not keep:
                drop(candidate, f"only one workflow spine allowed; kept '{keep.package.id}'")

    # 5. Single browser MCP.
    browsers = [c for c in candidates.values() if c.package.category == "browser"]
    if len(browsers) > 1:
        keep = _pick_preferred(browsers, config.policy.browser)
        for candidate in browsers:
            if candidate is not keep:
                drop(candidate, f"only one browser tool allowed; kept '{keep.package.id}'")

    # 6. Explicit conflicts (bidirectional), resolved in priority order.
    selected: dict[str, _Candidate] = {}
    for candidate in sorted(candidates.values(), key=_sort_key):
        clash = next(
            (
                other
                for other in selected.values()
                if other.package.id in candidate.package.conflicts_with
                or candidate.package.id in other.package.conflicts_with
            ),
            None,
        )
        if clash is not None:
            drop(candidate, f"conflicts with '{clash.package.id}'")
        else:
            selected[candidate.package.id] = candidate

    # 7. Cap the number of MCP servers.
    cap = config.policy.max_mcp_servers
    mcps = sorted(
        (c for c in selected.values() if c.package.kind == Kind.mcp),
        key=_sort_key,
    )
    for candidate in mcps[cap:]:
        selected.pop(candidate.package.id, None)
        skips.append(
            Skip(
                id=candidate.package.id,
                reason=f"MCP server cap reached (max={cap})",
                package=candidate.package,
            )
        )

    selections = [
        Selection(
            package=c.package,
            scope=c.scope,
            reason=c.reason,
            from_base=c.from_base,
        )
        for c in sorted(selected.values(), key=_sort_key)
    ]
    skips.sort(key=lambda s: s.id)
    return Plan(stack=descriptor, selections=selections, skips=skips)
