# 5 × 3 Team Audit — v1.0 release gate

Inherited from Preview Forge. Before any v1.0 release, five domains are
audited by three roles each (Lead / Domain expert / Red hat) for fifteen
total review passes. Findings cluster into issues; clusters of related
issues become single PRs.

This file is the **template + worksheet**. The actual review for the
v1.0 release is run in a fresh Claude Code session (or via the Decision
Panel skill) with this file as the working surface; each row gets filled
in.

## When to run (deferred)

**Decision: defer the audit until immediately before public transition
or marketplace registration PR is queued.** Recorded
2026-04-27 by 10-expert Decision Panel (7/10 chose A_STACK as the
domain model; ROI Analyst + Pragmatist's dissent on timing was
adopted — running 5×3 now, with external users = 0 and 92/92 automated
suites green, has marginal yield over what the hooks already catch).

Trigger conditions to actually run the audit:

- Public visibility transition queued (`gh repo edit ... --visibility public`)
- Or marketplace registration PR ready to submit
- Or first external user reports a non-trivial issue
- Or v1.x release where any domain has accumulated > 5 unverified findings

Until any of those fires, this worksheet stays empty and the project
continues feature work.

## How to run

1. Copy this file to `docs/REVIEW-5x3.<YYYY-MM-DD>.md`.
2. For each `(domain × role)` cell, run a focused review pass using the
   prompts below. Record findings in the cell.
3. After all 15 cells filled, gather all findings into a flat list and
   cluster by topic. Each cluster → one PR.
4. Re-run the v1.0 acceptance suite (verify-plugin, v0.1, v0.5, v1.0)
   after every PR. Release blocked until all four are green again.

## The five domains

Domain model: **A_STACK** (Stack 5-layer) — adopted by Decision Panel
2026-04-27 (7/10 majority). Each domain owns a layer of the artifact
stack; layers do not overlap.

| # | Domain | What it checks |
|---|---|---|
| **D1** | **Methodology + arc design** | Are the 8 methodology docs consistent with each other and with the templates? Do the arcs honor the act mapping? **D1 owns `schemas/*.json` (the contracts).** |
| **D2** | **Generator + templates** | Does `scripts/generate-deck.py` faithfully render every shape × every palette? Are the template slot contracts complete? **D2 is the *consumer* of D1's schemas, never the owner.** |
| **D3** | **Animation + recording** | Do the deck's animation engines (CSS + JS) cover every reference effect? Does cinematic mode hide everything per L1/L2/L5? |
| **D4** | **Hooks + audits** | **Charter (locked):** Layer-0 enforcement (cmd-modifier-guard, stale-count-detector, tone-ai-detector) **+** modifier-key safety verification across generated decks **+** `.env`/`.gitignore` policy enforcement (no secrets committable) **+** `verify-plugin.sh` coverage of all on-disk artifact counts. Charter is locked because D4 is the only domain that must catch its own evasion. |
| **D5** | **Documentation + accessibility** | README, CONTRIBUTING, SECURITY, methodology cross-references — self-consistent? OKLCH text/bg contrast ≥ 4.5:1 across all 3 palettes? Keyboard-only navigation in `deck-cinematic.html` complete? Browser compatibility claim (Safari 17+ / Chrome 113+ / Firefox 113+) honored or surfaced as warning? |

### Cross-domain ownership rules (mitigation #1)

To prevent double-counting and blind spots at domain seams:

- `schemas/*.json` → **D1 owns** (definitions). D2 consumes; D2 findings on schema violations are *escalated to D1*, not duplicated.
- `frame-spec.json` (runtime artifact) → **D2 owns** (it is generator output). D1 owns the schema that validates it.
- `deck-shell.html` palette tokens → **D2 owns** (substitution). D3 owns the runtime CSS keyframes the tokens flow into.
- Layer-0 hooks → **D4 owns**. D2 calls hooks but does not audit them.
- README count claims → **D5 owns** (documentation). D4 enforces the constraint via stale-count-detector but D5 owns the prose.

## The three roles

| Role | Stance |
|---|---|
| **Lead** | Lead engineer for the domain. Default-positive but rigorous. Signs off on the domain's design choices. |
| **Domain expert** | A hypothetical specialist (typographer for D5, accessibility expert for D5, animation lead for D3, etc.). Verifies the domain matches industry expectations. |
| **Red hat** | De Bono's red hat, applied adversarially. Looks for the failure mode that ships. Skeptical, hostile to assumptions. Blocks if anything smells. |

### Red-hat forced question (mitigation #2)

The Decision Panel flagged a specific failure mode: A_STACK runs the
risk of becoming a "self-congratulatory rubber-stamp" where Red-hat
findings duplicate what Layer-0 hooks already catch. To prevent this,
**every Red-hat cell must answer this question explicitly before
recording any finding**:

> *"What does this layer expose that the automated hooks
> (cmd-modifier-guard / stale-count-detector / tone-ai-detector /
> verify-plugin) and the four acceptance suites do **NOT** already
> verify?"*

If the Red-hat cannot identify a non-overlapping concern, the cell
records "no non-redundant finding — automation covers this layer" and
moves on. This is not a failure; it is honest signal that the layer is
adequately self-policed.

## The 15 cells

| | Lead | Domain expert | Red hat |
|---|---|---|---|
| **D1 Methodology** | _findings:_ | _findings:_ | _findings:_ |
| **D2 Generator** | _findings:_ | _findings:_ | _findings:_ |
| **D3 Animation/Recording** | _findings:_ | _findings:_ | _findings:_ |
| **D4 Hooks/Audits** | _findings:_ | _findings:_ | _findings:_ |
| **D5 Docs/A11y** | _findings:_ | _findings:_ | _findings:_ |

