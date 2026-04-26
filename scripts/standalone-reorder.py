#!/usr/bin/env python3
"""
standalone-reorder.py — `/pitch:reorder` runtime (v0.5).

L4 mitigation in code: when slide order changes, every downstream
ripple site reflows from a single source (frame-spec.json):

  - frame-spec.frames[*].position
  - frame-spec.frames[*].time_start_seconds
  - deck-config.slide_duration_seconds (re-ordered)
  - deck-config.summaries (re-ordered)
  - deck-config.progress_widths_pct (re-computed)
  - deck-config.ranges.opening|full.{start_position, end_position}
  - deck-config.hero.primary_position / echo_position

Then the deck is re-rendered via scripts/generate-deck.py so all 11
on-canvas timestamps + the JS SLIDE_DURATION array + cinematic button
labels stay in lockstep.

Usage:
  # Provide explicit new order (comma-separated frame_ids)
  python3 scripts/standalone-reorder.py \\
    --run runs/<id>/ \\
    --order cover,F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,close

  # Move a single frame to a target position (1-indexed)
  python3 scripts/standalone-reorder.py --run runs/<id>/ --move F4=2

  # Validate without writing (dry run)
  python3 scripts/standalone-reorder.py --run runs/<id>/ --order ... --dry-run

The brief is unchanged. Only frame-spec.json + deck-config.json are
overwritten in place; the deck-cinematic.html is regenerated.

Spec: methodology/01-narrative-arcs.md, commands/reorder.md,
memory/LESSONS.md#L4.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def parse_order(spec: str, current_ids: list[str]) -> list[str]:
    """Resolve --order flag. Accepts comma-separated full order; rejects
    any id that isn't in the current spec or any duplicate."""
    new_order = [s.strip() for s in spec.split(",") if s.strip()]
    if len(new_order) != len(current_ids):
        raise ValueError(
            f"--order has {len(new_order)} ids; spec has {len(current_ids)}. "
            f"Order must list every existing frame_id exactly once."
        )
    if set(new_order) != set(current_ids):
        missing = set(current_ids) - set(new_order)
        unknown = set(new_order) - set(current_ids)
        msg = []
        if missing:
            msg.append(f"missing: {sorted(missing)}")
        if unknown:
            msg.append(f"unknown: {sorted(unknown)}")
        raise ValueError("; ".join(msg))
    if len(set(new_order)) != len(new_order):
        raise ValueError("--order has duplicate frame_ids")
    return new_order


def parse_move(spec: str, current_ids: list[str]) -> list[str]:
    """Resolve --move flag (e.g. 'F4=2'). Returns the resulting full order."""
    if "=" not in spec:
        raise ValueError("--move format: <frame_id>=<target_position_1_indexed>")
    fid, target_s = spec.split("=", 1)
    fid = fid.strip()
    target = int(target_s)
    if fid not in current_ids:
        raise ValueError(f"--move: unknown frame_id {fid}")
    if target < 1 or target > len(current_ids):
        raise ValueError(f"--move: position {target} out of range 1..{len(current_ids)}")
    rest = [x for x in current_ids if x != fid]
    rest.insert(target - 1, fid)
    return rest


def reflow_frame_spec(spec: dict, new_order: list[str]) -> dict:
    """Mutate spec in-place: reorder frames, recompute position +
    time_start_seconds. duration_seconds is preserved per frame."""
    frames_by_id = {f["frame_id"]: f for f in spec["frames"]}
    new_frames = []
    cursor = 0.0
    for pos, fid in enumerate(new_order, start=1):
        frame = dict(frames_by_id[fid])  # shallow copy
        frame["position"] = pos
        frame["time_start_seconds"] = round(cursor, 2)
        cursor += float(frame["duration_seconds"])
        new_frames.append(frame)
    spec["frames"] = new_frames
    return spec


def maybe_reflow_hero(spec: dict) -> dict:
    """If the hero's primary_frame or echo_frame moved, re-derive
    primary_position / echo_position from the new ordering. The hero
    *frame_id* stays — only positions update."""
    hero = spec.get("hero") or {}
    if not hero:
        return spec
    primary = hero.get("primary_frame")
    echo = hero.get("echo_frame")
    pos_by_id = {f["frame_id"]: f["position"] for f in spec["frames"]}
    # primary_frame must still exist; if it doesn't, surface error to caller
    if primary and primary not in pos_by_id:
        raise ValueError(f"hero.primary_frame '{primary}' missing from new ordering")
    if echo and echo not in pos_by_id:
        raise ValueError(f"hero.echo_frame '{echo}' missing from new ordering")
    return spec


