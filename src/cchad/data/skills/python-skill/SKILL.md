---
name: python-conventions
description: Idiomatic, readable Python. Use when writing or reviewing Python.
---

# Python conventions

## Style
- Follow PEP 8; let a formatter (ruff/black) settle layout so you don't argue about it.
- Add type hints to function signatures. Prefer `X | None` over `Optional[X]` on 3.10+.
- Use f-strings for formatting.

## Data & structure
- Reach for `dataclasses` (or Pydantic at boundaries) instead of ad-hoc dicts for
  structured data.
- Use comprehensions for simple transforms; a plain loop when logic gets involved.
- Use `pathlib.Path` for filesystem paths, not string concatenation.
- Manage resources with `with` (context managers), not manual open/close.

## Robustness
- Catch specific exceptions, not bare `except:`. Add context and re-raise with `from`.
- Prefer standard library before adding a dependency.
- Keep functions small and single-purpose; return early instead of nesting.

## Environment
- Use a virtual environment (uv/venv). Pin dependencies in `pyproject.toml`.
