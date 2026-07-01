# The Claude Code plugin

cchad ships a thin Claude Code plugin so you can drive it without leaving the chat.
The plugin only calls the CLI — all the logic lives in the Python engine, so both
entry points behave identically.

## Install

```
/plugin marketplace add Cypsy1714/cchad
/plugin install cchad@cchad
```

The marketplace manifest lives at the repo root (`.claude-plugin/marketplace.json`)
and points at the plugin in [`plugins/cchad/`](../plugins/cchad).

## Commands

| Slash command | Runs | Purpose |
|---------------|------|---------|
| `/cchad:setup` | `uvx cchad setup …` | Pick a baseline (once). |
| `/cchad:plan` | `uvx cchad plan` | Preview the plan for this repo. |
| `/cchad:init` | `uvx cchad plan --json` → `uvx cchad init --yes` | Configure this repo. |
| `/cchad:sync` | `uvx cchad sync --yes` | Reproduce a committed manifest. |

`uvx` fetches the published package on first use, so there's no separate install step.

## How confirmation works

A `[y/N]` prompt inside a Bash tool call would block on stdin, so the plugin never
relies on interactive prompts. Instead `/cchad:init`:

1. runs `uvx cchad plan --json` and reads the machine-readable plan,
2. shows you the adds and skips in chat and asks you to confirm,
3. runs `uvx cchad init --yes` only after you say yes.

## After applying

Reload plugins or restart Claude Code so newly added MCP servers and skills load, and
commit `auto_plugins_mcps.md` so your teammates get the same setup. If the plan lists
a manual step (like installing the Superpowers plugin), the assistant surfaces the
exact command — cchad never runs installers for you.
