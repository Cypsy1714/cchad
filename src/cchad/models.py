"""Core data types shared across cchad.

Everything here is a plain, immutable-ish dataclass. Packages come from the
catalog (data), the resolver turns them into a Plan, and the manifest records
the project layer of that Plan on disk.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum


class Kind(str, Enum):
    """What a package fundamentally is."""

    mcp = "mcp"
    skill = "skill"
    spine = "spine"
    claude_md = "claude_md"


class InstallMethod(str, Enum):
    """How a package is written to disk when applied."""

    mcp_json = "mcp_json"
    plugin = "plugin"
    skill_dir = "skill_dir"
    claude_md_block = "claude_md_block"


class Scope(str, Enum):
    """Where a package lives. Base layer -> user, project layer -> project."""

    user = "user"
    project = "project"


@dataclass(frozen=True)
class Package:
    """A single installable unit, defined once in the catalog."""

    id: str
    kind: Kind
    name: str
    description: str = ""
    source: str = ""
    install_method: InstallMethod = InstallMethod.mcp_json
    category: str = ""
    default: bool = False
    default_scope: Scope = Scope.project
    conflicts_with: tuple[str, ...] = ()
    priority: int = 0


@dataclass
class StackDescriptor:
    """Normalized signals detected in a repository."""

    languages: set[str] = field(default_factory=set)
    frameworks: set[str] = field(default_factory=set)
    databases: set[str] = field(default_factory=set)
    infra: set[str] = field(default_factory=set)
    test_runners: set[str] = field(default_factory=set)

    @property
    def signals(self) -> set[str]:
        """The flat union of every signal, used for rule matching."""
        return (
            self.languages
            | self.frameworks
            | self.databases
            | self.infra
            | self.test_runners
        )

    def sorted_signals(self) -> list[str]:
        return sorted(self.signals)


@dataclass
class Selection:
    """A package the resolver decided to install, with the why."""

    package: Package
    scope: Scope
    reason: str
    from_base: bool = False


@dataclass
class Skip:
    """A package the resolver dropped, with the why."""

    id: str
    reason: str
    package: Package | None = None


@dataclass
class Plan:
    """The full output of the resolver: what to add and what was skipped."""

    stack: StackDescriptor
    selections: list[Selection] = field(default_factory=list)
    skips: list[Skip] = field(default_factory=list)

    def for_scope(self, scope: Scope) -> list[Selection]:
        return [s for s in self.selections if s.scope == scope]


@dataclass
class Policy:
    """Deconfliction limits applied when the project layer resolves."""

    max_mcp_servers: int = 5
    browser: str | None = "chrome-devtools-mcp"
    spine: str | None = "superpowers"


@dataclass
class BaseConfig:
    """The user's chosen base layer."""

    preset: str = "recommended"
    enable: list[str] = field(default_factory=list)
    disable: list[str] = field(default_factory=list)


@dataclass
class Config:
    """The whole of ~/.config/cchad/config.toml."""

    base: BaseConfig = field(default_factory=BaseConfig)
    policy: Policy = field(default_factory=Policy)
    catalog_sources: list[str] = field(default_factory=list)


@dataclass
class ManifestTool:
    """One installed tool as recorded in a manifest's frontmatter."""

    id: str
    kind: Kind
    source: str = ""
    scope: Scope = Scope.project
    version_pin: str = "latest"


@dataclass
class Manifest:
    """A parsed auto_plugins_mcps.md lockfile."""

    cchad_version: str
    generated: str
    stack: list[str]
    tools: list[ManifestTool] = field(default_factory=list)
    skipped: list[Skip] = field(default_factory=list)
    body: str = ""
