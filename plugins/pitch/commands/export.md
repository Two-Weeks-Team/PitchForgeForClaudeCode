---
description: Package a frozen run as a single self-contained artifact. v0.1.0 supports HTML; v0.5+ adds PDF, WebM, GIF, and a portable plugin bundle.
---

# /pitch:export [run_id] [--format=html|pdf|webm|gif|bundle]

Wraps a frozen run for distribution.

## Usage

```bash
# Default: copy deck-cinematic.html out as <project>-cinematic.html
/pitch:export

# Export named formats
/pitch:export --format=html
/pitch:export --format=pdf       # v0.5+
/pitch:export --format=webm      # v0.5+
/pitch:export --format=gif       # v1.0+
/pitch:export --format=bundle    # v1.0+ — tarball with brief, scenario, deck, run metadata
```

## v0.1.0 — HTML only

`deck-cinematic.html` is already self-contained (no external CSS / JS / fonts).
Export simply copies it to `exports/<project_name>-<runtime>s-<arc>-cinematic.html`
and emits a one-line summary:

```
✓ Exported: exports/preview-forge-160s-wow-first-cinematic.html (245 KB)
  Open this file in any modern browser. Press F11 for fullscreen, then O or F.
```

## v0.5+ — additional formats

| Format | How |
|---|---|
| `pdf` | Print-mode CSS already lives in deck-shell. Headless Chrome renders to PDF. |
| `webm` | MediaRecorder during cinematic playback. Browser saves the blob. |
| `gif` | WebM → ffmpeg → GIF (loops F4 + F11 by default; full demo on `--full`). |
| `bundle` | Tarball: brief.json, scenario.md, frame-spec.json, deck-config.json, deck-cinematic.html, recording-config.json, trace.jsonl, retro.md. Useful for archives + replay. |

## v1.0+ — Plugin bundle

Wraps the run as a Claude Code plugin so others can run
`/pitch:replay <run>` deterministically.

## Cross-references

- `commands/replay.md`
- `commands/gallery.md`
