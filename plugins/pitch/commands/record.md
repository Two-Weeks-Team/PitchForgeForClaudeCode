---
description: Phase P7 only — emit deck-cinematic.html with countdown overlay, range-bounded auto-advance, and modifier-key safety. The final shippable artifact you record with OBS.
---

# /pitch:record [run_id]

Adds the recording layer. Reads `runs/<id>/deck-animated.html` and emits
`runs/<id>/deck-cinematic.html` — the file you point OBS at.

## Usage

```bash
# Default
/pitch:record

# Specific run
/pitch:record runs/2026-04-27-preview-forge

# v0.5+ MediaRecorder direct capture (browser saves WebM)
/pitch:record --capture
```

## What gets added

Per `methodology/07-recording-protocol.md`:

- **Cinematic mode** — `body.cinematic` class hides the on-canvas VO
  overlay, the floating timer, and the navbar; only the canvas remains.
- **Countdown overlay** — `3 → 2 → 1 → GO` in 1-second cadence before
  cinematic playback begins. Recorder gets ≥ 4s to confirm capture
  started.
- **Range-bounded playback** — `playRange(start, end)` runs
  auto-advance only between two positions. Default ranges: `O` =
  opening (wow → first thrill), `F` = full (wow → outro).
- **Modifier-key safety (L1)** — keyboard handler early-returns on
  `Cmd` / `Ctrl` / `Alt` so browser shortcuts (`Cmd+R` reload,
  `Cmd+F` find, etc.) pass through.
- **L5 mitigation** — `body.cinematic #rec-timer { display: none }` so
  the floating timer never lands in the captured video.

## Outputs

- `runs/<id>/recording-config.json`
- `runs/<id>/deck-cinematic.html`

## Recording workflow (printed after success)

```
1. Open deck-cinematic.html in Chrome / Safari / Firefox (latest).
2. Press F11 for fullscreen.
3. Open OBS / Loom. Add window capture for the browser.
4. Click Start Recording.
5. Switch to the browser. Press O (opening) or F (full).
   ↓ 3-2-1-GO countdown (4s)
   ↓ Cinematic playback runs the configured range
   ↓ END overlay at completion
6. Press Stop in OBS.
```

## Cross-references

- `agents/engineers/recording-engineer.md`
- `methodology/07-recording-protocol.md`
- `hooks/cmd-modifier-guard.py` — Layer-0 hook validates L1.
- `memory/LESSONS.md#L1` `#L2` `#L5`