def run_generator(brief_path: Path, spec_path: Path, output: Path) -> None:
    """Re-invoke scripts/generate-deck.py with the *updated* frame-spec
    (not just the brief) so deck-config + recording-config +
    deck-cinematic.html all reflow without arc template overriding the
    reorder. --frame-spec instructs the generator to honor the spec."""
    cmd = [
        sys.executable,
        str(REPO_ROOT / "scripts" / "generate-deck.py"),
        "--brief", str(brief_path),
        "--frame-spec", str(spec_path),
        "--output", str(output),
    ]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        sys.stderr.write(proc.stdout + "\n" + proc.stderr)
        raise RuntimeError("generate-deck.py failed during reorder reflow")


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--run", required=True, help="path to runs/<id>/ (must contain brief.json + frame-spec.json)")
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--order", help="comma-separated full new order (frame_ids)")
    g.add_argument("--move",  help="single move: <frame_id>=<target_position_1_indexed>")
    p.add_argument("--dry-run", action="store_true", help="validate + print preview, do not write")
    p.add_argument("--skip-regen", action="store_true",
                   help="update frame-spec.json only, skip deck-cinematic.html regeneration")
    args = p.parse_args(argv)

    run_dir = Path(args.run)
    brief_path = run_dir / "brief.json"
    spec_path = run_dir / "frame-spec.json"
    if not brief_path.exists() or not spec_path.exists():
        print(f"[FAIL] {run_dir} must contain brief.json + frame-spec.json", file=sys.stderr)
        return 2

    spec = load_json(spec_path)
    current_ids = [f["frame_id"] for f in sorted(spec["frames"], key=lambda f: f["position"])]

    try:
        if args.order:
            new_order = parse_order(args.order, current_ids)
        else:
            new_order = parse_move(args.move, current_ids)
    except ValueError as e:
        print(f"[FAIL] {e}", file=sys.stderr)
        return 2

    if new_order == current_ids:
        print("[noop] order unchanged.")
        return 0

    # Validation: hero placement preserved
    try:
        spec = reflow_frame_spec(spec, new_order)
        spec = maybe_reflow_hero(spec)
    except ValueError as e:
        print(f"[FAIL] {e}", file=sys.stderr)
        return 2

    # Validation: G2 — sum(duration) ≈ runtime ± 5%
    runtime = float(spec["runtime_seconds"])
    sum_dur = sum(float(f["duration_seconds"]) for f in spec["frames"]
                  if f["frame_id"] not in ("cover", "close"))
    delta = abs(sum_dur - runtime) / runtime if runtime else 0.0
    if delta > 0.05:
        print(f"[FAIL] G2 violation after reorder: content sum {sum_dur}s vs target {runtime}s "
              f"(delta {delta:.1%}). Adjust frame durations or reduce runtime.",
              file=sys.stderr)
        return 2

    # Preview
    print("=== reorder preview ===")
    print(f"run: {run_dir}")
    print(f"old order: {','.join(current_ids)}")
    print(f"new order: {','.join(new_order)}")
    print(f"content sum: {sum_dur}s (target {int(runtime)}s, delta {delta:.1%})")
    print()

    if args.dry_run:
        print("[dry-run] no files written.")
        return 0

    # Write back
    write_json(spec_path, spec)
    print(f"✓ wrote {spec_path}")

    if args.skip_regen:
        print("[skip-regen] downstream artifacts (deck-config / recording-config / "
              "deck-cinematic.html) are now stale — re-run generate-deck.py to refresh.")
        return 0

    deck_path = run_dir / "deck-cinematic.html"
    try:
        run_generator(brief_path, spec_path, deck_path)
    except RuntimeError as e:
        print(f"[FAIL] regeneration failed: {e}", file=sys.stderr)
        return 1
    print(f"✓ regenerated {deck_path}")
    print(f"✓ deck-config.json + recording-config.json refreshed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
