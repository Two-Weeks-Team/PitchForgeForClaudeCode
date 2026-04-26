---
description: Run the full 7-phase PitchForge pipeline. Tier 1 (Auto) by default; pass --tier=guided for the Socratic interview, --tier=master for multi-turn iteration.
---

# /pitch:new "<project one-liner>"

The single command that takes a project from idea to recording-ready cinematic deck.

## Usage

```bash
# Tier 1 (Auto) — defaults applied, ~10 min
/pitch:new "Preview Forge — 144 personas turn one-line idea into full-stack app"

# Tier 2 (Guided) — Socratic interview, ~30 min
/pitch:new "..." --tier=guided

# Tier 3 (Master) — interactive multi-turn, unbounded
/pitch:new "..." --tier=master

# With explicit overrides (skips matching Batch A questions)
/pitch:new "..." \
  --tier=guided \
  --runtime=160 \
  --arc=wow-first \
  --hero="Preview is all you need." \
  --audience=hackathon-judges
```

## Flags

| Flag | Type | Default | Effect |
|---|---|---|---|
| `--tier` | enum | `auto` | `auto` / `guided` / `master` |
| `--runtime` | integer | `180` | seconds, 30–600 |
| `--arc` | enum | (heuristic) | `wow-first` / `problem-first` / `story` / `teaser` |
| `--hero` | string | (auto-generated) | hero copy verbatim |
| `--audience` | enum | `hackathon-judges` | passes to brief Batch A |
| `--palette` | string | `oklch-warm-gold` | color palette name |
| `--from-file` | path | — | YAML brief shortcuts all batches |
| `--from-pf` | path | — | Preview Forge run idea.spec.json — extracts persona/surface |
| `--no-cache` | flag | off | bypass any cached scenario / shape selections |

## Phase outputs

After completion, `runs/<id>/` contains:

```
runs/<id>/
├── brief.json                  # P1
├── scenario.md                 # P2
├── frames-spec.json            # P2
├── storyboard.html             # P3
├── tone-audit.json             # P4
├── deck.html                   # P5
├── deck-animated.html          # P6
├── deck-cinematic.html         # P7  ← record this
├── trace.jsonl                 # phase-by-phase log
└── retro.md                    # auto-extracted lessons (post-run)
```

## Cross-references

- `skills/cinematic-pitch/SKILL.md` — entry-point skill
- `agents/meta/pitch-supervisor.md` — orchestrator
- `methodology/00-brief-discovery.md` — what Phase P1 asks
