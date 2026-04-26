---
description: Phase P2 only — regenerate scenario.md + frame-spec.json from an existing brief.json. Used to swap arcs, retune timestamps, or refresh the storyboard plan without re-interviewing.
---

# /pitch:scenario [run_id]

Regenerates the scenario for an existing run. Hands `runs/<id>/brief.json`
to `scenario-architect`; that agent reloads the chosen arc, splices the
brief's hero + key visuals, and emits `scenario.md` + `frame-spec.json`.

## Usage

```bash
# Regenerate scenario for the most recent run
/pitch:scenario

# Specify run id explicitly
/pitch:scenario runs/2026-04-27-preview-forge

# Override the arc
/pitch:scenario --arc=problem-first

# Override the runtime
/pitch:scenario --runtime=180
```

## Flags

| Flag | Effect |
|---|---|
| `--arc` | Override `brief.narrative_arc` for this regeneration only. |
| `--runtime` | Override `brief.runtime_seconds` (timestamps reflow). |
| `--palette` | Override `brief.color_palette`. |

If a flag is supplied, the brief is *not* mutated on disk — the override
applies only to the produced scenario. Use `/pitch:new --tier=guided` to
update the brief itself.

## Outputs

- `runs/<id>/scenario.md` (overwritten)
- `runs/<id>/frame-spec.json` (overwritten)

Downstream phases (P3 onwards) become stale and must be re-run via
`/pitch:storyboard`, `/pitch:deck`, etc., or in one shot via
`/pitch:new --tier=auto --resume=<id>` (v0.5+).

## Cross-references

- `agents/writers/scenario-architect.md`
- `methodology/01-narrative-arcs.md`
- `methodology/05-frame-shape-library.md`
