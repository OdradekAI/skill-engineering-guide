# Auditing Guide

Comprehensive guide to auditing bundle-plugins with Bundles Forge. Covers all four audit scopes, their tooling, and recommended workflows.

## Overview

Bundles Forge provides four audit scopes, each targeting a different level of granularity:

| Scope | When to Use | Categories | Script |
|-------|------------|-----------|--------|
| **Full Project** | Pre-release, major changes, initial review | 10 categories, 60+ checks | `audit_project.py` |
| **Single Skill** | Reviewing one skill, third-party skill evaluation | 4 categories (Structure, Quality, Cross-Refs, Security) | `audit_skill.py` |
| **Workflow** | After adding/removing skills, chain integration check | 3 layers (Static, Semantic, Behavioral), W1-W12 | `audit_workflow.py` |
| **Security-Only** | Quick safety scan, pre-install check | 5 attack surfaces | `scan_security.py` |

All scopes share the same scoring formula, severity levels, and report conventions. The agent auto-detects scope from the target path — or you can invoke scripts directly.

---

## Common Concepts

### Severity Levels

| Level | Meaning |
|-------|---------|
| **Critical** | Skill/project will not work correctly, or contains active security threats |
| **Warning** | Works but has quality issues or suspicious patterns needing review |
| **Info** | Improvement opportunities |

### Scoring Formula

Each category is scored 0-10:

```
baseline = max(0, 10 - (critical_count × 3 + warning_count × 1))
```

The auditor agent may adjust the baseline by **±2 points** with rationale. Overall score = weighted average across categories.

### Go/No-Go Logic

| Condition | Recommendation |
|-----------|---------------|
| Any Critical finding | **NO-GO** |
| Warnings only | **CONDITIONAL GO** |
| All checks pass | **GO** |

### Report Locations

All audit reports are saved to `.bundles-forge/` with timestamped filenames:
- Full audit: `<project>-<version>-audit.YYYY-MM-DD.md`
- Skill audit: `<skill-name>-<version>-skill-audit.YYYY-MM-DD.md`
- Workflow audit: `<project>-<version>-workflow-audit.YYYY-MM-DD.md`
- Security scan: `<project>-<version>-security-scan.YYYY-MM-DD.md`

### Exit Codes (All Scripts)

| Code | Meaning |
|------|---------|
| `0` | Pass — no issues |
| `1` | Warnings found |
| `2` | Critical findings |

All scripts accept `--json` for machine-readable output.

---

## Full Project Audit

**When to use:** Pre-release quality gate, reviewing after significant changes, evaluating a third-party bundle-plugin before installation.

### Via Agent

```
/bundles-audit
```

The agent detects the project root (has `skills/` + `package.json`) and runs all 10 categories. If subagents are available, it dispatches the `auditor` agent for automated assessment.

### Via Script

```bash
python scripts/audit_project.py <project-root>        # markdown report
python scripts/audit_project.py --json <project-root>  # JSON output
```

`audit_project.py` orchestrates three sub-scripts:
- `lint_skills.py` — skill quality linting (Q1-Q17, S9, X1-X3, G1-G5)
- `scan_security.py` — security pattern scanning (5 attack surfaces)
- `audit_workflow.py` — workflow integration analysis (W1-W12)

Then adds its own checks for structure, manifests, version sync, hooks, testing, and documentation.

### 10 Categories

| # | Category | Weight | Key Checks |
|---|----------|--------|------------|
| 1 | Structure | High (3) | `skills/` exists, directory layout, bootstrap skill |
| 2 | Platform Manifests | Medium (2) | Manifest JSON valid, paths resolve |
| 3 | Version Sync | High (3) | `.version-bump.json` completeness, no drift |
| 4 | Skill Quality | Medium (2) | Frontmatter, descriptions, token budget (Q1-Q17) |
| 5 | Cross-References | Medium (2) | `project:skill` resolution, relative paths (X1-X3) |
| 6 | Workflow | High (3) | Graph topology, integration symmetry, artifacts (W1-W12) |
| 7 | Hooks | Medium (2) | Bootstrap injection, platform detection |
| 8 | Testing | Medium (2) | Test directory, prompts, A/B eval results |
| 9 | Documentation | Low (1) | README, install docs, CHANGELOG |
| 10 | Security | High (3) | 5 attack surfaces — skill content, hooks, plugins, agents, scripts |

