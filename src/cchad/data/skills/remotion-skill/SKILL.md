---
name: remotion-conventions
description: Programmatic video with Remotion — compositions, timing, and rendering. Use when building Remotion videos.
---

# Remotion conventions

Guidance for building maintainable programmatic video with Remotion.

## Compositions
- Register each video as a `<Composition>` with explicit `durationInFrames`,
  `fps`, `width`, and `height`. Keep these in one constants file.
- Drive everything from props so the same composition renders many variations.

## Timing
- Treat frames as the unit of time. Convert seconds with `fps` (`seconds * fps`)
  rather than hard-coding frame numbers.
- Read the current frame with `useCurrentFrame()` and animate with
  `interpolate()` / `spring()`. Keep animation math pure and frame-driven so
  every render is deterministic.
- Clamp `interpolate` with `extrapolateLeft/Right: "clamp"` to avoid values
  running past their range.

## Structure
- Build small presentational components (a title, a lower-third, a transition)
  and compose them in a sequence with `<Sequence>`.
- Offset timing with `<Sequence from={…}>` instead of branching on the frame
  number inside a component.

## Rendering
- Keep assets deterministic: use `staticFile()` for bundled media and avoid
  randomness that isn't seeded.
- Render from the CLI (`npx remotion render`) in CI so output is reproducible.
