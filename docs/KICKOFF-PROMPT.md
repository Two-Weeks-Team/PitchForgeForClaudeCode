# Kickoff Prompt

Copy the block below verbatim into a **new Claude Code session** running in
the `PitchForgeForClaudeCode` working directory.

The prompt sets working context, points the assistant at the right docs, and
locks the milestone target. It is intentionally explicit — Claude does not
need to re-discover any of the prior design conversation.

---

## Paste this:

```
You are now working on PitchForge for Claude Code (Two-Weeks-Team/PitchForgeForClaudeCode).

This is a Claude Code plugin (sibling to Preview Forge, NOT a derivative)
that turns project context into a 60–300 second cinematic, recording-ready
demo deck through a 7-phase pipeline.

Working directory:
  /Users/<you>/Documents/GitHub/PitchForgeForClaudeCode

Read these files in order before doing anything else:

  1. docs/PROPOSAL.md        — full design specification, FROZEN
  2. docs/HANDOFF.md         — current state + ordered task list
  3. plugins/pitch/memory/CLAUDE.md   — Layer-0 session rules
  4. plugins/pitch/memory/LESSONS.md  — cross-run failures to avoid

Then run:

  bash scripts/verify-plugin.sh

This must currently pass at the documented baseline (verify-plugin.sh
prints "All verification checks passed."). Confirm before continuing.

Your milestone is v0.1.0 — minimum runnable pipeline (Tier 1 Auto). The
ordered task list is in docs/HANDOFF.md § "What's next". Work through it
in order. After v0.1.0 ships, continue to v0.5.0, then v1.0.0.

Conventions:

  - English-only output for every artifact (Layer-0 Rule from PreviewForge).
  - Conventional Commits → release-please auto-bumps semver.
  - Methodology docs (plugins/pitch/methodology/00-07.md) are the source of
    truth for what each phase does. Read the relevant phase doc before
    implementing the corresponding agent or command.
  - The reference example plugins/pitch/examples/preview-forge-160s/deck.html
    is the canonical deck — when you implement templates/deck-shell.html,
    parameterize from this file.

Do NOT:

  - Change PROPOSAL.md without an issue + discussion.
  - Add Korean (or any non-English) text to repo artifacts.
  - Break the verify-plugin.sh baseline.
  - Introduce external CDN dependencies in templates.

Time budget: unbounded. The user said "1.0.0까지 밀어붙여" (push through to
1.0.0). Take it. Iterate in waves; each wave should land verify-plugin.sh
green.

Start by reading PROPOSAL.md, then HANDOFF.md, then run verify-plugin.sh,
then begin v0.1.0 task #1 (the three remaining schemas).
```

---

## Why this prompt is structured this way

- **Working directory is explicit** — Claude doesn't infer; it reads.
- **Read order matters** — PROPOSAL gives "what we're building," HANDOFF gives "where we are," CLAUDE.md gives "how to behave," LESSONS.md gives "what's already been learned."
- **`verify-plugin.sh` baseline check** — establishes a known-good starting state. If it fails, something is wrong before any new work begins.
- **Milestone is named** — v0.1.0 is the immediate target. v0.5.0 and v1.0.0 are the long arc.
- **"Do NOT" list is short and high-impact** — only the failure modes that cost meaningful time in the prior conversation.
- **Time budget is explicit** — unbounded, but waves should leave the build green.

## Backup: minimum kickoff (if the user wants brevity)

If the user wants a shorter prompt:

```
PitchForge v0.1.0. Working dir: /Users/<you>/Documents/GitHub/PitchForgeForClaudeCode. Read docs/HANDOFF.md, run verify-plugin.sh, then start the v0.1.0 task list.
```

The full prompt is preferred — it loads the design intent up front and avoids
the next session re-asking questions the prior conversation already settled.
