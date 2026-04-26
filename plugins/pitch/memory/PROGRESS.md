# Progress

## v0.1.0 — in progress (kicked off 2026-04-27)

### Completed

- 2026-04-27: repository scaffold, directory tree.
- 2026-04-27: `docs/PROPOSAL.md` (full design specification preserved verbatim).
- 2026-04-27: `README.md`, `LICENSE` (Apache-2.0), `NOTICE`, `CHANGELOG.md`.
- 2026-04-27: Plugin manifests — `marketplace.json`, `plugin.json`.
- 2026-04-27: Methodology docs 00–07 (8 documents).
- 2026-04-27: `examples/preview-forge-160s/deck.html` reference example
  copied verbatim from Preview Forge `claudedocs/winning-storyboard-deck-v2.html`.
- 2026-04-27: Memory seeds — `CLAUDE.md`, `PROGRESS.md` (this file), `LESSONS.md`.

### Planned for v0.1.0 release

- Schemas — `pitch-brief.schema.json`, `frame-spec.schema.json`,
  `deck-config.schema.json`, `recording-config.schema.json`.
- Skill — `skills/cinematic-pitch/SKILL.md`.
- Commands — `bootstrap.md`, `new.md`, `help.md` (3 of 14).
- Agents — `pitch-supervisor.md`, `brief-extractor.md` (2 of 13).
- Frame shape templates — `chain.html`, `gallery-hero.html` (2 of 9).
- Narrative arc — `wow-first-160s.json` (1 of 4).
- Color palette — `oklch-warm-gold.json` (1 of 3).
- Deck shell template — `deck-shell.html` (extracted parametric form of the reference example).
- `scripts/verify-plugin.sh`.
- `.github/workflows/ci.yml` (ubuntu + macOS matrix).
- `.gitignore`, `CONTRIBUTING.md`, `SECURITY.md`.

### Acceptance criteria for v0.1.0

A fresh user runs `/pitch:new "<project>"` once and produces a deck
qualitatively equivalent to `examples/preview-forge-160s/`. Three phases
internally: brief → assemble → cinematic. Tier 1 Auto only.
