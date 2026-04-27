# Changelog

All notable changes to PitchForge are documented here.
The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) and
SemVer is auto-bumped via [release-please](https://github.com/googleapis/release-please)
from Conventional Commit messages.

## [0.2.0](https://github.com/Two-Weeks-Team/PitchForgeForClaudeCode/compare/v0.1.0...v0.2.0) (2026-04-27)


### Features

* **ci:** release-please CD pipeline (mirrors Preview Forge) ([c0154cd](https://github.com/Two-Weeks-Team/PitchForgeForClaudeCode/commit/c0154cdc17f397a936c68733b352f06ac953c94a))
* **v0.5:** wire /pitch:hero, /pitch:reorder, /pitch:tone runtime ([ac9cc32](https://github.com/Two-Weeks-Team/PitchForgeForClaudeCode/commit/ac9cc329c085fb8aeb93c9170593485a29ac56cc))
* v1.0.0 candidate — PitchForge plugin (initial commit) ([75ce32d](https://github.com/Two-Weeks-Team/PitchForgeForClaudeCode/commit/75ce32debdeb1572ece18e15da086fe2617588da))
* **v1.0:** recording kit + playbook for video team handoff ([76fe6ba](https://github.com/Two-Weeks-Team/PitchForgeForClaudeCode/commit/76fe6ba8a7a82a6f33c9179fbac37ecdfd2bc3eb))

## [Unreleased] — v1.0.0 candidate (recursive proof + multi-format export)

### Added — v1.0
- `scripts/export-deck.py` — multi-format export entry point. Supports
  `--format=html` (default), `--format=bundle` (tar.gz of every run
  artifact), `--format=pdf` / `--format=webm` / `--format=gif` (prints the
  exact one-line command using headless Chrome / MediaRecorder /
  ffmpeg). Bundles the brief, frame-spec, deck-config, recording-config,
  scenario, tone-audit, deck-cinematic, trace, and retro into a single
  shippable.
- `tests/fixtures/pitchforge-self/brief.json` — the plugin's own pitch
  brief. Hero: "Pitch is all you need." Recursive proof: PitchForge can
  produce its own demo deck.
- `tests/e2e/v1.0-recursive.sh` — recursive-proof + export acceptance
  test. 15/15 assertions pass.
- `docs/REVIEW-5x3.md` — 5×3 team-audit worksheet for v1.0 release gate.
  Five domains × three roles × explicit prompts. Inherited practice from
  Preview Forge.
- Generator now writes `brief.json` into the run dir on every invocation
  (not only when `--one-liner` synthesizes a brief), so downstream
  commands (status / export / replay / gallery) always have a complete
  run on disk.

### Test suite — at v1.0 candidate state
- `verify-plugin.sh`: 36/36
- `tests/e2e/regenerate-reference-deck.sh` (v0.1 acceptance): 26/26
- `tests/e2e/v0.5-variety.sh` (v0.5 variety): 15/15
- `tests/e2e/v1.0-recursive.sh` (v1.0 recursive + export): 15/15
- **Total: 92/92 across all suites.**

### Note on Tier 3 Master + 5×3 review
Tier 3 multi-turn iteration and the 5×3 team audit live as documented
practices (`docs/REVIEW-5x3.md` worksheet, `agents/meta/pitch-pm.md`
gate handlers). Their runtime is human-or-model-mediated; the v1.0
candidate ships the **structure** and the worksheet.

## v0.5.0 candidate (Tier 1 Auto + variety + MediaRecorder)

### Added — variety
- 4 more frame-shape templates (total 9): `hierarchy-diagram`, `modal-live-json`,
  `triple-pane`, `terminal-browser`. Every reference-deck shape now has its own
  template file for the assembler agent to pick up at runtime.
- 4 more narrative arcs (total 5 covering 3 length tiers):
  `wow-first-60s.json`, `problem-first-180s.json`, `story-300s.json`,
  `teaser-45s.json`.
- 2 more color palettes (total 3): `monochrome-cinema.json`,
  `pastel-light.json`. Each preserves the six role tokens so any arc swaps
  cleanly.
- Generator (`scripts/generate-deck.py`) now resolves the closest matching
  arc template by `(name, runtime)` and supports
  `--runtime / --arc / --palette / --hero / --capture` flags.
- `tests/e2e/v0.5-variety.sh` — exercises every arc × every palette
  (5 × 3 = 15 combinations) and asserts each produces a deck that passes
  Layer-0 hooks. Currently 15/15 pass.

### Added — recording
- Optional MediaRecorder integration in deck-shell: when `recording-config.capture.enabled`
  is true, `playRange` arms `getDisplayMedia` and downloads a WebM blob on
  range completion. No-op when disabled — the deck stays portable.
- `--capture` flag on the generator wires this through.

## v0.1.0 candidate (Tier 1 Auto pipeline runnable)

### Added — minimum runnable pipeline
- Schemas (4 / 4): `pitch-brief`, `frame-spec`, `deck-config`, `recording-config`.
- Agents (13 / 13, 5-tier): meta(2) + writers(4) + designers(3) + engineers(3) + reviewers(1).
- Commands (15 / 15): the 14 documented commands plus `/pitch:help`.
- Hooks (3 / 3, Layer-0): `cmd-modifier-guard.py`, `stale-count-detector.py`,
  `tone-ai-detector.py`.
- Templates: `deck-shell.html` (parametric, ~1000 lines, derived from the
  reference deck), 5 frame-shape templates (`chain`, `stack-strikethrough`,
  `counter-roll`, `gallery-hero`, `repo-install`), 1 narrative arc
  (`wow-first-160s.json`), 1 color palette (`oklch-warm-gold.json`).
- Generator: `scripts/generate-deck.py` — Tier 1 Auto end-to-end. Takes a
  brief or a one-liner, emits brief/frame-spec/deck-config/recording-config
  JSON plus a self-contained `deck-cinematic.html`.
- Acceptance test: `tests/e2e/regenerate-reference-deck.sh` regenerates a
  deck from a fixture brief mirroring the reference deck and asserts
  qualitative equivalence (slide count, hero verbatim, modifier-key safety,
  tone-audit pass, all shapes rendered, timestamps within 5%).
- `verify-plugin.sh` expanded from 18 checks to 30, covering schemas,
  methodology, memory, reference, agents, commands, hooks, templates.
- `tests/fixtures/preview-forge-160s/brief.json` — the canonical fixture.

### Earlier scaffold (preserved)
- Initial repository scaffold under `Two-Weeks-Team/PitchForgeForClaudeCode`.
- `docs/PROPOSAL.md` — full design specification (preserved verbatim from the
  exploratory session that produced the v2 cinematic deck for the Preview Forge
  hackathon submission).
- `README.md` — project overview, install path, hero-copy methodology summary.
- `LICENSE` — Apache-2.0.
- `NOTICE` — attribution and acknowledgments.
- `.claude-plugin/marketplace.json` — Two-Weeks-Team marketplace registration.
- `plugins/pitch/.claude-plugin/plugin.json` — plugin manifest, version 0.1.0.
- `plugins/pitch/examples/preview-forge-160s/deck.html` — reference example.
- Methodology docs 00–07 (8 / 8).
- Memory seeds: `CLAUDE.md`, `PROGRESS.md`, `LESSONS.md`, `HERO_CATALOG.md`.
- Skill `cinematic-pitch`.
- CI workflow (ubuntu + macOS matrix).

### Layer-0 enforcement (v0.1.0)
- L1 — Modifier-key safety: `cmd-modifier-guard.py` validates every generated
  deck has `if (e.metaKey || e.ctrlKey || e.altKey) return;` in its keydown
  handler.
- L4 — Reorder reflow: `frame-spec.json` is the single source for every
  timestamp. `deck-config.json` is rederived; eleven ripple sites are
  generated, never edited by hand.
- L5 — Cinematic mode hides the floating rec-timer
  (`body.cinematic #rec-timer { display: none !important }`).
- Rule 4 — Hero copy verbatim: `tone-ai-detector.py` enforces byte-for-byte
  match in primary + echo frames.
- Rule 9 — Stale counts: `stale-count-detector.py` cross-checks README
  claims vs. on-disk counts (scoped to `<!-- pf:counts:start --> ... -->`).
