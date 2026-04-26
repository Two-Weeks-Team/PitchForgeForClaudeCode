#!/usr/bin/env python3
"""
generate-deck.py — Tier 1 Auto deck generator (v0.1.0).

Pipeline (all in-process):
  brief.json  →  frame-spec.json
  frame-spec  →  deck-config.json
  deck-config + frame-spec + deck-shell.html  →  deck-cinematic.html

Why not a chain of subprocess agent calls?
  v0.1.0 ships the *minimum runnable pipeline*. The agent docs describe
  *what* each phase does; this script is the *executable* expression of
  that for Tier 1 Auto. Tier 2/3 will add agent-mediated branches in
  v0.5+.

Usage:
  python3 scripts/generate-deck.py \
      --brief tests/fixtures/preview-forge-160s/brief.json \
      --output runs/preview-forge-160s/deck-cinematic.html

  # Or with a one-liner (Tier 1 Auto from scratch — uses defaults):
  python3 scripts/generate-deck.py \
      --one-liner "Preview Forge — 144 personas turn one-line idea into full-stack app" \
      --output runs/quick/deck-cinematic.html

Outputs (alongside --output):
  brief.json            (only if --one-liner was used)
  frame-spec.json
  deck-config.json
  recording-config.json
  deck-cinematic.html

Dependencies: stdlib only (json, re, pathlib, argparse).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

REPO_ROOT = Path(__file__).resolve().parent.parent
PLUGIN_DIR = REPO_ROOT / "plugins" / "pitch"
TEMPLATES = PLUGIN_DIR / "templates"

SCHEMA_VERSION = "0.1.0"


# ---------- helpers -------------------------------------------------------- #

def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def fmt_time(seconds: float) -> str:
    """Format an absolute second count as m:ss (one digit minutes ok)."""
    m = int(seconds) // 60
    s = int(round(seconds)) % 60
    return f"{m}:{s:02d}"


def fmt_time_range(start: float, end: float) -> str:
    return f"{fmt_time(start)} – {fmt_time(end)}"


def _resolve_arc_template(arc_name: str, runtime: int) -> Path:
    """Pick the arc template whose declared runtime is closest to `runtime`.

    Prefers an exact name+runtime match. Falls back to the same arc-name at
    its closest available length. Falls back further to wow-first-160s if the
    arc-name is unknown entirely (so generation never aborts).
    """
    arcs_dir = TEMPLATES / "narrative-arcs"
    exact = arcs_dir / f"{arc_name}-{runtime}s.json"
    if exact.exists():
        return exact

    # All variants of this arc name
    variants = sorted(arcs_dir.glob(f"{arc_name}-*s.json"))
    if variants:
        def variant_runtime(p: Path) -> int:
            m = re.search(r"-(\d+)s\.json$", p.name)
            return int(m.group(1)) if m else 999_999
        return min(variants, key=lambda p: abs(variant_runtime(p) - runtime))

    # Final fallback — never abort generation.
    return arcs_dir / "wow-first-160s.json"


def split_hero_words(hero: str) -> tuple[list[str], int]:
    """Split a hero line into words and pick an accent index.

    The accent word defaults to "all" (paper-title), or the third word for
    rule-of-three, or the first capitalized verb otherwise.
    """
    words = hero.split()
    if not words:
        return [hero], 0
    lowered = [w.strip(".,").lower() for w in words]
    if "all" in lowered:
        return words, lowered.index("all")
    return words, max(0, len(words) // 2 - 1)


# ---------- Tier 1 Auto brief synthesis ------------------------------------ #

def synthesize_brief(
    one_liner: str,
    *,
    runtime: int = 160,
    arc: str | None = None,
    palette: str = "oklch-warm-gold",
    hero: str | None = None,
) -> dict:
    """Mirror brief-extractor.md § Tier 1 Auto synthesis ruleset."""
    project_name = next(
        (w for w in one_liner.split() if w[:1].isupper() and not w.endswith(".")),
        one_liner.split()[0] if one_liner.split() else "Untitled",
    )
    # Arc selection heuristic per methodology/01-narrative-arcs.md.
    if arc is None:
        if runtime <= 60:
            arc = "teaser"
        elif runtime <= 240:
            arc = "wow-first"
        else:
            arc = "story"
    if hero is None:
        hero = f"{project_name} is all you need."
        if not hero[0].isupper():
            hero = hero[0].upper() + hero[1:]
    return {
        "_schema_version": SCHEMA_VERSION,
        "_filled_ratio": 0.50,
        "project_name": project_name,
        "project_one_liner": one_liner[:280],
        "audience": "hackathon-judges",
        "runtime_seconds": runtime,
        "narrative_arc": arc,
        "hero_copy": hero,
        "hero_pattern": "paper-title-inversion",
        "color_palette": palette,
        "tone": "agro-drop-thrill",
        "judging_criteria": [
            {"name": "Impact", "weight": 0.30},
            {"name": "Demo", "weight": 0.25},
            {"name": "Originality", "weight": 0.25},
            {"name": "Depth", "weight": 0.20},
        ],
        "key_visuals": [],
        "constraints": ["english-only", "single-html", "no-third-party-deps"],
    }


# ---------- P2 — scenario-architect synthesis ------------------------------ #

def build_frame_spec(brief: dict) -> dict:
    """Splice brief into the chosen arc template; emit frame-spec.json."""
    arc_name = brief.get("narrative_arc", "wow-first")
    runtime = int(brief.get("runtime_seconds", 160))
    palette = brief.get("color_palette", "oklch-warm-gold")
    hero_copy = brief.get("hero_copy", "")
    project = brief.get("project_name", "Untitled")

    arc_path = _resolve_arc_template(arc_name, runtime)
    arc = load_json(arc_path)

    # Recompute time_start_seconds running sum so reorders stay consistent.
    frames = []
    cursor = 0.0
    hero_words, accent_idx = split_hero_words(hero_copy)
    for beat in arc["beats"]:
        duration = float(beat.get("duration_seconds", 8))
        time_start = cursor
        cursor += duration

        voiceover = (beat.get("stock_voiceover") or "").replace("{{hero_copy}}", hero_copy)
        heading = (beat.get("stock_heading") or "").replace("{{project_name}}", project)
        accent = beat.get("stock_heading_accent_word") or ""
        meta_tag = beat.get("stock_meta_tag") or ""
        script_h2 = (beat.get("stock_script_h2") or "").replace("{{project_name}}", project)

        frame = {
            "frame_id": beat["frame_id"],
            "position": int(beat["position"]),
            "shape": beat["shape"],
            "time_start_seconds": round(time_start, 2),
            "duration_seconds": duration,
            "act": beat.get("act", "thrill"),
            "heading": heading,
            "heading_accent_word": accent,
            "meta_tag": meta_tag,
            "script_h2": script_h2,
            "voiceover": voiceover,
            "delivery_note": beat.get("delivery_note", ""),
            "tone_note": beat.get("tone_note", ""),
            "show_echo_ribbon": beat.get("show_echo_ribbon", True),
            "shape_props": {},
            "animation_timeline": [],
        }
        if beat.get("navbar_keys_label"):
            frame["navbar_keys_label"] = beat["navbar_keys_label"]
        frames.append(frame)

    primary_frame = next((f for f in frames if f["act"] == "drop" and f["shape"] == "gallery-hero"), None)
    if primary_frame is None:
        primary_frame = next((f for f in frames if f["shape"] == "gallery-hero"), frames[0])
    echo_frame = next((f for f in reversed(frames) if f["shape"] == "repo-install"), frames[-1])

    return {
        "_schema_version": SCHEMA_VERSION,
        "_brief_run_id": "tier1-auto",
        "project_name": project,
        "subtitle": brief.get("project_one_liner", ""),
        "runtime_seconds": runtime,
        "narrative_arc": arc_name,
        "color_palette": palette,
        "tone_profile": brief.get("tone", "agro-drop-thrill"),
        "hero": {
            "copy": hero_copy,
            "pattern": brief.get("hero_pattern", "paper-title-inversion"),
            "primary_frame": primary_frame["frame_id"],
            "echo_frame": echo_frame["frame_id"],
            "split_words": hero_words,
            "accent_word_index": accent_idx,
        },
        "frames": frames,
        "delivery_notes": {f["frame_id"]: {"delivery": f["delivery_note"], "tone": f["tone_note"]} for f in frames},
    }


# ---------- P5 — deck-config + render -------------------------------------- #

def short_id_label(frame_id: str) -> str:
    """`F4` → `F4`, `cover` → `Cover`, `close` → `End`."""
    if frame_id == "cover":
        return "Cover"
    if frame_id == "close":
        return "End"
    return frame_id


def slide_class(frame_id: str, shape: str) -> str:
    """Derive the .slide variant class."""
    if frame_id == "cover":
        return "cover"
    if frame_id == "close":
        return "close"
    if shape == "gallery-hero" and frame_id != "F8":
        # primary hero placement = full-bleed (no script panel)
        return "hero"
    return ""


def build_deck_config(brief: dict, spec: dict) -> dict:
    """Emit deck-config.json mirroring agents/engineers/deck-assembler.md."""
    palette_name = spec.get("color_palette", "oklch-warm-gold")
    palette = load_json(TEMPLATES / "color-palettes" / f"{palette_name}.json")
    arc_path = _resolve_arc_template(spec["narrative_arc"], int(spec["runtime_seconds"]))
    arc = load_json(arc_path)

    frames = sorted(spec["frames"], key=lambda f: f["position"])
    durations = [f["duration_seconds"] for f in frames]
    total = sum(durations)

    progress_widths: list[float] = []
    running = 0.0
    for d in durations:
        running += d
        progress_widths.append(round((running / total) * 100, 2) if total else 0.0)

    summaries = []
    for f in frames:
        title = f"{short_id_label(f['frame_id'])}"
        if f.get("script_h2"):
            label = f["script_h2"]
        elif f.get("heading"):
            label = f["heading"]
        else:
            label = brief.get("hero_copy", "")
        # Strip any HTML
        label = re.sub(r"<[^>]+>", "", label).strip() or brief.get("hero_copy", "")
        summaries.append([title, label])

    # Ranges from arc template; map to actual positions.
    ranges_arc = arc.get("ranges", {})
    opening = ranges_arc.get("opening") or {"start_position": 2, "end_position": 5, "label": "opening", "button_label": "▶ Opening", "key": "o"}
    full = ranges_arc.get("full") or {"start_position": 2, "end_position": len(frames) - 1, "label": "full", "button_label": "▶ Full", "key": "f"}

    hero = spec["hero"]
    return {
        "_schema_version": SCHEMA_VERSION,
        "_frame_spec_run_id": spec.get("_brief_run_id", "tier1-auto"),
        "title": f"{spec['project_name']} · Storyboard Deck — {int(spec['runtime_seconds'])}s · {spec['narrative_arc']}",
        "subtitle": spec.get("subtitle", ""),
        "id_label": f"{spec['project_name'].upper()} · STORYBOARD DECK",
        "version_label": brief.get("version", "v0.1.0"),
        "tagline": brief.get("tagline", f"{spec['narrative_arc'].upper().replace('-', ' ')} ARC · v0.1.0"),
        "palette": palette,
        "slide_duration_seconds": durations,
        "summaries": summaries,
        "progress_widths_pct": progress_widths,
        "hero": {
            "copy": hero["copy"],
            "split_words": hero["split_words"],
            "accent_word_index": hero["accent_word_index"],
            "primary_position": next((f["position"] for f in frames if f["frame_id"] == hero["primary_frame"]), 2),
            "echo_position": next((f["position"] for f in frames if f["frame_id"] == hero["echo_frame"]), len(frames) - 1),
            "echo_ribbon_text": _hero_with_accent_html(hero),
        },
        "cover": _build_cover(brief, spec, frames, total),
        "close": _build_close(brief, spec, total),
        "ranges": {
            "opening": opening,
            "full": full,
        },
        "rec_timer_total_frames": len(frames),
    }


def _hero_with_accent_html(hero: dict) -> str:
    words = list(hero.get("split_words") or [hero.get("copy", "")])
    idx = hero.get("accent_word_index", 0)
    out = []
    for i, w in enumerate(words):
        if i == idx:
            out.append(f"<i>{w}</i>")
        else:
            out.append(w)
    return " ".join(out)


def _build_cover(brief: dict, spec: dict, frames: list[dict], total: float) -> dict:
    hero_inline = _hero_with_accent_html(spec["hero"])
    primary_frame = next((f for f in frames if f["frame_id"] == spec["hero"]["primary_frame"]), frames[0])
    primary_time = fmt_time_range(
        primary_frame["time_start_seconds"],
        primary_frame["time_start_seconds"] + primary_frame["duration_seconds"],
    )
    return {
        "eyebrow": f"★ A {int(spec['runtime_seconds'])}-second narrative in {len(frames)} slides",
        "hero_inline": hero_inline,
        "cta": "→ press → to begin",
        "meta": [
            {"value": f"{int(spec['runtime_seconds'])} s", "label": "runtime"},
            {"value": str(len(frames) - 2), "label": "frames"},  # exclude cover + close
            {"value": primary_time, "label": f"{primary_frame['frame_id']} hero"},
            {"value": f"{len(brief.get('judging_criteria') or [])} / {len(brief.get('judging_criteria') or [])}", "label": "judging axes"},
            {"value": f"{len(brief.get('prize_categories') or [])} / {len(brief.get('prize_categories') or [])}", "label": "prize hooks"},
        ],
    }


def _build_close(brief: dict, spec: dict, total: float) -> dict:
    project = spec["project_name"]
    hero_inline = _hero_with_accent_html(spec["hero"])
    return {
        "headline": f"Now go record it — and let the room <i>feel</i> it.",
        "stat_line": f"<b>{int(total)} seconds.</b> &nbsp;<b>{len(spec['frames']) - 2} frames.</b> &nbsp;<b>One line.</b>",
        "checks": [
            "OBS · 1080p · 30 fps · H.264 · two-pass",
            "Terminal · dark theme · font ≥ 18 pt",
            "Mic · RMS −18 dB · true peak −1 dBFS",
            "Browser · cache cleared · dark theme",
            "Claude Code · agent panel + file tree visible",
            "5 takes minimum · best of 5",
            f"Title card · End card holds 2 s",
            "YouTube unlisted · description ends with hero line",
            "Pause <b>before</b> the hero line, never after",
            "Drop the tool — confidence beats polish",
            "Quiet awe, not pride",
            "Honest variant if score under target — stronger story",
        ],
        "call": f"★ \"{spec['hero']['copy'].upper()}\"  ·  THIS IS THE LAST WORD ON SCREEN ★",
        "repo_line": f"github.com/Two-Weeks-Team/{project}ForClaudeCode · v0.1.0 · Apache-2.0",
    }


# ---------- P5/P6/P7 — render frames into HTML ----------------------------- #

def render_hero_words_html(words: list[str], accent_idx: int) -> str:
    """Build the F4 hero canvas's per-word reveal markup."""
    parts = []
    for i, w in enumerate(words):
        # Add trailing nbsp between words (last word ends with the literal text)
        is_last = i == len(words) - 1
        text = w if is_last else f"{w}&nbsp;"
        if i == accent_idx:
            text = f"<i>{w}</i>{'' if is_last else '&nbsp;'}"
        parts.append(f'<span class="w" style="--n:{i}">{text}</span>')
    return "".join(parts)


