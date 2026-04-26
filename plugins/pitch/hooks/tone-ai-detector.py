#!/usr/bin/env python3
"""
Layer-0 hook — tone-ai-detector

Mechanical detector for AI-narrated tone in voiceover lines. Implements
the NEVER-list and Doumont staccato checks from
plugins/pitch/methodology/03-tone-energy.md.

Triggered:
  - Post-write of frame-spec.json (after tone-editor)
  - As part of /pitch:tone --audit-only
  - Standalone via tests/

Behavior:
  - Reads frame-spec.json
  - Walks frames[*].voiceover
  - Applies the rule set (NEVER-list, staccato density, hero preservation,
    em-dash held breath in act=drop, rhetorical question in act=thrill,
    first-person in opening 3 frames)
  - Writes a tone-audit.json next to frame-spec.json (or to --output)
  - Exits 0 when violation_count == 0; 1 otherwise (gate G4 fail).

Layer-0 alignment:
  - Rule 4 (sacred hero): byte-for-byte match enforced.
  - Rule 5 (Doumont staccato): fragment avg word count cap.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

NEVER_PATTERNS: list[tuple[str, re.Pattern[str]]] = [
    ("NEVER:as-you-can-see",        re.compile(r"\bas you can see\b", re.IGNORECASE)),
    ("NEVER:video-self-ref",        re.compile(r"\bin this video we['']?ll see\b", re.IGNORECASE)),
    ("NEVER:hospitality-opener",    re.compile(r"\blet me show you\b", re.IGNORECASE)),
    ("NEVER:youtube-boilerplate",   re.compile(r"\bthanks for watching\b", re.IGNORECASE)),
    ("NEVER:disfluency",            re.compile(r"\b(?:um+|uh+|like,)\b", re.IGNORECASE)),
    ("NEVER:adverb-chain",          re.compile(r"\b(?:really\s+very|very\s+really|really\s+actually|very\s+actually|actually\s+really)\b", re.IGNORECASE)),
    ("NEVER:smooth-over",           re.compile(r"\b(?:kind of|sort of|well\s*,)\b", re.IGNORECASE)),
]

HTML_TAG_RE = re.compile(r"</?[a-zA-Z][^>]*>")
PERIOD_SPLIT_RE = re.compile(r"\.\s+")
WORD_RE = re.compile(r"\b[A-Za-z']+\b")


def strip_html(text: str) -> str:
    return HTML_TAG_RE.sub("", text)


def average_fragment_words(text: str) -> float:
    cleaned = strip_html(text).strip()
    if not cleaned:
        return 0.0
    fragments = [f.strip() for f in PERIOD_SPLIT_RE.split(cleaned) if f.strip()]
    if not fragments:
        return 0.0
    word_counts = [len(WORD_RE.findall(f)) for f in fragments]
    return sum(word_counts) / len(word_counts)


def audit(spec: dict) -> dict:
    frames = spec.get("frames", []) or []
    hero_copy = (spec.get("hero") or {}).get("copy", "")
    primary_id = (spec.get("hero") or {}).get("primary_frame")
    echo_id = (spec.get("hero") or {}).get("echo_frame")

    violations: list[dict] = []

    # Per-frame checks — NEVER-list + staccato density.
    for frame in frames:
        vo = frame.get("voiceover") or ""
        if not vo:
            continue
        cleaned = strip_html(vo)
        for rule, pattern in NEVER_PATTERNS:
            m = pattern.search(cleaned)
            if m:
                violations.append({
                    "frame_id": frame.get("frame_id"),
                    "rule": rule,
                    "match": m.group(0),
                    "line": vo,
                })
        avg = average_fragment_words(cleaned)
        if avg > 12.0:
            violations.append({
                "frame_id": frame.get("frame_id"),
                "rule": "STACCATO:too-long",
                "fragment_avg_words": round(avg, 2),
                "line": vo,
            })

    # Hero copy byte-for-byte preservation.
    if hero_copy:
        for label, target_id in (("HERO:paraphrased", primary_id), ("HERO:echo-paraphrased", echo_id)):
            if not target_id:
                continue
            target = next((f for f in frames if f.get("frame_id") == target_id), None)
            if target is None:
                continue
            cleaned_vo = strip_html(target.get("voiceover") or "")
            if hero_copy not in cleaned_vo:
                violations.append({
                    "frame_id": target_id,
                    "rule": label,
                    "expected": hero_copy,
                    "got": cleaned_vo,
                })

    # First-person in opening 3 frames (positions 1-3, ignoring cover with empty VO).
    opening = sorted(
        (f for f in frames if isinstance(f.get("position"), int) and 1 <= f["position"] <= 4),
        key=lambda f: f["position"],
    )
    opening_vo = " ".join(strip_html(f.get("voiceover") or "") for f in opening)
    if opening_vo.strip():
        if not re.search(r"\b(?:we|you|i|i'm|i've|we're|we've)\b", opening_vo, re.IGNORECASE):
            violations.append({
                "frame_id": opening[0]["frame_id"] if opening else "(opening)",
                "rule": "FIRST-PERSON:missing-opener",
                "scanned_positions": [f.get("position") for f in opening],
            })

    # Em-dash in at least one Act B (drop) frame.
    drop_frames = [f for f in frames if f.get("act") == "drop"]
    if drop_frames:
        if not any("—" in (f.get("voiceover") or "") for f in drop_frames):
            violations.append({
                "frame_id": drop_frames[0].get("frame_id"),
                "rule": "EM-DASH:missing-act-b",
                "act": "drop",
            })

    # Rhetorical question in at least one Act C (thrill) frame.
    thrill_frames = [f for f in frames if f.get("act") == "thrill"]
    if thrill_frames:
        if not any("?" in (f.get("voiceover") or "") for f in thrill_frames):
            violations.append({
                "frame_id": thrill_frames[0].get("frame_id"),
                "rule": "RHETORICAL:missing-act-c",
                "act": "thrill",
            })

    return {
        "phase": "P4-audit",
        "frames_audited": len(frames),
        "violations": violations,
        "violation_count": len(violations),
        "gate_g4_pass": len(violations) == 0,
    }


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("frame_spec", help="path to frame-spec.json")
    parser.add_argument("--output", help="path to write tone-audit.json (default: alongside spec)")
    parser.add_argument("--quiet", action="store_true", help="suppress detail; only print summary")
    args = parser.parse_args(argv)

    spec_path = Path(args.frame_spec)
    if not spec_path.exists():
        print(f"[FAIL] frame-spec.json not found: {spec_path}", file=sys.stderr)
        return 2
    try:
        spec = json.loads(spec_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        print(f"[FAIL] invalid JSON in frame-spec: {exc}", file=sys.stderr)
        return 2

    report = audit(spec)
    out_path = Path(args.output) if args.output else spec_path.parent / "tone-audit.json"
    out_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    if not args.quiet:
        for v in report["violations"]:
            print(f"  ✗ {v.get('frame_id')} :: {v.get('rule')}")
    print(f"[{'ok' if report['gate_g4_pass'] else 'FAIL'}] tone-audit: {report['violation_count']} violation(s)  →  {out_path}")
    return 0 if report["gate_g4_pass"] else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
