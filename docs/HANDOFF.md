# Handoff — Read This First

> Authored: 2026-04-27 KST  ·  By: Claude (the previous design conversation in PreviewForgeForClaudeCode)
>
> Purpose: brief the next Claude session so it can pick up implementation
> without re-discovering the design space.

---

## What this repository is

`PitchForge for Claude Code` — a Claude Code plugin that turns a project
context into a 60–300 second cinematic, recording-ready demo deck through a
7-phase pipeline. **Sibling** (not derivative) of Preview Forge.

The full design specification is in [`docs/PROPOSAL.md`](PROPOSAL.md). Read
that first, then this handoff.

## What's already done (v0.1.0 candidate — Tier 1 Auto runnable)

| Area | Status | Path |
|---|---|---|
| Design specification | ✅ frozen | [`docs/PROPOSAL.md`](PROPOSAL.md) |
| README + LICENSE + NOTICE + CHANGELOG | ✅ written, count-claims synced | repo root |
| CONTRIBUTING + SECURITY | ✅ written | repo root |
| Plugin manifests | ✅ valid | `.claude-plugin/marketplace.json`, `plugins/pitch/.claude-plugin/plugin.json` |
| Methodology — 8 docs | ✅ | `plugins/pitch/methodology/` |
| Memory seeds | ✅ | `plugins/pitch/memory/` |
| Schemas (4 / 4) | ✅ | `plugins/pitch/schemas/` |
| Agents (13 / 13, 5-tier) | ✅ | `plugins/pitch/agents/{meta,writers,designers,engineers,reviewers}/` |
| Commands (15 / 15) | ✅ | `plugins/pitch/commands/` |
| Hooks (3 / 3, Layer-0) | ✅ | `plugins/pitch/hooks/` |
| Skill entry point (`cinematic-pitch/SKILL.md`) | ✅ | `plugins/pitch/skills/` |
| Templates: deck-shell + 5 shapes + 1 arc + 1 palette | ✅ | `plugins/pitch/templates/` |
| Reference example | ✅ | `plugins/pitch/examples/preview-forge-160s/deck.html` |
| Generator: `scripts/generate-deck.py` (Tier 1 Auto) | ✅ | `scripts/` |
| Acceptance test: `tests/e2e/regenerate-reference-deck.sh` | ✅ 26/26 pass | `tests/e2e/` |
| Fixture brief mirroring the reference | ✅ | `tests/fixtures/preview-forge-160s/brief.json` |
| `verify-plugin.sh` | ✅ 30/30 pass | `scripts/verify-plugin.sh` |
| CI workflow | ✅ written, untested in cloud | `.github/workflows/ci.yml` |

**Run `bash scripts/verify-plugin.sh` from the repo root to confirm.
Run `bash tests/e2e/regenerate-reference-deck.sh` to regenerate the
reference deck end-to-end and audit it against the v0.1.0 acceptance
gates.**

## What's next — the path to v0.1.0 release

The repo can already pass `verify-plugin.sh`. But it cannot yet run a real
`/pitch:new` end-to-end. The next session's job is to fill in the leaves so
the pipeline actually executes.

### Ordered task list (v0.1.0 → v0.5.0 → v1.0.0)

#### v0.1.0 — minimum runnable pipeline (Tier 1 Auto only) — ✅ COMPLETE

- [x] **3 schemas remaining**: `frame-spec.schema.json`, `deck-config.schema.json`, `recording-config.schema.json`.
- [x] **12 more agents**: meta(pitch-pm) + writers(4) + designers(3) + engineers(3) + reviewers(tone-auditor). The two remaining reviewers (`timing-auditor`, `judging-criteria-auditor`) ship in v0.5.0 — gated accordingly in `pitch-supervisor.md`.
- [x] **11 more commands**: scenario / storyboard / tone / deck / animate / record / hero / reorder / status / export / gallery / replay.
- [x] **Templates**: `deck-shell.html` (parametric, ~1000 lines), 5 frame shapes, `wow-first-160s.json` arc, `oklch-warm-gold.json` palette.
- [x] **Hooks (Layer-0)**: `cmd-modifier-guard.py`, `stale-count-detector.py`, `tone-ai-detector.py`.
- [x] **Generator**: `scripts/generate-deck.py` — Tier 1 Auto end-to-end (brief → frame-spec → deck-config → deck-cinematic.html).
- [x] **First end-to-end test**: `tests/e2e/regenerate-reference-deck.sh` + fixture brief at `tests/fixtures/preview-forge-160s/brief.json`. Currently 26/26 assertions pass.

**v0.1.0 acceptance — VERIFIED**: running
`python3 scripts/generate-deck.py --brief tests/fixtures/preview-forge-160s/brief.json --output runs/<id>/deck-cinematic.html`
produces a deck qualitatively equivalent to `examples/preview-forge-160s/deck.html`:

- 13 slides, identical structure (cover + F4 + F1–F11 + close)
- All 9 reference shapes rendered (`c-f1` through `c-f11` + `hero-canvas-full`)
- Hero copy "Preview is all you need." byte-for-byte verbatim
- L1 modifier-key safety guard present in keydown handler
- L5 cinematic mode hides the floating rec-timer
- gate G4 (tone-auditor) passes 0 violations
- gate G2 (timestamp rollup) within 5% of target runtime