def render_hero_tiles(count: int = 30) -> str:
    """30 hue-rotated tiles for the F4 wow gallery (and F8 interactive variant)."""
    rows: list[str] = []
    rows_def = [
        # (lightness pair, chroma, hue_step_offset)
        (0.55, 0.18, 0),
        (0.45, 0.16, 15),
        (0.40, 0.14, 0),
    ]
    cols = 6
    rows_n = 5
    i = 0
    out = []
    for r in range(rows_n):
        L_a = 0.55 - 0.05 * r if r < 3 else 0.45 - 0.05 * (r - 2)
        L_b = L_a - 0.20
        chroma = 0.18 if r < 2 else (0.16 if r < 4 else 0.14)
        offset = (r * 15) % 60
        for c in range(cols):
            h = (offset + c * (360 // cols)) % 360
            grad = (
                f"linear-gradient(135deg,"
                f"oklch({L_a:.2f} {chroma:.2f} {h}),"
                f"oklch({L_b:.2f} {chroma:.2f} {h}))"
            )
            out.append(f'<div class="tile" style="background:{grad}"></div>')
            i += 1
            if i >= count:
                break
        if i >= count:
            break
    return "\n            ".join(out)


def render_gallery_cards_grid() -> str:
    """F8 — 6×N gallery of hue-rotated cards with one .sel highlight."""
    cards = []
    hues = [0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330,
            15, 45, 75, 105, 135, 165, 195, 225, 255, 285, 315, 345,
            0, 120]
    for i, h in enumerate(hues):
        sel = " sel" if i == 7 else ""  # 8th card highlighted (matches reference)
        cards.append(f'<div class="card{sel}" style="--h:{h}"></div>')
    return "\n              ".join(cards)


def render_chain_frame(frame: dict, *, variant: str, blocks: list[str], terminal: dict[str, Any]) -> str:
    """Render a chain-shape canvas (F1 problem variant or F3 pivot variant)."""
    accent_word = frame.get("heading_accent_word") or ""
    heading = frame.get("heading") or ""
    if accent_word and accent_word in heading:
        heading_html = heading.replace(accent_word, f'<span class="accent">{accent_word}</span>')
    else:
        heading_html = heading

    block_html = []
    delays = [1.0, 1.6, 2.2]
    arrow_delays = [1.35, 1.95, 2.55]
    for i, txt in enumerate(blocks):
        first_class = " first" if (variant == "f3" and i == 0) else ""
        anim = "bloom" if (variant == "f3" and i == 0) else "pop"
        block_html.append(
            f'<div class="blk{first_class}" data-anim="{anim}" style="--d:{delays[i] if i < len(delays) else 2.5}s">{txt}</div>'
        )
        if i < len(arrow_delays) and i < len(blocks) - 1:
            block_html.append(
                f'<div class="arr" data-anim="fade" style="--d:{arrow_delays[i]}s">→</div>'
            )

    # Terminal block
    if variant == "f1":
        block_html.append('<div class="arr" data-anim="fade" style="--d:2.55s">→</div>')
        block_html.append(f'<div class="blk q">{terminal.get("text", "?")}</div>')
    elif variant == "f3":
        # pivot variant has no terminal "?"; the first block bloomed instead
        pass

    return f'''
        <div class="canvas-frame c-{variant}">
          <div class="h" data-anim="up" style="--d:.15s">{heading_html}</div>
          <div class="arrow">
            {"".join(block_html)}
          </div>
        </div>'''


def render_stack_strikethrough_frame(frame: dict, rows: list[dict[str, str]]) -> str:
    accent_word = frame.get("heading_accent_word") or ""
    heading = frame.get("heading") or ""
    heading_html = (
        heading.replace(accent_word, f'<span class="accent">{accent_word}</span>')
        if accent_word and accent_word in heading
        else heading
    )
    row_html = []
    for i, row in enumerate(rows):
        delay = 1.0 + i * 1.0
        row_html.append(
            f'<div class="row" data-anim="right" style="--d:{delay}s">'
            f'<span>{row["label"]}</span><span class="v">{row["value"]}</span></div>'
        )
    return f'''
        <div class="canvas-frame c-f2">
          <div class="h" data-anim="up" style="--d:.15s">{heading_html}</div>
          <div class="stack">
            {"".join(row_html)}
          </div>
        </div>'''


def render_counter_roll_frame(label: str, target: int, duration_ms: int, breakdown: str, *, stops: str = "") -> str:
    return f'''
        <div class="canvas-frame c-f5">
          <div class="lbl" data-anim="up" style="--d:.2s">{label}</div>
          <div class="count num-roll" data-counter data-target="{target}" data-dur="{duration_ms}" data-stops="{stops}">0</div>
          <div class="breakdown" data-anim="fade" style="--d:2.6s">{breakdown}</div>
        </div>'''


def render_hierarchy_diagram_frame(label: str) -> str:
    """The reference deck's six-tier engineering company. v0.1.0 ships
    a faithful inline SVG; v0.5+ generalizes via shape_props."""
    return f'''
        <div class="canvas-frame c-f6">
          <div class="lbl">{label}</div>
          <svg viewBox="0 0 540 280">
            <g font-family="ui-sans-serif" font-size="9.5" fill="oklch(0.85 0.02 250)">
              <circle cx="270" cy="40" r="13" fill="oklch(0.78 0.16 65)" stroke="oklch(0.92 0.10 65)" stroke-width="1.5"/>
              <text x="270" y="44" text-anchor="middle" fill="#1b1107" font-weight="700" font-size="9">M1</text>
              <text x="270" y="20" text-anchor="middle" fill="oklch(0.78 0.16 65)" font-size="9" font-weight="700">Run Supervisor (1)</text>
              <line x1="270" y1="53" x2="200" y2="80" stroke="oklch(0.40 0.04 250)" stroke-width="1"/>
              <line x1="270" y1="53" x2="340" y2="80" stroke="oklch(0.40 0.04 250)" stroke-width="1"/>
              <circle cx="200" cy="86" r="9" fill="oklch(0.66 0.16 290)"/>
              <text x="200" y="89" text-anchor="middle" fill="#fff" font-size="8" font-weight="700">M2</text>
              <circle cx="340" cy="86" r="9" fill="oklch(0.66 0.16 290)"/>
              <text x="340" y="89" text-anchor="middle" fill="#fff" font-size="8" font-weight="700">M3</text>
              <text x="200" y="105" text-anchor="middle" font-size="8.5">Cost Monitor</text>
              <text x="340" y="105" text-anchor="middle" font-size="8.5">Chief Eng PM</text>
              <line x1="340" y1="95" x2="80"  y2="135" stroke="oklch(0.30 0.04 250)" stroke-width=".7"/>
              <line x1="340" y1="95" x2="170" y2="135" stroke="oklch(0.30 0.04 250)" stroke-width=".7"/>
              <line x1="340" y1="95" x2="270" y2="135" stroke="oklch(0.30 0.04 250)" stroke-width=".7"/>
              <line x1="340" y1="95" x2="370" y2="135" stroke="oklch(0.30 0.04 250)" stroke-width=".7"/>
              <line x1="340" y1="95" x2="470" y2="135" stroke="oklch(0.30 0.04 250)" stroke-width=".7"/>
              <g font-size="8.5">
                <rect x="40"  y="135" width="80" height="34" rx="5" fill="oklch(0.28 0.10 220)" stroke="oklch(0.74 0.13 220)"/>
                <text x="80"  y="150" text-anchor="middle" fill="oklch(0.94 0.05 220)" font-weight="700">Ideation 29</text>
                <text x="80"  y="162" text-anchor="middle" fill="oklch(0.74 0.13 220)" font-size="8">26 advocates</text>
                <rect x="130" y="135" width="80" height="34" rx="5" fill="oklch(0.28 0.16 350)" stroke="oklch(0.74 0.18 350)"/>
                <text x="170" y="150" text-anchor="middle" fill="oklch(0.94 0.10 350)" font-weight="700">Panels 45</text>
                <text x="170" y="162" text-anchor="middle" fill="oklch(0.74 0.18 350)" font-size="8">TP·BP·UP·RP</text>
                <rect x="230" y="135" width="80" height="34" rx="5" fill="oklch(0.28 0.10 145)" stroke="oklch(0.78 0.17 145)"/>
                <text x="270" y="150" text-anchor="middle" fill="oklch(0.94 0.07 145)" font-weight="700">Spec 9</text>
                <text x="270" y="162" text-anchor="middle" fill="oklch(0.78 0.17 145)" font-size="8">7 critics</text>
                <rect x="330" y="135" width="80" height="34" rx="5" fill="oklch(0.28 0.14 65)" stroke="oklch(0.78 0.16 65)"/>
                <text x="370" y="150" text-anchor="middle" fill="oklch(0.94 0.10 65)" font-weight="700">Eng 25</text>
                <text x="370" y="162" text-anchor="middle" fill="oklch(0.78 0.16 65)" font-size="8">5×5 teams</text>
                <rect x="430" y="135" width="80" height="34" rx="5" fill="oklch(0.28 0.16 25)" stroke="oklch(0.72 0.21 25)"/>
                <text x="470" y="150" text-anchor="middle" fill="oklch(0.94 0.10 25)" font-weight="700">QA+J+A 24</text>
                <text x="470" y="162" text-anchor="middle" fill="oklch(0.72 0.21 25)" font-size="8">5J + 5A</text>
              </g>
              <rect x="100" y="200" width="340" height="40" rx="6" fill="oklch(0.20 0.04 250)" stroke="oklch(0.74 0.13 220)" stroke-dasharray="4 3"/>
              <text x="270" y="218" text-anchor="middle" fill="oklch(0.74 0.13 220)" font-weight="700" font-size="10">SQLite Blackboard</text>
              <text x="270" y="231" text-anchor="middle" fill="oklch(0.66 0.02 250)" font-size="8.5">single source of truth — every agent reads + writes here</text>
              <text x="270" y="260" text-anchor="middle" fill="oklch(0.66 0.02 250)" font-size="9" font-weight="700">Layer-0 Hooks: factory-policy · askuser-enforcement · auto-retro · idea-drift · cost-regression · escalation · post-h1-signal</text>
            </g>
          </svg>
        </div>'''


def render_modal_live_json_frame() -> str:
    return '''
        <div class="canvas-frame c-f7">
          <div class="editor">
            <div class="left">
              <div class="pf tw" data-typewriter="$ /pf:new &quot;auto-organize meeting notes + extract action items&quot;" data-tw-dur="1500" data-tw-delay="200"></div>
              <div class="modal" data-anim="up" style="--d:1.9s">
                <h4>Question 1 / 4 · target_persona</h4>
                <div class="opt"     data-anim="fade" style="--d:2.3s">Marketing PM</div>
                <div class="opt sel" data-anim="pop"  style="--d:2.7s">Legal paralegal</div>
                <div class="opt"     data-anim="fade" style="--d:2.5s">Product analyst</div>
                <div class="opt"     data-anim="fade" style="--d:2.5s">General knowledge worker</div>
              </div>
            </div>
            <div class="right">
              <h5 data-anim="fade" style="--d:.4s">runs/&lt;id&gt;/idea.spec.json</h5>
              <div data-anim="fade" style="--d:3.3s">{</div>
              <div data-anim="right" style="--d:3.6s">&nbsp;&nbsp;<span class="k">"target_persona"</span>: <span class="s">"legal-paralegal"</span>,</div>
              <div data-anim="right" style="--d:4.0s">&nbsp;&nbsp;<span class="k">"surface.platform"</span>: <span class="s">"web-app"</span>,</div>
              <div data-anim="right" style="--d:4.4s">&nbsp;&nbsp;<span class="k">"killer_feature"</span>: <span class="s">"extract-action-items"</span>,</div>
              <div data-anim="right" style="--d:4.8s">&nbsp;&nbsp;<span class="k">"must_have_constraints"</span>: [<span class="s">"redact-PII"</span>],</div>
              <div data-anim="right" style="--d:5.2s">&nbsp;&nbsp;<span class="k">"_filled_ratio"</span>: <span class="s">0.83</span></div>
              <div data-anim="fade" style="--d:5.6s">}</div>
              <div class="ratio" data-anim="bloom" style="--d:6.2s">▣ ground-truth (≥ 0.7)</div>
            </div>
          </div>
        </div>'''


def render_gallery_interactive_frame() -> str:
    cards = render_gallery_cards_grid()
    return f'''
        <div class="canvas-frame c-f8">
          <div class="browser">
            <div class="bar">localhost · runs/&lt;id&gt;/gallery.html</div>
            <div class="body">
              {cards}
            </div>
          </div>
          <div class="ripple" style="top:42%;left:42%"></div>
          <div class="cursor" style="top:46%;left:46%"></div>
        </div>'''


def render_triple_pane_frame() -> str:
    return '''
        <div class="canvas-frame c-f9">
          <span class="speed">×8 timelapse</span>
          <div class="triple">
            <div class="pane spec" data-anim="fade" style="--d:.2s">
              <h5>SpecDD · OpenAPI</h5>
              <span class="lock" data-anim="pop" style="--d:3.4s">🔒 SHA-256</span>
              <div data-anim="right" style="--d:.5s">openapi: 3.1.0</div>
              <div data-anim="right" style="--d:.8s">info:</div>
              <div data-anim="right" style="--d:1.1s">&nbsp;&nbsp;title: meeting-…</div>
              <div data-anim="right" style="--d:1.4s">paths:</div>
              <div data-anim="right" style="--d:1.7s">&nbsp;&nbsp;/notes:</div>
              <div data-anim="right" style="--d:1.9s">&nbsp;&nbsp;&nbsp;&nbsp;post:</div>
              <div data-anim="right" style="--d:2.2s">&nbsp;&nbsp;/actions:</div>
              <div data-anim="right" style="--d:2.4s">&nbsp;&nbsp;&nbsp;&nbsp;get:</div>
              <div data-anim="right" style="--d:2.7s">&nbsp;&nbsp;/redact:</div>
              <div data-anim="right" style="--d:2.9s">&nbsp;&nbsp;&nbsp;&nbsp;post:</div>
              <div data-anim="fade" style="--d:3.6s;color:var(--green);margin-top:8px">✓ locked</div>
            </div>
            <div class="pane team" data-anim="fade" style="--d:.4s">
              <h5>5 teams · parallel</h5>
              <div class="row" data-anim="right" style="--d:1.2s">apps/api</div>
              <div class="row" data-anim="right" style="--d:1.5s">apps/web</div>
              <div class="row" data-anim="right" style="--d:1.8s">prisma/</div>
              <div class="row" data-anim="right" style="--d:2.1s">deploy/</div>
              <div class="row" data-anim="right" style="--d:2.4s">packages/sdk</div>
              <div data-anim="fade" style="--d:3.0s;color:var(--warm);margin-top:10px">25 engineers · live</div>
            </div>
            <div class="pane score" data-anim="fade" style="--d:.6s">
              <h5>TestDD · score</h5>
              <div class="num num-roll" data-counter data-target="499" data-dur="3800" data-delay="2200" data-stops="412,478">0</div>
              <div class="max">/ 500</div>
              <div class="gauge"><i></i></div>
              <div class="checks">
                <span data-anim="pop" style="--d:6.0s">✓</span><span data-anim="pop" style="--d:6.2s">✓</span><span data-anim="pop" style="--d:6.4s">✓</span><span data-anim="pop" style="--d:6.6s">✓</span><span data-anim="pop" style="--d:6.8s">✓</span>
              </div>
              <div data-anim="fade" style="--d:7.2s;color:var(--muted);margin-top:8px;font-family:ui-sans-serif;font-size:11.5px">5 judges + 5 auditors</div>
            </div>
          </div>
        </div>'''


def render_terminal_browser_frame() -> str:
    return '''
        <div class="canvas-frame c-f10">
          <div class="term">
            <div data-anim="right" style="--d:.2s">$ /pf:freeze</div>
            <div data-anim="right" style="--d:.5s"><span class="ok">✓</span> Score 499/500 · 5 auditors signed</div>
            <div data-anim="right" style="--d:.8s"><span class="arr">→</span> Awaiting H2 approval…</div>
            <div data-anim="right" style="--d:1.5s;margin-top:10px">$ /pf:preview &lt;run&gt;</div>
            <div data-anim="right" style="--d:1.7s"><span class="ok">✓</span> profile=standard</div>
            <div data-anim="right" style="--d:1.9s"><span class="ok">✓</span> port :18080 free</div>
            <div data-anim="right" style="--d:2.1s"><span class="ok">✓</span> apps/api · apps/web · pnpm dev</div>
            <div data-anim="right" style="--d:2.3s"><span class="arr">↗</span> opening browser…</div>
          </div>
          <div class="deploybtn">Deploy ✓</div>
          <div class="browser2">
            <div class="bar"><span class="url">localhost:18080/notes</span></div>
            <div class="body">
              <h4 data-anim="up" style="--d:3.3s">Meeting · 2026-04-26 · Q2 planning</h4>
              <div class="item" data-anim="right" style="--d:3.7s"><span>Send pricing draft to legal</span><span class="badge">due 04-30</span></div>
              <div class="item" data-anim="right" style="--d:4.0s"><span>Schedule demo for ACME</span><span class="badge">today</span></div>
              <div class="item" data-anim="right" style="--d:4.3s"><span>Review SOC2 evidence</span><span class="badge">@andrea</span></div>
              <div class="item" data-anim="right" style="--d:4.6s"><span>File expense reimbursement</span><span class="badge">@kim</span></div>
            </div>
          </div>
        </div>'''


def render_repo_install_frame(deck_config: dict, hero_echo_html: str) -> str:
    project = deck_config["title"].split(" · ")[0]
    repo = f"github.com/Two-Weeks-Team/{project.replace(' ', '')}ForClaudeCode"
    badges = [
        ("CI · passing", "green", 0.5),
        ("Marketplace · valid", "cool", 0.6),
        ("Pages · live", "cool", 0.7),
        (deck_config.get("version_label", "v0.1.0"), "warm", 0.8),
        ("License Apache-2.0", "", 0.9),
        ("Built with Opus 4.7", "warm", 1.0),
        ("Claude Code Plugin", "cool", 1.1),
        ("PitchForge", "green", 1.2),
        ("Cinematic", "warm", 1.3),
        ("OBS-ready", "cool", 1.4),
        ("★ stars", "", 1.5),
    ]
    badge_html = "\n            ".join(
        f'<span class="b {variant}" data-anim="pop" style="--d:{d}s">{label}</span>'
        for label, variant, d in badges
    )
    install = "$ /plugin marketplace add Two-Weeks-Team/PitchForgeForClaudeCode\\n$ /plugin install pitch@two-weeks-team"
    return f'''
        <div class="canvas-frame c-f11">
          <div class="repo" data-anim="up" style="--d:.1s"><b>{repo}</b> · {deck_config.get("version_label", "v0.1.0")}</div>
          <div class="badges">
            {badge_html}
          </div>
          <div class="install tw" data-typewriter="{install}" data-tw-dur="2200" data-tw-delay="1900"></div>
          <div class="lockup" data-anim="bloom" style="--d:4.5s">Built with <b>Claude Opus 4.7</b><br><span class="lockup-echo">{hero_echo_html}</span></div>
        </div>'''


SHAPE_PROPS_DEFAULTS = {
    "F1": {
        "blocks": ["idea", "spec", "tests"],
        "terminal": {"text": "?"},
    },
    "F3": {
        "blocks": ["26 results", "spec", "tests"],
    },
    "F2": {
        "rows": [
            {"label": "SaaS that pivoted away from its first spec", "value": "v1 → v2 → v3"},
            {"label": "Test suite green, product killed", "value": "100% pass"},
            {"label": "OpenAPI locked, customer hated the UX", "value": "spec ≠ value"},
        ],
    },
    "F5": {
        "label": "how many opus 4.7 personas built that gallery?",
        "target": 144,
        "duration_ms": 1400,
        "breakdown": "26 advocates · 40 panelists · 25 engineers · 14 QA · 5 judges · 5 auditors · 9 spec · 20 ideation · 3 meta",
    },
    "F6": {"label": "six-tier engineering company"},
}


def render_canvas_for_frame(frame: dict, *, deck_config: dict) -> str:
    fid = frame["frame_id"]
    shape = frame["shape"]
    if shape == "cover":
        return ""  # cover canvas is rendered by render_cover_body
    if shape == "close":
        return ""  # close canvas is rendered by render_close_body
    if shape == "gallery-hero":
        # Hero placement vs interactive variant — drive by frame id (F4 vs F8)
        if fid == "F8":
            return render_gallery_interactive_frame()
        # primary hero placement
        words_html = render_hero_words_html(
            deck_config["hero"]["split_words"],
            deck_config["hero"]["accent_word_index"],
        )
        tiles = render_hero_tiles()
        echo_mini = deck_config.get("tagline", "")
        vo_overlay = frame.get("voiceover", "")
        return f'''
        <div class="hero-canvas-full">
          <div class="grid">
            {tiles}
          </div>
          <div class="lab"><span class="hero-letters">{words_html}</span></div>
          <div class="echo-mini" data-anim="fade" style="--d:3.4s">{echo_mini}</div>
          <div class="vo-overlay" data-anim="up" style="--d:4.0s">{vo_overlay}</div>
        </div>'''
    if shape == "chain":
        defaults = SHAPE_PROPS_DEFAULTS.get(fid, {"blocks": ["a", "b", "c"], "terminal": {"text": "?"}})
        variant = "f1" if fid == "F1" else "f3"
        return render_chain_frame(
            frame,
            variant=variant,
            blocks=defaults["blocks"],
            terminal=defaults.get("terminal", {"text": "?"}),
        )
    if shape == "stack-strikethrough":
        defaults = SHAPE_PROPS_DEFAULTS.get(fid, {"rows": []})
        return render_stack_strikethrough_frame(frame, defaults["rows"])
    if shape == "counter-roll":
        d = SHAPE_PROPS_DEFAULTS.get(fid, {})
        return render_counter_roll_frame(
            label=d.get("label", ""),
            target=d.get("target", 100),
            duration_ms=d.get("duration_ms", 1400),
            breakdown=d.get("breakdown", ""),
            stops=d.get("stops", ""),
        )
    if shape == "hierarchy-diagram":
        d = SHAPE_PROPS_DEFAULTS.get(fid, {"label": ""})
        return render_hierarchy_diagram_frame(d.get("label", ""))
    if shape == "modal-live-json":
        return render_modal_live_json_frame()
    if shape == "triple-pane":
        return render_triple_pane_frame()
    if shape == "terminal-browser":
        return render_terminal_browser_frame()
    if shape == "repo-install":
        hero_echo = _hero_with_accent_html(
            {"split_words": deck_config["hero"]["split_words"], "accent_word_index": deck_config["hero"]["accent_word_index"]}
        )
        # Use the literal hero copy preserving accent
        hero_words = deck_config["hero"]["split_words"]
        idx = deck_config["hero"]["accent_word_index"]
        hero_html_words = []
        for i, w in enumerate(hero_words):
            hero_html_words.append(f"<i>{w}</i>" if i == idx else w)
        hero_html = " ".join(hero_html_words)
        return render_repo_install_frame(deck_config, hero_html)
    return ""


def render_cover_slide(deck_config: dict) -> str:
    cover = deck_config["cover"]
    meta_html = "".join(
        f'<div><b>{m["value"]}</b> · {m["label"]}</div>'
        for m in cover.get("meta", [])
    )
    return f'''
  <section class="slide cover active" data-slide="1" data-id="cover">
    <div class="topbar">
      <span class="time">00:00</span>
      <span class="id">{deck_config["id_label"]}</span>
      <span class="right"><span class="counter">01 / {len(deck_config["slide_duration_seconds"])}</span><span class="esc">esc · overview</span></span>
    </div>
    <div class="body">
      <div class="canvas-wrap">
        <div class="cover-content">
          <div class="cover-eyebrow">{cover["eyebrow"]}</div>
          <div class="cover-title">{deck_config["title"].split(" · ")[0]}</div>
          <div class="cover-sub">{deck_config.get("subtitle", "")}</div>
          <div class="cover-hero">{cover["hero_inline"]}</div>
          <div class="cover-tag">{deck_config.get("tagline", "")}</div>
          <div class="cover-meta">
            {meta_html}
          </div>
          <div class="cover-cta">{cover.get("cta", "→ press → to begin")}</div>
        </div>
      </div>
    </div>
    <div class="navbar">
      <span class="keys"><kbd>→</kbd><kbd>space</kbd> next · <kbd>esc</kbd> overview · <kbd>1-9</kbd> jump</span>
      <div class="progress"><i style="width:{deck_config["progress_widths_pct"][0]}%"></i></div>
      <span class="nav-btn" data-act="next">next →</span>
    </div>
  </section>'''


def render_close_slide(deck_config: dict, position: int, total: int) -> str:
    close = deck_config["close"]
    checks_html = "\n            ".join(f"<div>{c}</div>" for c in close.get("checks", []))
    return f'''
  <section class="slide close" data-slide="{position}" data-id="close">
    <div class="topbar">
      <span class="time">— · END</span>
      <span class="id">NOW GO RECORD IT</span>
      <span class="right"><span class="counter">{position:02d} / {total}</span><span class="esc">esc · overview</span></span>
    </div>
    <div class="body">
      <div class="canvas-wrap">
        <div class="close-content">
          <div class="close-stat">{close["stat_line"]}</div>
          <div class="close-h">{close["headline"]}</div>
          <div class="close-checks">
            {checks_html}
          </div>
          <div class="close-call">{close["call"]}</div>
          <div class="close-repo">{close["repo_line"]}</div>
        </div>
      </div>
    </div>
    <div class="navbar">
      <span class="nav-btn" data-act="prev">← prev</span>
      <span class="keys"><kbd>esc</kbd> overview · <kbd>1</kbd> back to cover</span>
      <div class="progress"><i style="width:100%"></i></div>
      <span class="nav-btn" data-act="first">↺ restart</span>
    </div>
  </section>'''


def render_content_slide(frame: dict, deck_config: dict, *, position: int, total: int) -> str:
    """Generic content slide (anything that isn't cover or close)."""
    fid = frame["frame_id"]
    shape = frame["shape"]
    cls = slide_class(fid, shape)
    cls_attr = f"slide {cls}".strip()
    show_echo = frame.get("show_echo_ribbon", True) and cls != "hero" and cls != "cover" and cls != "close"
    echo_html = ""
    if show_echo:
        echo_html = f'<span class="echo">{deck_config["hero"]["echo_ribbon_text"]}</span>'

    time_label = fmt_time_range(frame["time_start_seconds"], frame["time_start_seconds"] + frame["duration_seconds"])
    id_label_full = f"{fid} · {(frame.get('meta_tag') or '').upper().replace('ACT II ·', '·').replace('ACT III ·', '·').replace('ACT IV ·', '·').replace('ACT V ·', '·').strip()}"
    if not (frame.get("meta_tag") or "").strip():
        id_label_full = fid
    counter = f"{position:02d} / {total}"

    canvas = render_canvas_for_frame(frame, deck_config=deck_config)

    # Hero slide hides script panel
    script_panel = ""
    if cls != "hero":
        script_panel = f'''
      <div class="script-wrap">
        <div class="meta-tag">{frame.get("meta_tag", "")}</div>
        <h2>{frame.get("script_h2", "")}</h2>
        <div class="vo">{frame.get("voiceover", "")}</div>
        <div class="stage">
          <b>Delivery:</b> {frame.get("delivery_note", "")}
          <span class="tone">tone: {frame.get("tone_note", "")}</span>
        </div>
      </div>'''

    navbar_keys = frame.get("navbar_keys_label") or "<kbd>←</kbd> · <kbd>→</kbd> · <kbd>esc</kbd>"
    if frame.get("navbar_keys_label"):
        keys_attrs = ' style="color:var(--gold);font-weight:700"'
    else:
        keys_attrs = ""

    return f'''
  <section class="{cls_attr}" data-slide="{position}" data-id="{fid.lower()}">
    {echo_html}
    <div class="topbar">
      <span class="time">{time_label}</span>
      <span class="id">{id_label_full}</span>
      <span class="right"><span class="counter">{counter}</span><span class="esc">esc · overview</span></span>
    </div>
    <div class="body">
      <div class="canvas-wrap">
        {canvas}
      </div>{script_panel}
    </div>
    <div class="navbar">
      <span class="nav-btn" data-act="prev">← prev</span>
      <span class="keys"{keys_attrs}>{navbar_keys}</span>
      <div class="progress"><i style="width:{deck_config["progress_widths_pct"][position - 1]}%"></i></div>
      <span class="nav-btn" data-act="next">next →</span>
    </div>
  </section>'''


def render_frames_html(spec: dict, deck_config: dict) -> str:
    frames = sorted(spec["frames"], key=lambda f: f["position"])
    total = len(frames)
    out = []
    for idx, frame in enumerate(frames, start=1):
        if frame["frame_id"] == "cover":
            out.append(render_cover_slide(deck_config))
        elif frame["frame_id"] == "close":
            out.append(render_close_slide(deck_config, idx, total))
        else:
            out.append(render_content_slide(frame, deck_config, position=idx, total=total))
    return "\n".join(out)


# ---------- recording-config + final HTML render --------------------------- #

def build_recording_config(deck_config: dict) -> dict:
    ranges = deck_config.get("ranges", {})
    opening = ranges.get("opening") or {}
    full = ranges.get("full") or {}
    return {
        "_schema_version": SCHEMA_VERSION,
        "_deck_config_run_id": deck_config.get("_frame_spec_run_id", "tier1-auto"),
        "modes": {
            "review": {"body_class": ""},
            "recording": {"body_class": "rec", "floating_timer": True},
            "cinematic": {"body_class": "rec cinematic", "hide_vo_overlay": True, "hide_floating_timer": True},
        },
        "keymap": {
            "next": ["ArrowRight", "ArrowDown", " ", "PageDown", "Enter"],
            "prev": ["ArrowLeft", "ArrowUp", "PageUp"],
            "first": ["Home"],
            "last": ["End"],
            "overview": ["Escape"],
            "toggle_rec": ["r", "R"],
            "toggle_auto": ["a", "A"],
            "replay": ["p", "P"],
        },
        "countdown": {
            "sequence": ["3", "2", "1", "GO"],
            "cadence_ms": 1000,
            "label_template": "CINEMATIC PLAYBACK STARTS IN… ${range_label}",
        },
        "ranges": [
            {
                "key": opening.get("key", "o"),
                "start_position": opening.get("start_position", 2),
                "end_position": opening.get("end_position", 5),
                "label": opening.get("label", "opening"),
            },
            {
                "key": full.get("key", "f"),
                "start_position": full.get("start_position", 2),
                "end_position": full.get("end_position", len(deck_config["slide_duration_seconds"]) - 1),
                "label": full.get("label", "full"),
            },
        ],
        "modifier_safety": {
            "guard_metaKey": True,
            "guard_ctrlKey": True,
            "guard_altKey": True,
            "guard_shiftKey": False,
        },
        "capture": {"enabled": False},
    }


def render_deck_html(spec: dict, deck_config: dict, recording_config: dict) -> str:
    shell_path = TEMPLATES / "deck-shell.html"
    shell = shell_path.read_text(encoding="utf-8")

    palette_tokens = deck_config["palette"]["tokens"]
    for token, val in palette_tokens.items():
        shell = shell.replace(f"{{{{palette.{token}}}}}", val)

    frames_html = render_frames_html(spec, deck_config)
    slide_count = len(deck_config["slide_duration_seconds"])

    opening = deck_config["ranges"]["opening"]
    full = deck_config["ranges"]["full"]
    countdown = recording_config["countdown"]

    short = lambda label: label.split("·")[0].strip() if "·" in label else label

    replacements = {
        "{{title}}": deck_config["title"],
        "{{frames}}": frames_html,
        "{{slide_count}}": str(slide_count),
        "{{ranges.opening.label}}": opening["label"],
        "{{ranges.opening.short_label}}": short(opening["label"]),
        "{{ranges.opening.button_label}}": opening.get("button_label", "▶ Opening"),
        "{{ranges.opening.start_position_zero_indexed}}": str(opening["start_position"] - 1),
        "{{ranges.opening.end_position_zero_indexed}}": str(opening["end_position"] - 1),
        "{{ranges.full.label}}": full["label"],
        "{{ranges.full.short_label}}": short(full["label"]),
        "{{ranges.full.button_label}}": full.get("button_label", "▶ Full"),
        "{{ranges.full.start_position_zero_indexed}}": str(full["start_position"] - 1),
        "{{ranges.full.end_position_zero_indexed}}": str(full["end_position"] - 1),
        "{{slide_duration_seconds}}": json.dumps(deck_config["slide_duration_seconds"]),
        "{{summaries}}": json.dumps(deck_config["summaries"], ensure_ascii=False),
        "{{countdown_sequence}}": json.dumps(countdown["sequence"]),
        "{{countdown_cadence_ms}}": str(countdown["cadence_ms"]),
        "{{capture_enabled_js}}": "true" if recording_config.get("capture", {}).get("enabled") else "false",
    }
    for k, v in replacements.items():
        shell = shell.replace(k, v)
    return shell


# ---------- entrypoint ----------------------------------------------------- #

def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    g = p.add_mutually_exclusive_group(required=True)
    g.add_argument("--brief", help="path to brief.json (Tier 2 / Tier 3 input)")
    g.add_argument("--one-liner", help="project description (Tier 1 Auto)")
    p.add_argument("--output", required=True, help="path for deck-cinematic.html (sibling JSON files written alongside)")
    p.add_argument("--runtime", type=int, default=160, help="runtime seconds (Tier 1 Auto only; default 160)")
    p.add_argument("--arc", default=None, help="narrative arc name (Tier 1 Auto only; auto-selected by runtime)")
    p.add_argument("--palette", default="oklch-warm-gold", help="color palette name (Tier 1 Auto only)")
    p.add_argument("--hero", default=None, help="hero copy verbatim (Tier 1 Auto only; default = paper-title pattern)")
    p.add_argument("--capture", action="store_true", help="enable in-browser MediaRecorder capture (v0.5+)")
    p.add_argument("--frame-spec", default=None,
                   help="reuse an existing frame-spec.json (skip P2 regeneration; "
                        "used by /pitch:reorder so reorder reflow survives)")
    args = p.parse_args(argv)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)

    if args.brief:
        brief_path = Path(args.brief)
        brief = load_json(brief_path)
    else:
        brief = synthesize_brief(
            args.one_liner,
            runtime=args.runtime,
            arc=args.arc,
            palette=args.palette,
            hero=args.hero,
        )
    # Always copy/write the brief into the output dir so downstream
    # commands (status, export, replay, gallery) have a complete run on
    # disk regardless of how the brief got there.
    write_json(output.parent / "brief.json", brief)

    if args.frame_spec:
        # /pitch:reorder path — caller has already produced an updated
        # frame-spec.json. Honor it instead of regenerating from arc.
        spec_src = Path(args.frame_spec)
        if not spec_src.exists():
            print(f"[FAIL] --frame-spec not found: {spec_src}", file=sys.stderr)
            return 2
        spec = load_json(spec_src)
    else:
        spec = build_frame_spec(brief)
    write_json(output.parent / "frame-spec.json", spec)

    deck_config = build_deck_config(brief, spec)
    write_json(output.parent / "deck-config.json", deck_config)

    recording_config = build_recording_config(deck_config)
    if args.capture:
        recording_config["capture"]["enabled"] = True
    write_json(output.parent / "recording-config.json", recording_config)

    html = render_deck_html(spec, deck_config, recording_config)
    output.write_text(html, encoding="utf-8")

    sum_dur = sum(deck_config["slide_duration_seconds"])
    target = int(spec["runtime_seconds"])
    print("=== generate-deck.py ===")
    print(f"brief:        {brief.get('project_name', '?')} · {target}s · {brief.get('narrative_arc', '?')}")
    print(f"hero:         \"{brief.get('hero_copy', '')}\"")
    print(f"frames:       {len(spec['frames'])} (sum duration {sum_dur:.0f}s, target {target}s)")
    print(f"output:       {output}")
    print(f"sibling JSON: brief / frame-spec / deck-config / recording-config")
    print()
    print("Next: open the deck in a browser, press F11, then O for the opening sequence.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
