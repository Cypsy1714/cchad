"""The cchad command line. Thin wiring: every command loads config, resolves,
and calls the engine. Human output uses rich; ``--json`` prints plain JSON so
the Claude Code plugin can parse it.
"""

from __future__ import annotations

import json
import os
import subprocess
from datetime import date
from pathlib import Path

import typer
from rich.console import Console
from rich.table import Table

from cchad import __version__
from cchad.apply import ApplyError, apply_selections, remove_from_disk
from cchad.apply.atomic import Journal
from cchad.catalog import Catalog, load_catalog
from cchad.config import load_config, save_config
from cchad.detect import detect_stack
from cchad.display import plan_to_dict, print_apply_result, print_plan
from cchad.manifest import (
    ManifestError,
    diff_plan,
    read_manifest,
    render,
    render_doc,
)
from cchad.models import BaseConfig, Config, ManifestTool, Scope, Selection, StackDescriptor
from cchad.paths import config_path, journal_path, manifest_path, user_home
from cchad.resolve import base_ids, resolve
from cchad.sync import SyncError
from cchad.sync import sync as run_sync

app = typer.Typer(
    add_completion=False,
    no_args_is_help=True,
    help="A package manager and lockfile for your Claude Code setup.",
)
base_app = typer.Typer(no_args_is_help=True, help="Manage the base layer (your global tooling).")
config_app = typer.Typer(no_args_is_help=True, help="Manage cchad configuration.")
app.add_typer(base_app, name="base")
app.add_typer(config_app, name="config")

console = Console()
err = Console(stderr=True)


# --------------------------------------------------------------------------- #
# Shared helpers
# --------------------------------------------------------------------------- #
def _warn(message: str) -> None:
    err.print(f"[yellow]warning:[/] {message}")


def _today() -> str:
    return date.today().isoformat()


def _catalog(config: Config) -> Catalog:
    return load_catalog(sources=config.catalog_sources, warn=_warn)


def _resolve_plan(repo: Path, *, include_base: bool = True):
    config = load_config()
    if not include_base:
        config = Config(
            base=BaseConfig(preset="__none__"),
            policy=config.policy,
            catalog_sources=config.catalog_sources,
        )
    catalog = _catalog(config)
    plan = resolve(catalog, detect_stack(repo), config)
    return config, catalog, plan


def _read_manifest_or_exit(repo: Path):
    try:
        return read_manifest(manifest_path(repo))
    except ManifestError as exc:
        err.print(f"[red]error:[/] {exc}")
        raise typer.Exit(1) from exc


def _split_ids(raw: str) -> list[str]:
    return [item.strip() for item in raw.split(",") if item.strip()]


# --------------------------------------------------------------------------- #
# Root
# --------------------------------------------------------------------------- #
def _version_callback(value: bool) -> None:
    if value:
        console.print(__version__)
        raise typer.Exit()


@app.callback()
def _root(
    _version: bool = typer.Option(
        False, "--version", callback=_version_callback, is_eager=True, help="Show version and exit."
    ),
) -> None:
    """cchad configures Claude Code for a repo and records it in a committed manifest."""


# --------------------------------------------------------------------------- #
# setup — choose and apply the base layer
# --------------------------------------------------------------------------- #
def _prompt_preset(catalog: Catalog, default: str) -> str:
    names = list(catalog.presets)
    console.print("[bold]Pick a baseline:[/]")
    for index, name in enumerate(names, 1):
        console.print(f"  {index}) [cyan]{name}[/] — {', '.join(catalog.presets[name])}")
    default_index = names.index(default) + 1 if default in names else 1
    choice = typer.prompt("Choice", default=str(default_index))
    try:
        return names[int(choice) - 1]
    except (ValueError, IndexError):
        return default if default in names else names[0]


def _customize(catalog: Catalog, config: Config) -> None:
    current = sorted(base_ids(catalog, config))
    console.print(f"Current base packages: {', '.join(current)}")
    for package_id in _split_ids(typer.prompt("Disable ids (comma-separated)", default="")):
        if package_id not in config.base.disable:
            config.base.disable.append(package_id)
        if package_id in config.base.enable:
            config.base.enable.remove(package_id)
    for package_id in _split_ids(typer.prompt("Enable extra ids (comma-separated)", default="")):
        if package_id not in config.base.enable:
            config.base.enable.append(package_id)
        if package_id in config.base.disable:
            config.base.disable.remove(package_id)


