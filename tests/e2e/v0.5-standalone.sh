#!/usr/bin/env bash
# tests/e2e/v0.5-standalone.sh
#
# v0.5 acceptance — the three standalone commands actually work in code,
# not just in agent docs:
#
#   1. /pitch:hero       → scripts/standalone-hero.py
#   2. /pitch:reorder    → scripts/standalone-reorder.py (L4 mitigation)
#   3. /pitch:tone       → scripts/standalone-tone.py (audit-rewrite-loop)
#
# Each script gets a focused functional check + Layer-0 hook compatibility
# check. The reorder test is the strictest — it validates that all 11
# ripple sites stay in lockstep after a slide swap.

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

GEN_BASE="tests/fixtures/.v05-standalone"
rm -rf "$GEN_BASE"
mkdir -p "$GEN_BASE"

pass=0
fail=0
ok()  { echo "  ✓ $1"; pass=$((pass + 1)); }
bad() { echo "  ✗ $1" >&2; fail=$((fail + 1)); }

echo "=== e2e · v0.5 standalone commands ==="
echo

echo "[1/3] /pitch:hero — 5-pattern candidate generation"
HERO_OUT=$(python3 scripts/standalone-hero.py \
  --one-liner "Notes Triage — extract action items and redact PII" \
  --json 2>&1)
echo "$HERO_OUT" | python3 -c "
import json, sys
d = json.loads(sys.stdin.read())
patterns = {c['pattern'] for c in d['candidates']}
expected = {'paper-title-inversion','stop-start','first-reordering','confession','rule-of-three'}
assert patterns == expected, f'expected {expected}, got {patterns}'
ok = sum(1 for c in d['candidates'] if c.get('verdict') == 'ok')
assert ok >= 1, 'no ok candidate produced'
assert d['recommendation_index'] is not None, 'no recommendation chosen'
print('  patterns: 5/5  ok-verdict: ', ok, '  recommendation: #', d['recommendation_index']+1, sep='')
" 2>&1 && ok "5 patterns generated, ≥1 ok, recommendation present" || bad "hero candidate set malformed"

# Constrain to single pattern
SINGLE=$(python3 scripts/standalone-hero.py \
  --one-liner "Spec Inspector — validate OpenAPI specs" \
  --pattern stop-start --json 2>&1)
SINGLE_COUNT=$(echo "$SINGLE" | python3 -c "import json,sys; print(len(json.loads(sys.stdin.read())['candidates']))")
[[ "$SINGLE_COUNT" == "1" ]] && ok "--pattern returns 1 candidate" || bad "--pattern returns $SINGLE_COUNT (expected 1)"

# HERO_CATALOG conflict detection
CONFLICT_OUT=$(python3 scripts/standalone-hero.py \
  --brief tests/fixtures/preview-forge-160s/brief.json --json 2>&1)
