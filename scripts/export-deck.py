#!/usr/bin/env python3
"""
export-deck.py — package a frozen run for distribution (v1.0).

v0.1.0 behavior is "copy the HTML out". v1.0 expands that to:

  --format=html    (default)  — copy deck-cinematic.html to exports/
  --format=bundle  — tarball: brief.json + frame-spec.json + deck-config.json
                     + recording-config.json + deck-cinematic.html + tone-audit.json
  --format=pdf     — print instructions (requires headless Chrome by user)
  --format=webm    — print MediaRecorder workflow (requires --capture at gen time)
  --format=gif     — print ffmpeg one-liner that converts a webm tail-loop
                     of F4 + F11 into a 6-second hero loop GIF

The script is intentionally minimal — formats that need binary toolchains
(headless Chrome for PDF, ffmpeg for GIF) print the exact one-line command
the user needs to run. PitchForge does not bundle binaries.

Usage:
  python3 scripts/export-deck.py --run runs/<id>/ [--format=<fmt>] [--out exports/]
"""
from __future__ import annotations

import argparse
import shutil
import sys
import tarfile
from pathlib import Path


def export_html(run_dir: Path, out_dir: Path) -> Path:
    src = run_dir / "deck-cinematic.html"
    if not src.exists():
        raise FileNotFoundError(f"deck-cinematic.html not in {run_dir}")
    out_dir.mkdir(parents=True, exist_ok=True)
    name = _slugify(run_dir) + "-cinematic.html"
    dest = out_dir / name
    shutil.copy2(src, dest)
    return dest


def export_bundle(run_dir: Path, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    base = _slugify(run_dir)
    dest = out_dir / f"{base}.bundle.tar.gz"
    files = [
        "brief.json", "frame-spec.json", "deck-config.json",
        "recording-config.json", "deck-cinematic.html",
        "tone-audit.json", "scenario.md", "trace.jsonl", "retro.md",
    ]
    with tarfile.open(dest, "w:gz") as tar:
        for name in files:
            p = run_dir / name
            if p.exists():
                tar.add(p, arcname=f"{base}/{name}")
    return dest


def print_pdf_instructions(run_dir: Path, out_dir: Path) -> None:
    src = (run_dir / "deck-cinematic.html").resolve()
    out_dir.mkdir(parents=True, exist_ok=True)
    dest = out_dir / (_slugify(run_dir) + ".pdf")
    print("PDF export requires headless Chrome. Run:")
    print()
    print(f"  google-chrome --headless --disable-gpu \\")
    print(f"    --print-to-pdf='{dest}' \\")
    print(f"    'file://{src}'")
    print()
    print("  # or with macOS Chrome:")
    print(f"  /Applications/Google\\ Chrome.app/Contents/MacOS/Google\\ Chrome \\")
    print(f"    --headless --disable-gpu \\")
    print(f"    --print-to-pdf='{dest}' \\")
    print(f"    'file://{src}'")


def print_webm_instructions(run_dir: Path, out_dir: Path) -> None:
    print("WebM export uses the deck's built-in MediaRecorder hook.")
    print()
    print("Re-generate the deck with --capture so the script wires it up:")
    print()
    print(f"  python3 scripts/generate-deck.py \\")
    print(f"    --brief {run_dir}/brief.json \\")
    print(f"    --output {run_dir}/deck-cinematic.html \\")
    print(f"    --capture")
    print()
    print("Then open the regenerated file, press F to play the full range —")
    print("the browser prompts for screen-capture permission and downloads")
    print("a .webm blob automatically when END overlay appears.")


def print_gif_instructions(run_dir: Path, out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    out_dir_abs = out_dir.resolve()
    print("GIF export requires ffmpeg + an existing WebM (see --format=webm).")
    print()
    print("Convert a 6-second hero-loop (F4 wow + F11 outro) to GIF:")
    print()
    print(f"  ffmpeg -i pitchforge-recording.webm \\")
    print(f"    -vf 'fps=15,scale=960:-2:flags=lanczos' \\")
    print(f"    -t 6 \\")
    print(f"    {out_dir_abs}/{_slugify(run_dir)}-hero.gif")
    print()
    print("The 960px width keeps file size under ~5 MB while preserving the")
    print("hero copy legibly. Drop fps to 12 if you need < 3 MB.")


def _slugify(run_dir: Path) -> str:
    """Build a stable, user-visible export base name from the run dir.

    Prefers the brief's `project_name` (slugified) when available, falls back
    to the run dir's last segment with leading dots stripped. Hidden test
    dirs like `.generated` therefore become a meaningful prefix.
    """
    try:
        import json as _json
        brief_path = run_dir / "brief.json"
        if brief_path.exists():
            data = _json.loads(brief_path.read_text(encoding="utf-8"))
            project = (data.get("project_name") or "").strip()
            runtime = data.get("runtime_seconds") or ""
            arc = data.get("narrative_arc") or ""
            if project:
                slug = "-".join(filter(None, [
                    re.sub(r"[^A-Za-z0-9]+", "-", project).strip("-").lower(),
                    f"{runtime}s" if runtime else "",
                    arc,
                ]))
                if slug:
                    return slug
    except Exception:
        pass
    name = run_dir.name.lstrip(".").replace("/", "_").strip("_")
    return name or "pitchforge-export"


# regex import lazily — only needed inside _slugify
import re  # noqa: E402


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True, help="path to runs/<id>/ (must contain deck-cinematic.html)")
    p.add_argument("--format", choices=["html", "bundle", "pdf", "webm", "gif"], default="html")
    p.add_argument("--out", default="exports", help="output directory (default: exports/)")
    args = p.parse_args(argv)

    run_dir = Path(args.run)
    if not run_dir.is_dir():
        print(f"[FAIL] run dir not found: {run_dir}", file=sys.stderr)
        return 1

    out_dir = Path(args.out)
    fmt = args.format

    print(f"=== export-deck.py ({fmt}) ===")
    if fmt == "html":
        dest = export_html(run_dir, out_dir)
        size = dest.stat().st_size
        print(f"✓ {dest} ({size // 1024} KB)")
        print()
        print("Open this file in any modern browser. Press F11, then O or F.")
    elif fmt == "bundle":
        dest = export_bundle(run_dir, out_dir)
        size = dest.stat().st_size
        print(f"✓ {dest} ({size // 1024} KB)")
        print()
        print("Distribute this tarball — recipient runs `/pitch:replay <run>`")
        print("or simply opens deck-cinematic.html directly.")
    elif fmt == "pdf":
        print_pdf_instructions(run_dir, out_dir)
    elif fmt == "webm":
        print_webm_instructions(run_dir, out_dir)
    elif fmt == "gif":
        print_gif_instructions(run_dir, out_dir)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
