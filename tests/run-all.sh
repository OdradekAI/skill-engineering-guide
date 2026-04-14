#!/usr/bin/env bash
#
# run-all.sh — run all Python test suites and report summary
#
set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TOTAL_PASS=0
TOTAL_FAIL=0

if command -v python3 &>/dev/null || command -v python &>/dev/null; then
  PYTHON_CMD=$(command -v python3 || command -v python)

  for py_test in test_scripts.py test_integration.py; do
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "Running: $py_test (Python)"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    if "$PYTHON_CMD" "$SCRIPT_DIR/$py_test" -v; then
      TOTAL_PASS=$((TOTAL_PASS + 1))
    else
      TOTAL_FAIL=$((TOTAL_FAIL + 1))
    fi
  done
else
  echo ""
  echo "[WARN] Python not found — skipping Python tests"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Overall: $TOTAL_PASS test suites passed, $TOTAL_FAIL failed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

exit $TOTAL_FAIL