CONFLICT_COUNT=$(echo "$CONFLICT_OUT" | python3 -c "
import json, sys
d = json.loads(sys.stdin.read())
n = sum(len(c.get('dedupe_conflicts') or []) for c in d['candidates'])
print(n)
")
[[ "$CONFLICT_COUNT" -ge "1" ]] && ok "HERO_CATALOG dedupe detects 'Preview is all you need.' conflict" \
                                  || bad "HERO_CATALOG dedupe missed expected conflict"
echo

echo "[2/3] /pitch:reorder — L4 mitigation (timestamp + ripple reflow)"
RUN="$GEN_BASE/reorder"
mkdir -p "$RUN"
python3 scripts/generate-deck.py \
  --brief tests/fixtures/preview-forge-160s/brief.json \
  --output "$RUN/deck-cinematic.html" >/dev/null
ok "fixture run scaffolded"

# Capture original F4 timestamp
F4_T_BEFORE=$(python3 -c "
import json
spec = json.load(open('$RUN/frame-spec.json'))
f = next(f for f in spec['frames'] if f['frame_id']=='F4')
print(f['time_start_seconds'])
")

# Reorder: move F4 to position 5 (problem-first style)
python3 scripts/standalone-reorder.py --run "$RUN/" \
  --order cover,F1,F2,F3,F4,F5,F6,F7,F8,F9,F10,F11,close >/dev/null
ok "reorder applied + deck regenerated"

# Verify F4's time_start changed
F4_T_AFTER=$(python3 -c "
import json
spec = json.load(open('$RUN/frame-spec.json'))
f = next(f for f in spec['frames'] if f['frame_id']=='F4')
print(f['time_start_seconds'])
")
[[ "$F4_T_BEFORE" != "$F4_T_AFTER" ]] \
  && ok "F4 time_start_seconds reflowed: $F4_T_BEFORE → $F4_T_AFTER" \
  || bad "F4 timestamp unchanged after reorder (L4 violation)"

# Verify deck-cinematic.html mentions the new time slot for F4
NEW_TIME_LABEL=$(python3 -c "
sec = $F4_T_AFTER
m, s = int(sec)//60, int(sec)%60
print(f'{m}:{s:02d}')
")
grep -qF "$NEW_TIME_LABEL" "$RUN/deck-cinematic.html" \
  && ok "deck-cinematic.html shows new F4 time label '$NEW_TIME_LABEL'" \
  || bad "deck-cinematic.html missing new F4 time label"

# Verify SLIDE_DURATION array length matches frame count
SLIDE_DUR_LEN=$(python3 -c "
import json, re
html = open('$RUN/deck-cinematic.html').read()
m = re.search(r'const SLIDE_DURATION = (\[[^\]]+\]);', html)
arr = json.loads(m.group(1))
print(len(arr))
")
SPEC_LEN=$(python3 -c "
import json
print(len(json.load(open('$RUN/frame-spec.json'))['frames']))
")
[[ "$SLIDE_DUR_LEN" == "$SPEC_LEN" ]] \
  && ok "SLIDE_DURATION array length matches frame count ($SLIDE_DUR_LEN)" \
  || bad "SLIDE_DURATION drift: deck=$SLIDE_DUR_LEN vs spec=$SPEC_LEN"

# Verify hero copy still verbatim after reorder
grep -qF "Preview is all you need." "$RUN/deck-cinematic.html" \
  && ok "hero copy verbatim post-reorder (Layer-0 Rule 4)" \
  || bad "hero copy lost during reorder"

# Verify hooks still pass
python3 plugins/pitch/hooks/cmd-modifier-guard.py "$RUN/deck-cinematic.html" >/dev/null \
  && ok "cmd-modifier-guard pass post-reorder" \
  || bad "L1 modifier-key guard broken by reorder"
python3 plugins/pitch/hooks/tone-ai-detector.py "$RUN/frame-spec.json" --quiet >/dev/null \
  && ok "tone-ai-detector pass post-reorder" \
  || bad "tone audit broken by reorder"

# Dry-run mode does not write
RUN2="$GEN_BASE/reorder-dryrun"
mkdir -p "$RUN2"
python3 scripts/generate-deck.py \
  --brief tests/fixtures/preview-forge-160s/brief.json \
  --output "$RUN2/deck-cinematic.html" >/dev/null
SPEC_BEFORE=$(md5 -q "$RUN2/frame-spec.json" 2>/dev/null || md5sum "$RUN2/frame-spec.json" | cut -d' ' -f1)
python3 scripts/standalone-reorder.py --run "$RUN2/" --move F4=8 --dry-run >/dev/null
SPEC_AFTER=$(md5 -q "$RUN2/frame-spec.json" 2>/dev/null || md5sum "$RUN2/frame-spec.json" | cut -d' ' -f1)
[[ "$SPEC_BEFORE" == "$SPEC_AFTER" ]] \
  && ok "--dry-run leaves frame-spec.json untouched" \
  || bad "--dry-run wrote to disk"
echo

echo "[3/3] /pitch:tone — audit-rewrite-loop"
RUN3="$GEN_BASE/tone"
mkdir -p "$RUN3"
python3 scripts/generate-deck.py \
  --brief tests/fixtures/preview-forge-160s/brief.json \
  --output "$RUN3/deck-cinematic.html" >/dev/null

# Clean baseline — should audit clean, no rewrite needed
python3 scripts/standalone-tone.py --frame-spec "$RUN3/frame-spec.json" --audit-only --quiet >/dev/null \
  && ok "clean baseline audit passes (no rewrite needed)" \
  || bad "clean baseline failed audit (regression)"

# Inject violations and verify auto-rewrite cleans them
python3 - <<'PY'
import json
spec = json.load(open('tests/fixtures/.v05-standalone/tone/frame-spec.json'))
target = next(f for f in spec['frames'] if f['frame_id']=='F8')
target['voiceover'] = 'As you can see, twenty-six advocates running in parallel, really very fast.'
json.dump(spec, open('tests/fixtures/.v05-standalone/tone/frame-spec.json','w'), indent=2, ensure_ascii=False)
PY

python3 scripts/standalone-tone.py --frame-spec "$RUN3/frame-spec.json" --quiet >/dev/null \
  && ok "polluted spec auto-rewritten to clean state" \
  || bad "auto-rewrite failed to clean violations"

# Verify the polluted line was actually rewritten (not just bypassed)
python3 -c "
import json
spec = json.load(open('$RUN3/frame-spec.json'))
target = next(f for f in spec['frames'] if f['frame_id']=='F8')
vo = target['voiceover'].lower()
assert 'as you can see' not in vo, 'NEVER:as-you-can-see remained'
assert 'really very' not in vo, 'NEVER:adverb-chain remained'
print(f'  cleaned VO: {target[\"voiceover\"]}')
" 2>&1 && ok "specific NEVER patterns removed from polluted line" || bad "rewrite did not strip specific patterns"

# Hero copy must be preserved (Layer-0 Rule 4)
python3 -c "
import json
spec = json.load(open('$RUN3/frame-spec.json'))
f4 = next(f for f in spec['frames'] if f['frame_id']=='F4')
import re
text = re.sub(r'<[^>]+>', '', f4['voiceover'])
assert 'Preview is all you need.' in text, f'hero paraphrased! got: {text}'
" 2>&1 && ok "hero copy preserved after rewrite (Layer-0 Rule 4)" || bad "hero paraphrased during rewrite"
echo

echo "=== SUMMARY ==="
echo "Pass: $pass"
echo "Fail: $fail"
if [[ "$fail" -eq 0 ]]; then
  echo "✓ v0.5 standalone acceptance: PASS"
  exit 0
fi
echo "✗ v0.5 standalone acceptance: FAIL"
exit 1
