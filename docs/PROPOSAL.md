# PitchForge — Proposal v1.0

> **"Attention 다음의 카피, Keynote 없이 만드는 데모."**
>
> Authored: 2026-04-27 KST · Authored by: Claude (this conversation) on behalf of Two-Weeks-Team
>
> Status: **Approved** — proceed straight through to v1.0.0
>
> Source: extracted verbatim from the exploratory session that produced
> `PreviewForgeForClaudeCode/claudedocs/winning-storyboard-deck-v2.html`
> (the 160s cinematic deck for the *Built with Opus 4.7* hackathon submission).
> The workflow that built that deck became the design specification for this plugin.

---

## ① Positioning Thesis

A single self-contained HTML file that is **both** a full-screen slide deck **and**
the recording source for a demo video. One Socratic interview → 7-phase workflow
→ animated, recording-ready cinematic deck. Browser-only, OBS-ready, paper-grade
hero copy, human-presenter delivery.

**Pain points addressed** (drawn from the original session):

1. Hackathon teams spending hours in Keynote/PowerPoint the night before submission
   instead of building the product.
2. Loom recordings that sound AI-narrated — flat cadence, "as you can see" filler,
   no emotional arc.
3. Tome / Pitch / Gamma generate static slides that aren't built for *recording*.
4. Hero copy ("Attention is all you need" / "Stop chatting, start engineering") is
   the single highest-leverage line in any pitch — and there is no tool that helps
   craft it.
5. Reordering slides means manually editing every timestamp; lengthening the hero
   from 10s to 30s breaks every downstream marker.

**Solution shape**: a Claude Code plugin that owns the pitch-to-deck pipeline end-to-end.

---

## ② Naming + Identity

| Decision | Value |
|---|---|
| GitHub repo | `Two-Weeks-Team/PitchForgeForClaudeCode` |
| Plugin id | `pitch` |
| Slash command namespace | `/pitch:*` |
| Marketplace name | `pitchforge` |
| License | Apache-2.0 |
| Sibling positioning | *Not* a Preview Forge dependency. PF + PitchForge are sibling products under the Two-Weeks-Team forge family. PF builds the app; PitchForge films the app. |

Tagline (working): **"Preview is all you need. PitchForge is how you show it."**

---

## ③ Repository Scaffold

```
PitchForgeForClaudeCode/
├── .claude-plugin/marketplace.json
├── plugins/pitch/
│   ├── .claude-plugin/plugin.json
│   ├── agents/                         # 13 agents, 5-tier
│   │   ├── meta/                       # 2 — pitch-supervisor, pitch-pm
│   │   ├── writers/                    # 4 — brief-extractor, scenario-architect, hero-copywriter, tone-editor
│   │   ├── designers/                  # 3 — frame-designer, color-arc-designer, motion-designer
│   │   ├── engineers/                  # 3 — deck-assembler, animation-engineer, recording-engineer
│   │   └── reviewers/                  # 1+ — tone-auditor, timing-auditor, judging-criteria-auditor
│   ├── commands/                       # 14 slash commands under /pitch:*
│   ├── skills/cinematic-pitch/         # the entry-point skill
│   ├── hooks/                          # Layer-0: stale-count, tone-ai, modifier-guard
│   ├── schemas/                        # 4 — pitch-brief, frame-spec, deck-config, recording-config
│   ├── methodology/                    # 8 docs — the IP of the plugin
│   ├── templates/
│   │   ├── deck-shell.html             # 1300+ line reference (extracted from the v2 deck)
│   │   ├── frame-shapes/               # 9 reusable canvas shapes
│   │   ├── narrative-arcs/             # 4 templates — wow-first, problem-first, story, teaser
│   │   └── color-palettes/             # 3 OKLCH palettes
│   ├── examples/preview-forge-160s/    # the deck this plugin's own design came from
│   ├── memory/                         # CLAUDE.md / PROGRESS.md / LESSONS.md / HERO_CATALOG.md
│   └── bin/pitch                       # CLI helper
├── docs/
│   ├── PROPOSAL.md                     # ← this file
│   ├── DEMO-STORYBOARD.md              # the plugin's own demo (recursive)
│   └── SUBMISSION.md
├── tests/{fixtures,e2e,unit}/
├── scripts/
│   ├── verify-plugin.sh
│   ├── generate-deck.py                # frame-spec.json → deck.html
│   └── audit-deck.py
├── .github/workflows/ci.yml            # ubuntu + macOS matrix
├── CHANGELOG.md
├── CONTRIBUTING.md
├── SECURITY.md
├── LICENSE                             # Apache-2.0
├── NOTICE
└── README.md
```

