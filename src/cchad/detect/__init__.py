"""Stack detection: read a repo, return a normalized :class:`StackDescriptor`.

Detection is pure and side-effect free — it only reads files. Each parser adds
whatever signals it can; the union of them is the descriptor the resolver and
rules match against.
"""

from __future__ import annotations

from pathlib import Path

from cchad.models import StackDescriptor

from .parsers import (
    parse_config_files,
    parse_go_mod,
    parse_js_lockfiles,
    parse_package_json,
    parse_pyproject,
    parse_requirements,
    scan_extensions,
)

__all__ = ["detect_stack"]


def detect_stack(root: Path | str) -> StackDescriptor:
    """Inspect ``root`` and return everything cchad can tell about its stack."""
    root = Path(root)
    descriptor = StackDescriptor()
    if not root.is_dir():
        return descriptor

    parse_package_json(root, descriptor)
    parse_js_lockfiles(root, descriptor)
    parse_pyproject(root, descriptor)
    parse_requirements(root, descriptor)
    parse_go_mod(root, descriptor)
    parse_config_files(root, descriptor)
    scan_extensions(root, descriptor)
    return descriptor
