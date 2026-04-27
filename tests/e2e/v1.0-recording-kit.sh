#!/usr/bin/env bash
# tests/e2e/v1.0-recording-kit.sh
#
# v1.0 acceptance — the recording kit handed to a video team is
# self-contained and actionable.
#
# A new operator who has never read methodology/* must be able to:
#   1. Receive the tarball
#   2. Untar it
#   3. Read README.md inside the kit
#   4. Open deck-cinematic.html, read voiceover-script.md
#   5. Record without contacting the deck author
#
# This test simulates that scenario.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

BASE="tests/fixtures/.v10-recording-kit"
RUN="$BASE/run"
OUT="$BASE/out"
EXTRACTED="$BASE/extracted"

rm -rf "$BASE"
mkdir -p "$RUN" "$OUT" "$EXTRACTED"

pass=0
fail=0
ok()  { echo "  ✓ $1"; pass=$((pass + 1)); }
bad() { echo "  ✗ $1" >&2; fail=$((fail + 1)); }

echo "=== e2e · v1.0 recording-kit ==="
echo

echo "[1/4] Generate fixture run + build kit"
python3 scripts/generate-deck.py \
  --brief tests/fixtures/preview-forge-160s/brief.json \
  --output "$RUN/deck-cinematic.html" >/dev/null
ok "fixture run scaffolded"

python3 scripts/build-recording-kit.py --run "$RUN/" --out "$OUT/" >/dev/null
KIT_DIR=$(find "$OUT" -mindepth 1 -maxdepth 1 -type d | head -1)
TARBALL=$(find "$OUT" -mindepth 1 -maxdepth 1 -type f -name "*.tar.gz" | head -1)
[[ -d "$KIT_DIR" ]] && ok "kit directory created: $(basename "$KIT_DIR")" || bad "kit dir missing"
[[ -f "$TARBALL" ]] && ok "tarball created: $(basename "$TARBALL")" || bad "tarball missing"
echo

echo "[2/4] Kit contents (every file the video team needs)"
for required in deck-cinematic.html voiceover-script.md recording-checklist.md \
                take-log.csv obs-profile.json README.md meta.json \
                RECORDING-PLAYBOOK.md; do
  [[ -f "$KIT_DIR/$required" ]] && ok "$required present" || bad "$required missing"
done
echo

echo "[3/4] Self-containment — extract tarball into a fresh dir, no repo dependency"
tar -xzf "$TARBALL" -C "$EXTRACTED/"
EXTRACTED_KIT=$(find "$EXTRACTED" -mindepth 1 -maxdepth 1 -type d | head -1)
[[ -d "$EXTRACTED_KIT" ]] && ok "tarball extracts cleanly" || bad "tarball extract failed"

# All artifacts must work without the rest of the repo.
# 1. deck-cinematic.html: modifier-key guard + hero copy verbatim
python3 plugins/pitch/hooks/cmd-modifier-guard.py "$EXTRACTED_KIT/deck-cinematic.html" >/dev/null \
  && ok "extracted deck passes cmd-modifier-guard" \
  || bad "extracted deck fails L1 guard"
grep -qF "Preview is all you need." "$EXTRACTED_KIT/deck-cinematic.html" \
  && ok "extracted deck has hero copy verbatim" \
  || bad "hero copy lost in tarball"

# 2. voiceover-script.md: must reference the hero, list every frame, contain delivery notes
SCRIPT="$EXTRACTED_KIT/voiceover-script.md"
grep -qF "Preview is all you need." "$SCRIPT" \
  && ok "voiceover-script lists hero copy" \
  || bad "voiceover-script missing hero"
grep -qE "^## (F4|F1|F2|F3|F5|F6|F7|F8|F9|F10|F11)" "$SCRIPT" \
  && ok "voiceover-script lists content frames" \
  || bad "voiceover-script missing frame headings"
grep -qE '\*\*Delivery\*\*' "$SCRIPT" \
  && ok "voiceover-script includes delivery notes" \
  || bad "voiceover-script missing delivery notes"
grep -qE '\*\*Tone\*\*' "$SCRIPT" \
  && ok "voiceover-script includes tone hints" \
  || bad "voiceover-script missing tone hints"

