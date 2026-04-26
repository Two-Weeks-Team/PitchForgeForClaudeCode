---
description: Phase P4 only — audit and rewrite the voiceover. Catches AI-narration patterns and rewrites into Doumont staccato + agro-drop-thrill act mapping. Mandatory before P5.
---

# /pitch:tone [run_id]

Runs `tone-auditor` followed by `tone-editor` (rewrite) and re-audit
loop. Output: `frame-spec.json` with rewritten `voiceover` per frame
and `tone-audit.json` showing what was flagged + fixed.

## Usage

```bash
# Audit + rewrite the most recent run
/pitch:tone

# Specify run
/pitch:tone runs/2026-04-27-preview-forge

# Audit only — no rewrite
/pitch:tone --audit-only

# Switch tone profile (v0.5+)
/pitch:tone --profile=calm-academic
```

## What it catches

Per `methodology/03-tone-energy.md`:

- NEVER-list patterns: `as you can see`, `let me show you`,
  `thanks for watching`, disfluencies, adverb chains, smooth-overs.
- Doumont staccato — fragments that average > 12 words.
- First-person verbs missing in opening 3 lines.
- Em-dash held breath missing in Act B (`drop`).
- Rhetorical question missing in Act C (`thrill`).
- Hero copy paraphrase (Layer-0 Rule 4 violation — flagged as a hard
  block; tone-editor cannot quietly rewrite it; user is asked).

## Loop structure

```
tone-auditor → flags?
  no  → exit, gate G4 passes
  yes → tone-editor rewrites → tone-auditor flags again
        ≤ 3 retries
        if flags persist → halt, surface to pitch-pm
```

## Outputs

- `runs/<id>/frame-spec.json` (overwritten with new VO)
- `runs/<id>/tone-audit.json` (audit log: violations before / fixes / violations after)

## Cross-references

- `agents/writers/tone-editor.md`
- `agents/reviewers/tone-auditor.md`
- `methodology/03-tone-energy.md`
