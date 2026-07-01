---
description: Choose your cchad baseline and apply it to your user scope (run once).
---
Help the user pick a cchad baseline that applies across all their projects.

1. Explain the three presets briefly: **minimal**, **recommended** (default), **full**.
2. Ask which they want.
3. Run `uvx cchad setup --preset <choice> --yes` with the Bash tool.
4. Report what was written, and surface any manual steps the output lists (for
   example, installing the Superpowers plugin). cchad never runs installers for
   the user — relay those commands for them to run.
5. Tell them to open a repo and run `/cchad:init` next.
