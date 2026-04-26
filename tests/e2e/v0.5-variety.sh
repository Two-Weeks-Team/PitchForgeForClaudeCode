#!/usr/bin/env bash
# tests/e2e/v0.5-variety.sh
#
# v0.5.0 acceptance — exercise the full variety: every arc × every palette.
# Each combination must produce a valid deck-cinematic.html that passes the
# Layer-0 hooks (cmd-modifier-guard + tone-ai-detector).
#
# Why a separate test from v0.1.0?
#   The v0.1.0 acceptance is qualitative-equivalence to the *reference deck*.
#   The v0.5 acceptance is range coverage — that swapping arc / palette /
#   runtime never breaks the contract. Same gates, broader inputs.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

GEN_BASE="tests/fixtures/.v05-variety"
rm -rf "$GEN_BASE"

ARCS=("wow-first-60s" "wow-first-160s" "problem-first-180s" "story-300s" "teaser-45s")
PALETTES=("oklch-warm-gold" "monochrome-cinema" "pastel-light")

pass=0
fail=0
ok()  { echo "  ✓ $1"; pass=$((pass + 1)); }
bad() { echo "  ✗ $1" >&2; fail=$((fail + 1)); }

echo "=== e2e · v0.5 variety (5 arcs × 3 palettes = 15 combinations) ==="
echo

for arc_full in "${ARCS[@]}"; do
  arc_name=$(echo "$arc_full" | sed -E 's/-[0-9]+s$//')
  arc_runtime=$(echo "$arc_full" | grep -oE '[0-9]+' | tail -1)
  for palette in "${PALETTES[@]}"; do
    label="$arc_full × $palette"
    run_dir="$GEN_BASE/$arc_full-$palette"
    brief_path="$run_dir/brief.json"
    mkdir -p "$run_dir"
    cat > "$brief_path" <<EOF
{
  "_schema_version": "0.1.0",
  "_filled_ratio": 0.50,
  "project_name": "Variety Test",
  "project_one_liner": "Variety smoke test for $arc_full + $palette.",
  "audience": "hackathon-judges",
  "runtime_seconds": $arc_runtime,
  "narrative_arc": "$arc_name",
  "hero_copy": "Variety is all you need.",
  "hero_pattern": "paper-title-inversion",
  "color_palette": "$palette",
  "tone": "agro-drop-thrill",
  "judging_criteria": [{"name":"Demo","weight":1.0}],
  "constraints": ["english-only","single-html","no-third-party-deps"]
}
EOF

    if ! python3 scripts/generate-deck.py --brief "$brief_path" --output "$run_dir/deck-cinematic.html" >/dev/null 2>&1; then
      bad "$label · generator crashed"
      continue
    fi

    if ! python3 plugins/pitch/hooks/cmd-modifier-guard.py "$run_dir/deck-cinematic.html" >/dev/null; then
      bad "$label · modifier-key guard fail"
      continue
    fi

    if ! python3 plugins/pitch/hooks/tone-ai-detector.py "$run_dir/frame-spec.json" --quiet >/dev/null; then
      bad "$label · tone audit fail"
      continue
    fi

    if ! grep -qF "Variety is all you need." "$run_dir/deck-cinematic.html"; then
      bad "$label · hero copy missing in deck-cinematic.html"
      continue
    fi

    ok "$label"
  done
done
echo
echo "=== SUMMARY ==="
echo "Pass: $pass"
echo "Fail: $fail"
if [[ "$fail" -eq 0 ]]; then
  echo "✓ v0.5 variety acceptance: PASS"
  exit 0
fi
echo "✗ v0.5 variety acceptance: FAIL"
exit 1