---

## ④ The 7-Phase Workflow → Slash Command Mapping

The workflow was discovered by retrospectively analyzing the session that produced
the v2 deck. Every demo we have ever built passes through these 7 phases — the
plugin formalizes them as a pipeline.

| Phase | Command | Owning agent(s) | Artifact |
|---|---|---|---|
| **P1 · Brief** | `/pitch:new "<project>"` | `brief-extractor` + `pitch-pm` | `runs/<id>/brief.json` (Socratic 4-batch interview) |
| **P2 · Scenario** | `/pitch:scenario` | `scenario-architect` | `scenario.md` + `frames-spec.json` |
| **P3 · Storyboard** | `/pitch:storyboard` | `frame-designer` + `color-arc-designer` | `storyboard.html` (static visual review) |
| **P4 · Tone** | `/pitch:tone` | `tone-editor` + `tone-auditor` | VO rewrite + AI-ness audit report |
| **P5 · Deck** | `/pitch:deck` | `deck-assembler` | `deck.html` (navigable but unanimated) |
| **P6 · Animate** | `/pitch:animate` | `motion-designer` + `animation-engineer` | `deck-animated.html` |
| **P7 · Record** | `/pitch:record` | `recording-engineer` | `deck-cinematic.html` (O / F / R / A / P keys) |
| Cross | `/pitch:hero` | `hero-copywriter` | 5 inversion-pattern candidates |
| Cross | `/pitch:reorder` | `scenario-architect` | reorders slides + auto-recalculates all timestamps |
| Audit | `/pitch:status` | `judging-criteria-auditor` + `timing-auditor` | 6-gate pass/fail matrix |

`/pitch:new` alone runs the entire pipeline (Tier 1 Auto). Each command can also
be invoked individually for fine-grained iteration (Tier 2 Guided / Tier 3 Master).

### The 14 commands

```
/pitch:bootstrap       # first-time workspace setup
/pitch:new <project>   # P1-P7 end-to-end
/pitch:hero            # cross — refine hero copy in isolation
/pitch:scenario        # P2 only
/pitch:storyboard      # P3 only
/pitch:deck            # P5 only
/pitch:animate         # P6 only
/pitch:record          # P7 only
/pitch:tone            # P4 only — audit + rewrite
/pitch:reorder         # cross — swap slide order, reflow timestamps
/pitch:status          # audit — 6-gate pass/fail
/pitch:export          # package as single self-contained HTML
/pitch:gallery         # browse past pitches
/pitch:replay <run>    # deterministic replay from trace.jsonl
/pitch:help            # full command reference
```

---

## ⑤ Tier Model (progressive disclosure)

### Tier 1 — Auto (≈10 min, ≈10k tokens)
User provides three sentences. Plugin generates a complete 160s deck with sensible
defaults (wow-first arc, OKLCH warm-gold palette, paper-title hero copy, 9 frames).

**Use for**: hackathon demos, internal updates, casual launches.

### Tier 2 — Guided (≈30 min, ≈40k tokens) — **default**
3-batch `AskUserQuestion`:

- Batch A (4 required) — audience / runtime / hero copy / narrative arc.
- Batch B (5–8 optional) — judging criteria / prize categories / backup variants / tone / color palette.
- Batch C (frame-by-frame) — one-line concept per frame.

Output: brief.md + scenario.md + storyboard.html + deck.html (4 files).

### Tier 3 — Master (interactive, unbounded tokens)
Multi-turn iteration like the session that designed this plugin:
v1 → v2 tone fork, hero copy refinement, slide reordering, fine-tuning F4
duration from 30s → 10s, etc.

---

## ⑥ Roadmap (4 milestones)

