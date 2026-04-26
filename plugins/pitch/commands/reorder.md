---
description: Cross-cutting — swap slide order, then auto-reflow every timestamp, the SLIDE_DURATION array, the summaries array, the cinematic button labels, and the progress widths. Never edit timestamps by hand (L4).
---

# /pitch:reorder [run_id] <new_order>

The most error-prone manual operation in the original session. Eleven
separate `time` fields, one JS array, one summaries array, one set of
button labels — eleven places to drift.

This command regenerates all of them from one source: `frame-spec.json`.

## Usage

```bash
# Move F4 to position 2 (the wow-first arc layout)
/pitch:reorder cover,F4,F1,F2,F3,F5,F6,F7,F8,F9,F10,F11,close

# Specify run id
/pitch:reorder runs/2026-04-27-preview-forge cover,F4,F1,F2,F3,F5,...,close

# Pre-set arcs by name
/pitch:reorder --arc=problem-first
```

## What runs

1. **scenario-architect** reads the current `frame-spec.json` and the new
   order. It rewrites `position` and `time_start_seconds` for every
   frame.
2. **deck-assembler** re-derives `deck-config.json` (palette stays;
   slide_duration_seconds[], summaries[], progress_widths_pct[],
   ranges{} all reflow).
3. **animation-engineer** runs to confirm no per-element delays became
   absurd (a frame that was 30s and is now 10s requires the L3 hero
   stagger override).
4. **recording-engineer** updates the cinematic button labels +
   `playRange()` start/end positions in the keymap.

## Validation

Before writing back, the supervisor runs:

- `sum(duration_seconds) ∈ [runtime * 0.95, runtime * 1.05]` (G2).
- Every `frame_id` in the new order is present in the old spec exactly
  once.
- The hero's `primary_frame` and `echo_frame` are still in the order;
  if not, the hero placement is recomputed.

## Outputs

All of these are overwritten:

- `runs/<id>/scenario.md`
- `runs/<id>/frame-spec.json`
- `runs/<id>/deck-config.json`
- `runs/<id>/deck.html`
- `runs/<id>/deck-animated.html`
- `runs/<id>/deck-cinematic.html`

A reorder is a full regeneration of P2 onwards. P1 (the brief) is
unchanged.

## Cross-references

- `memory/LESSONS.md#L4` — reordering must reflow all eleven places.
- `agents/writers/scenario-architect.md`
- `agents/engineers/deck-assembler.md`
