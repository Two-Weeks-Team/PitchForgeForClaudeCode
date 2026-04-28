#!/usr/bin/env bash
# tests/e2e/v0.5-xss-escape.sh
#
# Verifies the allowlist HTML escape (introduced after the panel's
# C_XSS_ESCAPE vote) actually neutralizes a malicious brief.json:
#
#   - Raw <script> in any user-controlled field never reaches output
#   - </script> brake-out from JS string literals never reaches output
#   - Real inline event handlers (onerror=, onload=, ...) are absent
#   - The trusted markup inside arc templates (<b>, <i>) survives intact
#   - The new Layer-0 hook html-escape-validator.py passes on both
#     the malicious-input deck and a clean deck
#
# Companion fixture: tests/fixtures/xss-poc/brief.json

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
cd "$ROOT"

POC_BRIEF="tests/fixtures/xss-poc/brief.json"
GEN_DIR="tests/fixtures/xss-poc/.generated"
CLEAN_DIR="tests/fixtures/preview-forge-160s/.generated"

rm -rf "$GEN_DIR"

pass=0
fail=0
ok()  { echo "  ✓ $1"; pass=$((pass + 1)); }
bad() { echo "  ✗ $1" >&2; fail=$((fail + 1)); }

echo "=== e2e · v0.5 xss-escape (allowlist HTML escape) ==="
echo

echo "[1/4] Generate decks (malicious + clean)"
python3 scripts/generate-deck.py --brief "$POC_BRIEF" --output "$GEN_DIR/deck-cinematic.html" >/dev/null
ok "malicious-input deck generated"

python3 scripts/generate-deck.py --brief tests/fixtures/preview-forge-160s/brief.json \
  --output "$CLEAN_DIR/deck-cinematic.html" >/dev/null
ok "clean reference deck regenerated"
echo

echo "[2/4] Malicious payloads neutralized in HTML output"
RAW_SCRIPT=$(grep -c "<script>alert" "$GEN_DIR/deck-cinematic.html" || true)
[[ "$RAW_SCRIPT" -eq 0 ]] && ok "no raw <script>alert in output" \
                         || bad "$RAW_SCRIPT raw <script>alert occurrences"

BRAKE_OUT=$(grep -c "</script><img" "$GEN_DIR/deck-cinematic.html" || true)
[[ "$BRAKE_OUT" -eq 0 ]] && ok "no </script> JS brake-out" \
                        || bad "$BRAKE_OUT </script> brake-out occurrences"

DOUBLE_ESCAPE=$(grep -c "&amp;lt;" "$GEN_DIR/deck-cinematic.html" || true)
[[ "$DOUBLE_ESCAPE" -eq 0 ]] && ok "no double-escape" \
                            || bad "$DOUBLE_ESCAPE double-escape occurrences"

ESCAPED_SCRIPT=$(grep -c "&lt;script&gt;" "$GEN_DIR/deck-cinematic.html" || true)
[[ "$ESCAPED_SCRIPT" -ge 1 ]] && ok "user '<script>' rendered as escaped &lt;script&gt; (${ESCAPED_SCRIPT}×)" \
                             || bad "expected escaped <script> rendering, got $ESCAPED_SCRIPT"

# JS context: any literal `</script>` in an inline JS string would terminate the script tag
INLINE_BREAK=$(python3 -c "
import re
html = open('$GEN_DIR/deck-cinematic.html').read()
# Find the inline <script> block range
m = re.search(r'<script>(.*?)</script>', html, re.DOTALL)
if not m:
    print('NO_SCRIPT_BLOCK')
else:
    body = m.group(1)
    # Look for any unescaped </script> hidden inside JS string literals.
    # safe_json_for_script should have rewritten </ to <\\/.
    if '</script>' in body:
        print('LEAK')
    else:
        print('CLEAN')
")
[[ "$INLINE_BREAK" == "CLEAN" ]] && ok "inline <script> block has no </script> brake-out" \
                                || bad "inline <script> brake-out: $INLINE_BREAK"
echo

echo "[3/4] Trusted markup preserved on clean deck"
TRUSTED_B=$(grep -c '<b>' "$CLEAN_DIR/deck-cinematic.html" || true)
[[ "$TRUSTED_B" -ge 5 ]] && ok "trusted <b> markup preserved on clean deck (${TRUSTED_B}×)" \
                       || bad "trusted <b> markup count too low: $TRUSTED_B"

TRUSTED_I=$(grep -c '<i>' "$CLEAN_DIR/deck-cinematic.html" || true)
[[ "$TRUSTED_I" -ge 1 ]] && ok "trusted <i> markup preserved on clean deck (${TRUSTED_I}×)" \
                       || bad "trusted <i> markup count too low: $TRUSTED_I"

# The hero copy must STILL be byte-for-byte present after the escape pass
grep -qF "Preview is all you need." "$CLEAN_DIR/deck-cinematic.html" \
  && ok "hero copy verbatim on clean deck (Layer-0 Rule 4 holds through escape)" \
  || bad "hero copy lost under escape pass"
echo

echo "[4/4] html-escape-validator hook passes on both decks"
python3 plugins/pitch/hooks/html-escape-validator.py "$GEN_DIR/deck-cinematic.html" >/dev/null \
  && ok "hook passes on malicious-input deck (escapes neutralized payloads)" \
  || bad "hook flagged the malicious-input deck (escape leak)"

python3 plugins/pitch/hooks/html-escape-validator.py "$CLEAN_DIR/deck-cinematic.html" >/dev/null \
  && ok "hook passes on clean deck" \
  || bad "hook flagged the clean deck (false positive)"

# A negative-test: hand-craft a deck with a real inline event handler and
# confirm the hook FAILS it. This guards against the hook ever being
# silently neutered (e.g. by an over-escape that hides the test).
NEG_DIR="$GEN_DIR/.negative"
mkdir -p "$NEG_DIR"
cat > "$NEG_DIR/bad.html" <<'HTML'
<!DOCTYPE html>
<html><body>
<img src=x onerror="alert(1)">
<script>let x = 1;</script>
</body></html>
HTML
if python3 plugins/pitch/hooks/html-escape-validator.py "$NEG_DIR/bad.html" >/dev/null 2>&1; then
  bad "hook FAILED to flag a hand-crafted XSS sample (negative test)"
else
  ok "hook correctly flags hand-crafted XSS sample (negative test passes)"
fi
echo

echo "=== SUMMARY ==="
echo "Pass: $pass"
echo "Fail: $fail"
if [[ "$fail" -eq 0 ]]; then
  echo "✓ v0.5 xss-escape acceptance: PASS"
  exit 0
fi
echo "✗ v0.5 xss-escape acceptance: FAIL"
exit 1
