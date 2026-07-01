---
name: typescript-conventions
description: Idiomatic, type-safe TypeScript. Use when writing or reviewing TypeScript.
---

# TypeScript conventions

## Types
- Turn on `strict` and keep it on. Fix type errors; don't paper over them.
- Avoid `any`. Reach for `unknown` at boundaries and narrow it, or write a proper
  type. Use `as` casts only when you truly know better than the compiler.
- Model states with discriminated unions (`type Result = Ok | Err`) instead of
  optional-field grab-bags. Let the compiler force you to handle every case.
- Prefer `type` aliases for unions and function types; use `interface` for object
  shapes you expect to extend or implement.

## Safety
- Don't abuse the non-null assertion `!`. Handle the `undefined` case or narrow it.
- Type function inputs and public return values explicitly; let inference handle
  local variables.
- Use `readonly` and `as const` for data that shouldn't change.

## Practical
- Derive types from a single source of truth (`typeof`, `keyof`, indexed access,
  utility types) rather than hand-copying shapes.
- Validate external data (API responses, env) at the boundary with a schema library
  so the rest of the code can trust its types.
