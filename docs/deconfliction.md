# Deconfliction

Deconfliction is why cchad exists. More tools is not better: two workflow spines or
two browser MCPs fight each other and degrade the agent. The resolver produces a
minimal, non-conflicting set — deterministically, with a reason for every drop.

## The algorithm

Given the catalog, the detected stack, and your config, the resolver runs these steps
in order:

1. **Base set** — `expand(preset) + enable − disable` from your config.
2. **Project set** — the union of `recommend` from every rule whose `when` signals are
   all present in the stack.
3. **Candidates** — base ∪ project, each tagged with its `default_scope`. Base
   membership wins the "why" label.
4. **Single spine** — if more than one `kind: spine` is a candidate, keep the one named
   by `policy.spine` (or the highest priority) and drop the rest.
5. **Single browser** — the same rule for `category: browser`, using `policy.browser`.
6. **Conflicts** — walk candidates in priority order; drop any whose `conflicts_with`
   intersects an already-kept package (checked both directions).
7. **Cap** — limit `kind: mcp` to `policy.max_mcp_servers`, keeping the highest
   priority; the overflow is skipped.

The output is a **plan**: `add` (id, scope, reason) and `skip` (id, reason).

## Determinism

Ties are always broken by `priority` (higher first), then by `id`. The same inputs
always produce the same plan, so `cchad plan` is reproducible and reviewable.

## Worked example

Config uses `recommended` and also enables `playwright-mcp`, with
`max_mcp_servers = 3`. The repo detects `mongodb` and `postgres`.

- Candidates: context7, github-mcp, chrome-devtools-mcp, playwright-mcp, superpowers,
  karpathy-claude-md, mongodb-mcp, postgres-mcp.
- **Single browser** drops `playwright-mcp` (kept `chrome-devtools-mcp`).
- **Cap (3)** keeps the three highest-priority MCPs — context7 (80), github-mcp (70),
  chrome-devtools-mcp (60) — and skips `mongodb-mcp` and `postgres-mcp`.

Result:

```
add:  context7, github-mcp, chrome-devtools-mcp, superpowers, karpathy-claude-md
skip: playwright-mcp  (only one browser tool allowed; kept 'chrome-devtools-mcp')
      mongodb-mcp     (MCP server cap reached (max=3))
      postgres-mcp    (MCP server cap reached (max=3))
```

## Tuning

- Change the winner: set `policy.browser` or `policy.spine` to another id.
- Allow more servers: raise `policy.max_mcp_servers`.
- Force a package in or out: `cchad base add/remove` (base) or `cchad add/remove`
  (project), or add `conflicts_with` / `priority` in the catalog.
