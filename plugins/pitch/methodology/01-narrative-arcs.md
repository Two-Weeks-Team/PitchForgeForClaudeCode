# Methodology 01 — Narrative Arcs (Phase P2)

A narrative arc is a templated sequence of beats with timing and a stock visual
concept per beat. Picking an arc is the single highest-leverage decision in the
brief — it determines the emotional shape of the video.

PitchForge ships **four** arcs.

---

## Arc 1 — `wow-first` (default)

Show the destination first. Explain why later. The Apple-keynote shape.

**Best for**: hackathon judges who scroll, investors with short patience,
products with a strong visual hero.

**Beats** (160s reference, scales linearly):

| # | Frame ID | Time | Concept | Frame shape |
|---|---|---|---|---|
| 1 | F4 | 0:00–0:10 | Hero gallery + paper-title hero copy | `gallery-hero` |
| 2 | F1 | 0:10–0:18 | Problem framing — chain that ends in `?` | `chain` |
| 3 | F2 | 0:18–0:28 | Failure cascade — three strikethrough rows | `stack-strikethrough` |
| 4 | F3 | 0:28–0:35 | Pivot — chain reverses, color shifts to green | `chain` (green variant) |
| 5 | F5 | 0:35–0:40 | Kick — counter rolls 0→N | `counter-roll` |
| 6 | F6 | 0:40–1:00 | Architecture — hierarchy diagram | `hierarchy-diagram` |
| 7 | F7 | 1:00–1:20 | Socratic / form interaction | `modal-live-json` |
| 8 | F8 | 1:20–1:50 | Selection — gallery + click ripple | `gallery-hero` (interactive variant) |
| 9 | F9 | 1:50–2:20 | Build timelapse — three-pane split | `triple-pane` |
| 10 | F10 | 2:20–2:35 | Payoff — auto-launch terminal + browser | `terminal-browser` |
| 11 | F11 | 2:35–2:40 | Outro — repo + install snippet | `repo-install` |

**Hero copy placement**: F4 (immediate) and F11 (echo).

**Color arc**: gold (problem) → red (failure) → green (pivot) → gold (hero echo).

---

## Arc 2 — `problem-first`

Build tension then release. The classic TED-talk shape.

**Best for**: B2B audiences, complex problems that need framing, education-heavy
products.

**Beats** (180s reference):

| # | Frame ID | Time | Concept | Frame shape |
|---|---|---|---|---|
| 1 | F1 | 0:00–0:10 | Problem framing — chain ends in `?` | `chain` |
| 2 | F2 | 0:10–0:25 | Failure cascade — three strikethrough rows | `stack-strikethrough` |
| 3 | F3 | 0:25–0:35 | Pivot — chain reverses | `chain` (green variant) |
| 4 | F4 | 0:35–1:00 | Wow gallery + hero copy | `gallery-hero` |
| 5–11 | … | 1:00–3:00 | (same as `wow-first` from F5 onwards) | … |

**Hero copy placement**: F4 (delayed) and F11 (echo).

**Color arc**: red (problem) → red (failure) → green (pivot) → gold (reveal) → gold (echo).

---

## Arc 3 — `story` (long form)

Three-act narrative with a protagonist. For 5-minute keynotes and conference talks.

**Best for**: keynote presentations, founder stories, narrative-heavy launches.

**Beats** (300s reference):

| Act | Frame range | Time | Theme |
|---|---|---|---|
| **Act I — Setup** | F1–F3 | 0:00–1:00 | Who, where, what's at stake |
| **Act II — Confrontation** | F4–F8 | 1:00–3:30 | The hero attempts, fails, regroups |
| **Act III — Resolution** | F9–F11 | 3:30–5:00 | Triumph + reflection |

**Hero copy placement**: end of Act I and end of Act III.

---

## Arc 4 — `teaser` (short form, 30–60s)

Wow → kick → outro. No explanation, no architecture. For social media,
ad spots, landing-page background loops.

**Best for**: 30s teasers, twitter videos, hero loops on landing pages.

**Beats** (45s reference):

| # | Frame ID | Time | Concept |
|---|---|---|---|
| 1 | F4 | 0:00–0:25 | Wow gallery + hero copy |
| 2 | F5 | 0:25–0:35 | Kick — counter |
| 3 | F11 | 0:35–0:45 | Repo + install snippet + hero echo |

**Hero copy placement**: F4 (immediate, full hold).

---

## Arc selection heuristic

```
runtime ≤ 60      → teaser (regardless of audience)
runtime 60–240    → wow-first (default)  OR  problem-first if audience == B2B / education
runtime 240–600   → story
runtime > 600     → reject (PitchForge is not a webinar tool)
```

The brief's `narrative_arc` field overrides this heuristic.

---

## What an arc template ships

Each arc lives in `templates/narrative-arcs/<arc-name>-<runtime>.json` and contains:

- `name` (string), `runtime_seconds` (int)
- `beats` (array of `{frame_id, time_start, time_end, concept, shape}`)
- `hero_copy_placement` (array of frame_ids)
- `color_arc` (array of `{frame_id, palette_role}`)
- `delivery_notes` (per-beat tone hints)

The `scenario-architect` agent loads the chosen arc, splices the brief's
`hero_copy` and `key_visuals` into the right beats, and emits `scenario.md`
+ `frames-spec.json`.

---

## Adding a new arc (post-v1.0)

In v2.0 the arc DSL becomes user-extensible:

1. Author `templates/narrative-arcs/my-arc-Ns.json`.
2. Validate against `schemas/narrative-arc.schema.json`.
3. Drop in. `/pitch:new --arc=my-arc` picks it up automatically.

---

## Cross-references

- `methodology/02-hero-copy-patterns.md` — what to put at the placement points.
- `methodology/04-color-arc.md` — palettes that map to the color-arc field.
- `methodology/05-frame-shape-library.md` — what each shape renders.
- `agents/writers/scenario-architect.md` — the agent that walks the arc.