### v0.1.0 — MVP (Day 1–3)
Goal: end-to-end reproducibility of the original session's deck.

- `/pitch:new` single command — 4-question Socratic.
- 1 narrative arc (`wow-first-180s`).
- 5 frame shapes (`chain` / `stack` / `counter` / `gallery` / `repo-install`).
- `templates/deck-shell.html` extracted from the v2 deck.
- 1 hero-copy pattern (paper-title inversion).
- Apache-2.0 / GitHub release-please / CI matrix.

**Acceptance**: a fresh user runs `/pitch:new "<project>"` once and produces a
160s deck that is qualitatively equivalent to `examples/preview-forge-160s/`.

### v0.5.0 — Tier 2 (Week 1)
Goal: guided variety.

- All 9 frame shapes.
- 4 narrative arcs (wow-first / problem-first / story / teaser).
- 3 color palettes.
- 3 length templates (60s / 180s / 300s).
- 3-batch `AskUserQuestion`.
- `/pitch:tone` standalone — Doumont staccato + `agro→drop→thrill` ruleset.
- `/pitch:reorder` — auto-reflow timestamps.
- `/pitch:hero` — 5 inversion candidates per call.
- Layer-0 hooks: `stale-count-detector`, `tone-ai-detector`.
- MediaRecorder API integration — in-browser recording → WebM export.

### v1.0.0 — Production (Week 2)
Goal: publishable.

- Tier 3 (Master) — multi-turn iteration with `LESSONS.md` cross-run learning.
- Multi-format export — HTML / PDF / WebM / GIF.
- A/B preview — light/dark, alternate length/arc.
- Marketplace registration (GitHub-hosted first; Anthropic official once approved).
- 5×3 team audit (lead / domain expert / red hat × 5 domains).
- Full CHANGELOG / SECURITY / CONTRIBUTING.
- **Recursive proof** — the plugin's own hero demo video is built with the plugin.

### v2.0.0 — Ecosystem (Month 2+)
- User-defined frame shapes (`templates/frame-shapes/custom/`).
- Narrative arc DSL (JSON definitions for new arcs).
- Plugin chain — `pf:freeze` → `pitch:new` (Preview Forge output → PitchForge input).
- Multi-language voiceover (Whisper TTS optional).
- Industry-specific stock visual libraries (SaaS / Mobile / B2B / Consumer).

---

## ⑦ Practices Inherited from Preview Forge

