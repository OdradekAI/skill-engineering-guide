# Skill Audit Checklist

> Tables in this file are auto-generated from `audit-checks.json` by `generate_checklists.py`. Do not edit table rows directly.

Structured criteria for evaluating a single skill. Subset of the full project checklist (`plugin-checklist.md`) — 4 categories applicable at skill scope. Use this when running a skill audit on a standalone skill directory or SKILL.md file.

For full project audits (10 categories), see `plugin-checklist.md`. For workflow integration checks, see `workflow-checklist.md`.

## Scoring

Each category is scored 0-10. Scripts compute a **baseline score** using the formula:

```
baseline = max(0, 10 - (critical_count × 3 + warning_count × 1))
```

The auditor agent (or inline auditor) may adjust the baseline by **±2 points** to account for qualitative factors the formula cannot capture. Any adjustment must include a one-sentence rationale in the report.

**Interpretation:**
- **10** — All checks pass, exemplary implementation
- **7-9** — Minor issues only (info-level)
- **4-6** — Has warnings that should be addressed
- **1-3** — Critical issues that prevent correct operation
- **0** — Category entirely missing

### Category Weights

| Weight Level | Numeric Value | Categories |
|-------------|--------------|------------|
| High | 3 | Structure, Security |
| Medium | 2 | Skill Quality, Cross-References |

**Overall score** = `sum(score_i × weight_i) / sum(weight_i)` (total weight = 10).

---

## Category 1: Structure (Weight: High)

<!-- BEGIN:skill/structure -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| S2 | Warning | At least one platform manifest directory present | `audit_plugin.py` |
| S9 | Info | Skill directory names match `name` field in SKILL.md frontmatter | `audit_skill.py` |
<!-- END:skill/structure -->

---

## Category 2: Skill Quality (Weight: Medium)

Run all quality checks on the target SKILL.md.

<!-- BEGIN:skill/quality -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| Q1 | Critical | YAML frontmatter present (between `---` delimiters) | `audit_skill.py` |
| Q2 | Critical | `name` field exists in frontmatter | `audit_skill.py` |
| Q3 | Critical | `description` field exists in frontmatter | `audit_skill.py` |
| Q4 | Warning | `name` uses only letters, numbers, hyphens | `audit_skill.py` |
| Q5 | Warning | `description` starts with "Use when..." | `audit_skill.py` |
| Q6 | Warning | `description` describes triggering conditions, not workflow summary | `audit_skill.py` |
| Q7 | Warning | `description` is under 250 characters (truncated in skill listing beyond this) | `audit_skill.py` |
| Q8 | Warning | Frontmatter total under 1024 characters | `audit_skill.py` |
| Q9 | Warning | SKILL.md body under 500 lines | `audit_skill.py` |
| Q10 | Info | Skill has Overview section | `audit_skill.py` |
| Q11 | Info | Skill has Common Mistakes section | `audit_skill.py` |
| Q12 | Info | Heavy reference content (100+ lines) extracted to supporting files | `audit_skill.py` |
| Q13 | Warning/Info | Token budget: bootstrap skill body ≤ 200 lines (warning); regular skill reports estimated token count when high (info) | `audit_skill.py` |
| Q14 | Warning | `allowed-tools` frontmatter references scripts/paths that actually exist | `audit_skill.py` |
| Q15 | Info | Conditional blocks (`If ... unavailable` etc.) over 30 lines should be in `references/` | `audit_skill.py` |
| Q16 | Warning | `allowed-tools` declares external CLI tools (not git/python/node/npm/npx/bash or bin/scripts paths) but SKILL.md body has no `## Prerequisites` section | `audit_skill.py` |
<!-- END:skill/quality -->

**Description anti-patterns (Q6):**
- Contains step-by-step workflow → agents shortcut to description
- Uses phrases like "first... then... finally..."
- Describes what the skill does instead of when to use it

---

## Category 3: Cross-References (Weight: Medium)

Static link resolution within the skill content.

<!-- BEGIN:skill/cross_references -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| X1 | Warning | All `<project>:<skill-name>` references resolve to existing skills | `audit_skill.py` |
| X2 | Warning | No broken relative-path references to supporting files | `audit_skill.py` |
| X3 | Warning | Text references to subdirectories (`references/`, `templates/`, etc.) match actual skill directory contents | `audit_skill.py` |
| X4 | Info | No orphan files in `references/` — every `.md` and `.json` file is referenced by `SKILL.md` or a sibling reference file | `audit_skill.py` |
<!-- END:skill/cross_references -->

**How to check:**
1. Extract all `<project>:<name>` patterns from the SKILL.md
2. Verify each `<name>` matches a directory under `skills/`
3. Extract all relative file references and verify they exist
4. Scan for prose references to subdirectories and verify they exist
5. Run `bundles-forge audit-skill <skill-directory>` — results include X1-X3 findings

---

## Category 4: Security (Weight: High)

Security checks scoped to the skill's content and references. Uses IDs from `security-checklist.md`.

<!-- BEGIN:skill/security -->
| Check | Risk | Criteria | Automation |
|-------|------|----------|------------|
| SC1 | Critical | Instructions to read `.env`, `.ssh/`, `credentials`, `secrets`, `tokens`, `api_key` files | `audit_security.py` (suspicious) |
| SC9 | Critical | Phrases like "ignore previous instructions", "override safety", "disable verification" | `audit_security.py` |
| SC13 | Critical | Unicode homoglyphs, zero-width characters, right-to-left override characters | `audit_security.py` |
| SC15 | Info | Excessively long line (>500 chars) — may indicate obfuscated or machine-generated content | `audit_security.py` |
| AG1 | Critical | Instructions to "ignore", "override", or "bypass" safety guidelines or user instructions | `audit_security.py` (suspicious) |
| AG6 | Info | Missing scope constraints (agent prompt doesn't limit what files/actions are in scope) | `agent-only` |
<!-- END:skill/security -->

**Quick check:** Grep for high-risk patterns in the skill directory:
```
curl|wget|nc |eval\(|child_process|\.env|api_key|secret|ignore safety|override|bypass
```

---

## Audit Report Template

After running all checks, compile findings using `references/skill-report-template.md` — three-layer structure (Decision Brief, Findings by Category, Skill Profile) with decision vocabulary for self-check and third-party evaluation contexts.
