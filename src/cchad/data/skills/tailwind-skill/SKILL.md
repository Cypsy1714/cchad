---
name: tailwind-conventions
description: Tailwind CSS patterns. Use when styling with Tailwind.
---

# Tailwind conventions

## Utilities first
- Compose utilities in markup; that's the point. Reach for a component abstraction
  (React/Vue component) to reuse styles, not a pile of `@apply`.
- Use `@apply` sparingly, only for small, genuinely repeated primitives.

## Design system
- Drive spacing, colors, and typography from `tailwind.config` tokens, not one-off
  arbitrary values like `mt-[13px]`. Extend the theme instead of hard-coding.
- Keep a consistent scale; if you keep reaching for arbitrary values, add a token.

## Responsive & state
- Build mobile-first: unprefixed base, then `sm:`/`md:`/`lg:` overrides.
- Use state variants (`hover:`, `focus:`, `disabled:`, `dark:`) rather than custom CSS.

## Practical
- Order long class lists consistently (a plugin like prettier-plugin-tailwindcss helps).
- Extract truly repeated multi-utility patterns into components; don't copy-paste them.
