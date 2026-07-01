# Configuration

Your personal, global choices live in **`~/.config/cchad/config.toml`**
(or `$XDG_CONFIG_HOME/cchad/config.toml`). It is not committed — it governs your
[base layer](concepts.md) and the deconfliction policy. Edit it directly or with
`cchad config edit`.

```toml
[base]
preset  = "recommended"          # minimal | recommended | full
enable  = ["sequential-thinking"] # extra base packages on top of the preset
disable = ["chrome-devtools-mcp"] # preset items to drop

[policy]
max_mcp_servers = 5
browser = "chrome-devtools-mcp"  # which single browser MCP wins
spine   = "superpowers"          # which single workflow spine wins

[catalog]
sources = [
  "~/.config/cchad/my-catalog.yaml",
  "github:my-org/cchad-catalog",
]
```

## `[base]`

| Key | Default | Meaning |
|-----|---------|---------|
| `preset` | `"recommended"` | The named bundle that seeds your base layer. |
| `enable` | `[]` | Extra package ids to add on top of the preset. |
| `disable` | `[]` | Package ids from the preset to remove. |

The base set is `expand(preset) + enable − disable`. Manage it with
`cchad base add/remove`, which edit `enable`/`disable` for you.

## `[policy]`

| Key | Default | Meaning |
|-----|---------|---------|
| `max_mcp_servers` | `5` | Cap on active MCP servers; the lowest-priority overflow is skipped. |
| `browser` | `"chrome-devtools-mcp"` | The single browser MCP kept when more than one is a candidate. |
| `spine` | `"superpowers"` | The single workflow spine kept when more than one is a candidate. |

Set `browser` or `spine` to a different catalog id to change the winner. Both apply
whenever the project layer resolves on top of your base — see
[deconfliction](deconfliction.md).

## `[catalog]`

| Key | Default | Meaning |
|-----|---------|---------|
| `sources` | `[]` | Extra catalog YAMLs merged on top of the shipped one. |

Each source may be a local path or a `github:owner/repo` reference and can add
`packages`, `presets`, and `rules`. Later sources override earlier ones by `id`. See
[extending](extending.md).

A missing config file is equivalent to all defaults, so cchad works out of the box
before you ever run `cchad setup`.
