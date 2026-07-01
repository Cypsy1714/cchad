# Concepts

cchad is small once you know its vocabulary.

## Packages

A **package** is one installable unit. Every package has a `kind`:

| Kind | What it is | How it's applied |
|------|-----------|------------------|
| `mcp` | An MCP server | an entry in `.mcp.json` (project) or `~/.claude.json` (user) |
| `skill` | A Claude Code skill | a directory under `.claude/skills/` |
| `spine` | A workflow framework | a Claude Code plugin (manual step) |
| `claude_md` | A behavior block | a fenced block in `CLAUDE.md` |

Packages are defined once, as data, in the [catalog](catalog.md).

## The two layers

cchad separates *who you are* from *what a repo needs*.

- **Base layer** — packages you want across all projects. Installed once into your
  **user** scope (`~/.claude/`). Chosen with a preset and stored in your
  [config](configuration.md). Applied by `cchad setup`.
- **Project layer** — packages a specific repo needs, auto-detected from its stack.
  Installed into the **project** scope and recorded in the committed
  [manifest](manifest.md). Applied by `cchad init`.

Each package declares a `default_scope` (`user` or `project`) that decides which
layer it belongs to. A `user`-scoped package installs globally; a `project`-scoped
one installs per-repo and is shared through the manifest.

## Presets and rules

- A **preset** is a named bundle of base packages: `minimal`, `recommended`
  (default), or `full`. It selects your base layer.
- A **rule** maps a detected stack signal to package recommendations — e.g.
  `mongodb` → `mongodb-mcp`. Rules select the project layer.

## The flow

```
detect stack ─▶ resolve (base + rules, then deconflict) ─▶ plan ─▶ apply ─▶ manifest
```

1. **Detect** — read `package.json`, `pyproject.toml`, lockfiles, configs, and file
   extensions into a normalized stack descriptor.
2. **Resolve** — combine the base layer and the matching rules, then
   [deconflict](deconfliction.md): one spine, one browser, drop conflicts, cap MCPs.
3. **Plan** — the result: packages to add (with scope and reason) and packages
   skipped (with reason). Preview it before anything is written.
4. **Apply** — write real config files, atomically, with backups.
5. **Manifest** — record the project layer in `auto_plugins_mcps.md` so the team
   shares it.

## Files at a glance

| File | Scope | Committed? | Purpose |
|------|-------|-----------|---------|
| `~/.config/cchad/config.toml` | personal | no | your base choices + policy |
| `<repo>/auto_plugins_mcps.md` | team | **yes** | the project lockfile |
| `<repo>/.mcp.json` | project | usually | MCP servers for the repo |
| `~/.claude.json`, `~/.claude/` | user | no | your global Claude Code config |
