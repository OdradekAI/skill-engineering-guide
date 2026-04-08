#!/usr/bin/env bash
#
# test-bootstrap-injection.sh — verify session-start hook produces valid JSON
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
HOOK="$REPO_ROOT/hooks/session-start"

PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL: $1"; }

echo "=== Bootstrap Injection Tests ==="
echo ""

echo "[1] Hook script exists"
if [[ -f "$HOOK" ]]; then
  pass "hooks/session-start exists"
else
  fail "hooks/session-start missing"
  echo "=== Results: $PASS passed, $FAIL failed ==="
  exit 1
fi

echo ""
echo "[2] Hook reads correct bootstrap skill"
if grep -q "using-bundles-forge/SKILL.md" "$HOOK"; then
  pass "references using-bundles-forge/SKILL.md"
else
  fail "does not reference using-bundles-forge/SKILL.md"
fi

echo ""
echo "[3] Hook output is valid JSON (Claude Code mode)"
claude_output=$(CLAUDE_PLUGIN_ROOT="$REPO_ROOT" bash "$HOOK" 2>/dev/null) || true
if echo "$claude_output" | python3 -m json.tool > /dev/null 2>&1; then
  pass "Claude Code hook output is valid JSON"
else
  if echo "$claude_output" | python -m json.tool > /dev/null 2>&1; then
    pass "Claude Code hook output is valid JSON"
  else
    fail "Claude Code hook output is not valid JSON"
  fi
fi

echo ""
echo "[4] Hook output is valid JSON (Cursor mode)"
cursor_output=$(CURSOR_PLUGIN_ROOT="$REPO_ROOT" bash "$HOOK" 2>/dev/null) || true
if echo "$cursor_output" | python3 -m json.tool > /dev/null 2>&1; then
  pass "Cursor hook output is valid JSON"
else
  if echo "$cursor_output" | python -m json.tool > /dev/null 2>&1; then
    pass "Cursor hook output is valid JSON"
  else
    fail "Cursor hook output is not valid JSON"
  fi
fi

echo ""
echo "[5] Hook output contains bootstrap content"
if echo "$claude_output" | grep -q "EXTREMELY_IMPORTANT"; then
  pass "output contains EXTREMELY_IMPORTANT marker"
else
  fail "output missing EXTREMELY_IMPORTANT marker"
fi

if echo "$claude_output" | grep -q "bundles-forge"; then
  pass "output contains bundles-forge reference"
else
  fail "output missing bundles-forge reference"
fi

echo ""
echo "[6] Hook detects platforms"
if grep -q 'CURSOR_PLUGIN_ROOT' "$HOOK"; then
  pass "detects Cursor platform"
else
  fail "missing Cursor platform detection"
fi

if grep -q 'CLAUDE_PLUGIN_ROOT' "$HOOK"; then
  pass "detects Claude Code platform"
else
  fail "missing Claude Code platform detection"
fi

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
