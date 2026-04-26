#!/usr/bin/env python3
"""
Layer-0 hook — stale-count-detector

Detects drift between counted artifacts on disk and the counts asserted
in README.md, deck "What's inside" tables, and the verify-plugin.sh
output. Mitigates Layer-0 Rule 9 ("stale counts kill credibility").

Triggered:
  - Post-write of README.md
  - Post-write of any deck.html / deck-cinematic.html
  - As part of /pitch:status (gate G5)

Behavior:
  - Walks plugins/pitch/ counting agents, commands, schemas, methodology
    docs, frame shapes, narrative arcs, color palettes, hooks.
  - Loads expected counts from --readme path (default README.md).
  - Reports drift > 0 as failure.

Heuristic count extraction from README:
  - Looks for patterns like "13 agents", "14 commands", "9 frame shapes",
    "4 narrative arcs", "3 color palettes", "8 methodology docs".
  - Compares to actual file counts.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path


def count_files(root: Path, *, glob: str, exclude_names: set[str] | None = None) -> int:
    exclude_names = exclude_names or set()
    return sum(
        1
        for p in root.glob(glob)
        if p.is_file() and p.name not in exclude_names
    )


def actual_counts(plugin_dir: Path) -> dict[str, int]:
    return {
        "agents": count_files(plugin_dir / "agents", glob="**/*.md"),
        "commands": count_files(plugin_dir / "commands", glob="*.md"),
        "schemas": count_files(plugin_dir / "schemas", glob="*.json"),
        "methodology": count_files(plugin_dir / "methodology", glob="*.md"),
        "frame-shapes": count_files(plugin_dir / "templates" / "frame-shapes", glob="*.html"),
        "narrative-arcs": count_files(plugin_dir / "templates" / "narrative-arcs", glob="*.json"),
        "color-palettes": count_files(plugin_dir / "templates" / "color-palettes", glob="*.json"),
        "hooks": count_files(plugin_dir / "hooks", glob="*.py"),
    }


# README-claim extraction patterns. Each entry maps a label → regex matching
# explicit numeric claims. The regex groups the digit count.
CLAIM_PATTERNS = {
    "agents":         re.compile(r"(\d+)\s+(?:total\s+)?agents?\b", re.IGNORECASE),
    "commands":       re.compile(r"(\d+)\s+(?:slash\s+)?commands?\b", re.IGNORECASE),
    "schemas":        re.compile(r"(\d+)\s+schemas?\b", re.IGNORECASE),
    "methodology":    re.compile(r"(\d+)\s+methodology\b", re.IGNORECASE),
    "frame-shapes":   re.compile(r"(\d+)\s+frame[- ]shapes?\b", re.IGNORECASE),
    "narrative-arcs": re.compile(r"(\d+)\s+narrative\s+arcs?\b", re.IGNORECASE),
    "color-palettes": re.compile(r"(\d+)\s+(?:color\s+)?palettes?\b", re.IGNORECASE),
    "hooks":          re.compile(r"(\d+)\s+(?:layer-0\s+)?hooks?\b", re.IGNORECASE),
}


CLAIM_BLOCK_RE = re.compile(
    r"<!--\s*pf:counts:start\s*-->(?P<body>.*?)<!--\s*pf:counts:end\s*-->",
    re.DOTALL,
)


def claimed_counts(text: str) -> dict[str, int]:
    """Return claims per category.

    If the README contains a `<!-- pf:counts:start --> ... <!-- pf:counts:end -->`
    block, only that block is scanned (authoritative source). Otherwise we fall
    back to a whole-file scan (legacy behavior; less reliable, prone to false
    positives from roadmap text).
    """
    block = CLAIM_BLOCK_RE.search(text)
    scope = block.group("body") if block else text
    out: dict[str, int] = {}
    for label, pattern in CLAIM_PATTERNS.items():
        match = pattern.search(scope)
        if match:
            out[label] = int(match.group(1))
    return out


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--plugin-dir",
        default="plugins/pitch",
        help="Path to plugins/pitch (default: plugins/pitch)",
    )
    parser.add_argument(
        "--readme",
        default="README.md",
        help="README path to scan for count claims (default: README.md)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit 1 if any claim is missing from README (otherwise warn).",
    )
    args = parser.parse_args(argv)

    plugin = Path(args.plugin_dir)
    if not plugin.is_dir():
        print(f"[FAIL] plugin dir not found: {plugin}", file=sys.stderr)
        return 1

    actual = actual_counts(plugin)

    readme_path = Path(args.readme)
    claimed: dict[str, int] = {}
    if readme_path.exists():
        claimed = claimed_counts(readme_path.read_text(encoding="utf-8"))
    else:
        print(f"[warn] README not found at {readme_path}; running file-count audit only.")

    print("=== stale-count-detector ===")
    print(f"plugin dir: {plugin}")
    print(f"readme:     {readme_path}")
    print()
    print(f"{'category':<18} {'actual':>8} {'claimed':>8} {'drift':>8}")
    print("-" * 50)

    drift_count = 0
    missing_count = 0
    for label, n in sorted(actual.items()):
        c = claimed.get(label)
        if c is None:
            missing_count += 1
            print(f"{label:<18} {n:>8} {'—':>8} {'(no claim)':>8}")
            continue
        delta = n - c
        flag = "" if delta == 0 else f"  ✗ drift {delta:+d}"
        if delta != 0:
            drift_count += 1
        print(f"{label:<18} {n:>8} {c:>8} {delta:>+8}{flag}")

    print()
    print(f"drift items:   {drift_count}")
    print(f"missing claims:{missing_count}")

    if drift_count > 0:
        print("[FAIL] stale counts detected — README claims diverge from disk.")
        return 1
    if args.strict and missing_count > 0:
        print("[FAIL] strict mode — README missing one or more counted categories.")
        return 1
    print("[ok] all counted categories agree (or are absent in README).")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
