# Contributing to PitchForge

Welcome. This document is the only contract you need to read.

## Language

All artifacts in this repository are written in **English**. That includes:
issues, pull requests, commits, code, comments, voiceover scripts in
methodology examples, on-screen text in templates. Korean (and any other
language) is permitted **only** as a burnt-in subtitle layer in the final
captured video — the video itself is a visual artifact, not a repo artifact.

This rule was inherited from the Preview Forge sibling plugin where the
inconsistency cost a full review cycle. We are not repeating that mistake.

## Commit messages

[Conventional Commits](https://www.conventionalcommits.org/). `release-please`
auto-bumps the version on merge. Examples:

```
feat(commands): add /pitch:reorder timestamp reflow
fix(rec-mode): grid-template-rows must be 1fr in body.rec
docs(methodology): document the em-dash held-breath convention
test(fixtures): regression for L1 — modifier-key safety
```

Scope examples: `commands` / `agents` / `methodology` / `templates` /
`schemas` / `hooks` / `examples` / `docs`.

## Adding a frame shape (v0.5+)

1. Author `plugins/pitch/templates/frame-shapes/<id>.html` per the
   shape contract in `methodology/05-frame-shape-library.md`.
2. Validate against `schemas/frame-shape.schema.json`.
3. Add a row to the shape table in `methodology/05`.
4. Add a fixture in `tests/fixtures/frame-shapes/<id>/`.
5. Reference it from at least one `examples/` deck.

## Adding a narrative arc (v2.0+)

1. Author `plugins/pitch/templates/narrative-arcs/<arc>-<runtime>.json`
   per the schema.
2. Document it in `methodology/01-narrative-arcs.md` (new section).
3. Add a heuristic-selection rule update in `agents/writers/scenario-architect.md`.
4. Add an example deck under `examples/<project>-<arc>/`.

## Adding a hero copy pattern

1. Document the pattern in `methodology/02-hero-copy-patterns.md` with:
   examples, when-to-use, when-to-avoid, voiceover delivery rule.
2. Add the pattern enum value to `schemas/pitch-brief.schema.json`.
3. Update `agents/writers/hero-copywriter.md` with the generation rule.

## Adding a methodology lesson

When a run exposes a recurring failure that future runs should avoid, append
to `plugins/pitch/memory/LESSONS.md` using the documented format. Add the
fixture to `tests/fixtures/<lesson-name>/`. Reference the lesson ID in any
PR that addresses the underlying code.

## CI

PRs run `bash scripts/verify-plugin.sh` on:

- ubuntu-latest (Linux)
- macos-14 (Apple Silicon)

Both must pass before merge.

## Code review

Reviewers check, in order:

1. Conventional Commit message + clear scope.
2. CHANGELOG.md updated under `[Unreleased]`.
3. Methodology doc updated if the change is in scope.
4. Tests added if a new failure mode is being prevented.
5. `verify-plugin.sh` passes locally.
6. No stale counts in README or templates.
7. No Korean (or non-English) text in non-burnt-in artifacts.
