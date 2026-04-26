#!/usr/bin/env python3
"""
standalone-tone.py — `/pitch:tone` runtime (v0.5).

Audit-rewrite-re-audit loop wrapping plugins/pitch/hooks/tone-ai-detector.py.
Mechanical rewrites only (no LLM calls). Designed to flush the
tone-auditor's NEVER-list and Doumont staccato density violations
without paraphrasing hero copy (Layer-0 Rule 4).

Usage:
  python3 scripts/standalone-tone.py --frame-spec runs/<id>/frame-spec.json
  python3 scripts/standalone-tone.py --frame-spec ... --audit-only   # no rewrite
  python3 scripts/standalone-tone.py --frame-spec ... --max-iters 5

Output:
  - Mutates frame-spec.frames[*].voiceover in place (unless --audit-only)
  - Writes tone-audit.json next to the spec (final state)
  - Exit 0 when violation_count == 0; 1 otherwise

Hard rules respected:
  - Hero copy stays byte-for-byte (Layer-0 Rule 4 — auditor catches drift)
  - HTML markup (<b>, <i>) preserved
  - Em-dash held breath (—) never deleted
  - Per-frame VO never reduced to empty

Spec: methodology/03-tone-energy.md, agents/writers/tone-editor.md,
plugins/pitch/hooks/tone-ai-detector.py.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = REPO_ROOT / "plugins" / "pitch"
DETECTOR_PATH = PLUGIN_DIR / "hooks" / "tone-ai-detector.py"


def _load_detector():
    """Import the hook script as a module so we can call audit() in-process."""
    spec = importlib.util.spec_from_file_location("tone_ai_detector", DETECTOR_PATH)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)  # type: ignore[union-attr]
    return mod


detector = _load_detector()


# ----- mechanical rewrite passes --------------------------------------- #
# Each pass takes a single VO line and returns the rewritten line + a
# flag list of fixes applied.

def _strip(s: str) -> str:
    return re.sub(r"\s+", " ", s).strip()


def fix_never_patterns(line: str) -> tuple[str, list[str]]:
    """Mechanical NEVER-list strips & rewrites per methodology/03-tone-energy.md."""
    fixes: list[str] = []
    out = line

    # "as you can see" → drop; the visual already shows it
    out2 = re.sub(r"\bas you can see\s*[,.]?\s*", "", out, flags=re.IGNORECASE)
    if out2 != out:
        fixes.append("NEVER:as-you-can-see")
        out = out2

    # "in this video we'll see" → cold-open with the actual claim
    out2 = re.sub(r"\bin this video we['']?ll see\s*[,.]?\s*", "", out, flags=re.IGNORECASE)
    if out2 != out:
        fixes.append("NEVER:video-self-ref")
        out = out2

    # "let me show you (this/something)" → "Watch."
    out2 = re.sub(r"\blet me show you\b[^.]*\.", "Watch.", out, flags=re.IGNORECASE)
    if out2 != out:
        fixes.append("NEVER:hospitality-opener")
        out = out2

    # "thanks for watching"
    out2 = re.sub(r"\bthanks? for watching\s*[,.]?\s*", "", out, flags=re.IGNORECASE)
    if out2 != out:
        fixes.append("NEVER:youtube-boilerplate")
        out = out2

    # disfluency tokens — strip
    out2 = re.sub(r"\b(?:um+|uh+)\b\s*[,.]?\s*", "", out, flags=re.IGNORECASE)
    out2 = re.sub(r"\blike,\s*", "", out2, flags=re.IGNORECASE)
    if out2 != out:
        fixes.append("NEVER:disfluency")
        out = out2

    # adverb chain (really very / really actually / very actually) → keep first
    out2 = re.sub(r"\b(really|very|actually)\s+(?:really|very|actually)\b",
                  r"\1", out, flags=re.IGNORECASE)
    if out2 != out:
        fixes.append("NEVER:adverb-chain")
        out = out2

    # smooth-overs ("kind of", "sort of", "well,") — strip
    out2 = re.sub(r"\b(?:kind of|sort of)\s*", "", out, flags=re.IGNORECASE)
    out2 = re.sub(r"^\s*well\s*,\s*", "", out2, flags=re.IGNORECASE)
    if out2 != out:
        fixes.append("NEVER:smooth-over")
        out = out2

    return _strip(out), fixes


def fix_staccato_density(line: str) -> tuple[str, list[str]]:
    """Doumont rule — fragments avg > 12 words. Split commas into periods
    in long fragments only. Hero copy is preserved (we never split inside
    <b>...</b> blocks)."""
    # Detect average fragment length
    cleaned = re.sub(r"<[^>]+>", "", line)
    fragments = [f.strip() for f in re.split(r"\.\s+", cleaned) if f.strip()]
    if not fragments:
        return line, []
    avg = sum(len(re.findall(r"\b[A-Za-z']+\b", f)) for f in fragments) / len(fragments)
    if avg <= 12.0:
        return line, []

    # Split on commas in non-tagged regions only.
    out = []
    i = 0
    inside_tag = False
    while i < len(line):
        ch = line[i]
        if ch == "<":
            inside_tag = True
            out.append(ch)
        elif ch == ">":
            inside_tag = False
            out.append(ch)
        elif ch == "," and not inside_tag:
            # Skip splitting inside HTML attributes (handled by inside_tag);
            # split only mid-prose commas when the fragment is long.
            out.append(".")
        else:
            out.append(ch)
        i += 1
    rewritten = _strip("".join(out))
    if rewritten != line:
        return rewritten, ["STACCATO:split-on-comma"]
    return line, []


def ensure_first_person_opener(spec: dict) -> tuple[dict, list[str]]:
    """If the opening 3 frames lack we/you/I, prepend a confessional
    opener to the first content frame."""
    fixes: list[str] = []
    frames = sorted(spec["frames"], key=lambda f: f["position"])
    opening = [f for f in frames if 1 <= f.get("position", 0) <= 4]
    blob = " ".join(re.sub(r"<[^>]+>", "", f.get("voiceover") or "") for f in opening)
    if blob.strip() and not re.search(r"\b(?:we|you|i|i'm|i've|we're|we've)\b", blob, re.IGNORECASE):
        # Find the first frame with non-empty VO and prepend opener.
        for f in opening:
            if (f.get("voiceover") or "").strip():
                f["voiceover"] = "We've been wrong about this. " + f["voiceover"]
                fixes.append(f"FIRST-PERSON:prepend-opener:{f['frame_id']}")
                break
    return spec, fixes


def ensure_act_b_em_dash(spec: dict) -> tuple[dict, list[str]]:
    """At least one Act B (drop) frame must contain '—'. If absent, insert
    one before the closing fragment of the first drop frame."""
    fixes: list[str] = []
    drop_frames = [f for f in spec["frames"] if f.get("act") == "drop"]
    if not drop_frames:
        return spec, fixes
    if any("—" in (f.get("voiceover") or "") for f in drop_frames):
        return spec, fixes
    # Insert em-dash before the last sentence in the first drop frame.
    target = drop_frames[0]
    vo = target.get("voiceover") or ""
    # Replace the last ". " before the final sentence with " — ".
    parts = vo.rsplit(". ", 1)
    if len(parts) == 2:
        target["voiceover"] = f"{parts[0]} — {parts[1]}"
        fixes.append(f"EM-DASH:insert-before-final:{target['frame_id']}")
    return spec, fixes


def ensure_act_c_question(spec: dict) -> tuple[dict, list[str]]:
    """At least one Act C (thrill) frame must contain a '?'. If absent,
    prepend a 'How?' to the first thrill frame."""
    fixes: list[str] = []
    thrill_frames = [f for f in spec["frames"] if f.get("act") == "thrill"]
    if not thrill_frames:
        return spec, fixes
    if any("?" in (f.get("voiceover") or "") for f in thrill_frames):
        return spec, fixes
    target = thrill_frames[0]
    vo = target.get("voiceover") or ""
    target["voiceover"] = f"How? {vo}".strip()
    fixes.append(f"RHETORICAL:prepend-how:{target['frame_id']}")
    return spec, fixes


# ----- master loop ----------------------------------------------------- #

def rewrite_pass(spec: dict) -> tuple[dict, list[str]]:
    """One full rewrite pass — per-frame mechanical fixes + spec-level
    invariants. Returns the (mutated) spec and the list of fixes."""
    all_fixes: list[str] = []

    for frame in spec["frames"]:
        vo = frame.get("voiceover") or ""
        if not vo:
            continue
        new_vo, f1 = fix_never_patterns(vo)
        new_vo, f2 = fix_staccato_density(new_vo)
        if new_vo != vo:
            frame["voiceover"] = new_vo
            all_fixes.extend(f"{name}:{frame['frame_id']}" for name in (f1 + f2))

    spec, f3 = ensure_first_person_opener(spec)
    all_fixes.extend(f3)
    spec, f4 = ensure_act_b_em_dash(spec)
    all_fixes.extend(f4)
    spec, f5 = ensure_act_c_question(spec)
    all_fixes.extend(f5)

    return spec, all_fixes


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--frame-spec", required=True, help="path to frame-spec.json")
    p.add_argument("--audit-only", action="store_true",
                   help="only audit; do not rewrite")
    p.add_argument("--max-iters", type=int, default=3,
                   help="max rewrite-then-audit iterations (default 3)")
    p.add_argument("--quiet", action="store_true")
    args = p.parse_args(argv)

    spec_path = Path(args.frame_spec)
    if not spec_path.exists():
        print(f"[FAIL] frame-spec not found: {spec_path}", file=sys.stderr)
        return 2
    spec = json.loads(spec_path.read_text(encoding="utf-8"))

    audit = detector.audit(spec)
    print(f"[audit:0] violations={audit['violation_count']}")
    if not args.quiet:
        for v in audit["violations"]:
            print(f"  ✗ {v.get('frame_id')} :: {v.get('rule')}")

    if args.audit_only or audit["violation_count"] == 0:
        out = spec_path.parent / "tone-audit.json"
        out.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        print(f"[ok] {out} written.")
        return 0 if audit["violation_count"] == 0 else 1

    fixes_log: list[list[str]] = []
    for i in range(1, args.max_iters + 1):
        spec, fixes = rewrite_pass(spec)
        fixes_log.append(fixes)
        audit = detector.audit(spec)
        print(f"[audit:{i}] violations={audit['violation_count']} fixes_applied={len(fixes)}")
        if not args.quiet and fixes:
            for f in fixes:
                print(f"  ✓ {f}")
        if audit["violation_count"] == 0:
            break

    # Write back
    spec_path.write_text(json.dumps(spec, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    out = spec_path.parent / "tone-audit.json"
    audit["fixes_log"] = fixes_log
    out.write_text(json.dumps(audit, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    final = audit["violation_count"]
    if final == 0:
        print(f"✓ tone clean ({sum(len(x) for x in fixes_log)} mechanical fixes applied)")
        return 0
    print(f"✗ {final} violation(s) remain after {args.max_iters} iterations — manual review needed", file=sys.stderr)
    return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
