# 5 × 3 Team Audit — v1.0 release gate

Inherited from Preview Forge. Before any v1.0 release, five domains are
audited by three roles each (Lead / Domain expert / Red hat) for fifteen
total review passes. Findings cluster into issues; clusters of related
issues become single PRs.

This file is the **template + worksheet**. The actual review for the
v1.0 release is run in a fresh Claude Code session with this file as
the working surface; each row gets filled in.

## How to run

1. Copy this file to `docs/REVIEW-5x3.<YYYY-MM-DD>.md`.
2. For each `(domain × role)` cell, run a focused review pass using the
   prompts below. Record findings in the cell.
3. After all 15 cells filled, gather all findings into a flat list and
   cluster by topic. Each cluster → one PR.
4. Re-run the v1.0 acceptance suite (verify-plugin, v0.1, v0.5, v1.0)
   after every PR. Release blocked until all four are green again.

## The five domains

| # | Domain | What it checks |
|---|---|---|
| **D1** | **Methodology + arc design** | Are the 8 methodology docs consistent with each other and with the templates? Do the arcs honor the act mapping? |
| **D2** | **Generator + templates** | Does `scripts/generate-deck.py` faithfully render every shape × every palette? Are the template slot contracts complete? |
| **D3** | **Animation + recording** | Do the deck's animation engines (CSS + JS) cover every reference effect? Does cinematic mode hide everything per L1/L2/L5? |
| **D4** | **Hooks + audits** | Do the three Layer-0 hooks (`cmd-modifier-guard`, `stale-count-detector`, `tone-ai-detector`) catch the failures they claim? Is `verify-plugin.sh` complete? |
| **D5** | **Documentation + accessibility** | README, CONTRIBUTING, SECURITY, methodology docs — are they self-consistent? Are non-English audiences served by visual subtitles? Is the deck-cinematic.html fully keyboard-navigable? |

## The three roles

| Role | Stance |
|---|---|
| **Lead** | Lead engineer for the domain. Default-positive but rigorous. Signs off on the domain's design choices. |
| **Domain expert** | A hypothetical specialist (typographer for D5, accessibility expert for D5, animation lead for D3, etc.). Verifies the domain matches industry expectations. |
| **Red hat** | De Bono's red hat, applied adversarially. Looks for the failure mode that ships. Skeptical, hostile to assumptions. Blocks if anything smells. |

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

## Cross-references

- `docs/PROPOSAL.md` § ⑦ "5×3 team audit" — the practice description.
- Preview Forge's audit log (sibling project) for prior precedent.
