# Extending cchad

You don't need to fork cchad to add packages. There are two layers of extensibility.

## 1. Ship-level (contributions)

Grow the shipped [`catalog.yaml`](../src/cchad/data/catalog.yaml),
[`presets.yaml`](../src/cchad/data/presets.yaml), and
[`rules.yaml`](../src/cchad/data/rules.yaml) and open a PR. Everyone gets the new
options on their next `cchad` upgrade. Adding a package or rule is usually a one-line
change — see [CONTRIBUTING](../CONTRIBUTING.md).

## 2. User / team-level (`[catalog].sources`)

Point cchad at your own YAML in `~/.config/cchad/config.toml`:

```toml
[catalog]
sources = [
  "~/.config/cchad/my-catalog.yaml",   # a local file
  "github:my-org/cchad-catalog",       # a git-hosted file
]
```

Each source is a YAML document that may add any of `packages`, `presets`, and `rules`
— the same schema as the shipped files ([catalog reference](catalog.md)):

```yaml
packages:
  - id: redis-mcp
    kind: mcp
    name: Redis MCP
    description: Inspect and query Redis from Claude Code.
    source: "npx -y @my-org/redis-mcp"
    install_method: mcp_json
    category: database
    default_scope: project
    priority: 45

rules:
  - when: [redis]
    recommend: [redis-mcp]

presets:
  team: [context7, github-mcp, redis-mcp, karpathy-claude-md]
```

### Merge rules

- Sources are applied **after** the shipped catalog, in the order listed.
- **Packages** and **presets** override earlier ones by `id` / name — so you can
  redefine `context7` to use a different source, or add a `team` preset.
- **Rules** are appended.

### `github:` source format

| Form | Fetches |
|------|---------|
| `github:owner/repo` | `catalog.yaml` at the repo root, default branch |
| `github:owner/repo/path/to/file.yaml` | that file |
| `github:owner/repo#v1.2.0` | pinned to a ref |

A source that can't be loaded prints a warning and is skipped — it never crashes the
CLI.

## Adding a detection signal

If your rule needs a signal cchad doesn't detect yet, add it to the mapping tables in
[`src/cchad/detect/mappings.py`](../src/cchad/detect/mappings.py) (a dependency name,
a config file, or a file extension → a signal) and open a PR.
