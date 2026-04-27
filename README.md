<div align="center">

# PitchForge for Claude Code

### One Socratic interview. Seven phases. One self-contained, recording-ready cinematic deck.

**A Claude Code plugin that turns project context into a 60–300 second demo video deck —
browser-native, OBS-ready, paper-grade hero copy, human-presenter delivery.**

[![CI](https://github.com/Two-Weeks-Team/PitchForgeForClaudeCode/actions/workflows/ci.yml/badge.svg)](https://github.com/Two-Weeks-Team/PitchForgeForClaudeCode/actions/workflows/ci.yml)
[![License: Apache 2.0](https://img.shields.io/github/license/Two-Weeks-Team/PitchForgeForClaudeCode)](LICENSE)
[![Built with Opus 4.7](https://img.shields.io/badge/Built%20with-Claude%20Opus%204.7-d4a574?logo=anthropic&logoColor=white)](https://www.anthropic.com/claude/opus)
[![Claude Code Plugin](https://img.shields.io/badge/Claude%20Code-Plugin-7aa6c2?logo=anthropic&logoColor=white)](https://code.claude.com/docs/en/plugins)
[![13 Agents](https://img.shields.io/badge/Agents-13-84c984)](docs/PROPOSAL.md)
[![15 Slash Commands](https://img.shields.io/badge/%2Fpitch%3A*-15%20commands-7aa6c2)](#slash-commands)
[![Status: v1.0.0 candidate](https://img.shields.io/badge/status-v1.0.0%20candidate-84c984)](CHANGELOG.md)

</div>

> **Not a Preview Forge dependency.** PitchForge is a sibling product in the
> Two-Weeks-Team forge family. PF builds the app; PitchForge films the app.

---

## Why this exists

Building a great demo video is a **7-hour problem solved 14× a year by every
team that ships**. The work decomposes the same way every time:

1. Brief — what are we showing, to whom, in how many seconds?
2. Scenario — beat-by-beat timeline + voiceover.
3. Storyboard — visual mockups for every beat.
4. Tone — rewrite voiceover so it doesn't sound AI-narrated.
5. Deck — assemble into a navigable HTML deck.
6. Animation — make every beat self-play at the right time.
7. Record — hide chrome, auto-advance, OBS-ready.

PitchForge captures the generic 90% into the plugin and isolates the unique
~10% (your hero copy, your three or four key visuals) into a Socratic
interview. **30 minutes to a deck that would have taken 7 hours.**

---

## The hero claim

```
Preview is all you need.
```

Five words. One paper-title cadence (≈ Vaswani et al., *Attention Is All You
Need*, 2017). It's the YouTube title, the submission summary header, the
README h1, and the social-card preview — **all the same line**. PitchForge
ships an entire methodology around finding *your* version of this line.

---

## Quick install

```bash
# 1. Add this marketplace
/plugin marketplace add Two-Weeks-Team/PitchForgeForClaudeCode

# 2. Install the plugin
/plugin install pitch@two-weeks-team

# 3. Reload so hooks, agents, and commands refresh
/reload-plugins

# 4. First-time setup (per workspace)
/pitch:bootstrap

# 5. Run the full 7-phase pipeline
/pitch:new "your project in one line"
```

### Update / pin a version

```bash
# Update to the latest published version
/plugin update pitch@two-weeks-team

#   — or, if update is not available in your Claude Code version —
/plugin uninstall pitch@two-weeks-team
/plugin install pitch@two-weeks-team
/reload-plugins

# Pin a specific past version (any tag from GitHub Releases)
/plugin uninstall pitch@two-weeks-team
/plugin install pitch@two-weeks-team@0.1.0
```

Every release is signed via [GitHub Releases](https://github.com/Two-Weeks-Team/PitchForgeForClaudeCode/releases).

After step 5, three to four files land in `runs/<id>/`:

```
runs/<id>/
├── brief.json          # what you said in the Socratic interview
├── scenario.md         # beat-by-beat timeline + voiceover
├── storyboard.html     # static visual review of every frame
└── deck.html           # the cinematic, recording-ready deck
```

Open `deck.html` in Chrome / Safari / Firefox. Press `O` for the opening
sequence, `F` for the full demo, `R` to toggle recording mode. Capture with
OBS / Loom / QuickTime.

---

## The 7-phase pipeline

| Phase | Command | Output |
|---|---|---|
| **P1 · Brief** | `/pitch:new <project>` (Socratic 4-batch) | `brief.json` |
| **P2 · Scenario** | `/pitch:scenario` | `scenario.md` + `frames-spec.json` |
| **P3 · Storyboard** | `/pitch:storyboard` | `storyboard.html` |
| **P4 · Tone** | `/pitch:tone` (audit + rewrite) | revised VO + AI-ness report |
| **P5 · Deck** | `/pitch:deck` | navigable `deck.html` |
| **P6 · Animate** | `/pitch:animate` | `deck-animated.html` |
| **P7 · Record** | `/pitch:record` | `deck-cinematic.html` (`O` `F` `R` `A` `P` keys) |

`/pitch:new` runs all seven phases in one call. Each phase can be re-run
individually for iteration.

---

## Tier model

| Tier | Mode | Time | Tokens | Use for |
|---|---|---|---|---|
| **Auto** | Three-sentence input → defaults applied | ~10 min | ~10k | Hackathon demos, internal updates |
| **Guided** | 3-batch Socratic (4 required + 5–8 optional + frame-by-frame) | ~30 min | ~40k | Real launches, investor pitches |
| **Master** | Multi-turn iteration (v1 → v2 → v3 forks) | unbounded | unbounded | Keynotes, reusable templates |

---

## Slash commands

### Run lifecycle
```
/pitch:bootstrap        # first-time workspace setup
/pitch:new <project>    # P1–P7 end-to-end
/pitch:status           # 6-gate audit pass/fail
/pitch:replay <run>     # deterministic replay from trace.jsonl
```

### Phase commands
```
/pitch:scenario         # P2 only
/pitch:storyboard       # P3 only
/pitch:deck             # P5 only
/pitch:animate          # P6 only
/pitch:record           # P7 only
/pitch:tone             # P4 only — audit + rewrite
```

### Cross-cutting
```
/pitch:hero             # 5 inversion-pattern hero copy candidates
/pitch:reorder          # swap slides + auto-reflow timestamps
```

### Assets + history
```
/pitch:gallery          # browse past pitches
/pitch:export           # package as standalone HTML
/pitch:help             # full reference + FAQ
```

---

## What ships in the plugin

The "v0.1.0 ships" column is the count *currently on disk* (validated by
`bash scripts/verify-plugin.sh` and the `stale-count-detector` Layer-0 hook).
The "v1.0 target" column is the roster the plugin grows into.

<!-- pf:counts:start -->

| Area | v0.1.0 ships | v1.0 target |
|---|---:|---:|
| 13 agents | 13 | 13 |
| 15 commands | 15 | 15 |
| 3 hooks | 3 | 3 |
| 8 methodology docs | 8 | 8 |
| 4 schemas | 4 | 4 |
| 9 frame shapes | 9 | 9 |
| 5 narrative arcs (3 lengths) | 5 | 4+ |
| 3 color palettes | 3 | 3 |
| 1 example | 1 | 1+ |

<!-- pf:counts:end -->

Detail:

| Area | Description |
|---|---|
| **Agents** | 5-tier — meta (2) + writers (4) + designers (3) + engineers (3) + reviewers (1+) |
| **Slash commands** | `/pitch:*` namespace (14 documented + `/pitch:help`) |
| **Skills** | `cinematic-pitch` (the entry-point skill) |
| **Hooks** | `stale-count-detector`, `tone-ai-detector`, `cmd-modifier-guard` |
| **Methodology docs** | brief / arcs / hero copy / tone / color / shapes / timing / recording |
| **Frame shape templates** | chain, stack, counter, gallery, diagram, modal+JSON, triple-pane, terminal+browser, repo+install |
| **Narrative arc templates** | wow-first (v0.1), problem-first / story / teaser (v0.5) |
| **Color palettes** | OKLCH warm-gold (v0.1), monochrome cinema / pastel light (v0.5) |
| **JSON schemas** | brief, frame-spec, deck-config, recording-config |
| **Examples** | `preview-forge-160s/` (the deck this plugin's design came from) |

---

## Hero copy methodology

PitchForge ships **five inversion patterns** for hero copy. Each is a tested
narrative shape that lets one line carry an entire pitch:

| Pattern | Shape | Example |
|---|---|---|
| **Paper-title inversion** | "X is all you need." | *"Preview is all you need."* |
| **Stop-Start** | "Stop X, start Y." | *"Stop chatting with AI. Start engineering with it."* |
| **First reordering** | "X first." | *"Result first."* |
| **Confession** | "We've been [doing it wrong]." | *"We've been lying."* |
| **Promise** | "[Number] [verb]. [Number] [noun]. [Number] [outcome]." | *"144 personas. One plugin. Two clicks."* |

`/pitch:hero` returns five candidates — one per pattern — for any project.

---

## Recording mode

The deck has three layered display modes:

| Mode | What's visible | Trigger |
|---|---|---|
| **Review** | Top bar + canvas + voiceover panel + control panel | (default) |
| **Recording** | Canvas only — chrome hidden, dark border, timer floating | `R` key |
| **Cinematic** | Recording mode + on-canvas VO subtitles also hidden + auto-advance + countdown | `O` (opening only) or `F` (full) key |

The OBS / Loom workflow is a single keypress:

```
1. Open deck.html in browser, fullscreen (F11).
2. Start screen recording.
3. Press O.
   → 3-2-1-GO countdown (4s — recorder gets ready).
   → Cinematic playback runs the configured slide range automatically.
   → END overlay appears at completion (2.4s).
4. Stop recording.
```

---

## Documentation

- 📘 [**Full proposal (v1.0)**](docs/PROPOSAL.md) — the design specification
- 🎬 [**Demo storyboard**](docs/DEMO-STORYBOARD.md) — the plugin's own demo (recursive)
- 📝 [**CHANGELOG**](CHANGELOG.md) — release history
- 🤝 [**Contributing**](CONTRIBUTING.md) — how to add frame shapes, narrative arcs, hero patterns
- 🛡️ [**Security policy**](SECURITY.md)

---

## Status

| Milestone | Target | Progress |
|---|---|---|
| **v0.1.0 — MVP** | end-to-end reproducibility of the reference example | 🚧 in progress |
| **v0.5.0 — Tier 2** | guided variety (9 shapes / 4 arcs / 3 palettes) | ⏳ planned |
| **v1.0.0 — Production** | publishable, marketplace-ready, recursively-proven | ⏳ planned |
| **v2.0.0 — Ecosystem** | user-defined shapes / DSL / plugin chain | ⏳ planned |

---

## License

[Apache-2.0](LICENSE). See [NOTICE](NOTICE) for attribution.

---

<div align="center">

<sub>Built with **Claude Opus 4.7** · Sibling to **[Preview Forge](https://github.com/Two-Weeks-Team/PreviewForgeForClaudeCode)** · Apache-2.0</sub>

<sub>**Preview is all you need. PitchForge is how you show it.**</sub>

</div>
