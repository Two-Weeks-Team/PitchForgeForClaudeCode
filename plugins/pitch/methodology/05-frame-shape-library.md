# Methodology 05 — Frame Shape Library (Phase P3 / P5 / P6)

Every frame in a deck reduces to one of nine reusable shapes. Each shape is
a CSS-rendered canvas mockup with declared animation hooks.

## The nine shapes

| ID | Use case | Reference frame in `examples/preview-forge-160s/` |
|---|---|---|
| `chain` | A → B → C → ? sequence with stagger animation | F1, F3 |
| `stack-strikethrough` | List of failure cases with strikethrough draw | F2 |
| `counter-roll` | Single huge number rolling 0 → N | F5 |
| `gallery-hero` | N×M tile grid + hero copy overlay (the wow shot) | F4, F8 |
| `hierarchy-diagram` | SVG tier diagram with sequential light-up | F6 |
| `modal-live-json` | Form / modal on left + live-filling JSON on right | F7 |
| `triple-pane` | 3-column split with independent timelines | F9 |
| `terminal-browser` | Terminal log + auto-launching browser tab | F10 |
| `repo-install` | Repo URL + badges + install snippet typewriter | F11 |

## Shape contract

Every shape file in `templates/frame-shapes/<id>.html` provides:

1. **Static skeleton** — HTML structure with `data-anim` attributes on animated elements.
2. **Slot variables** — `${heading}`, `${accent}`, `${items}`, etc., for the assembler to splice.
3. **Animation timeline** — comments declaring the default delays so motion-designer can adjust.
4. **Default duration hint** — the budget this shape comfortably fills.

## Shape selection heuristic

The `frame-designer` agent maps each beat's `concept` field to a shape:

```
"problem chain ending in question" → chain
"failure cases stacked"             → stack-strikethrough
"big number reveal"                  → counter-roll
"grid of mockups"                    → gallery-hero
"system architecture"                → hierarchy-diagram
"form + structured output"           → modal-live-json
"parallel build progress"            → triple-pane
"command line + browser opens"       → terminal-browser
"repo + install instructions"        → repo-install
```

Concepts that don't match → fall back to `frame-shape-fallback` (LLM-generated inline CSS, Tier 3 only).

## Shape extension (v2.0)

Author `templates/frame-shapes/custom/<id>.html` matching the shape contract; declare it in `schemas/frame-shape.schema.json`. The designer agent picks it up automatically.

## Cross-references

- `agents/designers/frame-designer.md`
- `agents/engineers/animation-engineer.md` — wires the timeline into CSS keyframes
- `templates/frame-shapes/*.html`
