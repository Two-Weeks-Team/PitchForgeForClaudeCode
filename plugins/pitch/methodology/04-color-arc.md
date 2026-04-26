# Methodology 04 — Color Arc (Cross-cutting)

A color arc is a per-frame palette assignment that visualizes the emotional
shape of the narrative. The viewer reads color before they read text.

## The default arc — `oklch-warm-gold`

| Frame role | Color | Meaning |
|---|---|---|
| Hero (F4) | `oklch(0.84 0.15 90)` — gold | Paradigm-shift claim |
| Problem (F1) | `oklch(0.84 0.15 90)` — gold | Aspiration not yet realized |
| Failure (F2) | `oklch(0.72 0.21 25)` — red | Indictment |
| Pivot (F3) | `oklch(0.78 0.17 145)` — green | The way out |
| Architecture (F6) | `oklch(0.72 0.18 290)` — violet | Structure |
| Payoff (F10) | `oklch(0.78 0.17 145)` — green | Working app |
| Outro (F11) | `oklch(0.84 0.15 90)` — gold | Hero echo |

**Sequence read top-to-bottom**: gold → gold → **red** → **green** → violet → green → gold.

The viewer sees a story even if they mute the audio.

## Three palettes ship in v0.5

- `oklch-warm-gold` (default) — the palette this plugin's own deck uses.
- `monochrome-cinema` — black/white/grey, single accent. For arthouse demos.
- `pastel-light` — light bg, muted accents. For consumer products.

Each palette defines six roles (`hero` / `problem` / `failure` / `pivot` / `architecture` / `payoff`) so any narrative arc can claim its colors deterministically.

## Custom palettes (v2.0)

Drop a JSON file into `templates/color-palettes/<name>.json` validating against `schemas/color-palette.schema.json`. `--palette=<name>` activates it.

## Cross-references

- `agents/designers/color-arc-designer.md`
- `templates/color-palettes/`
