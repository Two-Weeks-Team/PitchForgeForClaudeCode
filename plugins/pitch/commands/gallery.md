---
description: Browse past PitchForge runs. Renders a clickable gallery of every run/<id>/ in the workspace with project name, runtime, arc, hero, and verdict.
---

# /pitch:gallery

Renders an at-a-glance gallery of every run in the current workspace.

## Usage

```bash
/pitch:gallery
/pitch:gallery --since=2026-04-01
/pitch:gallery --status=shippable
/pitch:gallery --arc=wow-first
```

## Output

Generates `runs/.gallery.html` and surfaces the path. The gallery is a
single-page HTML, similar to the deck overview, where each tile is a run.

```
=== PitchForge runs · 4 found ===

▌ 2026-04-27 · Preview Forge · 160s · wow-first · ✅ shippable
▌ 2026-04-25 · Pitch Forge   · 160s · wow-first · ✅ shippable (recursive demo)
▌ 2026-04-22 · Notes Triage  ·  60s · teaser    · ⚠ needs-attention (G4 flagged)
▌ 2026-04-20 · Spec Inspector· 240s · story     · ✅ shippable

→ Open runs/.gallery.html in your browser to click through.
```

## Tile content

Per run:

- Project name + runtime + arc.
- The cover slide as a thumbnail (rendered from `deck-cinematic.html`
  via headless Chrome, or static placeholder in v0.1.0).
- Hero copy.
- Verdict (`shippable` / `needs-attention`).
- Quick links: open deck-cinematic, run /pitch:status, run /pitch:replay.

## Fork option (v0.5+)

Click *Fork* on a tile → copies the brief and scenario into a new
`runs/<id>/` for variant exploration without affecting the source.

## Cross-references

- `commands/status.md`
- `commands/replay.md`
- `commands/export.md`
