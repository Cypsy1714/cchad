# CLI reference

Run `cchad --help` or `cchad <command> --help` for the built-in version.

## Global flags

| Flag | Meaning |
|------|---------|
| `--version` | Print the version and exit. |
| `--json` | Machine-readable output (on `plan`, `init`, `update`). |
| `--yes`, `-y` | Skip confirmation prompts. |
| `--plan-only` | Show the plan and stop (on `init`). |
| `--no-base` | Ignore the base layer; resolve only from the repo's stack. |
| `--scope user\|project` | Override where a package installs (on `add`). |

## Commands

### `cchad setup`
Pick a base layer, save it to `config.toml`, and apply it to your **user** scope.

```bash
cchad setup                       # interactive
cchad setup --preset full --yes   # non-interactive
cchad setup --no-apply            # write config only
```

### `cchad init`
Detect this repo's stack, resolve a plan, preview it, apply the **project** layer, and
write the manifest.

```bash
cchad init            # preview, confirm, apply
cchad init --yes      # apply without confirming
cchad init --plan-only
cchad init --json     # print the plan as JSON (preview only unless --yes)
```

### `cchad plan`
Preview what cchad would configure, plus a diff against the committed manifest. Writes
nothing.

```bash
cchad plan
cchad plan --json
cchad plan --no-base
```

### `cchad apply`
Apply this repo's **committed manifest** to local config (atomic, with backups).

### `cchad sync`
Rebuild local config from the committed manifest — the teammate-onboarding command.
Idempotent.

```bash
cchad sync --yes
```

### `cchad update`
Reload the catalog (including your `[catalog].sources`) and show how the repo has
drifted from its manifest. Run `cchad init` to apply the drift.

### `cchad add` / `cchad remove`
Add or remove a project package directly in the manifest, and install/uninstall it.

```bash
cchad add postgres-mcp
cchad remove mongodb-mcp
```

> Note: `cchad init` regenerates the manifest from detection + rules, so a manual
> `add` may be dropped on the next `init`. Use `add`/`remove` for quick tweaks; for
> durable changes, add a rule or a `[catalog].source`.

### `cchad base list | add | remove`
Manage your base layer.

```bash
cchad base list
cchad base add sequential-thinking
cchad base remove chrome-devtools-mcp
```

### `cchad config path | edit`
Print or open your config file.

```bash
cchad config path
cchad config edit          # opens $EDITOR
```

### `cchad rollback`
Undo the last apply, restoring every file from its `.bak` backup (and deleting files
that apply created).