@app.command()
def setup(
    preset: str | None = typer.Option(None, "--preset", help="minimal | recommended | full."),
    yes: bool = typer.Option(False, "--yes", "-y", help="Non-interactive; accept defaults."),
    no_apply: bool = typer.Option(False, "--no-apply", help="Write config but do not apply."),
) -> None:
    """Choose your base layer, save it to config, and apply it to your user scope."""
    config = load_config()
    catalog = _catalog(config)

    if preset is None and not yes:
        preset = _prompt_preset(catalog, default=config.base.preset)
    preset = preset or config.base.preset or "recommended"
    if preset not in catalog.presets:
        err.print(
            f"[red]error:[/] unknown preset {preset!r}; "
            f"choose from {', '.join(catalog.presets)}"
        )
        raise typer.Exit(1)
    config.base.preset = preset

    if not yes and typer.confirm("Customize packages?", default=False):
        _customize(catalog, config)

    save_config(config)
    console.print(f"[green]Saved[/] {config_path()}")
    if no_apply:
        return

    plan = resolve(catalog, StackDescriptor(), config)
    journal = Journal()
    result = apply_selections(
        plan.for_scope(Scope.user), repo_root=None, home=user_home(), journal=journal
    )
    journal.save(journal_path())
    print_apply_result(console, result)
    console.print("\n[dim]Base applied. Run `cchad init` inside a repo to configure it.[/]")


# --------------------------------------------------------------------------- #
# plan / init / update — resolve for a repo
# --------------------------------------------------------------------------- #
@app.command()
def plan(
    json_out: bool = typer.Option(False, "--json", help="Machine-readable plan."),
    no_base: bool = typer.Option(False, "--no-base", help="Ignore the base layer."),
) -> None:
    """Preview what cchad would configure for this repo. Writes nothing."""
    repo = Path.cwd()
    _, _, resolved = _resolve_plan(repo, include_base=not no_base)
    manifest = _read_manifest_or_exit(repo)
    diff = diff_plan(resolved, manifest)
    if json_out:
        typer.echo(json.dumps(plan_to_dict(resolved, diff), indent=2))
        return
    print_plan(console, resolved, diff)
    if manifest is not None and not diff.has_changes:
        console.print("\n[green]Manifest is up to date — no changes.[/]")


@app.command()
def init(
    yes: bool = typer.Option(False, "--yes", "-y", help="Apply without confirmation."),
    json_out: bool = typer.Option(False, "--json", help="Machine-readable plan."),
    plan_only: bool = typer.Option(False, "--plan-only", help="Show the plan and stop."),
    no_base: bool = typer.Option(False, "--no-base", help="Ignore the base layer."),
) -> None:
    """Detect this repo's stack, resolve a plan, apply it, and write the manifest."""
    repo = Path.cwd()
    _, _, resolved = _resolve_plan(repo, include_base=not no_base)
    manifest = _read_manifest_or_exit(repo)
    diff = diff_plan(resolved, manifest)

    if json_out:
        typer.echo(json.dumps(plan_to_dict(resolved, diff), indent=2))
    else:
        print_plan(console, resolved, diff)

    if plan_only:
        return
    if not yes:
        if json_out:
            return  # preview only; re-run with --yes to apply
        if not typer.confirm("\nApply this plan to the repo?", default=True):
            console.print("Aborted.")
            return

    journal = Journal()
    try:
        result = apply_selections(
            resolved.for_scope(Scope.project), repo_root=repo, home=user_home(), journal=journal
        )
        journal.write_text(
            manifest_path(repo), render(resolved, version=__version__, generated=_today())
        )
    except ApplyError as exc:
        err.print(f"[red]error:[/] {exc}")
        raise typer.Exit(1) from exc

    result.written.append(str(manifest_path(repo)))
    journal.save(journal_path())
    if not json_out:
        print_apply_result(console, result)
        console.print(
            "\n[dim]Reload Claude Code so new servers/skills load, and commit "
            "auto_plugins_mcps.md.[/]"
        )


