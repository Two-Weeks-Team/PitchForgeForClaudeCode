#!/usr/bin/env bash
# PitchForge — plugin verification script.
# Usage: bash scripts/verify-plugin.sh
#
# Checks (v0.1.0 baseline; expand as MVP lands):
#   1. Manifests (marketplace.json + plugin.json)
#   2. Methodology docs (8 expected: 00-07)
#   3. Memory seeds (CLAUDE / PROGRESS / LESSONS / HERO_CATALOG)
#   4. Reference example (preview-forge-160s/deck.html)
#   5. Schemas validate as JSON (4 target by v0.1.0)
#   6. Agents (13 target — 5-tier)
#   7. Commands (15 target = 14 listed + help)
#   8. Hooks (4 target — Layer-0)
#   9. Templates (deck-shell + 5 frame shapes + 1 arc + 1 palette)

set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"
PLUGIN_DIR="$ROOT/plugins/pitch"

echo "=== PitchForge plugin verification ==="
echo "Root: $ROOT"
echo

pass=0
fail=0
ok()  { echo "  ✓ $1"; pass=$((pass + 1)); }
bad() { echo "  ✗ $1" >&2; fail=$((fail + 1)); }

echo "[1/5] Manifests"
python3 -c "
import json
m = json.load(open('.claude-plugin/marketplace.json'))
assert m['plugins'][0]['name'] == 'pitch', 'plugin name must be pitch'
print(m['plugins'][0]['version'])
" >/tmp/pitch_version 2>/dev/null \
  && ok "marketplace.json: plugin 'pitch' v$(cat /tmp/pitch_version)" \
  || bad "marketplace.json invalid"

python3 -c "
import json, re
d = json.load(open('$PLUGIN_DIR/.claude-plugin/plugin.json'))
assert d['name']=='pitch', 'name must be pitch'
assert re.match(r'^\d+\.\d+\.\d+', d['version']), 'version must be SemVer'
m = json.load(open('.claude-plugin/marketplace.json'))
p = next(p for p in m['plugins'] if p['name']=='pitch')
assert p['version'] == d['version'], f'version mismatch'
" 2>/dev/null \
  && ok "plugin.json: name=pitch + version parity with marketplace" \
  || bad "plugin.json invalid"
echo

echo "[2/5] Methodology docs (8 target)"
methodology_count=$(find "$PLUGIN_DIR/methodology" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
[[ "$methodology_count" -eq 8 ]] && ok "methodology docs: 8" || bad "methodology docs: $methodology_count (expected 8)"
for n in 00 01 02 03 04 05 06 07; do
  found=$(find "$PLUGIN_DIR/methodology" -name "${n}-*.md" 2>/dev/null | wc -l | tr -d ' ')
  [[ "$found" -ge 1 ]] && ok "methodology/${n}-*.md present" || bad "methodology/${n}-*.md missing"
done
echo

echo "[3/5] Memory seeds"
for f in CLAUDE.md PROGRESS.md LESSONS.md HERO_CATALOG.md; do
  [[ -f "$PLUGIN_DIR/memory/$f" ]] && ok "memory/$f" || bad "memory/$f missing"
done
echo

echo "[4/5] Reference example"
[[ -f "$PLUGIN_DIR/examples/preview-forge-160s/deck.html" ]] \
  && ok "examples/preview-forge-160s/deck.html present ($(wc -l < "$PLUGIN_DIR/examples/preview-forge-160s/deck.html") lines)" \
  || bad "examples/preview-forge-160s/deck.html missing"
echo

echo "[5/9] Schemas"
schema_count=$(find "$PLUGIN_DIR/schemas" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
[[ "$schema_count" -eq 4 ]] && ok "schemas: 4 (target met)" || bad "schemas: $schema_count (target 4)"
for f in "$PLUGIN_DIR"/schemas/*.json; do
  [[ -f "$f" ]] || continue
  python3 -m json.tool "$f" >/dev/null 2>&1 \
    && ok "$(basename "$f"): valid JSON" \
    || bad "$(basename "$f"): invalid JSON"
done
echo

echo "[6/9] Agents (13 target)"
agent_count=$(find "$PLUGIN_DIR/agents" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
[[ "$agent_count" -eq 13 ]] && ok "agents: 13 (target met)" || bad "agents: $agent_count (target 13)"
echo

echo "[7/9] Commands (15 target)"
command_count=$(find "$PLUGIN_DIR/commands" -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
[[ "$command_count" -eq 15 ]] && ok "commands: 15 (target met)" || bad "commands: $command_count (target 15)"
echo

echo "[8/9] Hooks (4 target)"
hook_count=$(find "$PLUGIN_DIR/hooks" -name "*.py" 2>/dev/null | wc -l | tr -d ' ')
[[ "$hook_count" -eq 4 ]] && ok "hooks: 4 (target met)" || bad "hooks: $hook_count (target 4)"
echo

echo "[9/9] Templates (deck-shell + 5 frame shapes + 1 arc + 1 palette)"
[[ -f "$PLUGIN_DIR/templates/deck-shell.html" ]] && ok "deck-shell.html present" || bad "deck-shell.html missing"
shape_count=$(find "$PLUGIN_DIR/templates/frame-shapes" -name "*.html" 2>/dev/null | wc -l | tr -d ' ')
[[ "$shape_count" -ge 5 ]] && ok "frame-shapes: $shape_count (≥ 5)" || bad "frame-shapes: $shape_count (< 5)"
arc_count=$(find "$PLUGIN_DIR/templates/narrative-arcs" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
[[ "$arc_count" -ge 1 ]] && ok "narrative-arcs: $arc_count" || bad "narrative-arcs: $arc_count (< 1)"
palette_count=$(find "$PLUGIN_DIR/templates/color-palettes" -name "*.json" 2>/dev/null | wc -l | tr -d ' ')
[[ "$palette_count" -ge 1 ]] && ok "color-palettes: $palette_count" || bad "color-palettes: $palette_count (< 1)"
for f in "$PLUGIN_DIR"/templates/narrative-arcs/*.json "$PLUGIN_DIR"/templates/color-palettes/*.json; do
  [[ -f "$f" ]] || continue
  python3 -m json.tool "$f" >/dev/null 2>&1 \
    && ok "$(basename "$f"): valid JSON" \
    || bad "$(basename "$f"): invalid JSON"
done
echo

echo "=== SUMMARY ==="
echo "Pass: $pass"
echo "Fail: $fail"
echo
if [[ "$fail" -eq 0 ]]; then
  echo "✓ All verification checks passed."
  exit 0
else
  echo "✗ $fail check(s) failed. Review above."
  exit 1
fi
