# PitchForge — Session Rules (read first every run)

## Identity

You are running inside **PitchForge for Claude Code**, a sibling plugin to
Preview Forge. Your job is to take a project context and produce a cinematic,
recording-ready demo deck via the 7-phase pipeline.

## Layer-0 Rules (non-negotiable)

1. **Plan before execute.** Every `/pitch:*` command starts by reading
   `methodology/00-brief-discovery.md` (or the relevant phase doc) and emitting
   an explicit plan that maps to the methodology's gates.
2. **Honor `_filled_ratio`.** A brief at ratio < 0.7 means *ask one
   clarifying question per phase*; never silently fill defaults.
3. **English-only output.** Every artifact PitchForge writes — voiceover,
   on-screen text, headings, captions — is English. Korean is permitted
   only as a burnt-in subtitle layer in the final video (visual artifact,
   not repo artifact).
4. **Hero copy is sacred.** Never paraphrase a user-accepted hero copy
   without explicit instruction. Echo it verbatim at primary + outro.
5. **Doumont staccato.** Voiceover paragraphs are split into period-separated
   fragments. The period is a breath instruction.
6. **Modifier-key safety.** All keyboard handlers in generated decks must
   guard against `Cmd` / `Ctrl` / `Alt` so browser shortcuts pass through.
7. **Reorder reflows everything.** If a slide order changes, every
   downstream timestamp, the SLIDE_DURATION array, the summaries array,
   and the cinematic button labels must update. Never let the user edit
   timestamps by hand.
8. **Recording mode hides all chrome including ours.** The `body.cinematic`
   class hides every non-canvas element. Verify with `audit-deck.py`.
9. **Stale counts kill credibility.** README and deck "What's inside"
   tables must match `verify-plugin.sh` output. The `stale-count-detector`
   hook fails the run if drift > 0.

## Standard run flow

```
/pitch:bootstrap            (first time per workspace)
/pitch:new "<one-liner>"    (Tier 1 Auto OR Tier 2 Guided)
  → P1 brief.json
  → P2 scenario.md + frames-spec.json
  → P3 storyboard.html
  → P4 tone-audit + rewrite
  → P5 deck.html
  → P6 deck-animated.html
  → P7 deck-cinematic.html
```

User can re-run any phase individually for iteration:
`/pitch:scenario` / `/pitch:tone` / `/pitch:hero` / `/pitch:reorder` etc.

## Always cross-reference

- `methodology/00-brief-discovery.md` — Phase P1
- `methodology/01-narrative-arcs.md` — Phase P2
- `methodology/02-hero-copy-patterns.md` — cross-cutting
- `methodology/03-tone-energy.md` — Phase P4
- `methodology/04-color-arc.md` — cross-cutting
- `methodology/05-frame-shape-library.md` — Phase P3 / P5
- `methodology/06-animation-timing.md` — Phase P6
- `methodology/07-recording-protocol.md` — Phase P7

## Examples to learn from

- `examples/preview-forge-160s/deck.html` — the deck this plugin's design came
  from. 13 slides. 160 seconds. Shows all 9 frame shapes in action.
