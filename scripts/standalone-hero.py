#!/usr/bin/env python3
"""
standalone-hero.py — `/pitch:hero` runtime (v0.5).

Generates 5 hero-copy candidates (one per inversion pattern) from a
project one-liner. Cross-checks `memory/HERO_CATALOG.md` to suppress
near-duplicates of prior accepted heroes.

Usage:
  # From a brief.json
  python3 scripts/standalone-hero.py --brief runs/<id>/brief.json

  # From a one-liner
  python3 scripts/standalone-hero.py --one-liner "PitchForge — turn project context into a cinematic deck"

  # Constrain to one pattern (returns 1 candidate, not 5)
  python3 scripts/standalone-hero.py --one-liner "..." --pattern paper-title-inversion

  # JSON output (stable for piping)
  python3 scripts/standalone-hero.py --one-liner "..." --json

Spec: methodology/02-hero-copy-patterns.md, agents/writers/hero-copywriter.md.

Anti-patterns are auto-rejected; near-duplicates of HERO_CATALOG entries
are flagged with `dedupe_conflicts`.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = REPO_ROOT / "plugins" / "pitch"
HERO_CATALOG = PLUGIN_DIR / "memory" / "HERO_CATALOG.md"

PATTERNS = [
    "paper-title-inversion",
    "stop-start",
    "first-reordering",
    "confession",
    "rule-of-three",
]

# Anti-patterns from methodology/02-hero-copy-patterns.md
ANTI_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("introducing", re.compile(r"\bintroducing\b", re.IGNORECASE)),
    ("welcome-to", re.compile(r"\bwelcome to\b", re.IGNORECASE)),
    ("for-x",      re.compile(r"\b\w+ for \w+\b", re.IGNORECASE)),
    ("adjective-stack", re.compile(r"\b(?:fast|secure|scalable|magnificent)\s*,\s*(?:fast|secure|scalable|magnificent)", re.IGNORECASE)),
]

# Stop-start templates — "old" verb is paired with "new" verb.
STOP_START_PAIRS = [
    ("wireframing",  "picking pictures"),
    ("chatting",     "engineering"),
    ("guessing",     "previewing"),
    ("speccing",     "showing"),
    ("explaining",   "demoing"),
    ("describing",   "showing"),
]

# Confession templates — "we've been [doing X wrong]"
CONFESSION_PHRASES = [
    "lying",
    "building backwards",
    "wireframing too late",
    "shipping unsupervised",
    "specing past the point",
]

# Rule-of-three numerator candidates derived from the one-liner.
# Falls back to a stock pattern if no numbers found.
RULE_OF_THREE_FALLBACK = "Three minutes. One line. One deck."


# ----- helpers ---------------------------------------------------------- #

def normalize_word(s: str) -> str:
    return re.sub(r"[^A-Za-z0-9]+", "", s).lower()


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, start=1):
        curr = [i]
        for j, cb in enumerate(b, start=1):
            curr.append(min(
                prev[j] + 1,
                curr[j - 1] + 1,
                prev[j - 1] + (0 if ca == cb else 1),
            ))
        prev = curr
    return prev[-1]


def extract_subject(one_liner: str, project_name: str | None = None) -> str:
    """Pull the most paradigm-shifty single noun from a one-liner.

    Priority:
      1. project_name (if it's a single word and < 16 chars)
      2. first capitalized non-trailing-period word in the one-liner
      3. first word > 3 letters that isn't a stop-word
      4. fallback: 'Preview'
    """
    stop = {"the", "and", "for", "with", "that", "into", "this", "from"}
    if project_name:
        # If it's a multi-word project name, prefer the head noun.
        head = project_name.split()[0]
        if len(head) <= 16 and head.isalpha():
            return head
    for w in one_liner.split():
        clean = w.strip(".,—–:;()")
        if clean and clean[:1].isupper() and not clean.endswith("."):
            return clean
    for w in one_liner.split():
        clean = w.strip(".,—–:;()").lower()
        if clean and len(clean) > 3 and clean not in stop:
            return clean.capitalize()
    return "Preview"


def extract_old_new_verbs(one_liner: str) -> tuple[str, str]:
    """Pick a (stop, start) pair whose 'new' verb sounds compatible
    with the one-liner. Heuristic only."""
    text = one_liner.lower()
    for old, new in STOP_START_PAIRS:
        # If the one-liner mentions the new-verb root, prefer that pair.
        if any(token in text for token in new.split()):
            return old, new
    return STOP_START_PAIRS[0]


def extract_confession_target(one_liner: str) -> str:
    """Pick a confession that mirrors the one-liner's pain point."""
    text = one_liner.lower()
    if "spec" in text:
        return "specing past the point"
    if "demo" in text or "video" in text or "deck" in text:
        return "wireframing too late"
    if "ship" in text or "release" in text:
        return "shipping unsupervised"
    if "build" in text or "code" in text:
        return "building backwards"
    return CONFESSION_PHRASES[0]


def extract_thing(one_liner: str, project_name: str | None) -> str:
    """For first-reordering pattern. Returns a noun that makes sense
    fronted by 'first'."""
    text = one_liner.lower()
    for kw in ["preview", "demo", "result", "picture", "spec", "story"]:
        if kw in text:
            return kw.capitalize()
    if project_name:
        head = project_name.split()[0]
        return head if len(head) <= 16 else "Preview"
    return "Preview"


def extract_three_clauses(one_liner: str, project_name: str | None) -> str:
    """For rule-of-three pattern. Tries to pull a plausible 'N-thing-A,
    N-thing-B, N-outcome' from numerals + nouns in the one-liner."""
    nums = re.findall(r"\b\d{2,4}\b", one_liner)
    nouns = re.findall(r"\b[a-z]{4,}\b", one_liner.lower())
    if nums and len(nouns) >= 2:
        return f"{nums[0]} {nouns[0]}. One {nouns[1]}. Two clicks."
    return RULE_OF_THREE_FALLBACK


# ----- pattern generators ---------------------------------------------- #

def gen_paper_title(one_liner: str, project_name: str | None) -> str:
    subject = extract_subject(one_liner, project_name)
    return f"{subject} is all you need."


def gen_stop_start(one_liner: str, project_name: str | None) -> str:
    old, new = extract_old_new_verbs(one_liner)
    return f"Stop {old}. Start {new}."


def gen_first_reordering(one_liner: str, project_name: str | None) -> str:
    return f"{extract_thing(one_liner, project_name)} first."


def gen_confession(one_liner: str, project_name: str | None) -> str:
    return f"We've been {extract_confession_target(one_liner)}."


def gen_rule_of_three(one_liner: str, project_name: str | None) -> str:
    return extract_three_clauses(one_liner, project_name)


PATTERN_GENS = {
    "paper-title-inversion": gen_paper_title,
    "stop-start":             gen_stop_start,
    "first-reordering":       gen_first_reordering,
    "confession":             gen_confession,
    "rule-of-three":          gen_rule_of_three,
}


# ----- catalog dedupe --------------------------------------------------- #

def load_catalog_heroes() -> list[str]:
    if not HERO_CATALOG.exists():
        return []
    text = HERO_CATALOG.read_text(encoding="utf-8")
    return re.findall(r'^\s*hero:\s*"([^"]+)"', text, flags=re.MULTILINE)


def dedupe_check(candidate: str, catalog: list[str], min_distance: int = 4) -> list[dict]:
    """Return list of catalog entries within Levenshtein < min_distance."""
    conflicts = []
    norm_c = normalize_word(candidate)
    for prior in catalog:
        norm_p = normalize_word(prior)
        d = levenshtein(norm_c, norm_p)
        if d < min_distance:
            conflicts.append({"prior": prior, "distance": d})
    return conflicts


# ----- anti-pattern guard ---------------------------------------------- #

def anti_pattern_violations(candidate: str) -> list[str]:
    return [name for name, pattern in ANTI_PATTERNS if pattern.search(candidate)]


def word_count(s: str) -> int:
    return len(re.findall(r"\S+", s))


# ----- main ----------------------------------------------------------- #

def generate_candidates(
    one_liner: str,
    project_name: str | None,
    only_pattern: str | None = None,
) -> list[dict]:
    catalog = load_catalog_heroes()
    patterns = [only_pattern] if only_pattern else PATTERNS
    out = []
    for p in patterns:
        try:
            text = PATTERN_GENS[p](one_liner, project_name)
        except KeyError:
            out.append({"pattern": p, "error": f"unknown pattern: {p}"})
            continue
        wc = word_count(text)
        anti = anti_pattern_violations(text)
        # Hard limit per methodology/02-hero-copy-patterns.md: max 12 words.
        too_long = wc > 12
        conflicts = dedupe_check(text, catalog)
        out.append({
            "pattern": p,
            "hero": text,
            "word_count": wc,
            "anti_patterns": anti,
            "too_long": too_long,
            "dedupe_conflicts": conflicts,
            "verdict": (
                "rejected (anti-pattern)"  if anti else
                "rejected (too long)"      if too_long else
                "warning (catalog conflict)" if conflicts else
                "ok"
            ),
        })
    return out


def recommend(candidates: list[dict]) -> int | None:
    """Index of the recommended candidate, or None if all rejected.

    Priority:
      1. paper-title-inversion if ok (default for technical / paradigm-shift framing)
      2. first ok candidate by enum order
    """
    ok = [(i, c) for i, c in enumerate(candidates) if c.get("verdict") == "ok"]
    if not ok:
        return None
    for i, c in ok:
        if c["pattern"] == "paper-title-inversion":
            return i
    return ok[0][0]


def render_human(candidates: list[dict], project: str, recommendation: int | None) -> str:
    out = []
    out.append(f"# Hero candidates · {project}\n")
    out.append("| # | Pattern | Hero | Verdict |")
    out.append("|---|---|---|---|")
    for i, c in enumerate(candidates, start=1):
        hero = c.get("hero", c.get("error", ""))
        out.append(f"| {i} | {c['pattern']} | \"{hero}\" | {c['verdict']} |")
    out.append("")
    if recommendation is not None:
        rec = candidates[recommendation]
        out.append(f"**Recommendation**: #{recommendation + 1} ({rec['pattern']}) — {rec['hero']}")
    else:
        out.append("**Recommendation**: none — all candidates rejected. Refine the one-liner or run with --pattern.")
    catalog_conflict_count = sum(len(c.get("dedupe_conflicts") or []) for c in candidates)
    out.append(f"**Catalog dedupe**: {catalog_conflict_count} conflict(s).")
    return "\n".join(out) + "\n"


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--brief", help="path to brief.json (project_one_liner is read from it)")
    g.add_argument("--one-liner", help="raw one-liner string (Tier 1 Auto)")
    p.add_argument("--pattern", choices=PATTERNS, default=None,
                   help="constrain to a single pattern (returns 1 candidate)")
    p.add_argument("--project-name", default=None,
                   help="project name override (otherwise pulled from brief or guessed from one-liner)")
    p.add_argument("--json", action="store_true",
                   help="emit JSON instead of human-readable markdown")
    args = p.parse_args(argv)

    if args.brief:
        brief_path = Path(args.brief)
        if not brief_path.exists():
            print(f"[FAIL] brief not found: {brief_path}", file=sys.stderr)
            return 2
        brief = json.loads(brief_path.read_text(encoding="utf-8"))
        one_liner = brief.get("project_one_liner") or brief.get("project_name") or ""
        project_name = args.project_name or brief.get("project_name")
    else:
        one_liner = args.one_liner
        project_name = args.project_name

    if not one_liner.strip():
        print("[FAIL] one-liner is empty", file=sys.stderr)
        return 2

    candidates = generate_candidates(one_liner, project_name, only_pattern=args.pattern)
    rec_idx = recommend(candidates)

    if args.json:
        print(json.dumps({
            "project_name": project_name,
            "one_liner": one_liner,
            "candidates": candidates,
            "recommendation_index": rec_idx,
        }, indent=2, ensure_ascii=False))
    else:
        print(render_human(candidates, project_name or "(unnamed)", rec_idx))

    return 0 if rec_idx is not None else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
