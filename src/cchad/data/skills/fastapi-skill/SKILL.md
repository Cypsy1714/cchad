---
name: fastapi-conventions
description: FastAPI routing, dependency injection, and async patterns. Use when building or reviewing FastAPI backends.
---

# FastAPI conventions

Guidance for building FastAPI services that stay clean under growth.

## Structure
- Group routes with `APIRouter` per resource; keep one router per module.
- Put request/response shapes in Pydantic models. Never accept or return raw
  `dict`s at the boundary — let the schema validate.
- Separate the web layer (routers) from business logic (services) so handlers
  stay thin.

## Dependencies
- Use `Depends()` for shared concerns: database sessions, the current user,
  settings. Don't reach for globals.
- Build a single settings object with `pydantic-settings` and inject it, rather
  than reading `os.environ` throughout the code.

## Async
- If a handler does I/O, make it `async` and use async clients. Never call a
  blocking library inside an async handler — offload it with `run_in_threadpool`.
- Open and close resources (DB sessions, HTTP clients) with dependencies or
  lifespan handlers, not per-request globals.

## Errors & validation
- Raise `HTTPException` with a precise status code; let Pydantic return 422 for
  bad input automatically.
- Return explicit response models so the OpenAPI schema stays accurate.