Total weight = 23. Overall score = `sum(score_i × weight_i) / 23`.

### Report Template

Full project audits use `skills/auditing/references/report-template.md` — six-layer structure: Decision Brief → Risk Matrix → Findings by Category → Methodology → Appendix.

### Checklists

- **Project checklist:** `skills/auditing/references/audit-checklist.md` (Categories 1-5, 7-10)
- **Workflow checklist:** `skills/auditing/references/workflow-checklist.md` (Category 6: W1-W12)
- **Security checklist:** `skills/auditing/references/security-checklist.md` (Category 10 detail)

---

## Single Skill Audit

**When to use:** Reviewing a single skill before integration, evaluating a third-party skill for security, quick quality check on a skill you're authoring.

### Via Agent

```
/bundles-audit skills/authoring
```

The agent detects a single skill directory (contains `SKILL.md`, no `skills/` subdirectory) and runs the 4 applicable categories.

### Via Script

```bash
python scripts/audit_skill.py <skill-directory>           # markdown report
python scripts/audit_skill.py <skill-directory>/SKILL.md   # also works
python scripts/audit_skill.py --json <skill-directory>     # JSON output
```

`audit_skill.py` orchestrates:
- `lint_skills.lint_skill()` — quality, structure, and cross-reference checks
- `scan_security` — security scanning scoped to the skill directory

You can also run the sub-scripts individually:

```bash
python scripts/lint_skills.py <skill-directory>     # quality + cross-refs
python scripts/scan_security.py <skill-directory>   # security scan
```

### 4 Categories

| # | Category | Weight | Key Checks |
|---|----------|--------|------------|
| 1 | Structure | High (3) | S2, S3, S9 — own directory, SKILL.md exists, name matches |
| 2 | Skill Quality | Medium (2) | Q1-Q17 — frontmatter, descriptions, tokens, sections |
| 3 | Cross-References | Medium (2) | X1-X3 — `project:skill` resolution, relative paths |
| 4 | Security | High (3) | SEC1, SEC5, SEC8-SEC10 — sensitive files, overrides, encoding |

Total weight = 10. Categories not applicable at skill scope: Platform Manifests, Version Sync, Hooks, Testing, Documentation.

### Third-Party Skill Scanning

When evaluating skills from external sources:

1. **Download without executing** — clone/download without running hooks or scripts
2. **Run skill audit** — `python scripts/audit_skill.py <downloaded-skill-dir>`
3. **Review critical findings** with the user before installation
4. **Never auto-install** a skill with unresolved critical security findings

### Report Template

Single skill audits use `skills/auditing/references/skill-report-template.md` — three-layer structure: Decision Brief → Findings by Category → Skill Profile. Includes two decision vocabularies:
- **Self-check:** PASS / PASS WITH NOTES / FAIL
- **Third-party evaluation:** SAFE TO INSTALL / REVIEW REQUIRED / DO NOT INSTALL

### Checklist

- **Skill checklist:** `skills/auditing/references/skill-checklist.md`

---

## Workflow Audit

**When to use:** After adding/removing skills from a workflow chain, modifying Integration sections or Inputs/Outputs, validating third-party skill integration, or when the full audit's Workflow category shows warnings.

### Via Agent

Request explicitly:
- "audit the workflow"
- "check workflow integration"
- "run workflow audit with focus on skill-a"

Or the agent suggests it when the Full audit's Workflow category shows findings.

### Via Script

```bash
python scripts/audit_workflow.py <project-root>                          # full workflow audit
python scripts/audit_workflow.py --focus-skills skill-a,skill-b <root>   # focused mode
python scripts/audit_workflow.py --json <project-root>                   # JSON output
```

### 3 Layers (W1-W12)

| Layer | Weight | Checks | Automation |
|-------|--------|--------|------------|
| Static Structure | High (3) | W1-W5: cycles, reachability, Inputs/Outputs presence, artifact ID matching | `lint_skills.py` graph analysis |
| Semantic Interface | Medium (2) | W6-W10: Integration completeness, artifact clarity, Calls/Called by symmetry | `audit_workflow.py` + agent review |
| Behavioral Verification | Low (1) | W11-W12: chain A/B eval, trigger/exit in context | `evaluator` agent dispatch |