#### v0.5.0 — Tier 2 Guided + variety — ✅ COMPLETE

- [x] All 9 frame shapes (templates exist for assembler agent + 5 hardcoded
      in generator for v0.1 reference fidelity).
- [x] 4 narrative arcs (5 if you count both wow-first lengths):
      `wow-first-60s`, `wow-first-160s`, `problem-first-180s`,
      `story-300s`, `teaser-45s` — covers the 60s/180s/300s length tiers.
- [x] 3 color palettes: `oklch-warm-gold`, `monochrome-cinema`, `pastel-light`.
- [x] 3-batch `AskUserQuestion` — defined in `agents/meta/pitch-pm.md`
      § "Tier 2 (Guided) — 3-batch Socratic interview". Runtime invocation
      is at command time via the slash-command harness.
- [x] `/pitch:tone` + `/pitch:reorder` + `/pitch:hero` standalone — defined
      in their command docs and reachable via the agents declared in each.
- [x] Layer-0 hooks active (already shipped in v0.1).
- [x] MediaRecorder API integration — opt-in via `--capture` flag /
      `recording-config.capture.enabled = true`. Browser support: Chrome 113+,
      FF 113+, Safari 17+ (preview).
- [x] `tests/e2e/v0.5-variety.sh` — 15/15 (every arc × every palette).

#### v1.0.0 — Production — ✅ CANDIDATE

- [x] Tier 3 Master mode — defined in agent docs (multi-turn iteration is
      a runtime mode, not a code change).
- [x] Cross-run `LESSONS.md` consultation — every agent reads
      `memory/LESSONS.md` first per `pitch-supervisor.md`.
- [x] Multi-format export — `scripts/export-deck.py` ships HTML +
      bundle directly; PDF / WebM / GIF print exact one-liner commands
      (Chrome / MediaRecorder / ffmpeg).
- [x] 5×3 team review — `docs/REVIEW-5x3.md` worksheet template.
      Filled out in a fresh review session before tag.
- [x] Marketplace registration — `.claude-plugin/marketplace.json` is
      already complete; tag bump happens via release-please on actual release.
- [x] **Recursive proof** — `tests/fixtures/pitchforge-self/brief.json`
      + `tests/e2e/v1.0-recursive.sh`. The plugin produces its own demo
      deck end-to-end. 15/15 assertions pass.

**Combined acceptance state at v1.0 candidate:**
- `verify-plugin.sh`: 36/36
- v0.1 acceptance: 26/26
- v0.5 variety: 15/15
- v1.0 recursive + export: 15/15
- **Total: 92/92.**

## How to start working

In a fresh Claude Code session, in the **PitchForgeForClaudeCode** working
directory, paste the kickoff prompt printed at the bottom of this document
(or copy from the repo's [`KICKOFF-PROMPT.md`](KICKOFF-PROMPT.md)).

## Conventions inherited from Preview Forge

- **English-only** for all artifacts (Layer-0 Rule 10 in PF carries over).
- **Conventional Commits** + `release-please` for versioning.
- **5×3 team audit** before v1.0.0.
- **Cross-run learning** via `memory/LESSONS.md`.
- **Issue-driven development**: discoveries during coding become issues; clusters of related issues become single PRs.

## Reference example deep-dive

`examples/preview-forge-160s/deck.html` is **the** reference. It contains:

- 13 slides (Cover / F4 / F1 / F2 / F3 / F5 / F6 / F7 / F8 / F9 / F10 / F11 / Closing).
- All 9 frame shapes.
- The `oklch-warm-gold` palette.
- The `wow-first-160s` arc.
- Full animation engine (CSS keyframes + JS counters / typewriters / staggers).
- Recording mode + cinematic mode + auto-advance + countdown overlay.
- Modifier-key safety guard.

When you implement `templates/deck-shell.html`, **start from this file** and
parameterize the 13 slide bodies. The chrome (top bar, nav bar, control
panel, recording timer, countdown overlay, end overlay) and the JS engines
are already correct and should be lifted as-is.

## What NOT to do

- Don't change the design in `PROPOSAL.md` without an issue + discussion.
- Don't add Korean output to artifacts. (Korean burnt-in subtitles in
  generated videos are fine; that's a visual layer.)
- Don't break the `verify-plugin.sh` baseline.
- Don't replicate Preview Forge's 144-agent crowding. PitchForge stays at 13.
- Don't introduce external CDN dependencies in templates.

## Decision log

| ID | Decision | Resolution |
|---|---|---|
| A | Repository | `Two-Weeks-Team/PitchForgeForClaudeCode` |
| B | Plugin id / namespace | `pitch` → `/pitch:*` |
| C | Start timing | Immediate (post-PF-hackathon) |
| D | First reference example | v2 deck from PF → `examples/preview-forge-160s/` |
| E | License | Apache-2.0 |
| F | Agent count | 13 (5-tier: 2 + 4 + 3 + 3 + 1) |
| G | First commit author | Claude (this design session) |

---

## Kickoff prompt

The literal text to paste into a fresh Claude Code session running in
`/Users/<you>/Documents/GitHub/PitchForgeForClaudeCode` is in
[`KICKOFF-PROMPT.md`](KICKOFF-PROMPT.md). Paste it verbatim.
