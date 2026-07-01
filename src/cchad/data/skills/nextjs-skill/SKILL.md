---
name: nextjs-conventions
description: Next.js App Router patterns. Use when building or reviewing Next.js apps.
---

# Next.js conventions

## Components
- Default to Server Components. Add `"use client"` only where you need state, effects,
  or browser APIs — and push it as far down the tree as possible.
- Fetch data in Server Components with `async`/`await`; don't ship data-fetching
  `useEffect` to the client when the server can do it.

## Routing & data
- Use the App Router (`app/`): `layout`, `page`, `loading`, `error`, and route handlers
  in `route.ts`.
- Colocate data fetching with the component that needs it and rely on the framework's
  caching/revalidation instead of hand-rolled caches.
- Stream with Suspense boundaries so slow data doesn't block the whole page.

## Practical
- Put metadata in the `metadata` export, not manual `<head>` tags.
- Keep secrets server-side; only `NEXT_PUBLIC_*` env vars reach the browser.
- Use `next/image` and `next/font` for images and fonts.
