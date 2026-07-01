# The manifest

`auto_plugins_mcps.md` is the committed lockfile for a repo's Claude Code setup. It is
the source of truth: `cchad apply` and `cchad sync` read its frontmatter, and your
teammates read its body in a PR.

## Anatomy

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
    version_pin: latest
  - id: react-patterns-skill
    kind: skill
    source: bundled:react-patterns-skill
    scope: project
skipped:
  - id: playwright-mcp
    reason: "only one browser tool allowed; kept 'chrome-devtools-mcp'"
---

# Claude Code setup for this repo

Detected stack: fastapi, javascript, mongodb, python, react, vite.

## Installed
- **context7** (mcp) — Version-pinned library docs; kills API hallucinations.
- **react-patterns-skill** (skill) — Idiomatic React — hooks, composition, ...

## Deliberately skipped
- **playwright-mcp** — only one browser tool allowed; kept 'chrome-devtools-mcp'.
```

## Frontmatter fields

| Field | Meaning |
|-------|---------|
| `cchad_version` | The version that generated the file. |
| `generated` | The date it was written. |
| `stack` | The detected signals, sorted. |
| `tools` | The **project layer** — each with `id`, `kind`, `source`, `scope`, `version_pin`. |
| `skipped` | Packages the resolver dropped, each with a `reason`. |

The manifest records only the **project layer**. Your base layer lives in your
personal [config](configuration.md), not here.

## How it's used

- `cchad init` **writes** the manifest from a fresh resolve.
- `cchad apply` / `cchad sync` **read** `tools` and materialize them to disk. Where a
  tool id is in your local catalog, its richer definition (bundled content, exact
  install method) is used; otherwise it's reconstructed from the manifest entry.
- `cchad plan` **diffs** a fresh resolve against the committed manifest and reports
  added / removed / changed tools — so "no changes" means your repo is in sync.

## Committing it

Commit `auto_plugins_mcps.md`. That is the whole point: the next person runs
`cchad sync` and gets the same MCP servers and skills you did. The manifest never
contains secrets, so it is safe to commit.
