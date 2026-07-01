## Engineering guidelines

**Think before coding.** Restate the problem in your own words. List the
constraints and the simplest thing that could possibly work before writing any
code. If the task is ambiguous, ask one clarifying question instead of guessing.

**Prefer the simplest design that works.** Fewer moving parts, fewer
abstractions, less cleverness. Three similar lines beat one premature helper.
Do not add features, options, or layers that the task did not ask for.

**Make surgical changes.** Touch only what the task requires. Do not refactor,
rename, or reformat unrelated code in the same change. Keep diffs small and
reviewable.

**Match the code that is already here.** Follow the existing naming, structure,
and patterns of the file you are editing rather than importing your own style.

**Write for the next reader.** Clear names over comments. Comment only the
non-obvious "why", never the "what". Delete dead code instead of commenting it
out.

**Verify your work.** Run the tests and linters. Reproduce the bug before you
fix it, and confirm the fix. Do not claim something works if you have not
checked it.
