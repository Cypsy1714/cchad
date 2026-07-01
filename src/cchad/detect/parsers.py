"""Parsers that read one kind of project file and add signals to a descriptor.

Every parser is defensive: a repo may contain malformed or partial files, and a
parse failure must never crash detection — it just contributes nothing.
"""

from __future__ import annotations

import json
import os
import re
import tomllib
from pathlib import Path

from cchad.models import StackDescriptor

from .mappings import (
    CONFIG_FILE_SIGNALS,
    EXTENSION_LANGUAGES,
    GO_MODULE_SIGNALS,
    IGNORE_DIRS,
    JS_DEPENDENCY_SIGNALS,
    JS_PREFIX_SIGNALS,
    PY_DEPENDENCY_SIGNALS,
    Signal,
)

_MAX_FILES_SCANNED = 20_000


def _add(descriptor: StackDescriptor, signal: Signal) -> None:
    field, value = signal
    getattr(descriptor, field).add(value)


def _read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None


def _js_signal(name: str) -> Signal | None:
    if name in JS_DEPENDENCY_SIGNALS:
        return JS_DEPENDENCY_SIGNALS[name]
    for prefix, signal in JS_PREFIX_SIGNALS.items():
        if name.startswith(prefix):
            return signal
    return None


def parse_package_json(root: Path, descriptor: StackDescriptor) -> None:
    path = root / "package.json"
    text = _read_text(path)
    if text is None:
        return
    descriptor.languages.add("javascript")
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return
    for section in ("dependencies", "devDependencies", "peerDependencies"):
        deps = data.get(section)
        if not isinstance(deps, dict):
            continue
        for name in deps:
            signal = _js_signal(name)
            if signal:
                _add(descriptor, signal)


def parse_js_lockfiles(root: Path, descriptor: StackDescriptor) -> None:
    lockfiles = {
        "package-lock.json": "npm",
        "pnpm-lock.yaml": "pnpm",
        "yarn.lock": "yarn",
        "bun.lockb": "bun",
    }
    for filename, manager in lockfiles.items():
        if (root / filename).exists():
            descriptor.languages.add("javascript")
            descriptor.infra.add(manager)


_PY_NAME_RE = re.compile(r"^[A-Za-z0-9._-]+")


def _normalize_py_name(raw: str) -> str | None:
    raw = raw.strip()
    if not raw or raw.startswith(("#", "-")):
        return None
    raw = raw.split(";", 1)[0]  # drop environment markers
    raw = raw.split("[", 1)[0]  # drop extras
    match = _PY_NAME_RE.match(raw)
    if not match:
        return None
    return match.group(0).lower().replace("_", "-")


def _py_signal(raw_name: str) -> Signal | None:
    name = _normalize_py_name(raw_name)
    if name is None:
        return None
    return PY_DEPENDENCY_SIGNALS.get(name)


def parse_pyproject(root: Path, descriptor: StackDescriptor) -> None:
    path = root / "pyproject.toml"
    text = _read_text(path)
    if text is None:
        return
    descriptor.languages.add("python")
    try:
        data = tomllib.loads(text)
    except tomllib.TOMLDecodeError:
        return

    names: list[str] = []

    project = data.get("project", {})
    if isinstance(project, dict):
        deps = project.get("dependencies")
        if isinstance(deps, list):
            names.extend(d for d in deps if isinstance(d, str))
        optional = project.get("optional-dependencies")
        if isinstance(optional, dict):
            for group in optional.values():
                if isinstance(group, list):
                    names.extend(d for d in group if isinstance(d, str))

    poetry = data.get("tool", {}).get("poetry", {}) if isinstance(data.get("tool"), dict) else {}
    if isinstance(poetry, dict):
        main = poetry.get("dependencies")
        if isinstance(main, dict):
            names.extend(k for k in main if k.lower() != "python")
        groups = poetry.get("group")
        if isinstance(groups, dict):
            for group in groups.values():
                group_deps = group.get("dependencies") if isinstance(group, dict) else None
                if isinstance(group_deps, dict):
                    names.extend(group_deps.keys())

    for name in names:
        signal = _py_signal(name)
        if signal:
            _add(descriptor, signal)


def parse_requirements(root: Path, descriptor: StackDescriptor) -> None:
    found = False
    for path in sorted(root.glob("requirements*.txt")):
        text = _read_text(path)
        if text is None:
            continue
        found = True
        for line in text.splitlines():
            signal = _py_signal(line)
            if signal:
                _add(descriptor, signal)
    if found:
        descriptor.languages.add("python")


def parse_go_mod(root: Path, descriptor: StackDescriptor) -> None:
    text = _read_text(root / "go.mod")
    if text is None:
        return
    descriptor.languages.add("go")
    for line in text.splitlines():
        line = line.strip()
        for module_prefix, signal in GO_MODULE_SIGNALS.items():
            if line.startswith(module_prefix) or line.startswith(f"require {module_prefix}"):
                _add(descriptor, signal)


def parse_config_files(root: Path, descriptor: StackDescriptor) -> None:
    for filename, signal in CONFIG_FILE_SIGNALS.items():
        if (root / filename).exists():
            _add(descriptor, signal)


def scan_extensions(root: Path, descriptor: StackDescriptor) -> None:
    scanned = 0
    for _dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if d not in IGNORE_DIRS and not d.startswith(".")]
        for filename in filenames:
            scanned += 1
            if scanned > _MAX_FILES_SCANNED:
                return
            suffix = os.path.splitext(filename)[1].lower()
            signal = EXTENSION_LANGUAGES.get(suffix)
            if signal:
                _add(descriptor, signal)