@app.command()
def update(json_out: bool = typer.Option(False, "--json", help="Machine-readable plan.")) -> None:
    """Reload the catalog and show how this repo has drifted from its manifest."""
    repo = Path.cwd()
    _, _, resolved = _resolve_plan(repo)
    manifest = _read_manifest_or_exit(repo)
    diff = diff_plan(resolved, manifest)
    if json_out:
        typer.echo(json.dumps(plan_to_dict(resolved, diff), indent=2))
        return
    print_plan(console, resolved, diff)
    if diff.has_changes:
        console.print("\nRun [bold]cchad init[/] to apply these changes.")
    else:
        console.print("\n[green]Everything is up to date.[/]")


# --------------------------------------------------------------------------- #
# apply / sync — materialize the committed manifest
# --------------------------------------------------------------------------- #
def _materialize(repo: Path, verb: str, yes: bool) -> None:
    config = load_config()
    catalog = _catalog(config)
    manifest = _read_manifest_or_exit(repo)
    if manifest is None:
        err.print("[red]error:[/] no auto_plugins_mcps.md here. Run `cchad init` first.")
        raise typer.Exit(1)
    if not yes and not typer.confirm(
        f"{verb} {len(manifest.tools)} tool(s) from the manifest into this repo?", default=True
    ):
        console.print("Aborted.")
        return
    journal = Journal()
    try:
        result, _ = run_sync(repo, catalog, home=user_home(), journal=journal)
    except (SyncError, ApplyError) as exc:
        err.print(f"[red]error:[/] {exc}")
        raise typer.Exit(1) from exc
    journal.save(journal_path())
    print_apply_result(console, result)
    console.print("\n[dim]Reload Claude Code so the servers and skills load.[/]")


@app.command()
def apply(
    yes: bool = typer.Option(False, "--yes", "-y", help="Apply without confirmation."),
) -> None:
    """Apply this repo's committed manifest to local config."""
    _materialize(Path.cwd(), "Apply", yes)


@app.command()
def sync(
    yes: bool = typer.Option(False, "--yes", "-y", help="Sync without confirmation."),
) -> None:
    """Rebuild local config from the committed manifest (teammate onboarding)."""
    _materialize(Path.cwd(), "Sync", yes)


# --------------------------------------------------------------------------- #
# add / remove — project-layer overrides written to the manifest
# --------------------------------------------------------------------------- #
@app.command()
def add(
    package_id: str = typer.Argument(..., help="Catalog id to add to this repo."),
    scope: str | None = typer.Option(None, "--scope", help="user | project."),
) -> None:
    """Add a package to this repo's manifest and install it."""
    repo = Path.cwd()
    config = load_config()
    catalog = _catalog(config)
    package = catalog.get(package_id)
    if package is None:
        err.print(f"[red]error:[/] unknown package {package_id!r}. See the catalog for valid ids.")
        raise typer.Exit(1)
    manifest = _read_manifest_or_exit(repo)
    if manifest is None:
        err.print("[red]error:[/] no manifest yet. Run `cchad init` first.")
        raise typer.Exit(1)

    selection_scope = Scope(scope) if scope else package.default_scope
    tool = ManifestTool(
        id=package.id, kind=package.kind, source=package.source, scope=selection_scope
    )
    tools = [t for t in manifest.tools if t.id != package.id] + [tool]
    descriptions = {
        t.id: (catalog.get(t.id).description if catalog.get(t.id) else "") for t in tools
    }

    journal = Journal()
    journal.write_text(
        manifest_path(repo),
        render_doc(
            version=__version__,
            generated=_today(),
            stack=manifest.stack,
            tools=tools,
            skipped=manifest.skipped,
            descriptions=descriptions,
        ),
    )
    result = apply_selections(
        [Selection(package=package, scope=selection_scope, reason="added via cchad add")],
        repo_root=repo,
        home=user_home(),
        journal=journal,
    )
    journal.save(journal_path())
    console.print(f"[green]Added[/] {package.id} to the manifest.")
    print_apply_result(console, result)


