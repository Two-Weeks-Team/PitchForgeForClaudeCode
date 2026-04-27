#!/usr/bin/env bash
# tests/e2e/regenerate-reference-deck.sh
#
# v0.1.0 acceptance test: regenerate the reference deck from
# tests/fixtures/preview-forge-160s/brief.json and verify *qualitative*
# equivalence to plugins/pitch/examples/preview-forge-160s/deck.html.
#
# v0.1.0 acceptance is qualitative — same structure, palette, hero,
# ranges, modifier-key safety, gate G4 pass — not byte-identical.
# Byte equivalence becomes a v1.0 goal once the assembler agent runs.
#
# Usage: bash tests/e2e/regenerate-reference-deck.sh
# Exits non-zero on any failed assertion.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

FIXTURE_DIR="tests/fixtures/preview-forge-160s"
GEN_DIR="$FIXTURE_DIR/.generated"
REFERENCE="plugins/pitch/examples/preview-forge-160s/deck.html"

pass=0
fail=0
ok()  { echo "  ✓ $1"; pass=$((pass + 1)); }
bad() { echo "  ✗ $1" >&2; fail=$((fail + 1)); }

echo "=== e2e · regenerate reference deck (v0.1.0 acceptance) ==="
echo

echo "[1/6] Generate from fixture brief"
python3 scripts/generate-deck.py \
  --brief "$FIXTURE_DIR/brief.json" \
  --output "$GEN_DIR/deck-cinematic.html" \
  >/dev/null
[[ -f "$GEN_DIR/deck-cinematic.html" ]] && ok "deck-cinematic.html written" || bad "deck not written"
[[ -f "$GEN_DIR/frame-spec.json" ]]      && ok "frame-spec.json written"      || bad "frame-spec missing"
[[ -f "$GEN_DIR/deck-config.json" ]]     && ok "deck-config.json written"     || bad "deck-config missing"
[[ -f "$GEN_DIR/recording-config.json" ]]&& ok "recording-config.json written" || bad "recording-config missing"
echo

echo "[2/6] Hero copy preservation (Layer-0 Rule 4)"
HERO="Preview is all you need."
grep -qF "$HERO" "$GEN_DIR/frame-spec.json"      && ok "hero verbatim in frame-spec.json"      || bad "hero paraphrased in frame-spec"
grep -qF "$HERO" "$GEN_DIR/deck-cinematic.html"  && ok "hero verbatim in deck-cinematic.html"  || bad "hero paraphrased in deck-cinematic.html"
echo

echo "[3/6] Modifier-key safety (Layer-0 hook)"
python3 plugins/pitch/hooks/cmd-modifier-guard.py "$GEN_DIR/deck-cinematic.html" \
  >/dev/null \
  && ok "cmd-modifier-guard pass" \
  || bad "cmd-modifier-guard fail"
echo

echo "[4/6] Tone audit (gate G4)"
python3 plugins/pitch/hooks/tone-ai-detector.py "$GEN_DIR/frame-spec.json" --quiet \
  >/dev/null \
  && ok "tone-ai-detector: 0 violations" \
  || bad "tone-ai-detector flagged violations (see $GEN_DIR/tone-audit.json)"
echo

echo "[5/6] Structural parity with reference"
REF_SLIDES=$(grep -c '<section class="slide' "$REFERENCE" || true)
GEN_SLIDES=$(grep -c '<section class="slide' "$GEN_DIR/deck-cinematic.html" || true)
[[ "$REF_SLIDES" -eq "$GEN_SLIDES" ]] && ok "slide count: $GEN_SLIDES (reference $REF_SLIDES)" \
                                     || bad "slide count drift: gen=$GEN_SLIDES vs ref=$REF_SLIDES"

GEN_KEYDOWN=$(grep -c "case 'r': case 'R'" "$GEN_DIR/deck-cinematic.html" || true)
[[ "$GEN_KEYDOWN" -ge 1 ]] && ok "R/A/P keymap wired" || bad "R/A/P keymap missing"

GEN_RANGES=$(grep -c "playRange(" "$GEN_DIR/deck-cinematic.html" || true)
[[ "$GEN_RANGES" -ge 4 ]] && ok "playRange wired (≥ 4 call-sites — keymap + buttons)" \
                          || bad "playRange call-site count: $GEN_RANGES (expected ≥ 4)"

# Body classes for the three modes
grep -q "body.rec" "$GEN_DIR/deck-cinematic.html"        && ok "body.rec class CSS present"        || bad "body.rec missing"
grep -q "body.cinematic" "$GEN_DIR/deck-cinematic.html"  && ok "body.cinematic class CSS present"  || bad "body.cinematic missing"

# Countdown overlay
grep -q "countdown-num" "$GEN_DIR/deck-cinematic.html"   && ok "countdown overlay element present" || bad "countdown overlay missing"

# Frame coverage — every shape in the v0.1 set rendered at least once
for shape_class in c-f1 c-f2 c-f3 c-f5 c-f6 c-f7 c-f8 c-f9 c-f10 c-f11 hero-canvas-full; do
  grep -q "$shape_class" "$GEN_DIR/deck-cinematic.html" \
    && ok "shape $shape_class rendered" \
    || bad "shape $shape_class missing"
done
echo

echo "[6/6] frame-spec validity"
python3 -c "
import json, sys
spec = json.load(open('$GEN_DIR/frame-spec.json'))
total_runtime = spec['runtime_seconds']
sum_dur = sum(f['duration_seconds'] for f in spec['frames'] if f['frame_id'] not in ('cover','close'))
delta = abs(sum_dur - total_runtime) / total_runtime
assert delta <= 0.05, f'G2 fail: content sum {sum_dur}s vs target {total_runtime}s (delta {delta:.1%})'
assert spec['hero']['copy'] == 'Preview is all you need.', 'hero drift'
assert any(f['frame_id'] == 'F4' for f in spec['frames']), 'F4 missing'
assert any(f['frame_id'] == 'F11' for f in spec['frames']), 'F11 missing'
print('OK')
" >/dev/null && ok "G2 timestamp rollup within 5%" || bad "G2 timestamp rollup failed"
echo

echo "=== SUMMARY ==="
echo "Pass: $pass"
echo "Fail: $fail"
if [[ "$fail" -eq 0 ]]; then
  echo "✓ v0.1.0 acceptance: PASS"
  exit 0
fi
echo "✗ v0.1.0 acceptance: FAIL"
exit 1
