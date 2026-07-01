---
name: vue-conventions
description: Vue 3 Composition API patterns. Use when building or reviewing Vue apps.
---

# Vue conventions

## Components
- Use `<script setup>` with the Composition API for new components.
- Keep components focused; extract reusable stateful logic into composables (`useX`).
- Type props and emits explicitly (`defineProps`, `defineEmits`).

## Reactivity
- Use `ref` for primitives and `reactive` for objects; don't destructure a `reactive`
  object (it breaks reactivity) — use `toRefs` if you must.
- Derive values with `computed` instead of watchers that write back state.
- Reach for `watch`/`watchEffect` only for genuine side effects, and clean them up.

## Practical
- Keep templates declarative; move complex expressions into `computed`.
- Use `key` on `v-for`, tied to stable identity, never the index.
- Prefer a store (Pinia) for shared state over prop-drilling or event buses.
