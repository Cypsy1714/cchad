---
name: react-patterns
description: Idiomatic React — hooks, composition, and clear state boundaries. Use when writing or reviewing React components.
---

# React patterns

Guidance for writing React that stays readable as it grows.

## Components
- Keep components small and single-purpose. If a component does two things,
  split it.
- Prefer composition (passing children / render props) over configuration via a
  growing list of boolean props.
- Derive state during render instead of storing values you can compute.

## Hooks
- Every `useEffect` needs a clear reason to exist. If it only transforms props
  into state, you probably don't need it — compute the value inline.
- List every dependency an effect reads. Don't silence the linter; fix the
  dependency.
- Extract reused stateful logic into a custom `useX` hook rather than copying
  effect bodies between components.

## State
- Keep state as local as possible; lift it only when two components truly share
  it.
- Model server data with a data-fetching library (React Query / SWR) instead of
  hand-rolled `useEffect` + `useState` loading flags.
- Keep a single source of truth. Don't mirror the same value in two states.

## Rendering
- Give lists stable `key`s tied to identity, never the array index.
- Reach for `useMemo` / `useCallback` only when you have a measured performance
  problem, not by default.
