# cchad

**A package manager and lockfile for your Claude Code setup.**

[![CI](https://github.com/Cypsy1714/cchad/actions/workflows/ci.yml/badge.svg)](https://github.com/Cypsy1714/cchad/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/cchad.svg)](https://pypi.org/project/cchad/)
[![Python](https://img.shields.io/pypi/pyversions/cchad.svg)](https://pypi.org/project/cchad/)
[![License: MIT](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

cchad scans a repo, detects its tech stack, and installs a curated, **deconflicted**
set of MCP servers and skills for [Claude Code](https://claude.com/claude-code) —
recording every choice in a committed manifest so anyone who clones the repo gets
an identical setup with one command.

> **Mental model:** a preset is your base tooling · `auto_plugins_mcps.md` is the
> lockfile · `cchad sync` is `npm install`.

---

## Why

Claude Code gets its power from MCP servers, skills, and hooks — but assembling the
right set is tedious and easy to get wrong:

- **Discovery is manual.** The ecosystem is thousands of repos; finding the few that
  matter for *this* project is research every time.
- **Tools fight each other.** Stack two workflow frameworks or two browser MCPs and
  they conflict and degrade the agent.
- **Config isn't shared.** Everyone hand-configures their own `.claude/` and
  `.mcp.json`, so teammates drift.

cchad does **curated + auto-detected + deconflicted + team-synced** in one tool, and
the result is a plain file you can read and review in a PR.

## What makes it different

1. **The manifest is the source of truth.** A committed, human-readable
   `auto_plugins_mcps.md` records what was detected, what got installed, and *why*.
   The CLI applies the manifest — it never hides config in an opaque blob.
2. **Deconfliction is first-class.** At most one workflow spine, one browser MCP, a
   capped number of servers, no redundant duplicates — every drop comes with a reason.

Principles: **minimal by default**, **plan before apply**, **safe** (atomic writes,
backups, rollback, never auto-runs untrusted installers).

---

## Install

```bash
# with uv (recommended)
uv tool install cchad          # or run ad-hoc: uvx cchad --help

# or with pipx
pipx install cchad
```

Inside Claude Code, install the plugin instead:

```
/plugin marketplace add Cypsy1714/cchad
/plugin install cchad@cchad
```

## Quickstart

### In a terminal

```bash
cchad setup        # once: pick a baseline, applied to your user scope
cchad init         # in a repo: detect → preview plan → apply + write the manifest
```

### In Claude Code

```
/cchad:setup       # once: pick a baseline
/cchad:init        # in a repo: preview the plan, confirm, apply
```

### Onboarding a teammate

Someone clones a repo that already has `auto_plugins_mcps.md` committed:

```bash
cchad sync         # rebuilds their local .mcp.json / .claude to match the manifest
```

They open Claude Code and it's configured identically.

---

## How it works

cchad has **two layers**:

| Layer | Scope | Lives in | Set by |
|-------|-------|----------|--------|
| **Base** | user (`~/.claude/`) | your `config.toml` | `cchad setup` |
| **Project** | this repo | committed `auto_plugins_mcps.md` | `cchad init` |

- A **preset** (`minimal` / `recommended` / `full`) picks your base tooling — the
  things you want in every project.
- **Rules** map the detected stack to project packages (e.g. `mongodb` → the MongoDB
  MCP, `react` → a React skill).
- The **resolver** merges both layers and deconflicts them (see
  [docs/deconfliction.md](docs/deconfliction.md)).
- **Apply** writes real config: `.mcp.json`, skill directories, and a fenced block in
  `CLAUDE.md`. Plugins are never auto-installed — cchad prints the exact command.

## The manifest

`auto_plugins_mcps.md` is committed to the repo. Its frontmatter is what cchad reads;
the body is what your teammates review in a PR.

```markdown
---
cchad_version: 0.1.0
generated: 2026-07-01
stack: [fastapi, javascript, mongodb, python, react, vite]
tools:
  - id: context7
    kind: mcp
    source: npx -y @upstash/context7-mcp
    scope: project
  - id: mongodb-mcp
    kind: mcp
    source: npx -y mongodb-mcp-server
    scope: project
skipped:
  - id: playwright-mcp
    reason: "only one browser tool allowed; kept 'chrome-devtools-mcp'"
---

# Claude Code setup for this repo
...
```

## Commands

| Command | What it does |
|---------|--------------|
| `cchad setup` | Pick a base layer, save config, apply it to your user scope. |
| `cchad init` | Detect the stack, preview the plan, apply it, write the manifest. |
| `cchad plan` | Preview the plan (and diff vs the manifest). Writes nothing. |
| `cchad apply` | Apply this repo's committed manifest to local config. |
| `cchad sync` | Rebuild local config from the committed manifest (onboarding). |
| `cchad update` | Reload the catalog and show drift vs the manifest. |
| `cchad add / remove <id>` | Add or remove a project package in the manifest. |
| `cchad base list / add / remove` | Manage your base layer. |
| `cchad config edit` | Open your config in `$EDITOR`. |
| `cchad rollback` | Undo the last apply from its `.bak` backups. |

Global flags: `--json`, `--yes`, `--plan-only`, `--no-base`, `--scope`. See
[docs/cli.md](docs/cli.md).

## Configuration

Your personal base choices and policy live in `~/.config/cchad/config.toml` (not
committed):

```toml
[base]
preset  = "recommended"        # minimal | recommended | full
enable  = []                   # extra base packages
disable = []                   # preset items to drop

[policy]
max_mcp_servers = 5
browser = "chrome-devtools-mcp"  # which single browser MCP wins
spine   = "superpowers"          # which single workflow spine wins

[catalog]
sources = []                   # your own catalog YAMLs (paths or github: refs)
```

See [docs/configuration.md](docs/configuration.md).

## Extending the catalog

The value is the data. Add your own packages, presets, and rules — no code needed —
by pointing `[catalog].sources` at a YAML file or a `github:owner/repo` ref. Your
entries override the shipped ones by `id`. See [docs/extending.md](docs/extending.md).

## Safety

- **Plan before apply** — nothing touches disk without a preview.
- **Atomic writes + `.bak` backups + `cchad rollback`** — your existing `.mcp.json`
  and `.claude/` are never corrupted.
- **No auto-run installers** — cchad only writes config and installs from sources in
  its catalog. Plugins become a manual step with the exact command.
- **No secrets in the manifest** — servers that need keys reference environment
  variables; tokens are never written to committed files.

## Documentation

- [Concepts](docs/concepts.md) — the vocabulary and the two-layer model
- [CLI reference](docs/cli.md)
- [Configuration](docs/configuration.md)
- [The catalog](docs/catalog.md)
- [The manifest](docs/manifest.md)
- [Deconfliction](docs/deconfliction.md)
- [The Claude Code plugin](docs/plugin.md)
- [Extending cchad](docs/extending.md)

## Contributing

Issues and PRs welcome — see [CONTRIBUTING.md](CONTRIBUTING.md). Adding a package or a
detection rule is usually a one-line change to a YAML file.

## License

[MIT](LICENSE) © Cypsy1714
