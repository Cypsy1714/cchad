---
name: flask-conventions
description: Flask patterns. Use when building or reviewing Flask apps.
---

# Flask conventions

## Structure
- Use the application factory pattern (`create_app`) and register Blueprints per
  feature, so testing and configuration stay clean.
- Keep view functions thin; put logic in a service layer or model methods.
- Load configuration from the environment into a config object; keep secrets out of code.

## Requests & data
- Validate and deserialize input with a schema library (Pydantic / Marshmallow) instead
  of poking at `request.json` directly.
- Use parameterized queries or an ORM (SQLAlchemy); never build SQL from user input.
- Manage resources (DB sessions) via extensions or app/request lifecycle, not globals.

## Practical
- Return explicit status codes and consistent JSON for APIs.
- Register error handlers that map exceptions to responses; don't leak stack traces.
- Keep blueprints and extensions initialized in one place to avoid circular imports.
