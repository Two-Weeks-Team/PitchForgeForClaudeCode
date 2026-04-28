#!/usr/bin/env python3
"""
Layer-0 hook — html-escape-validator

Validates that a generated deck-cinematic.html does NOT contain raw
`<script>` tags outside the single trusted inline `<script>` block,
nor any `</script>` substrings that could break out of JS string
literals embedded in that block, nor obvious unescaped event-handler
attributes (`onerror=`, `onload=`, etc.) outside the deck's own
declared CSS keyframes.

Triggered:
  - Post-write of any deck-*.html
  - As part of /pitch:status (extends gate G6 mod-key safety)

Behavior:
  - Reads the file
  - Counts the inline `<script>` blocks; expects exactly 1 (the deck's own)
  - Scans for `</script>` outside that block
  - Scans for `<script` substrings inside string literals (heuristic)
  - Scans for inline event handlers in user-substituted areas
  - Exits 0 on pass, 1 on fail

This is a defense-in-depth check — `scripts/generate-deck.py` already
escapes user text via `escape_user_text` / `escape_with_inline_markup` /
`safe_json_for_script`, but this hook catches drift if a future PR
forgets the escape calls or adds a new substitution sink without
threading user input through them.
"""
from __future__ import annotations

import argparse
import re
import sys
from html.parser import HTMLParser
from pathlib import Path

# How many inline <script>...</script> blocks the deck-shell ships with.
# Update only if the deck-shell intentionally adds another script element.
EXPECTED_SCRIPT_BLOCKS = 1

# Event-handler attribute prefixes that should NEVER appear in PitchForge
# generator output (we don't use any inline event handlers; the deck wires
# every listener via addEventListener inside the trusted script block).
INLINE_HANDLERS = (
    "onerror=", "onload=", "onclick=", "onmouseover=", "onfocus=",
    "onblur=", "ontoggle=", "onbeforeprint=", "onmessage=", "oninput=",
    "onchange=", "onsubmit=", "onkeydown=", "onkeyup=", "onkeypress=",
)


def find_script_blocks(content: str) -> list[tuple[int, int]]:
    """Return [(start, end)] index ranges of each <script>…</script> block."""
    out = []
    pos = 0
    while True:
        s = content.find("<script", pos)
        if s == -1:
            break
        # Skip self-closing or attribute-only matches: find the next `>`
        gt = content.find(">", s)
        if gt == -1:
            break
        e = content.find("</script>", gt)
        if e == -1:
            break
        out.append((s, e + len("</script>")))
        pos = e + 1
    return out


def check_file(path: Path) -> tuple[bool, list[str]]:
    if not path.exists():
        return False, [f"file not found: {path}"]
    content = path.read_text(encoding="utf-8")
    failures: list[str] = []

    blocks = find_script_blocks(content)
    if len(blocks) > EXPECTED_SCRIPT_BLOCKS:
        failures.append(
            f"unexpected <script> block count: {len(blocks)} "
            f"(expected {EXPECTED_SCRIPT_BLOCKS}). Possible XSS injection."
        )

    # Reconstruct the document with script-block bodies replaced by a
    # placeholder so subsequent scans only look at HTML-context content.
    sanitized = []
    cursor = 0
    for s, e in blocks:
        sanitized.append(content[cursor:s])
        sanitized.append("[[SCRIPT_BLOCK]]")
        cursor = e
    sanitized.append(content[cursor:])
    html_only = "".join(sanitized)

    # No <script in HTML context.
    raw_script = re.findall(r"<script\b[^>]*>", html_only)
    if raw_script:
        failures.append(
            f"raw <script> tag(s) outside the trusted inline block: "
            f"{len(raw_script)} occurrence(s). User input is leaking into HTML context."
        )

    # No inline event handlers as ELEMENT ATTRIBUTES (escaped text content
    # like "&lt;img onerror=...&gt;" is harmless — html.parser sees it as
    # text, not as an attribute on a real element).
    class HandlerSniffer(HTMLParser):
        found: list[tuple[str, str]]
        def __init__(self) -> None:
            super().__init__(convert_charrefs=True)
            self.found = []
        def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
            for attr_name, _attr_val in attrs:
                if attr_name and attr_name.lower().startswith("on"):
                    self.found.append((tag, attr_name))
    sniffer = HandlerSniffer()
    try:
        sniffer.feed(html_only)
    except Exception as exc:  # pragma: no cover — html.parser is permissive
        failures.append(f"HTML parse error during handler scan: {exc}")
    for tag, attr in sniffer.found:
        failures.append(
            f"inline event handler '<{tag} {attr}=...>' found as a real element "
            f"attribute. PitchForge does not emit inline handlers; this is XSS-suspect."
        )
    # Also catch obvious raw-text leaks that html.parser may not have parsed
    # as attributes (e.g. partially-broken markup). Limit to handlers
    # appearing IMMEDIATELY after a literal `<tag` opener — escaped text
    # like "&lt;img onerror=" never matches because the leading char is `;`.
    for handler in INLINE_HANDLERS:
        pattern = re.compile(r"<[a-zA-Z][^>]*\s" + re.escape(handler), re.IGNORECASE)
        m = pattern.findall(html_only)
        if m:
            failures.append(
                f"inline event handler '{handler}' literal in tag opener "
                f"(parser may have missed it): {len(m)} occurrence(s)."
            )

    # No </script> bare-substring inside JS string literals — the generator's
    # `safe_json_for_script` should have rewritten any `</` to `<\/`. Scan
    # the script blocks themselves for the brake-out pattern.
    for s, e in blocks:
        body = content[s:e]
        # Strip the actual closing tag (last `</script>`) before scanning.
        inner = body[: body.rfind("</script>")]
        # Look for unescaped </script> in string-literal-ish positions.
        # Heuristic: any "</script>" inside the inner content is suspicious.
        if "</script>" in inner:
            failures.append(
                "unescaped '</script>' inside a script block — would terminate "
                "the script context. Run the output through `safe_json_for_script`."
            )

    return (len(failures) == 0), failures


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("paths", nargs="+", help="HTML file(s) to validate")
    args = p.parse_args(argv)

    rc = 0
    for raw in args.paths:
        path = Path(raw)
        ok, msgs = check_file(path)
        prefix = "[ok]" if ok else "[FAIL]"
        if ok:
            print(f"{prefix} {path}: html-escape clean")
        else:
            print(f"{prefix} {path}:")
            for m in msgs:
                print(f"   - {m}")
            rc = 1
    return rc


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
