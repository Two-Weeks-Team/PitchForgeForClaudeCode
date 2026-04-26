---
description: Phase P6 only — wire the per-frame animation timeline into deck-animated.html. Splits the work between motion-designer (designs the timeline) and animation-engineer (realizes it).
---

# /pitch:animate [run_id]

Animates the deck. Two-step phase:

1. **motion-designer** populates `frame-spec.frames[*].animation_timeline`.
2. **animation-engineer** reads that and applies `data-anim` attributes
   (CSS engine) and `data-counter` / `data-typewriter` attributes
   (JS engine) on the rendered slides.

## Usage

```bash
/pitch:animate
/pitch:animate runs/2026-04-27-preview-forge

# Re-design the timeline only (skip engineer step)
/pitch:animate --design-only

# Re-realize the existing timeline (skip designer step)
/pitch:animate --engineer-only
```

## Outputs

- `runs/<id>/frame-spec.json` (animation_timeline filled)
- `runs/<id>/deck-animated.html`

## Hero hold floor (L3)

If the primary frame's duration is < 8s, the hero word-reveal stagger
compresses from 0.12s/word to 0.08s/word so the hero is fully visible
within ~2s, leaving ≥ 5s of hold. This is automatic.

## Cross-references

- `agents/designers/motion-designer.md`
- `agents/engineers/animation-engineer.md`
- `methodology/06-animation-timing.md`
- `memory/LESSONS.md#L3`
