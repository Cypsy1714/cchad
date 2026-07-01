# Changelog

All notable changes to this project are documented here. The format is based on
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.1] - 2026-07-01

### Added
- **Baseline skills** matched by rules: language conventions for TypeScript,
  JavaScript, Python, and Go, plus framework skills for Next.js, Vue, Svelte,
  Tailwind, Express, Django, and Flask. (React, FastAPI, and Remotion shipped in 0.1.0.)
- Optional **`unless`** guard on rules, so the JavaScript skill is skipped on
  TypeScript repos.

## [0.1.0] - 2026-07-01

Initial release.

### Added
- **Stack detection** for JavaScript/TypeScript and Python (plus Go modules),
  reading `package.json`, `pyproject.toml`, `requirements*.txt`, `go.mod`, lockfiles,
  framework configs, and a file-extension histogram.
- **Curated catalog** of MCP servers, skills, a workflow spine, and a CLAUDE.md
  behavior block, defined entirely as data, with presets (`minimal`, `recommended`,
  `full`) and stack rules.
- **Deconfliction resolver**: one workflow spine, one browser MCP, explicit conflict
  handling, and an MCP-server cap — deterministic, with a reason for every drop.
- **Two-layer model**: a base layer applied to your user scope and a project layer
  recorded in a committed `auto_plugins_mcps.md` manifest.
- **Atomic apply** with `.bak` backups and `cchad rollback`.
- **Commands**: `setup`, `init`, `plan`, `apply`, `sync`, `update`, `add`, `remove`,
  `base list/add/remove`, `config path/edit`, and `rollback`, with `--json` output.
- **Claude Code plugin** with `/cchad:setup`, `/cchad:plan`, `/cchad:init`, and
  `/cchad:sync` slash commands.
- **Extensibility** via `[catalog].sources` (local or `github:` YAML), merged over
  the shipped catalog.

[Unreleased]: https://github.com/Cypsy1714/cchad/compare/v0.1.1...HEAD
[0.1.1]: https://github.com/Cypsy1714/cchad/compare/v0.1.0...v0.1.1
[0.1.0]: https://github.com/Cypsy1714/cchad/releases/tag/v0.1.0
