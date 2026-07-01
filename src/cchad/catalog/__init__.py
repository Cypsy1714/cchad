"""Load and merge the catalog, presets, and rules.

The shipped YAML files are the base. Users and teams extend them through
``[catalog].sources`` in config — each source is a YAML document that may add
``packages``, ``presets``, and ``rules``. Later sources override earlier ones by
``id`` (packages) or name (presets); rules are appended.
"""

from __future__ import annotations

import sys
import urllib.request
from collections.abc import Callable
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml

from cchad.data_files import data_text
from cchad.models import InstallMethod, Kind, Package, Scope

WarnFn = Callable[[str], None]


def _default_warn(message: str) -> None:
    print(f"warning: {message}", file=sys.stderr)


@dataclass(frozen=True)
class Rule:
    """A stack-detection mapping: when these signals appear, recommend these ids."""

    when: tuple[str, ...]
    recommend: tuple[str, ...]

    def matches(self, signals: set[str]) -> bool:
        return all(signal in signals for signal in self.when)


@dataclass
class Catalog:
    """Everything cchad knows: packages, presets, and rules — already merged."""

    packages: dict[str, Package] = field(default_factory=dict)
    presets: dict[str, list[str]] = field(default_factory=dict)
    rules: list[Rule] = field(default_factory=list)

    def get(self, package_id: str) -> Package | None:
        return self.packages.get(package_id)

    def expand_preset(self, name: str) -> list[str]:
        return list(self.presets.get(name, []))


def _package_from_dict(raw: dict[str, Any]) -> Package:
    return Package(
        id=raw["id"],
        kind=Kind(raw["kind"]),
        name=raw.get("name", raw["id"]),
        description=raw.get("description", ""),
        source=raw.get("source", ""),
        install_method=InstallMethod(raw.get("install_method", "mcp_json")),
        category=raw.get("category", ""),
        default=bool(raw.get("default", False)),
        default_scope=Scope(raw.get("default_scope", "project")),
        conflicts_with=tuple(raw.get("conflicts_with", []) or []),
        priority=int(raw.get("priority", 0)),
    )


def _apply_document(
    doc: dict[str, Any],
    packages: dict[str, Package],
    presets: dict[str, list[str]],
    rules: list[Rule],
    warn: WarnFn,
    origin: str,
) -> None:
    if not isinstance(doc, dict):
        warn(f"{origin}: expected a mapping at the top level; skipping")
        return

    for raw in doc.get("packages", []) or []:
        try:
            package = _package_from_dict(raw)
        except (KeyError, ValueError) as exc:
            warn(f"{origin}: skipping invalid package ({exc})")
            continue
        packages[package.id] = package

    for name, ids in (doc.get("presets", {}) or {}).items():
        presets[name] = list(ids)

    for raw in doc.get("rules", []) or []:
        try:
            rules.append(
                Rule(when=tuple(raw["when"]), recommend=tuple(raw["recommend"]))
            )
        except (KeyError, TypeError) as exc:
            warn(f"{origin}: skipping invalid rule ({exc})")


def _github_raw_url(source: str) -> str:
    # github:owner/repo[/path/to/file.yaml][#ref]
    body = source[len("github:") :]
    ref = "HEAD"
    if "#" in body:
        body, ref = body.split("#", 1)
    parts = body.split("/")
    owner, repo = parts[0], parts[1]
    path = "/".join(parts[2:]) if len(parts) > 2 else "catalog.yaml"
    return f"https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}"


def _fetch_url(url: str) -> str:
    with urllib.request.urlopen(url, timeout=10) as response:  # noqa: S310 (https only below)
        return response.read().decode("utf-8")


def _load_source_text(source: str, warn: WarnFn) -> str | None:
    try:
        if source.startswith(("http://", "https://")):
            return _fetch_url(source)
        if source.startswith("github:"):
            return _fetch_url(_github_raw_url(source))
        path = Path(source).expanduser()
        if path.is_file():
            return path.read_text(encoding="utf-8")
        warn(f"catalog source not found: {source}")
        return None
    except Exception as exc:  # noqa: BLE001 — a bad source must not crash the CLI
        warn(f"failed to load catalog source {source!r}: {exc}")
        return None


def load_catalog(
    sources: list[str] | None = None,
    warn: WarnFn | None = None,
) -> Catalog:
    """Load the shipped catalog and merge any extra ``sources`` on top."""
    warn = warn or _default_warn
    packages: dict[str, Package] = {}
    presets: dict[str, list[str]] = {}
    rules: list[Rule] = []

    for filename in ("catalog.yaml", "presets.yaml", "rules.yaml"):
        doc = yaml.safe_load(data_text(filename))
        _apply_document(doc, packages, presets, rules, warn, origin=f"shipped:{filename}")

    for source in sources or []:
        text = _load_source_text(source, warn)
        if text is None:
            continue
        doc = yaml.safe_load(text)
        _apply_document(doc, packages, presets, rules, warn, origin=source)

    return Catalog(packages=packages, presets=presets, rules=rules)
