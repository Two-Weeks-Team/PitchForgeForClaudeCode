# Methodology 07 — Recording Protocol (Phase P7)

The deck is the recording source. PitchForge ships three layered display modes
that toggle via keyboard so a single browser tab can serve as the entire
production environment.

## The three modes

| Mode | What's visible | Trigger |
|---|---|---|
| **Review** | Top bar + canvas + voiceover panel + control panel | (default) |
| **Recording** | Canvas only — chrome hidden, dark border, floating ● timer | `R` key |
| **Cinematic** | Recording + on-canvas VO subtitles also hidden + auto-advance + countdown | `O` (opening only) or `F` (full) key |

Recording mode keeps the floating timer for take-management. Cinematic mode
hides everything — the captured frame is canvas-only.

## The OBS workflow (single keypress)

```
1. Open deck.html in a browser. Press F11 for fullscreen.
2. Open OBS. Add window capture for the browser. Set output to 1080p / 30fps.
3. Click Start Recording in OBS.
4. Switch to the browser. Press O.
   ↓
   3-2-1-GO countdown overlay appears (4 seconds — recorder gets ready).
   ↓
   Cinematic playback runs the configured slide range automatically.
   Each frame's animation timeline plays per the brief's runtime.
   ↓
   END overlay appears at completion (2.4s).
5. Click Stop Recording in OBS.
6. (Optional) Re-record with `P` to replay the current slide cleanly.
```

Total user keypresses during recording: **one** (the `O` to begin).

## Modifier-key safety

Keyboard shortcuts must NOT intercept browser-native combinations (`Cmd+R`, `Cmd+F`, `Cmd+O`, etc.). The deck's keyboard handler is guarded:

```js
document.addEventListener('keydown', e => {
  if (e.target.tagName === 'INPUT' || e.target.tagName === 'TEXTAREA') return;
  if (e.metaKey || e.ctrlKey || e.altKey) return;  // CRITICAL — never intercept browser shortcuts
  switch (e.key) {
    case 'r': case 'R': toggleRec(); break;
    case 'o': case 'O': playRange(...); break;
    // ...
  }
});
```

The `cmd-modifier-guard` Layer-0 hook validates this in any user-modified deck before publishing.

## Range-bounded playback

`playRange(start, end)` runs auto-advance only between two slide indices.
Used to capture partial sequences:

- `O` → opening only (covers the wow + indictment + pivot)
- `F` → full demo (covers the entire pitch)
- Custom ranges via `playRange(N, M)` from the JS console

After the end-index slide finishes its budget, the END overlay appears and auto-advance halts. The deck stays on the last slide so the user can stop the recorder cleanly.

## Re-record without leaving the page

Press `P` to replay the current slide's animations. Useful when the voiceover stumbles — drop the take, press P, do it again.

## Reorder reflow

If the user reorders slides via `/pitch:reorder`, all 11 timestamp fields, the SLIDE_DURATION array, the summaries array, and the cinematic button labels are updated by the assembler. The user never edits timestamps by hand.

This was the most error-prone manual step in the original session that produced this plugin's reference deck.

## v0.5+ — MediaRecorder integration

`/pitch:record --capture` triggers an in-browser MediaRecorder that writes a WebM blob to disk. Skip OBS entirely:

```
1. /pitch:record --capture  → opens deck.html with capture armed
2. Press O                    → countdown + cinematic + autorecord
3. WebM downloads at completion
```

Browser support: Chrome 113+ (full), Firefox 113+ (limited), Safari 17+ (preview only — falls back to OBS instructions).

## Cross-references

- `agents/engineers/recording-engineer.md`
- `commands/record.md`
- `hooks/cmd-modifier-guard.py`
