# Contributing to cchad

Thanks for helping! Most contributions are small and welcome — especially new
catalog packages and detection rules.

## Development setup

cchad uses [uv](https://docs.astral.sh/uv/).

```bash
git clone https://github.com/Cypsy1714/cchad
cd cchad
uv sync                 # create the environment and install dev deps

uv run ruff check .     # lint
uv run pytest           # test
uv run cchad --help     # run the CLI from source
```

Before opening a PR, make sure both `ruff check .` and `pytest` pass. CI runs them on
Python 3.12 and 3.13.

## Adding a package

Edit [`src/cchad/data/catalog.yaml`](src/cchad/data/catalog.yaml) and add an entry
(see the [catalog reference](docs/catalog.md) for the fields). Keep the catalog
**curated** — prefer a few high-value packages over many. If the package should be
recommended for a stack, add a rule too.

## Adding a rule

Edit [`src/cchad/data/rules.yaml`](src/cchad/data/rules.yaml):

```yaml
- when: [django]
  recommend: [django-mcp]
```

If the signal (`django`) isn't detected yet, add it to
[`src/cchad/detect/mappings.py`](src/cchad/detect/mappings.py) and cover it with a test
in `tests/test_detect.py`.

## Guidelines

- **Keep it simple.** Small, focused changes. No new dependencies without a reason.
- **Data over code.** Prefer extending the YAML data files to adding logic.
- **Test behavior.** Add or update a test for any behavior change.
- **Never auto-run installers.** cchad writes config and installs from catalog
  sources only — keep it that way.

## Commit and PR

- Write clear commit messages (imperative mood: "Add …", "Fix …").
- Fill in the pull request template.
- One logical change per PR keeps review easy.

By contributing, you agree that your contributions are licensed under the
[MIT License](LICENSE).
