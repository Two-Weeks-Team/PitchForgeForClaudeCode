#!/usr/bin/env python3
"""
build-recording-kit.py — package a frozen run for the video team.

The video team is **not** PitchForge's authors. They receive a kit and
must be able to record without reading any agent docs or methodology
files. Every artifact in the kit answers a specific question they will
have at the mic.

Output: `<out>/<project-slug>-<runtime>s-<arc>-recording-kit/` directory
plus a `.tar.gz` of the same.

Inside the kit:
  - deck-cinematic.html         — the recording source (self-contained)
  - voiceover-script.md         — frame-by-frame VO with delivery + tone
  - recording-checklist.md      — pre-flight sheet (one per session)
  - take-log.csv                — per-take tracking template
  - obs-profile.json            — suggested OBS scene config
  - README.md                   — run-specific copy of the playbook intro
  - meta.json                   — run id, runtime, arc, hero, key visuals

Spec: docs/RECORDING-PLAYBOOK.md.

Usage:
  python3 scripts/build-recording-kit.py --run runs/<id>/
  python3 scripts/build-recording-kit.py --run runs/<id>/ --out exports/

  # Dry run (validate, no tarball)
  python3 scripts/build-recording-kit.py --run runs/<id>/ --no-tarball
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import shutil
import sys
import tarfile
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLAYBOOK = REPO_ROOT / "docs" / "RECORDING-PLAYBOOK.md"


def slugify(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "-", s).strip("-").lower() or "pitchforge"


def fmt_time(seconds: float) -> str:
    m = int(seconds) // 60
    s = int(round(seconds)) % 60
    return f"{m}:{s:02d}"


def load_run(run_dir: Path) -> dict:
    required = ["brief.json", "frame-spec.json", "deck-config.json",
                "deck-cinematic.html"]
    missing = [f for f in required if not (run_dir / f).exists()]
    if missing:
        raise FileNotFoundError(f"run {run_dir} missing: {missing}")
    return {
        "brief":       json.loads((run_dir / "brief.json").read_text(encoding="utf-8")),
        "spec":        json.loads((run_dir / "frame-spec.json").read_text(encoding="utf-8")),
        "deck_config": json.loads((run_dir / "deck-config.json").read_text(encoding="utf-8")),
        "deck_html":   (run_dir / "deck-cinematic.html"),
    }


# ---- voiceover-script.md ------------------------------------------------ #

ACT_TONE_HINT = {
    "cover":  "title-card calm",
    "agro":   "prosecutor opening — confront, do not describe",
    "drop":   "keynote reveal — slow, then quiet",
    "thrill": "maker explaining their workshop — casual, confident",
    "outro":  "arrival — the hero echo is the last word on screen",
    "close":  "title-card close — hold for the recorder to cut",
}


def render_voiceover_script(brief: dict, spec: dict) -> str:
    out = io.StringIO()
    project = spec.get("project_name", "Untitled")
    runtime = int(spec.get("runtime_seconds", 0))
    arc = spec.get("narrative_arc", "")
    hero = (spec.get("hero") or {}).get("copy", "")
    print(f"# Voiceover script · {project} · {runtime}s · {arc}", file=out)
    print(file=out)
    print(f"> Hero copy: **{hero}**", file=out)
    print(f"> Read it slowly. Each syllable lands. Half-beat silence after.", file=out)
    print(file=out)
    print(f"Total runtime: {runtime} seconds. Frames: {len(spec.get('frames', []))}.", file=out)
    print("Voiceover lines below are *verbatim* — do not paraphrase the hero copy.", file=out)
    print(file=out)
    print("---", file=out)
    print(file=out)

    for frame in sorted(spec.get("frames", []), key=lambda f: f.get("position", 0)):
        fid = frame.get("frame_id")
        if fid in ("cover", "close"):
            # Cover/close are visual holds — no VO, but include the hold note
            print(f"## {fid} · {fmt_time(frame.get('time_start_seconds', 0))} – "
                  f"{fmt_time(frame.get('time_start_seconds', 0) + frame.get('duration_seconds', 0))} "
                  f"({int(frame.get('duration_seconds', 0))}s · {frame.get('act')})", file=out)
            print(file=out)
            print(f"> *(silent hold — let the title settle.)*", file=out)
            note = frame.get("delivery_note") or "Hold the screen for the recorder."
            print(f"**Delivery**: {note}", file=out)
            print(file=out)
            continue

        time_label = (
            f"{fmt_time(frame.get('time_start_seconds', 0))} – "
            f"{fmt_time(frame.get('time_start_seconds', 0) + frame.get('duration_seconds', 0))}"
        )
        print(f"## {fid} · {time_label} ({int(frame.get('duration_seconds', 0))}s · {frame.get('act')})", file=out)
        print(file=out)
        if frame.get("script_h2"):
            print(f"**Heading on screen**: *{frame['script_h2']}*", file=out)
            print(file=out)
        vo = (frame.get("voiceover") or "").strip()
        if vo:
            # Strip HTML for readability; keep <b> as a delivery emphasis cue.
            display = re.sub(r"</?[bi]>", "**", vo)
            display = re.sub(r"<[^>]+>", "", display)
            print(f"**VO**:", file=out)
            print(f"> {display}", file=out)
            print(file=out)
        delivery = frame.get("delivery_note") or "(no specific direction)"
        tone = frame.get("tone_note") or ACT_TONE_HINT.get(frame.get("act", ""), "")
        print(f"**Delivery**: {delivery}", file=out)
        print(f"**Tone**: {tone}", file=out)
        print(file=out)

    # Em-dash legend
    print("---", file=out)
    print(file=out)
    print("## Symbol legend", file=out)
    print(file=out)
    print("- `—` (em-dash): held breath, 0.4–0.6 s pause. Read the silence.", file=out)
    print("- `**bold**`: stress / land the word. The deck shows it in gold.", file=out)
    print("- `.` (period mid-line): Doumont staccato breath. Each fragment a beat.", file=out)
    return out.getvalue()


# ---- recording-checklist.md -------------------------------------------- #

def render_recording_checklist(brief: dict, spec: dict) -> str:
    project = spec.get("project_name", "Untitled")
    runtime = int(spec.get("runtime_seconds", 0))
    return f"""# Recording checklist · {project} · {runtime}s

