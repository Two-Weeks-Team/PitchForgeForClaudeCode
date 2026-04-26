# Methodology 00 — Brief Discovery (Phase P1)

The Socratic interview that turns a one-line project description into a
structured brief. All downstream phases depend on this.

## Output schema

`runs/<id>/brief.json` — validates against `schemas/pitch-brief.schema.json`.

```json
{
  "_schema_version": "0.1.0",
  "_filled_ratio": 0.83,
  "project_name": "Preview Forge",
  "project_one_liner": "144 Opus 4.7 personas turn a one-line idea into a frozen full-stack app.",
  "audience": "hackathon-judges",
  "runtime_seconds": 160,
  "narrative_arc": "wow-first",
  "hero_copy": "Preview is all you need.",
  "hero_pattern": "paper-title-inversion",
  "judging_criteria": [
    {"name": "Impact",       "weight": 0.30},
    {"name": "Demo",         "weight": 0.25},
    {"name": "Opus 4.7 use", "weight": 0.25},
    {"name": "Depth",        "weight": 0.20}
  ],
  "prize_categories": ["most-creative-opus", "keep-thinking", "managed-agents"],
  "color_palette": "oklch-warm-gold",
  "key_visuals": [
    "26-mockup gallery",
    "144 counter",
    "6-tier hierarchy diagram"
  ],
  "constraints": ["english-only", "single-html", "no-third-party-deps"],
  "backup_variants": ["score-misses-499", "api-fails", "build-overruns"]
}
```

## The 4-batch interview (Tier 2 default)

### Batch A — required (4 questions)

The minimum set to render a usable scenario. If the user skips Batch A,
the plugin halts.

| Field | Question | Type | Default |
|---|---|---|---|
| `audience` | Who is the primary viewer of this video? | enum: `hackathon-judges` / `investors` / `customers` / `internal-team` / `conference-audience` | — |
| `runtime_seconds` | How many seconds total? | integer 30–600 | 180 |
| `hero_copy` | The single line that becomes the YouTube title and the social card. (One sentence. Five to nine words.) | string | — |
| `narrative_arc` | What shape does the story take? | enum: `wow-first` / `problem-first` / `story` / `before-after` | `wow-first` |

### Batch B — optional (5–8 questions)

Refines tone and judging fit. User can skip; plugin uses defaults.

| Field | Question |
|---|---|
| `judging_criteria` | What axes will the viewer score this on? (List with weights.) |
| `prize_categories` | Are there specific prize hooks to wire in? |
| `color_palette` | Use a palette name from `templates/color-palettes/` or `brand-default`. |
| `tone` | Default is `agro-drop-thrill` (human-presenter). Alternatives: `calm-academic`, `playful-warm`, `corporate-clean`. |
| `backup_variants` | What goes wrong on demo day? |
| `constraints` | Hard constraints (English-only, single-file, no external CDN, etc.). |

### Batch C — frame-by-frame (one line each)

For each beat in the chosen narrative arc, one sentence describing the visual concept.
Defaults to the arc's stock concept set.

## Inputs that shortcut the interview

- **From the command line**: `/pitch:new "<one-liner>" --runtime=160 --arc=wow-first --hero="<copy>"` skips Batch A.
- **From a frontmatter file**: `--from-file=brief.yaml` skips all batches.
- **From a Preview Forge run**: `--from-pf=runs/<id>/idea.spec.json` extracts persona, surface, killer-feature directly into Batch A defaults (sibling-plugin chain).

## `_filled_ratio` cascade

Mirrors Preview Forge's idea-spec.

| Ratio | Mode | What downstream phases do |
|---|---|---|
| `≥ 0.7` | `ground-truth` | Generate full deck without further questions |
| `0.4 – 0.7` | `hint` | Use as suggestion; ask one clarifying question per phase |
| `0.2 – 0.4` | `low-confidence` | Treat as rough sketch; ask explicit confirmation each phase |
| `< 0.2` | `fallback-omit-spec` | Use stock defaults; do not propagate brief contents |

## Validation gates

Brief is rejected if:

- `runtime_seconds` is outside 30–600.
- `hero_copy` is longer than 12 words.
- `narrative_arc` is not in the enum.
- `judging_criteria` weights don't sum to 1.0 ± 0.05.
- `audience` is not specified and `_filled_ratio < 0.5`.

Rejected briefs trigger a remediation loop, never a hard exit.

## Cross-references

- `methodology/01-narrative-arcs.md` — what each arc shape produces.
- `methodology/02-hero-copy-patterns.md` — pattern library for the hero copy line.
- `schemas/pitch-brief.schema.json` — JSON schema reference.
- `agents/writers/brief-extractor.md` — the agent that runs this phase.
