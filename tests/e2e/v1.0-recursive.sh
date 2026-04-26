#!/usr/bin/env bash
# tests/e2e/v1.0-recursive.sh
#
# v1.0.0 acceptance — recursive proof + export pipeline.
#
# 1. Generate the plugin's own demo deck from
#    tests/fixtures/pitchforge-self/brief.json (recursive proof — the plugin
#    builds its own pitch deck).
# 2. Run all Layer-0 hooks against the produced artifacts.
# 3. Exercise scripts/export-deck.py for each format that has actionable
#    output (html, bundle).

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

FIXTURE_DIR="tests/fixtures/pitchforge-self"
GEN_DIR="$FIXTURE_DIR/.generated"
EXPORTS_DIR="$FIXTURE_DIR/.exports"

rm -rf "$GEN_DIR" "$EXPORTS_DIR"

pass=0
fail=0
ok()  { echo "  ✓ $1"; pass=$((pass + 1)); }
bad() { echo "  ✗ $1" >&2; fail=$((fail + 1)); }

echo "=== e2e · v1.0 recursive proof + export ==="
echo

echo "[1/4] Recursive — plugin builds its own demo deck"
python3 scripts/generate-deck.py \
  --brief "$FIXTURE_DIR/brief.json" \
  --output "$GEN_DIR/deck-cinematic.html" \
  >/dev/null
[[ -f "$GEN_DIR/deck-cinematic.html" ]] && ok "deck-cinematic.html written" || bad "deck not written"
[[ -f "$GEN_DIR/frame-spec.json" ]]      && ok "frame-spec.json written"      || bad "frame-spec missing"

# Hero copy verbatim (Layer-0 Rule 4)
HERO="Pitch is all you need."
grep -qF "$HERO" "$GEN_DIR/deck-cinematic.html" \
  && ok "PitchForge hero copy verbatim in deck" \
  || bad "hero copy paraphrased"
echo

echo "[2/4] Layer-0 hooks on recursive output"
python3 plugins/pitch/hooks/cmd-modifier-guard.py "$GEN_DIR/deck-cinematic.html" >/dev/null \
  && ok "cmd-modifier-guard pass" \
  || bad "cmd-modifier-guard fail"
python3 plugins/pitch/hooks/tone-ai-detector.py "$GEN_DIR/frame-spec.json" --quiet >/dev/null \
  && ok "tone-ai-detector pass" \
  || bad "tone-ai-detector flagged violations"
python3 plugins/pitch/hooks/stale-count-detector.py --plugin-dir plugins/pitch --readme README.md --strict >/dev/null \
  && ok "stale-count-detector strict pass" \
  || bad "stale-count drift"
echo

echo "[3/4] Export — html + bundle"
python3 scripts/export-deck.py --run "$GEN_DIR/" --format html --out "$EXPORTS_DIR/" >/dev/null
ls "$EXPORTS_DIR"/*-cinematic.html >/dev/null 2>&1 \
  && ok "html export written" \
  || bad "html export missing"

python3 scripts/export-deck.py --run "$GEN_DIR/" --format bundle --out "$EXPORTS_DIR/" >/dev/null
ls "$EXPORTS_DIR"/*.bundle.tar.gz >/dev/null 2>&1 \
  && ok "bundle.tar.gz export written" \
  || bad "bundle export missing"

# Bundle should contain the key files
bundle=$(ls "$EXPORTS_DIR"/*.bundle.tar.gz | head -1)
for member in brief.json frame-spec.json deck-cinematic.html recording-config.json; do
  if tar -tzf "$bundle" 2>/dev/null | grep -q "/$member$"; then
    ok "bundle contains $member"
  else
    bad "bundle missing $member"
  fi
done
echo

echo "[4/4] PDF / WebM / GIF instructions print without error"
python3 scripts/export-deck.py --run "$GEN_DIR/" --format pdf  --out "$EXPORTS_DIR/" >/dev/null && ok "pdf instructions" || bad "pdf instructions"
python3 scripts/export-deck.py --run "$GEN_DIR/" --format webm --out "$EXPORTS_DIR/" >/dev/null && ok "webm instructions" || bad "webm instructions"
python3 scripts/export-deck.py --run "$GEN_DIR/" --format gif  --out "$EXPORTS_DIR/" >/dev/null && ok "gif instructions" || bad "gif instructions"
echo

echo "=== SUMMARY ==="
echo "Pass: $pass"
echo "Fail: $fail"
if [[ "$fail" -eq 0 ]]; then
  echo "✓ v1.0 recursive proof + export: PASS"
  exit 0
fi
echo "✗ v1.0 recursive proof + export: FAIL"
exit 1