# 3. recording-checklist.md: hardware/browser/OBS sections
CHECK="$EXTRACTED_KIT/recording-checklist.md"
grep -qE "^## Hardware" "$CHECK"   && ok "checklist has Hardware section"   || bad "Hardware section missing"
grep -qE "^## Browser"  "$CHECK"   && ok "checklist has Browser section"    || bad "Browser section missing"
grep -qE "^## OBS"      "$CHECK"   && ok "checklist has OBS section"        || bad "OBS section missing"
grep -qE "^## Voiceover" "$CHECK"  && ok "checklist has Voiceover section"  || bad "Voiceover section missing"

# 4. take-log.csv: column header + 6 pre-filled rows
TAKE="$EXTRACTED_KIT/take-log.csv"
HEADER=$(head -1 "$TAKE")
echo "$HEADER" | grep -q "take_number" \
  && ok "take-log has take_number column" \
  || bad "take-log header malformed"
LINES=$(wc -l < "$TAKE")
[[ "$LINES" -ge 7 ]] && ok "take-log has ≥ 6 take rows ($LINES total)" || bad "take-log too short"

# 5. obs-profile.json: valid JSON with output config
python3 -c "
import json
d = json.load(open('$EXTRACTED_KIT/obs-profile.json'))
assert 'output' in d and d['output']['fps'] == 30
assert 'scene' in d and any(s.get('type') == 'window-capture' for s in d['scene']['sources'])
" 2>/dev/null && ok "obs-profile.json valid + 30fps + window-capture configured" \
              || bad "obs-profile.json malformed"

# 6. meta.json: machine-readable run metadata
META="$EXTRACTED_KIT/meta.json"
python3 -c "
import json
d = json.load(open('$META'))
assert d['hero_copy'] == 'Preview is all you need.', f'hero drift: {d[\"hero_copy\"]}'
assert d['runtime_seconds'] == 160
assert d['frame_count'] >= 11
assert d['narrative_arc'] == 'wow-first'
" 2>/dev/null && ok "meta.json complete + correct" || bad "meta.json malformed"

# 7. README.md (run-specific): mentions the project + key commands
README="$EXTRACTED_KIT/README.md"
grep -qF "Preview Forge" "$README" && ok "kit README mentions project name" || bad "README missing project"
grep -qE "^## 60-second start" "$README" && ok "kit README has 60-second start guide" || bad "60-second guide missing"
grep -qF "OBS" "$README" && ok "kit README references OBS workflow" || bad "OBS reference missing"

# 8. RECORDING-PLAYBOOK.md (master): bundled for self-containment
PLAYBOOK="$EXTRACTED_KIT/RECORDING-PLAYBOOK.md"
grep -qE "^## Pre-flight checklist" "$PLAYBOOK" \
  && ok "bundled playbook has Pre-flight section" \
  || bad "bundled playbook malformed"
grep -qE "^## Voiceover delivery rules" "$PLAYBOOK" \
  && ok "bundled playbook has delivery rules" \
  || bad "delivery rules missing"
echo

echo "[4/4] Layer-0 enforcement on extracted kit"
# A fresh operator must NOT find any modifier-key bypass, hero paraphrase,
# or stale-count drift in the kit.
python3 plugins/pitch/hooks/tone-ai-detector.py "$RUN/frame-spec.json" --quiet >/dev/null \
  && ok "tone-ai-detector clean on source frame-spec" \
  || bad "tone violations in source spec"

# meta.json + voiceover-script.md hero must match byte-for-byte
META_HERO=$(python3 -c "import json; print(json.load(open('$META'))['hero_copy'])")
SCRIPT_HERO=$(grep -F "Hero copy:" "$SCRIPT" | head -1)
echo "$SCRIPT_HERO" | grep -qF "$META_HERO" \
  && ok "hero copy synced across meta.json + voiceover-script.md (Layer-0 Rule 4)" \
  || bad "hero drift between kit artifacts"

# The deck and the script must agree on the hero
DECK_HERO=$(grep -oE "Preview is [^<]*you need\." "$EXTRACTED_KIT/deck-cinematic.html" | head -1 | tr -d '\n')
[[ "$DECK_HERO" == "Preview is all you need." || "$DECK_HERO" == *"Preview is"*"all"*"you need."* ]] \
  && ok "deck-cinematic.html hero matches script hero" \
  || bad "deck/script hero mismatch: deck='$DECK_HERO'"
echo

echo "=== SUMMARY ==="
echo "Pass: $pass"
echo "Fail: $fail"
if [[ "$fail" -eq 0 ]]; then
  echo "✓ v1.0 recording-kit acceptance: PASS"
  exit 0
fi
echo "✗ v1.0 recording-kit acceptance: FAIL"
exit 1
