# The catalog

The catalog is the master list of every package cchad knows about. It ships as data
in [`src/cchad/data/`](../src/cchad/data): `catalog.yaml`, `presets.yaml`, and
`rules.yaml`. To add options, edit these files or extend them via
[`[catalog].sources`](extending.md).

## Package schema (`catalog.yaml`)

```yaml
packages:
  - id: context7                 # unique slug (required)
    kind: mcp                     # mcp | skill | spine | claude_md (required)
    name: Context7                # human name (required)
    description: Version-pinned library docs; kills API hallucinations.
    source: "npx -y @upstash/context7-mcp"
    install_method: mcp_json      # mcp_json | plugin | skill_dir | claude_md_block
    category: docs                # free tag; "browser" and "workflow" carry policy
    default: true                 # part of the "recommended" defaults
    default_scope: project        # user (base) | project (per-repo)
    conflicts_with: []            # ids that cannot coexist with this one
    priority: 80                  # higher wins when deconflicting / capping
```

### `source` formats

| Form | Example | Result |
|------|---------|--------|
| stdio command | `npx -y @upstash/context7-mcp` | `{command, args}` in `.mcp.json` |
| HTTP server | `https://example.com/mcp` | `{type: http, url}` in `.mcp.json` |
| plugin | `plugin:superpowers@claude-plugins-official` | a manual install step |
| bundled | `bundled:react-patterns-skill` | content that ships inside cchad |
| provenance | `github:owner/repo` | a reference for externally sourced content |

### `install_method` targets

| Method | Project scope | User scope |
|--------|---------------|-----------|
| `mcp_json` | `<repo>/.mcp.json` | `~/.claude.json` |
| `skill_dir` | `<repo>/.claude/skills/<id>/` | `~/.claude/skills/<id>/` |
| `claude_md_block` | `<repo>/CLAUDE.md` | `~/.claude/CLAUDE.md` |
| `plugin` | reported as a manual step (never auto-run) | same |

## Presets (`presets.yaml`)

```yaml
presets:
  minimal:     [context7, github-mcp, karpathy-claude-md]
  recommended: [context7, github-mcp, chrome-devtools-mcp, superpowers, karpathy-claude-md]
  full:        [context7, github-mcp, chrome-devtools-mcp, superpowers, karpathy-claude-md, sequential-thinking]
```

## Rules (`rules.yaml`)

A rule fires when **every** signal in `when` is present in the detected stack. An
optional `unless` list vetoes the rule when any of its signals are present — handy
when one signal implies another.

```yaml
rules:
  - when: [mongodb]
    recommend: [mongodb-mcp]
  - when: [react]
    recommend: [react-patterns-skill]
  - when: [javascript]
    unless: [typescript]        # a TypeScript repo gets the TypeScript skill instead
    recommend: [javascript-skill]
```

## Shipped packages

| id | kind | scope | category |
|----|------|-------|----------|
| `context7` | mcp | project | docs |
| `github-mcp` | mcp | user | vcs |
| `chrome-devtools-mcp` | mcp | user | browser |
| `playwright-mcp` | mcp | user | browser |
| `sequential-thinking` | mcp | user | reasoning |
| `superpowers` | spine | user | workflow |
| `karpathy-claude-md` | claude_md | user | behavior |
| `mongodb-mcp` | mcp | project | database |
| `postgres-mcp` | mcp | project | database |
| `react-patterns-skill` | skill | project | frontend |
| `fastapi-skill` | skill | project | backend |
| `remotion-skill` | skill | project | media |
| `typescript-skill` | skill | project | language |
| `javascript-skill` | skill | project | language |
| `python-skill` | skill | project | language |
| `go-skill` | skill | project | language |
| `nextjs-skill` | skill | project | frontend |
| `vue-skill` | skill | project | frontend |
| `svelte-skill` | skill | project | frontend |
| `tailwind-skill` | skill | project | frontend |
| `express-skill` | skill | project | backend |
| `django-skill` | skill | project | backend |
| `flask-skill` | skill | project | backend |

Language and framework skills are matched by rules on the detected stack — e.g. a
Python + FastAPI repo gets `python-skill` and `fastapi-skill`, a TypeScript + React
repo gets `typescript-skill` and `react-patterns-skill`.

Some MCP servers need credentials (for example, `github-mcp` reads
`GITHUB_PERSONAL_ACCESS_TOKEN`). cchad never writes secrets — set them as environment
variables in your shell.
