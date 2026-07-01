---
name: javascript-conventions
description: Modern, readable JavaScript. Use when writing or reviewing plain JavaScript.
---

# JavaScript conventions

## Language
- Use `const` by default, `let` when you must reassign, never `var`.
- Use `===` / `!==`; avoid the coercing `==`.
- Prefer `async`/`await` over raw promise chains, and always handle rejections.
- Use ES modules (`import`/`export`), not CommonJS, in new code.

## Data
- Favor immutable transforms — `map`, `filter`, `reduce`, spread — over mutating loops.
- Use optional chaining (`?.`) and nullish coalescing (`??`) instead of long `&&`
  guards or `||` that swallows `0`/`""`.
- Destructure to name what you use.

## Structure
- Small, pure functions where possible; isolate side effects.
- Fail fast with early returns instead of deep nesting.
- Throw `Error` objects (not strings) and add context to the message.
