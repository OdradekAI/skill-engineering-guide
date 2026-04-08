#!/usr/bin/env bash
#
# test-skill-discovery.sh — verify all skills exist with valid SKILL.md and frontmatter
#
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_DIR="$REPO_ROOT/skills"

PASS=0
FAIL=0

pass() { PASS=$((PASS + 1)); echo "  PASS: $1"; }
fail() { FAIL=$((FAIL + 1)); echo "  FAIL: $1"; }

echo "=== Skill Discovery Tests ==="
echo ""

EXPECTED_SKILLS=(
  adapting-platforms
  auditing
  designing
  iterating-feedback
  managing-versions
  optimizing
  releasing
  scaffolding
  scanning-security
  using-bundles-forge
  writing-skill
)

echo "[1] Skills directory exists"
if [[ -d "$SKILLS_DIR" ]]; then
  pass "skills/ directory exists"
else
  fail "skills/ directory missing"
fi

echo ""
echo "[2] All expected skills present"
for skill in "${EXPECTED_SKILLS[@]}"; do
  if [[ -d "$SKILLS_DIR/$skill" ]]; then
    pass "$skill/ directory exists"
  else
    fail "$skill/ directory missing"
  fi
done

echo ""
echo "[3] Each skill has SKILL.md"
for skill in "${EXPECTED_SKILLS[@]}"; do
  if [[ -f "$SKILLS_DIR/$skill/SKILL.md" ]]; then
    pass "$skill/SKILL.md exists"
  else
    fail "$skill/SKILL.md missing"
  fi
done

echo ""
echo "[4] Each SKILL.md has valid frontmatter"
for skill in "${EXPECTED_SKILLS[@]}"; do
  local_file="$SKILLS_DIR/$skill/SKILL.md"
  [[ ! -f "$local_file" ]] && continue

  first_line=$(head -1 "$local_file")
  if [[ "$first_line" != "---" ]]; then
    fail "$skill/SKILL.md missing frontmatter opening ---"
    continue
  fi

  has_name=$(sed -n '/^---$/,/^---$/p' "$local_file" | grep -c '^name:' || true)
  has_desc=$(sed -n '/^---$/,/^---$/p' "$local_file" | grep -c '^description:' || true)

  if [[ "$has_name" -ge 1 ]]; then
    pass "$skill/SKILL.md has name field"
  else
    fail "$skill/SKILL.md missing name field"
  fi

  if [[ "$has_desc" -ge 1 ]]; then
    pass "$skill/SKILL.md has description field"
  else
    fail "$skill/SKILL.md missing description field"
  fi
done

echo ""
echo "[5] Skill directory names match frontmatter name"
for skill in "${EXPECTED_SKILLS[@]}"; do
  local_file="$SKILLS_DIR/$skill/SKILL.md"
  [[ ! -f "$local_file" ]] && continue

  fm_name=$(sed -n '/^---$/,/^---$/{ /^name:/{ s/^name: *//; s/^"//; s/"$//; p; } }' "$local_file" | head -1)
  if [[ "$fm_name" == "$skill" ]]; then
    pass "$skill name matches directory"
  else
    fail "$skill directory vs frontmatter name '$fm_name'"
  fi
done

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