## Review prompts (per cell)

### D1 — Methodology

- **Lead**: Walk through `methodology/00-07.md` and check every
  cross-reference resolves. Are gate definitions (G1–G6) consistent
  across `pitch-supervisor.md` and `commands/status.md`?
- **Domain expert** (narrative designer): Do the four arcs cover the
  realistic shape space? Where would a real demo not fit?
- **Red hat**: A user runs `/pitch:new` with a one-liner that doesn't
  match any tracked pattern. What breaks first?

### D2 — Generator

- **Lead**: Are all 9 frame shape templates honored by
  `scripts/generate-deck.py`? Currently 5 are hardcoded inline with
  rich content; the other 4 ship as templates. Is that gap acceptable
  for v1.0 or must it close?
- **Domain expert** (typographer): Do the OKLCH lightness ramps in
  the three palettes maintain ≥ 4.5:1 contrast on text-on-bg pairs?
- **Red hat**: A user reorders slides to put F4 (the wow) at the very
  end. Does the hero copy still get its primary placement, or do we
  emit a deck with no wow?

### D3 — Animation / Recording

- **Lead**: Every CSS keyframe (`aFade`, `aUp`, …, `aLand`) — does
  each frame in the reference deck use at most one per element?
- **Domain expert** (motion designer): The 0.12s per-word stagger —
  is that fast enough on 4K displays, slow enough on 1080p?
- **Red hat**: A user has an extension that intercepts F11. What
  breaks?

### D4 — Hooks / Audits

- **Lead**: `tone-ai-detector.py` — every NEVER-list pattern, em-dash
  rule, hero preservation rule actually fires on a synthetic
  violation? (Add fixtures.)
- **Domain expert** (linguist): Does the staccato density rule
  generalize to non-American English idioms?
- **Red hat**: A user drops a Korean voiceover into `frame-spec.json`.
  Does the audit silently pass? It should refuse with a Layer-0 Rule 3
  (English-only) violation. **(Currently absent — open issue.)**

### D5 — Docs / Accessibility

- **Lead**: README "What ships" table — every count claim has a
  hook-validatable line item.
- **Domain expert** (a11y): Press Tab. Can a keyboard-only user
  navigate the deck? Is focus-visible respected? Does the ESC menu
  list slides in reading order?
- **Red hat**: Open the deck in Safari 15. Does anything render? The
  README claims Safari 17+; what does the user see otherwise?

## Issue clustering format

After all 15 cells are filled, append:

```
## Cluster A — <topic>
- Source cells: D2-Lead, D2-Red, D3-Lead
- Severity: blocker / high / medium / low
- Proposed fix: <PR description>

## Cluster B — <topic>
…
```

The release commits one PR per cluster. After every PR:

1. Re-run `bash scripts/verify-plugin.sh`
2. Re-run `bash tests/e2e/regenerate-reference-deck.sh`
3. Re-run `bash tests/e2e/v0.5-variety.sh`
4. Re-run `bash tests/e2e/v1.0-recursive.sh`

Release is blocked until all four are green and every cell is filled.

## Domain split triggers (mitigation #4)

Each domain's scope was sized for v1.0. Two domains are flagged for
likely growth:

- **D3 (Animation + Recording)** — if any single audit run accumulates
  > 5 unverified findings in this domain, **split into D3a Animation /
  D3b Recording** for the next release. Trigger expected around v1.3
  per the Operator persona's pre-mortem.
- **D5 (Docs + A11y)** — if Domain-expert role-play feels heterogeneous
  ("typographer for docs, a11y expert for keyboard-nav cannot share a
  single persona"), **split into D5a Docs / D5b A11y** and merge
  **D4 Hooks** into **D2 Generator** to preserve the 5-domain count.
  Trigger noted by Domain Expert persona in v1.0 panel.

Splits are *prepared* now, *applied* on demand. The 5-domain budget is
the constant; which domains fill it can rotate.

## Decision Panel trace (origin of this worksheet)

| Date | Decision | Source |
|---|---|---|
| 2026-04-27 | Adopt Stack 5-layer (A_STACK) as the domain model | Decision Panel 7/10 majority — Strategist, Critical Reviewer, Risk Engineer, Domain Expert, Operator, Security Auditor, Pragmatist voted A_STACK |
| 2026-04-27 | Defer first audit run to immediately before public/marketplace transition | ROI Analyst + Pragmatist dissent (timing); user approval via /decision-panel + AskUserQuestion |
| 2026-04-27 | Add 4 mitigations (schema ownership rule, Red-hat forced question, D4 charter lock, split triggers) | Cross-cutting findings from 7 panelists; user approval to inline |

Dissenting voices preserved (must consult before any future audit run):

- **Devil's Advocate**: voted D_RISK; concern: "A_STACK becomes a
  self-congratulatory ritual that duplicates hook coverage."
  → addressed by mitigation #2 (Red-hat forced question).
- **ROI Analyst**: voted D_RISK; concern: "Marginal yield over
  92/92 automation while external users = 0."
  → addressed by deferring the run (When-to-run section).
- **Innovator**: voted OTHER (G_RECURSIVE); proposal: "PitchForge
  generates its own audit deck — dogfooding."
  → parked for v1.1+ trial; not blocking the v1.0 audit.

## Cross-references

- `docs/PROPOSAL.md` § ⑦ "5×3 team audit" — the practice description.
- Preview Forge's audit log (sibling project) for prior precedent.
- Decision Panel skill — `~/.claude/skills/decision-panel/`