Total weight = 6. Behavioral layer is scored 10 (perfect) when skipped; the report notes the skip.

### Focus Mode (Incremental Auditing)

When `--focus-skills skill-a,skill-b` is specified:

1. **All checks run on the full graph** — no analysis is skipped
2. **Findings are partitioned** into Focus Area (involving specified skills) and Context (all others)
3. **Report highlights** the focus skills while preserving full-graph visibility

This enables incremental validation after adding new skills without missing cascade effects.

**Typical workflow for adding third-party skills:**

```
1. Run blueprinting Scenario D (integration planning)
2. Add skills to the project
3. Run: python scripts/audit_workflow.py --focus-skills new-skill-a,new-skill-b .
4. Fix focus area findings
5. Review context findings for unexpected impacts
```

### Report Template

Workflow audits use `skills/auditing/references/workflow-report-template.md` — three-layer structure: Decision Brief → Findings by Layer → Skill Integration Map.

### Checklist

- **Workflow checklist:** `skills/auditing/references/workflow-checklist.md`

---

## Security-Only Scan

**When to use:** Quick safety check before installing a third-party bundle-plugin, pre-commit verification, or when you only care about security risks.

### Via Agent

```
/bundles-scan
```

Maps to the `bundles-forge:auditing` skill in security-only mode — runs only Category 10 (Security) across all 5 attack surfaces.

### Via Script

```bash
python scripts/scan_security.py <project-root>           # project-wide scan
python scripts/scan_security.py <skill-directory>         # single skill scan
python scripts/scan_security.py --json <project-root>     # JSON output
```

### 5 Attack Surfaces

| Surface | Risk Level | Examples |
|---------|-----------|---------|
| SKILL.md content | High | Sensitive file access, destructive commands, safety overrides, encoding tricks |
| Hook scripts | High | Network calls, env-var leakage, system config modification |
| OpenCode plugins | High | Dynamic code execution, network access, message manipulation |
| Agent prompts | Medium | Privilege escalation, scope expansion, safety overrides |
| Bundled scripts | Medium | Network calls, system modifications, unsanitized inputs |

### Checklist

- **Security checklist:** `skills/auditing/references/security-checklist.md` — full pattern list for all 5 surfaces

---

## After the Audit

| Report Source | Finding Level | Action |
|--------------|--------------|--------|
| Full project (`audit-report`) | Critical/Warning | `bundles-forge:optimizing` — Project Optimization (all 6 targets) |
| Single skill (`skill-report`) | Critical/Warning | `bundles-forge:optimizing` — Skill Optimization (4 targets + feedback) |
| Workflow (`workflow-report`) | W1-W12 findings | `bundles-forge:optimizing` Target 4 (Workflow Chain Integrity) |
| Any scope | Info | Note for future consideration |
| Any scope | All clear | `bundles-forge:releasing` for pre-release pipeline |

**Re-audit rule:** After fixing critical/warning issues, run one re-audit to verify. Do not loop more than once — if the re-audit still has issues, present them to the user for manual decision.

---

## CI Integration

### Script Composition

```bash
# Full pipeline: lint → security → full audit
python scripts/lint_skills.py --json . > lint.json
python scripts/scan_security.py --json . > security.json
python scripts/audit_project.py --json . > audit.json

# Single skill in CI
python scripts/audit_skill.py --json skills/my-skill > skill-audit.json

# Workflow check after PR that modifies skills
python scripts/audit_workflow.py --json --focus-skills changed-skill . > workflow.json
```

### Exit Code Usage

```bash
python scripts/audit_project.py . || echo "Audit found issues (exit $?)"

# Fail CI only on critical
python scripts/audit_project.py . ; [ $? -ne 2 ] || exit 1
```

### JSON Output

All scripts support `--json`. JSON output includes:
- `status` — PASS / WARN / FAIL
- `overall_score` — weighted average (0-10)
- `summary` — `{critical: N, warning: N}`
- `categories` / `layers` — per-category/layer breakdown with findings and scores
