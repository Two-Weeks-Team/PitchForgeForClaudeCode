---
description: 6-gate pass/fail audit for a run. Runs every reviewer agent and stale-count hook against the latest artifacts.
---

# /pitch:status [run_id]

Runs the 6-gate audit. v0.1.0 ships gates G1, G2, G4, G5, G6 active and
G3 (judging coverage) as informational only.

## Usage

```bash
# Audit the most recent run
/pitch:status

# Specify run
/pitch:status runs/2026-04-27-preview-forge
```

## The six gates

| Gate | What it checks | Owner |
|---|---|---|
| **G1** brief filled-ratio | `_filled_ratio ≥ 0.5` (P1 output) | `brief-extractor` |
| **G2** timestamp rollup | `sum(duration_seconds) ≈ runtime ± 5%` | `scenario-architect` |
| **G3** judging coverage | every brief axis fires in ≥ 2 frames | `judging-criteria-auditor` (v0.5+) |
| **G4** tone-auditor | NEVER-list flag count == 0 | `tone-auditor` |
| **G5** stale counts | README + deck "what's inside" tables match `verify-plugin.sh` | `stale-count-detector` hook |
| **G6** modifier-key safety | keydown handler early-returns on `Cmd`/`Ctrl`/`Alt` | `cmd-modifier-guard` hook |

A run is **shippable** when all 6 gates pass.

## Output

```
=== PitchForge run runs/2026-04-27-preview-forge — status ===

Brief:           Preview Forge — 144 personas turn one-line idea into full-stack app
Runtime:         160s (target 160s · delta 0s)
Arc:             wow-first
Hero:            "Preview is all you need."
Frames:          13 (cover + 11 + close)

Gates:
  G1 brief filled-ratio:        ✅ 0.83
  G2 timestamp rollup:          ✅ exact
  G3 judging coverage:          ℹ  4/4 axes covered (≥ 2 frames each) — informational in v0.1.0
  G4 tone-auditor flags:        ✅ 0
  G5 stale counts:              ✅ 0 drift
  G6 modifier-key safety:       ✅

Verdict: shippable.

Artifacts:
  runs/<id>/brief.json
  runs/<id>/scenario.md
  runs/<id>/frame-spec.json
  runs/<id>/deck-config.json
  runs/<id>/storyboard.html
  runs/<id>/tone-audit.json
  runs/<id>/deck.html
  runs/<id>/deck-animated.html
  runs/<id>/deck-cinematic.html
  runs/<id>/recording-config.json
  runs/<id>/trace.jsonl
```

## Failure mode example

```
  G2 timestamp rollup:          ❌ delta 12s — F8 duration must shrink to 18s
  G4 tone-auditor flags:        ❌ 3 flags
    F2:STACCATO:too-long
    F4:HERO:paraphrased  ← Layer-0 violation
    F8:NEVER:hospitality-opener

Verdict: needs-attention. Run /pitch:tone or /pitch:reorder to fix.
```

## Cross-references

- `agents/meta/pitch-supervisor.md` § "Gates"
- `agents/reviewers/tone-auditor.md`
- `hooks/stale-count-detector.py`
- `hooks/cmd-modifier-guard.py`