Run through **once per session** before the first take. Record the
session date, recorder name, and answers below.

```
Session date:   ____________________
Recorder name:  ____________________
Start time:     ____________________
End time:       ____________________
```

## Hardware

- [ ] Mic positioned 6–8 inches from mouth, pop filter on
- [ ] Mic peaks under −6 dBFS, RMS around −18 dBFS
- [ ] Headphones on (closed-back, monitoring through OBS)
- [ ] Display at 1920×1080 minimum (preferred 1440p+)
- [ ] Display in dark mode forced (no toggle mid-take)
- [ ] All notifications silenced (Slack / iMessage / mail / focus mode on)
- [ ] Keyboard backlight off

## Browser

- [ ] Browser version: Chrome 113+ / Safari 17+ / Firefox 113+ confirmed
- [ ] Cache cleared, no extensions enabled
- [ ] Bookmarks bar hidden, zoom = 100 %
- [ ] `deck-cinematic.html` opens via `file://` URL
- [ ] F11 → fullscreen tested, no chrome visible
- [ ] Pressed `O` once: countdown overlay appeared correctly
- [ ] Floating ● timer NOT visible during cinematic playback (Layer-0 L5)
- [ ] Voiceover overlay box NOT visible during cinematic playback

## OBS

- [ ] Profile imported from `obs-profile.json` (or manual config matched)
- [ ] Window Capture pointed at the browser (not display capture)
- [ ] Output: 1920×1080, 30 fps, H.264 CBR 12000 Kbps
- [ ] Recording format = mkv
- [ ] Mic/Aux source metering shows green
- [ ] Test 5-second clip recorded and played back successfully

## Voiceover prep

- [ ] Voiceover script (`voiceover-script.md`) read once silently
- [ ] Hero copy memorized: **{(spec.get('hero') or {}).get('copy', '?')}**
- [ ] Em-dash held breaths identified per frame
- [ ] Doumont staccato cadence rehearsed once cold
- [ ] Glass of water within reach

## Per-take rule

5 takes minimum. Best of 5. Beyond 5, break for water — fatigue wins.

| Take | Range | Result | Notes |
|---:|---|---|---|
| 1 |    |       |       |
| 2 |    |       |       |
| 3 |    |       |       |
| 4 |    |       |       |
| 5 |    |       |       |

