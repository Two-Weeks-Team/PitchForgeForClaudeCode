---
description: Full command reference and FAQ for PitchForge.
---

# /pitch:help

## Run lifecycle

| Command | Purpose |
|---|---|
| `/pitch:bootstrap` | First-time workspace setup — required once per workspace |
| `/pitch:new <project>` | End-to-end pipeline (P1 → P7) |
| `/pitch:status` | 6-gate audit pass/fail for the current run |
| `/pitch:replay <run>` | Deterministic replay from `trace.jsonl` |

## Phase commands

| Command | Phase | Purpose |
|---|---|---|
| `/pitch:scenario` | P2 | Regenerate scenario from existing brief |
| `/pitch:storyboard` | P3 | Regenerate storyboard.html from frames-spec |
| `/pitch:tone` | P4 | Audit + rewrite voiceover |
| `/pitch:deck` | P5 | Reassemble deck.html |
| `/pitch:animate` | P6 | Re-wire animations |
| `/pitch:record` | P7 | Add cinematic mode + recording controls |

## Cross-cutting

| Command | Purpose |
|---|---|
| `/pitch:hero` | Generate 5 inversion-pattern hero copy candidates |
| `/pitch:reorder` | Swap slide order; auto-reflow all timestamps |

## Assets + history

| Command | Purpose |
|---|---|
| `/pitch:gallery` | Browse past pitches |
| `/pitch:export` | Package run as a single self-contained HTML |

## FAQ

**Q: How long does a Tier 1 (Auto) run take?**
A: ~10 minutes, ~10k tokens. Output is a usable deck with default arc, palette, and hero pattern.

**Q: How long does a Tier 2 (Guided) run take?**
A: ~30 minutes, ~40k tokens. 3-batch Socratic interview. Output reflects user's specific brief.

**Q: Can I edit timestamps in the generated `deck-cinematic.html`?**
A: No. Use `/pitch:reorder` or `/pitch:scenario` to update — the deck regenerates timestamps from `frames-spec.json` so eleven separate `time` fields stay in sync. Manual edits drift.

**Q: How do I record the deck?**
A: Open `deck-cinematic.html` in Chrome / Safari / Firefox (latest). Press F11 for fullscreen. Start OBS / Loom screen capture. Press `O` (opening sequence) or `F` (full demo) — countdown gives you 4s to confirm capture started. Press stop when END overlay appears.

**Q: Can I add my own frame shape?**
A: In v2.0 yes — drop an HTML file into `templates/frame-shapes/custom/` matching `schemas/frame-shape.schema.json`. v0.1.0 ships nine built-in shapes; that covers ≥ 95% of demo concepts.

**Q: Does PitchForge depend on Preview Forge?**
A: No. They are sibling plugins in the Two-Weeks-Team forge family. Optional: `/pitch:new --from-pf=<run>` extracts persona/surface/killer-feature from a PF brief.

## Documentation

- `docs/PROPOSAL.md` — full design specification
- `methodology/00-07.md` — per-phase methodology
- `examples/preview-forge-160s/` — canonical reference deck