| Practice | Application |
|---|---|
| **release-please semver auto-bump** | Conventional Commits → tag generation |
| **CI matrix (ubuntu-latest + macos-14)** | Both runners must pass |
| **5×3 team audit** | Lead / Domain expert / Red hat × 5 domains, before v1.0 |
| **Layer-0 hook system** | `stale-count-detector` / `tone-ai-detector` / `cmd-modifier-guard` |
| **Cross-run LESSONS.md** | Patterns rejected once never re-suggested |
| **4-layer memory** | CLAUDE.md / PROGRESS.md / LESSONS.md / Anthropic Memory Tool |
| **Profile system** | `--tier=auto/guided/master` (variant of PF's `standard/pro/max`) |
| **Bootstrap command** | First-time workspace permission seeding |
| **English-only Rule 10** | All artifacts in English (Layer-0 enforced) |
| **Issue-driven improvement** | 5×3 review → issues → cluster PRs |

---

## ⑧ Differentiation Matrix

| Capability | Keynote/PowerPoint | Tome/Gamma/Pitch | reveal.js | Loom | **PitchForge** |
|---|:---:|:---:|:---:|:---:|:---:|
| Browser-native | ❌ | ✅ | ✅ | ✅ | ✅ |
| Recording-ready | ❌ | ❌ | ❌ | △ | ✅ |
| Brief→Deck automation | ❌ | △ | ❌ | ❌ | ✅ |
| Hero-copy guidance | ❌ | ❌ | ❌ | ❌ | ✅ |
| Human-tone audit | ❌ | ❌ | ❌ | ❌ | ✅ |
| Range-bounded auto-advance | ❌ | ❌ | △ | ❌ | ✅ |
| Tier color narrative | ❌ | ❌ | ❌ | ❌ | ✅ |
| Cross-run learning | ❌ | ❌ | ❌ | ❌ | ✅ |
| Single-file self-contained | ❌ | ❌ | ✅ | ❌ | ✅ |
| Apache-2.0 OSS | ❌ | ❌ | ✅ | ❌ | ✅ |

---

## ⑨ Risks + Mitigations

| Risk | Mitigation |
|---|---|
| Frame shape library cannot cover every visual concept | LLM-fallback (Tier 3): user describes a concept in one sentence → inline-CSS frame generated on the fly |
| Hero copy patterns are domain-dependent | 5-pattern catalog + industry-specific archives stored in `HERO_CATALOG.md` for cross-run reuse |
| Browser compatibility — `oklch()` / `clamp()` / `aspect-ratio` | Declare Safari 17+ / Chrome 113+ / FF 113+; ship optional fallback CSS at v1.0 |
| OBS / Loom integration cannot be invoked from the plugin | (a) v0.1: print on-screen instruction; (b) v0.5+: MediaRecorder API direct in-browser capture |
| Brand confusion with Preview Forge | README leads with "*not a Preview Forge dependency*"; separate marketplace; sibling-not-derivative tone |
| Anthropic official marketplace review queue | Ship via GitHub-hosted marketplace first; submit for official after v1.0.0 |
| Timestamp reflow on reordering | `/pitch:reorder` re-emits all 11 timestamp fields automatically; tested against the F4 → first-position case from the original session |

---

## ⑩ Recommended Initial Actions (now executing)

1. ✅ Repository scaffold — directory tree created.
2. ✅ Bootstrap commit — this `PROPOSAL.md` preserves the plan.
3. ⏳ Reference example — extract `winning-storyboard-deck-v2.html` from PreviewForgeForClaudeCode → `examples/preview-forge-160s/deck.html`.
4. ⏳ MVP scope — `/pitch:new` Tier 1 + 5 frame shapes + 1 hero copy pattern.
5. ⏳ Continuous push to v1.0.0 — multi-turn implementation.

---

## ⑪ Self-Audit (decisions made during this proposal)

The original conversation left 7 decisions to the implementer (this proposal):

| ID | Decision | Resolution | Rationale |
|---|---|---|---|
| A | Repository | `Two-Weeks-Team/PitchForgeForClaudeCode` | User-confirmed |
| B | Plugin id / namespace | `pitch` → `/pitch:*` | PF owns `/pf:*`; short and explicit |
| C | Start timing | Immediate | User: "1.0.0까지 밀어붙여" (push through to 1.0.0) |
| D | First reference example | v2 deck → `examples/preview-forge-160s/` | Verified artifact, recursive self-proof |
| E | License | Apache-2.0 | PF consistency, enterprise-friendly |
| F | Agent count | 13 (2+4+3+3+1) | Single-responsibility per agent without PF-style 144-crowding |
| G | First commit author | Claude (this session) | Sangguen on PF deadline; clean separation needed |

---

## ⑫ Why This Plugin Has to Exist

The session that produced the v2 deck took **7 hours** of human-AI collaboration
to discover and execute the 7-phase workflow. Most of that time was spent on
phases that are *not* unique to any project:

- Phase 1–2 (brief / scenario): generic across all demos.
- Phase 3 (storyboard): 9 frame shapes cover ~95 % of demo visuals.
- Phase 4 (tone): mechanical — the same Doumont / agro-drop-thrill rewrites apply.
- Phase 5 (deck assembly): pure boilerplate.
- Phase 6 (animation): identical CSS engine.
- Phase 7 (recording): identical control surface (R / O / F / A / P keys).

What is unique each time: hero copy, color choices, three or four key visuals.

PitchForge captures everything generic into the plugin and isolates the unique
~10 % into the Socratic interview. A user who would have spent 7 hours can produce
a comparable deck in 30 minutes.

That ratio — **14× compression with zero quality loss** — is the value proposition.

---

*End of proposal. The next document in the pipeline is `docs/DEMO-STORYBOARD.md`,
which will describe the plugin's own demo video, made with the plugin itself.*
