---
name: express-conventions
description: Express.js API patterns. Use when building or reviewing Express servers.
---

# Express conventions

## Structure
- Split routes into `Router`s per resource; keep handlers thin and put business logic
  in a service layer.
- Validate and parse input at the edge (a schema library) before it reaches logic.
- Centralize configuration; read env once into a typed config object.

## Middleware & errors
- Order middleware deliberately: parsers → auth → routes → error handler last.
- Wrap async handlers so rejected promises reach your error middleware (or use a
  helper / Express 5's built-in async handling) — don't let errors go unhandled.
- Use a single error-handling middleware that maps errors to status codes; don't leak
  stack traces to clients.

## Practical
- Never build SQL or shell strings from user input; use parameterized queries.
- Set security headers (helmet), enable CORS intentionally, and rate-limit public APIs.
- Return consistent JSON shapes and correct status codes.
