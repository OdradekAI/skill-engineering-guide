# Skill Audit Checklist

Structured criteria for evaluating a single skill. Subset of the full project checklist (`audit-checklist.md`) — 4 categories applicable at skill scope. Use this when running a skill audit on a standalone skill directory or SKILL.md file.

For full project audits (10 categories), see `audit-checklist.md`. For workflow integration checks (W1-W12), see `workflow-checklist.md`.

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

| Check | Severity | Criteria |
|-------|----------|----------|
| S2 | Critical | Skill has its own directory under `skills/` |
| S3 | Critical | Skill directory contains a `SKILL.md` |
| S9 | Info | Skill directory name matches `name` field in SKILL.md frontmatter |

---

## Category 2: Skill Quality (Weight: Medium)

Run all quality checks on the target SKILL.md.

| Check | Severity | Criteria |
|-------|----------|----------|
| Q1 | Critical | YAML frontmatter present (between `---` delimiters) |
| Q2 | Critical | `name` field exists in frontmatter |
| Q3 | Critical | `description` field exists in frontmatter |
| Q4 | Warning | `name` uses only letters, numbers, hyphens |
| Q5 | Warning | `description` starts with "Use when..." |
| Q6 | Warning | `description` describes triggering conditions, not workflow summary |
| Q7 | Warning | `description` is under 250 characters |
| Q8 | Warning | Frontmatter total under 1024 characters |
| Q9 | Warning | SKILL.md body under 500 lines |
| Q10 | Info | Skill has Overview section |
| Q11 | Info | Skill has Common Mistakes section |
| Q12 | Info | Heavy reference content (100+ lines) extracted to supporting files |
| Q13 | Warning/Info | Token budget: bootstrap skill body ≤ 200 lines (warning); regular skill reports estimated token count when high (info) |
| Q14 | Warning | `allowed-tools` frontmatter references scripts/paths that actually exist |
| Q15 | Info | Conditional blocks (`If ... unavailable` etc.) over 30 lines should be in `references/` |
| Q16 | Info | Non-bootstrap skills have an `## Inputs` section |
| Q17 | Info | Non-bootstrap skills have an `## Outputs` section |

**Description anti-patterns (Q6):**
- Contains step-by-step workflow → agents shortcut to description
- Uses phrases like "first... then... finally..."
- Describes what the skill does instead of when to use it

---

## Category 3: Cross-References (Weight: Medium)

Static link resolution within the skill content.

| Check | Severity | Criteria |
|-------|----------|----------|
| X1 | Warning | All `<project>:<skill-name>` references resolve to existing skills |
| X2 | Warning | No broken relative-path references to supporting files |
| X3 | Warning | Text references to subdirectories (`references/`, `templates/`, etc.) match actual skill directory contents |

**How to check:**
1. Extract all `<project>:<name>` patterns from the SKILL.md
2. Verify each `<name>` matches a directory under `skills/`
3. Extract all relative file references and verify they exist
4. Scan for prose references to subdirectories and verify they exist
5. Run `python scripts/audit_skill.py <skill-directory>` — results include X1-X3 findings

---

## Category 4: Security (Weight: High)

Security checks scoped to the skill's content and references.

| Check | Severity | Criteria |
|-------|----------|----------|
| SEC1 | Critical | No SKILL.md instructs agents to read sensitive files (`.env`, `.ssh/`, credentials) |
| SEC5 | Critical | No agent prompt contains safety override instructions ("ignore safety", "bypass") |
| SEC8 | Warning | No SKILL.md uses encoding tricks (unicode homoglyphs, zero-width chars) |
| SEC9 | Info | Agent prompts include explicit scope constraints |
| SEC10 | Info | Scripts use error handling (`set -euo pipefail` or equivalent) |

**Quick check:** Grep for high-risk patterns in the skill directory:
```
curl|wget|nc |eval\(|child_process|\.env|api_key|secret|ignore safety|override|bypass
```

---

## Audit Report Template

After running all checks, compile findings using `references/skill-report-template.md` — three-layer structure (Decision Brief, Findings by Category, Skill Profile) with decision vocabulary for self-check and third-party evaluation contexts.