@app.command()
def remove(
    package_id: str = typer.Argument(..., help="Catalog id to remove from this repo."),
) -> None:
    """Remove a package from this repo's manifest and delete it from local config."""
    repo = Path.cwd()
    config = load_config()
    catalog = _catalog(config)
    manifest = _read_manifest_or_exit(repo)
    if manifest is None:
        err.print("[red]error:[/] no manifest here.")
        raise typer.Exit(1)
    tool = next((t for t in manifest.tools if t.id == package_id), None)
    if tool is None:
        err.print(f"[red]error:[/] {package_id!r} is not in the manifest.")
        raise typer.Exit(1)

    tools = [t for t in manifest.tools if t.id != package_id]
    descriptions = {
        t.id: (catalog.get(t.id).description if catalog.get(t.id) else "") for t in tools
    }
    journal = Journal()
    journal.write_text(
        manifest_path(repo),
        render_doc(
            version=__version__,
            generated=_today(),
            stack=manifest.stack,
            tools=tools,
            skipped=manifest.skipped,
            descriptions=descriptions,
        ),
    )
    remove_from_disk([tool], repo_root=repo, home=user_home(), journal=journal)
    journal.save(journal_path())
    console.print(f"[green]Removed[/] {package_id} from the manifest and local config.")


# --------------------------------------------------------------------------- #
# rollback
# --------------------------------------------------------------------------- #
@app.command()
def rollback() -> None:
    """Undo the last apply, restoring files from their .bak backups."""
    path = journal_path()
    if not path.exists():
        console.print("Nothing to roll back.")
        return
    journal = Journal.load(path)
    restored = journal.rollback()
    if restored:
        console.print("[green]Rolled back:[/]")
        for target in restored:
            console.print(f"  [green]✓[/] {target}")
    else:
        console.print("Nothing to restore.")
    path.unlink()


# --------------------------------------------------------------------------- #
# base sub-commands
# --------------------------------------------------------------------------- #
@base_app.command("list")
def base_list() -> None:
    """List the packages in your base layer."""
    config = load_config()
    catalog = _catalog(config)
    table = Table(title="Base layer", title_justify="left", header_style="bold")
    table.add_column("Package")
    table.add_column("Name")
    table.add_column("Scope")
    table.add_column("Why", overflow="fold")
    for package_id, reason in sorted(base_ids(catalog, config).items()):
        package = catalog.get(package_id)
        table.add_row(
            package_id,
            package.name if package else "[red]unknown[/]",
            package.default_scope.value if package else "?",
            reason,
        )
    console.print(table)


@base_app.command("add")
def base_add(package_id: str = typer.Argument(..., help="Catalog id to add to your base.")) -> None:
    """Add a package to your base layer."""
    config = load_config()
    catalog = _catalog(config)
    if catalog.get(package_id) is None:
        err.print(f"[red]error:[/] unknown package {package_id!r}.")
        raise typer.Exit(1)
    if package_id not in config.base.enable:
        config.base.enable.append(package_id)
    if package_id in config.base.disable:
        config.base.disable.remove(package_id)
    save_config(config)
    console.print(f"[green]Added[/] {package_id} to base. Run `cchad setup` to apply.")


@base_app.command("remove")
def base_remove(
    package_id: str = typer.Argument(..., help="Catalog id to drop from your base."),
) -> None:
    """Remove a package from your base layer."""
    config = load_config()
    catalog = _catalog(config)
    if package_id in config.base.enable:
        config.base.enable.remove(package_id)
    in_preset = package_id in catalog.expand_preset(config.base.preset)
    if in_preset and package_id not in config.base.disable:
        config.base.disable.append(package_id)
    save_config(config)
    console.print(f"[green]Removed[/] {package_id} from base. Run `cchad setup` to apply.")


# --------------------------------------------------------------------------- #
# config sub-commands
# --------------------------------------------------------------------------- #
@config_app.command("path")
def config_show_path() -> None:
    """Print the path to your config file."""
    console.print(str(config_path()))


@config_app.command("edit")
def config_edit() -> None:
    """Open your config file in $EDITOR."""
    path = config_path()
    if not path.exists():
        save_config(load_config(), path)
    editor = os.environ.get("EDITOR") or os.environ.get("VISUAL") or "nano"
    try:
        subprocess.run([editor, str(path)], check=False)
    except FileNotFoundError:
        err.print(f"[red]error:[/] editor {editor!r} not found; set $EDITOR. Config: {path}")


def main() -> None:
    app()


if __name__ == "__main__":
    main()
