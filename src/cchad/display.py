"""Rendering helpers for the CLI: a plan as JSON, and a plan/result as tables."""

from __future__ import annotations

from typing import Any

from rich.console import Console
from rich.table import Table

from cchad.apply import ApplyResult
from cchad.manifest import ManifestDiff
from cchad.models import Plan


def plan_to_dict(plan: Plan, diff: ManifestDiff | None = None) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "stack": plan.stack.sorted_signals(),
        "add": [
            {
                "id": s.package.id,
                "name": s.package.name,
                "kind": s.package.kind.value,
                "scope": s.scope.value,
                "install_method": s.package.install_method.value,
                "source": s.package.source,
                "from_base": s.from_base,
                "reason": s.reason,
            }
            for s in plan.selections
        ],
        "skip": [{"id": s.id, "reason": s.reason} for s in plan.skips],
    }
    if diff is not None:
        payload["diff"] = {
            "added": diff.added,
            "removed": diff.removed,
            "changed": diff.changed,
            "unchanged": diff.unchanged,
        }
    return payload


def print_plan(console: Console, plan: Plan, diff: ManifestDiff | None = None) -> None:
    signals = plan.stack.sorted_signals()
    console.print(f"[bold]Detected stack:[/] {', '.join(signals) or '(none)'}\n")

    if plan.selections:
        table = Table(title="Will install", title_justify="left", header_style="bold")
        table.add_column("Package")
        table.add_column("Kind")
        table.add_column("Scope")
        table.add_column("Why", overflow="fold")
        for s in plan.selections:
            table.add_row(s.package.id, s.package.kind.value, s.scope.value, s.reason)
        console.print(table)
    else:
        console.print("[dim]Nothing to install.[/]")

    if plan.skips:
        table = Table(title="Skipped", title_justify="left", header_style="bold")
        table.add_column("Package")
        table.add_column("Reason", overflow="fold")
        for s in plan.skips:
            table.add_row(s.id, s.reason)
        console.print(table)

    if diff is not None and diff.has_changes:
        parts = []
        if diff.added:
            parts.append(f"[green]+{len(diff.added)}[/]")
        if diff.removed:
            parts.append(f"[red]-{len(diff.removed)}[/]")
        if diff.changed:
            parts.append(f"[yellow]~{len(diff.changed)}[/]")
        console.print(f"\nChanges vs manifest: {' '.join(parts)}")


def print_apply_result(console: Console, result: ApplyResult) -> None:
    if result.written:
        console.print("\n[bold green]Wrote:[/]")
        for path in result.written:
            console.print(f"  [green]✓[/] {path}")
    if result.manual_steps:
        console.print("\n[bold yellow]Manual steps (cchad never runs installers for you):[/]")
        for step in result.manual_steps:
            console.print(f"  [yellow]•[/] {step}")
