"""Safe, reversible file writes.

Every write goes through a temp file and an atomic ``os.replace`` so a file is
never left half-written. Before overwriting, the previous contents are copied to
``<file>.bak``. A :class:`Journal` records what changed so ``cchad rollback`` can
undo the last apply.
"""

from __future__ import annotations

import json
import os
import shutil
import tempfile
from dataclasses import asdict, dataclass, field
from pathlib import Path

BACKUP_SUFFIX = ".bak"


def atomic_write_text(path: Path, data: str) -> None:
    """Write ``data`` to ``path`` atomically, creating parent dirs as needed."""
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f"{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp):
            os.unlink(tmp)


@dataclass
class JournalEntry:
    target: str
    backup: str | None
    existed: bool


@dataclass
class Journal:
    """Records file changes from one apply so they can be rolled back."""

    entries: list[JournalEntry] = field(default_factory=list)

    def write_text(self, path: Path, data: str) -> None:
        path = Path(path)
        existed = path.exists()
        backup: str | None = None
        if existed:
            backup = f"{path}{BACKUP_SUFFIX}"
            shutil.copy2(path, backup)
        atomic_write_text(path, data)
        self.entries.append(JournalEntry(str(path), backup, existed))

    def rollback(self) -> list[str]:
        """Undo every recorded change, newest first. Returns restored paths."""
        restored: list[str] = []
        for entry in reversed(self.entries):
            target = Path(entry.target)
            if entry.existed and entry.backup and Path(entry.backup).exists():
                shutil.copy2(entry.backup, target)
                restored.append(entry.target)
            elif not entry.existed and target.exists():
                target.unlink()
                restored.append(entry.target)
        return restored

    def save(self, path: Path) -> None:
        payload = {"entries": [asdict(entry) for entry in self.entries]}
        atomic_write_text(path, json.dumps(payload, indent=2) + "\n")

    @classmethod
    def load(cls, path: Path) -> Journal:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        return cls([JournalEntry(**entry) for entry in data.get("entries", [])])
