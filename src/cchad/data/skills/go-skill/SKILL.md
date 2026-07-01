---
name: go-conventions
description: Idiomatic Go. Use when writing or reviewing Go.
---

# Go conventions

## Errors
- Return errors, don't panic in library code. Check every returned error.
- Wrap with context: `fmt.Errorf("loading config: %w", err)`, and compare with
  `errors.Is` / `errors.As`.

## Design
- Keep interfaces small and define them where they're consumed, not where they're
  implemented. Accept interfaces, return concrete types.
- Zero values should be useful; avoid constructors that only set defaults.
- Use `defer` for cleanup right after acquiring a resource.

## Concurrency
- Pass `context.Context` as the first argument to blocking calls and honor cancellation.
- Don't start a goroutine without knowing how it stops. Guard shared state with a
  mutex or a channel — "share memory by communicating."

## Practical
- Run `gofmt`/`go vet`; keep code `go test ./...`-green.
- Handle errors at the point you have enough context; don't log-and-return the same error.
