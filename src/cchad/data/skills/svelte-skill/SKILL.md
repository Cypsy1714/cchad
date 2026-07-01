---
name: svelte-conventions
description: Svelte and SvelteKit patterns. Use when building or reviewing Svelte apps.
---

# Svelte conventions

## Components
- Keep components small and let Svelte's reactivity do the work — assign to a variable
  to trigger updates rather than calling setters.
- Derive values reactively (`$:` in Svelte 4, `$derived` in Svelte 5 runes) instead of
  duplicating state.
- Lift shared state into stores (or runes) and subscribe with `$store`.

## SvelteKit
- Load data in `+page.server.ts` / `+page.ts` `load` functions, not in `onMount`.
- Keep secrets in server files (`+server.ts`, `$env/static/private`); never import them
  into client code.
- Use form actions for mutations so things work without JavaScript, then enhance.

## Practical
- Scope styles to the component by default; reach for `:global` sparingly.
- Clean up subscriptions and timers in `onDestroy`.
