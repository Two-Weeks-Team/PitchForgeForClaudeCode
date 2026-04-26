---
description: Cross-cutting — generate 5 hero-copy candidates (one per inversion pattern) for the current run's project_one_liner. The hero copy is the YouTube title, the README h1, the F4 overlay, and the F11 echo.
---

# /pitch:hero [run_id]

Hands the brief's `project_one_liner` to `hero-copywriter` and produces
five candidates — one per inversion pattern. Cross-checks
`memory/HERO_CATALOG.md` to avoid near-duplicates of prior accepted
heroes.

## Usage

```bash
# Suggest 5 candidates for the most recent run
/pitch:hero

# Specify run
/pitch:hero runs/2026-04-27-preview-forge

# Constrain to one pattern
/pitch:hero --pattern=paper-title-inversion

# Force regeneration (skip cache)
/pitch:hero --no-cache
```

## Output

```markdown
# Hero candidates · <project_name>

| # | Pattern | Hero |
|---|---|---|
| 1 | paper-title-inversion | "Preview is all you need." |
| 2 | stop-start | "Stop wireframing. Start picking pictures." |
| 3 | first-reordering | "Result first." |
| 4 | confession | "We've been building backwards." |
| 5 | rule-of-three | "144 personas. One plugin. Two clicks." |

**Recommendation**: 1 (matches paradigm-shift framing for AI/ML audience).
**Catalog dedupe**: 0 conflicts.
```

## Acceptance

When you accept a hero, this command:

1. Updates `runs/<id>/brief.json` (`hero_copy`, `hero_pattern`).
2. Appends to `memory/HERO_CATALOG.md` for cross-run dedupe.
3. Triggers a re-run of `/pitch:scenario` so the new hero propagates
   into `frame-spec.json` (primary + echo placement).

## Cross-references

- `agents/writers/hero-copywriter.md`
- `methodology/02-hero-copy-patterns.md`
- `memory/HERO_CATALOG.md`
