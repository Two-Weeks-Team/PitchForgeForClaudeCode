---
description: Phase P3 only — render storyboard.html from frame-spec.json for static visual review. No animations; this is the gate-H1 review surface.
---

# /pitch:storyboard [run_id]

Renders the storyboard. Each frame is a static, full-quality canvas
stacked vertically. The user scrolls and approves before P4 onwards.

## Usage

```bash
# Render storyboard for the most recent run
/pitch:storyboard

# Specify run
/pitch:storyboard runs/2026-04-27-preview-forge
```

## What runs

`frame-designer` reads `runs/<id>/frame-spec.json` plus the matching
`templates/frame-shapes/<shape>.html` per frame, splices slot variables,
and emits `runs/<id>/storyboard.html`.

`color-arc-designer` runs as a side-effect to substitute palette tokens
into each frame's accent color.

## Outputs

- `runs/<id>/storyboard.html` — single self-contained HTML.

Open it in a browser. Approve via `/pitch:status` (which runs the 6-gate
audit; G3 judging coverage runs here in particular).

## Why this exists separately from `/pitch:deck`

The storyboard is **static**. The deck is **navigable**. P3 is the
emotional review (does the visual story work?). P5 is the assembly
review (does the deck function as a single artifact?). They should not
be conflated.

## Cross-references

- `agents/designers/frame-designer.md`
- `agents/designers/color-arc-designer.md`
- `methodology/05-frame-shape-library.md`
