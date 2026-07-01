---
description: Detect this repo's stack and configure Claude Code (MCP servers + skills).
---
Help the user configure Claude Code for the current repository with cchad.

1. Run `uvx cchad plan --json` in the current working directory with the Bash tool
   and read the JSON plan.
2. Summarize it in chat: the packages to add (id, scope, why) and the ones
   deliberately skipped (with reason).
3. Ask the user to confirm.
4. On confirmation, run `uvx cchad init --yes` with the Bash tool.
5. Surface any manual steps from the output (cchad never runs installers itself).
6. Tell the user to reload Claude Code (or restart) so the new MCP servers and
   skills load, and to commit `auto_plugins_mcps.md` so teammates get the same setup.
