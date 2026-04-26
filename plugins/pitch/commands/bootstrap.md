---
description: First-time setup for PitchForge in this workspace. Seeds memory, validates plugin structure, and confirms browser support.
---

# /pitch:bootstrap

Run this once per workspace before invoking any other `/pitch:*` command.

## What it does

1. Verifies the `pitch` plugin is installed and reachable.
2. Validates `plugins/pitch/.claude-plugin/plugin.json` against the plugin schema.
3. Validates `plugins/pitch/schemas/*.json` are well-formed.
4. Reads `plugins/pitch/memory/CLAUDE.md` to establish session rules.
5. Creates `runs/` directory in the user's workspace if missing.
6. Seeds `.claude/settings.local.json` with the Bash permission patterns
   PitchForge needs (mkdir, cp, file:// open, OBS detection commands).
7. Detects browser availability:
   - Chrome / Safari / Firefox version → checks if `oklch()`, `clamp()`,
     and `aspect-ratio` CSS features are supported.
   - Falls back gracefully on older browsers.
8. Prints the run report.

## Output

```
=== PitchForge v0.1.0 — bootstrap ===
Plugin:                 ✓ pitch v0.1.0
Schemas validated:      ✓ 4/4
Memory seeded:          ✓ CLAUDE.md / PROGRESS.md / LESSONS.md / HERO_CATALOG.md
Workspace runs/:        ✓ created
Bash permissions:       ✓ seeded
Browser support:        ✓ Chrome 142, Safari 18.2, Firefox 141 detected

Next: /pitch:new "<your project in one line>"
```

If any check fails, the bootstrap halts with a remediation pointer.
