# Security Policy

## Reporting a vulnerability

Please report security issues privately using GitHub's
[private vulnerability reporting](https://github.com/Cypsy1714/cchad/security/advisories/new)
(Security → Report a vulnerability). Do not open a public issue for a vulnerability.

We'll acknowledge your report and work with you on a fix and disclosure timeline.

## Security model

cchad is designed to be safe by default:

- **Plan before apply.** Nothing is written without a preview.
- **Atomic writes and backups.** Every file is written atomically and backed up to
  `<file>.bak`; `cchad rollback` restores the last apply. Your existing `.mcp.json`
  and `.claude/` are never corrupted.
- **No auto-run installers.** cchad only writes configuration and installs from the
  sources listed in its catalog. It never executes an untrusted install script.
  Packages that require running a plugin installer are surfaced as a manual step with
  the exact command for you to review and run.
- **No secrets in committed files.** MCP servers that need credentials reference
  environment variables. cchad never writes tokens into `auto_plugins_mcps.md` or any
  committed file.

## Trusting catalog sources

`[catalog].sources` fetches YAML **data** (package definitions), never executable
code. Still, only add sources you trust — a package's `source` becomes a command that
Claude Code may run when it starts the MCP server. Review third-party catalogs the
same way you would review a dependency.