(See `take-log.csv` for the structured version.)
"""


# ---- take-log.csv ------------------------------------------------------ #

def render_take_log() -> str:
    buf = io.StringIO()
    writer = csv.writer(buf)
    writer.writerow([
        "take_number", "range", "started_at", "duration_s", "outcome",
        "lufs", "peak_dbfs", "issue_or_keeper", "filename", "notes",
    ])
    # Six pre-filled rows so the recorder fills in
    for i in range(1, 7):
        writer.writerow([i, "", "", "", "", "", "", "", "", ""])
    return buf.getvalue()


# ---- obs-profile.json -------------------------------------------------- #

def render_obs_profile(spec: dict) -> str:
    """A minimal OBS Studio scene/profile descriptor. OBS does not have a
    universal JSON-import path — this is descriptive metadata that the
    operator copies into Settings manually. Some OBS plugins consume this
    format; we document fields verbosely so a human can also use it."""
    project = spec.get("project_name", "PitchForge run")
    return json.dumps({
        "$schema": "https://obsproject.com/schemas/scene-profile-suggestion.json",
        "name": f"{project} cinematic",
        "scene": {
            "sources": [
                {
                    "type": "window-capture",
                    "name": "deck-cinematic browser window",
                    "match": "Google Chrome | Safari | Firefox running deck-cinematic.html",
                    "resolution": "1920x1080",
                    "fps": 30,
                },
                {
                    "type": "audio-input",
                    "name": "Microphone",
                    "device": "(set in OBS — operator's audio interface)",
                    "filters": [
                        {"type": "noise-suppression", "method": "rnnoise"},
                        {"type": "compressor", "ratio": "4:1", "threshold_db": -18, "attack_ms": 6, "release_ms": 60},
                        {"type": "limiter", "threshold_db": -1.0},
                    ],
                },
            ],
        },
        "output": {
            "format": "mkv",
            "encoder": "x264",
            "rate_control": "CBR",
            "video_bitrate_kbps": 12000,
            "audio_bitrate_kbps": 256,
            "audio_codec": "aac",
            "fps": 30,
            "resolution": "1920x1080",
        },
        "notes": [
            "Capture as mkv to survive crashes; remux to mp4 post-session.",
            "Hardware encoder (NVENC / VideoToolbox / AMF) acceptable when CPU x264 is unavailable, "
            "but bitrate must remain CBR 12000 Kbps to avoid cliff-edge quality drops.",
            "Do not enable Replay Buffer — keystroke 'P' overlap risk with the deck's replay key.",
        ],
    }, indent=2) + "\n"


# ---- README.md (run-specific) ------------------------------------------ #

def render_run_readme(brief: dict, spec: dict) -> str:
    project = spec.get("project_name", "Untitled")
    runtime = int(spec.get("runtime_seconds", 0))
    arc = spec.get("narrative_arc", "")
    hero = (spec.get("hero") or {}).get("copy", "")
    frames = spec.get("frames", [])
    primary = (spec.get("hero") or {}).get("primary_frame", "")
    primary_frame = next((f for f in frames if f.get("frame_id") == primary), None)
    primary_time = (
        f"{fmt_time(primary_frame['time_start_seconds'])} – "
        f"{fmt_time(primary_frame['time_start_seconds'] + primary_frame['duration_seconds'])}"
    ) if primary_frame else "(unknown)"

    return f"""# {project} — recording kit

