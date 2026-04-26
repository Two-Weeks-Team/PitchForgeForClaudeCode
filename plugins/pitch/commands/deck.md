---
description: Phase P5 only — assemble deck.html from frame-spec.json + templates. Navigable but unanimated; animation engine wires in P6.
---

# /pitch:deck [run_id]

Runs `deck-assembler`. Input: `runs/<id>/frame-spec.json` plus the
deck-shell + frame-shape templates. Output: a single self-contained
`deck.html` with all slides navigable via arrow keys + space + esc.

## Usage

```bash
/pitch:deck
/pitch:deck runs/2026-04-27-preview-forge
```

## Stages

1. **Derive `deck-config.json`** from `frame-spec.json` + `brief.json`
   (palette, slide-duration array, summaries, ranges, hero placement).
2. **Substitute** the deck-shell template with palette + metadata.
3. **Render each frame** using its shape template + slot values.
4. **Build the JS data arrays** — `SLIDE_DURATION`, `summaries`,
   `playRange()` start/end positions.
5. **Output** `deck.html`.

## Outputs

- `runs/<id>/deck-config.json` — render-time configuration.
- `runs/<id>/deck.html` — navigable deck.

## Animation note

After this phase, animations are wired to the CSS engine but the
per-frame timeline is empty. P6 (`/pitch:animate`) populates it.

## Cross-references

- `agents/engineers/deck-assembler.md`
- `templates/deck-shell.html`
- `templates/frame-shapes/*.html`
