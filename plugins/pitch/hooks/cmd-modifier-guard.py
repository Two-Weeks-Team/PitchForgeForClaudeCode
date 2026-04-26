#!/usr/bin/env python3
"""
Layer-0 hook — cmd-modifier-guard

Validates that any generated deck HTML contains the modifier-key safety
guard inside its keydown handler. Mitigates LESSONS.md L1.

Triggered: post-write of deck.html / deck-animated.html / deck-cinematic.html.

Behavior:
  - Reads the file.
  - Locates the inline <script> block containing `addEventListener('keydown'`.
  - Asserts the early-return clause is present (any of the patterns below).
  - Exits 0 on pass, 1 on fail.

Patterns considered safe (any one suffices):
  if (e.metaKey || e.ctrlKey || e.altKey) return;
  if(e.metaKey || e.ctrlKey || e.altKey) return;
  if (e.metaKey||e.ctrlKey||e.altKey) return;

Failure is a Layer-0 block: the deck must not be released without it,
because Cmd+R reload, Cmd+F find, etc. would be intercepted and break
the recording session.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REQUIRED_PATTERN = re.compile(
    r"if\s*\(\s*e\.metaKey\s*\|\|\s*e\.ctrlKey\s*\|\|\s*e\.altKey\s*\)\s*return\s*;",
    re.MULTILINE,
)
KEYDOWN_PATTERN = re.compile(
    r"addEventListener\(\s*['\"]keydown['\"]",
    re.MULTILINE,
)


def check_file(path: Path) -> tuple[bool, str]:
    if not path.exists():
        return False, f"file not found: {path}"
    try:
        content = path.read_text(encoding="utf-8")
    except Exception as exc:
        return False, f"read error: {exc}"

    if not KEYDOWN_PATTERN.search(content):
        # No keydown handler — nothing to guard. This is acceptable for
        # storyboard.html (static review surface). Treat as pass.
        return True, "no keydown handler — safe by absence"

    if not REQUIRED_PATTERN.search(content):
        return False, (
            "keydown handler does not guard modifier keys (L1 violation). "
            "Required clause: if (e.metaKey || e.ctrlKey || e.altKey) return;"
        )
    return True, "modifier-key guard present"


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", help="HTML file(s) to validate")
    parser.add_argument("--strict", action="store_true",
                        help="Treat any keydown handler without guard as failure")
    args = parser.parse_args(argv)

    rc = 0
    for raw in args.paths:
        path = Path(raw)
        ok, message = check_file(path)
        prefix = "[ok]" if ok else "[FAIL]"
        print(f"{prefix} {path}: {message}")
        if not ok:
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