Generated: {datetime.now(tz=timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}

## What's in this kit

| File | Purpose |
|---|---|
| `deck-cinematic.html` | The recording source. Open in a browser. |
| `voiceover-script.md` | Frame-by-frame VO + delivery + tone notes. |
| `recording-checklist.md` | Pre-flight sheet (one per session). |
| `take-log.csv` | Per-take tracking template. |
| `obs-profile.json` | Suggested OBS scene/output config. |
| `meta.json` | Machine-readable run metadata. |
| `README.md` | This file — run-specific quick start. |

## Run summary

- **Project**: {project}
- **Runtime**: {runtime} s ({arc} arc, {len(frames)} frames)
- **Hero copy**: **{hero}**
- **Primary hero placement**: frame `{primary}` at {primary_time}
- **Audience**: {brief.get('audience', '?')}

## 60-second start

1. Read `RECORDING-PLAYBOOK.md` (the master playbook in the parent docs)
   if this is your first PitchForge kit.
2. Open `deck-cinematic.html` in a modern browser. Press F11.
3. Press `O` to preview the opening sequence (~25–35s) without recording.
4. Read `voiceover-script.md` once silently.
5. Run through `recording-checklist.md`.
6. OBS → Start Recording → switch to browser → press `F` for the full demo.
7. Log each take in `take-log.csv`. Keep best of 5.

## Keyboard cheatsheet

| Key | Action |
|---|---|
| `→` `Space` `Enter` | next slide |
| `←` | prev slide |
| `Esc` | overview / exit overview |
| `O` | opening cinematic playback (range-bounded) |
| `F` | full cinematic playback |
| `R` | toggle recording mode (chrome hidden, ● timer visible) |
| `A` | toggle auto-advance (no countdown, no rec mode) |
| `P` | replay the current slide (re-trigger animations) |
| `1`–`9` | jump to slide N |
| (Cmd / Ctrl / Alt + anything) | passes through to the browser — never intercepted |

## Hand-back checklist

When you finish a session, the producer expects:

- All accepted takes as raw `mkv` (or `mp4`) files
- Filled-in `take-log.csv`
- One-line outcome note per take
- LUFS / peak readings
- A 30 s muted preview clip from the wow beat (frame `{primary}`)

Do not transcode, color-correct, or trim. The producer handles editing.
"""


# ---- meta.json --------------------------------------------------------- #

def render_meta(brief: dict, spec: dict) -> str:
    return json.dumps({
        "kit_schema_version": "0.1.0",
        "generated_at": datetime.now(tz=timezone.utc).isoformat(),
        "project_name":     spec.get("project_name"),
        "runtime_seconds":  spec.get("runtime_seconds"),
        "narrative_arc":    spec.get("narrative_arc"),
        "color_palette":    spec.get("color_palette"),
        "tone_profile":     spec.get("tone_profile"),
        "hero_copy":        (spec.get("hero") or {}).get("copy"),
        "hero_pattern":     (spec.get("hero") or {}).get("pattern"),
        "primary_frame":    (spec.get("hero") or {}).get("primary_frame"),
        "echo_frame":       (spec.get("hero") or {}).get("echo_frame"),
        "frame_count":      len(spec.get("frames", [])),
        "audience":         brief.get("audience"),
        "constraints":      brief.get("constraints"),
        "playbook_ref":     "docs/RECORDING-PLAYBOOK.md",
    }, indent=2, ensure_ascii=False) + "\n"


# ---- builder ------------------------------------------------------------ #

def build_kit(run_dir: Path, out_dir: Path, *, make_tarball: bool = True) -> tuple[Path, Path | None]:
    payload = load_run(run_dir)
    spec = payload["spec"]
    brief = payload["brief"]
    project_slug = slugify(spec.get("project_name", "pitchforge"))
    runtime = int(spec.get("runtime_seconds", 0))
    arc = spec.get("narrative_arc", "wow-first")

    kit_name = f"{project_slug}-{runtime}s-{arc}-recording-kit"
    kit_dir = out_dir / kit_name

    # Reset
    if kit_dir.exists():
        shutil.rmtree(kit_dir)
    kit_dir.mkdir(parents=True, exist_ok=True)

    # Copy the cinematic deck verbatim
    shutil.copy2(payload["deck_html"], kit_dir / "deck-cinematic.html")

    # Generated artifacts
    (kit_dir / "voiceover-script.md").write_text(render_voiceover_script(brief, spec), encoding="utf-8")
    (kit_dir / "recording-checklist.md").write_text(render_recording_checklist(brief, spec), encoding="utf-8")
    (kit_dir / "take-log.csv").write_text(render_take_log(), encoding="utf-8")
    (kit_dir / "obs-profile.json").write_text(render_obs_profile(spec), encoding="utf-8")
    (kit_dir / "README.md").write_text(render_run_readme(brief, spec), encoding="utf-8")
    (kit_dir / "meta.json").write_text(render_meta(brief, spec), encoding="utf-8")

    # Optionally include the master playbook so the kit is self-contained
    if PLAYBOOK.exists():
        shutil.copy2(PLAYBOOK, kit_dir / "RECORDING-PLAYBOOK.md")

    tarball_path: Path | None = None
    if make_tarball:
        tarball_path = out_dir / f"{kit_name}.tar.gz"
        with tarfile.open(tarball_path, "w:gz") as tar:
            tar.add(kit_dir, arcname=kit_name)
    return kit_dir, tarball_path


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True, help="path to runs/<id>/ (must contain brief.json + frame-spec.json + deck-cinematic.html)")
    p.add_argument("--out", default="exports", help="output directory (default: exports/)")
    p.add_argument("--no-tarball", action="store_true", help="skip producing the .tar.gz")
    args = p.parse_args(argv)

    run_dir = Path(args.run)
    out_dir = Path(args.out)
    try:
        kit_dir, tarball = build_kit(run_dir, out_dir, make_tarball=not args.no_tarball)
    except FileNotFoundError as e:
        print(f"[FAIL] {e}", file=sys.stderr)
        return 2

    file_count = sum(1 for _ in kit_dir.rglob("*") if _.is_file())
    total_bytes = sum(p.stat().st_size for p in kit_dir.rglob("*") if p.is_file())
    print("=== build-recording-kit ===")
    print(f"run:           {run_dir}")
    print(f"kit dir:       {kit_dir}")
    print(f"files in kit:  {file_count}")
    print(f"kit size:      {total_bytes // 1024} KB")
    if tarball:
        print(f"tarball:       {tarball} ({tarball.stat().st_size // 1024} KB)")
    print()
    print("Hand off the kit (or the tarball) to the video team. They follow")
    print("RECORDING-PLAYBOOK.md inside the kit; nothing else from this repo")
    print("is required.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
