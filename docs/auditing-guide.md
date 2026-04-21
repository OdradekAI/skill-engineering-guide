# Auditing Guide

[中文](auditing-guide.zh.md)

Comprehensive guide to auditing bundle-plugins with Bundles Forge. Covers all four audit scopes, their tooling, and recommended workflows.

## Overview

Bundles Forge provides four audit scopes, each targeting a different level of granularity:

| Scope | When to Use | Categories | CLI Command |
|-------|------------|-----------|--------|
| **Full Project** | Pre-release, major changes, initial review | 10 categories, 60+ checks | `bundles-forge audit-plugin` |
| **Single Skill** | Reviewing one skill, third-party skill evaluation | 4 categories (Structure, Quality, Cross-Refs, Security) | `bundles-forge audit-skill` |
| **Workflow** | After adding/removing skills, chain integration check | 3 layers (Static, Semantic, Behavioral), W1-W11 | `bundles-forge audit-workflow` |
| **Security-Only** | Quick pattern-based safety check, pre-install scan | 7 file categories, known dangerous patterns | `bundles-forge audit-security` |

All scopes share the same scoring formula, severity levels, and report conventions. The agent auto-detects scope from the target path — or you can invoke CLI commands directly.

> **Canonical source:** Execution details (scoring formula, report format, qualitative assessment criteria) are defined in `agents/auditor.md` — the single source of truth for the audit protocol. This guide summarizes those details for reference.

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
baseline = max(0, 10 - (critical_count × 3 + capped_warning_penalty))
```

Where `capped_warning_penalty = sum(min(count_per_check_id, 3))` — each distinct check ID contributes at most 3 points of penalty, preventing a single noisy check from overwhelming the score.

The auditor agent may adjust the baseline by **±2 points** with rationale. Overall score = weighted average across categories.

### Go/No-Go Logic

| Condition | Recommendation |
|-----------|---------------|
| Any Critical finding | **NO-GO** |
| Warnings only | **CONDITIONAL GO** |
| All checks pass | **GO** |

### Report Locations

All audit reports are saved to `.bundles-forge/audits/` in the workspace root, with timestamped filenames:
- Full audit: `<project>-v<version>-audit.YYYY-MM-DD[.<lang>].md`
- Skill audit: `<skill-name>-v<version>-skill-audit.YYYY-MM-DD[.<lang>].md`
- Workflow audit: `<project>-v<version>-workflow-audit.YYYY-MM-DD[.<lang>].md`
- Security scan: `<project>-v<version>-security-scan.YYYY-MM-DD[.<lang>].md`

Other artifact types use separate subdirectories: `.bundles-forge/evals/` (A/B and chain evaluations), `.bundles-forge/blueprints/` (design documents and inspection reports), `.bundles-forge/repos/` (cloned/extracted external targets).

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
bundles-forge:auditing
```

The agent detects the project root (has `skills/` directory) and runs all 10 categories. If subagents are available, it dispatches the `auditor` agent for automated assessment.

### Via Script

```bash
bundles-forge audit-plugin <target-dir>        # markdown report
bundles-forge audit-plugin --json <target-dir>  # JSON output
```

`audit_plugin.py` orchestrates four sub-scripts:
- `audit_skill.py` — skill quality linting (Q1-Q15, S9, X1-X4)
- `audit_security.py` — pattern-based security smell detection (7 file categories)
- `audit_workflow.py` — workflow integration analysis (W1-W9)
- `audit_docs.py` — documentation consistency (D1-D9)

Then adds its own checks for structure, manifests, version sync, hooks, and testing.

### 10 Categories

| # | Category | Weight | Key Checks |
|---|----------|--------|------------|
| 1 | Structure | High (3) | `skills/` exists, directory layout, bootstrap skill |
| 2 | Platform Manifests | Medium (2) | Manifest JSON valid, paths resolve |
| 3 | Version Sync | High (3) | `.version-bump.json` completeness, no drift |
| 4 | Skill Quality | Medium (2) | Frontmatter, descriptions, token budget (Q1-Q15) |
| 5 | Cross-References | Medium (2) | `project:skill` resolution, relative paths, orphan detection (X1-X4) |
| 6 | Workflow | High (3) | Graph topology, integration symmetry, artifacts (W1-W11) |
| 7 | Hooks | Medium (2) | Bootstrap injection, platform detection (functional correctness only) |
| 8 | Testing | Medium (2) | Test directory, prompts, A/B eval results |
| 9 | Documentation | Low (1) | Documentation consistency via `bundles-forge audit-docs` (D1-D9) |
| 10 | Security | High (3) | 7 attack surfaces — SC/HK/OC/AG/BS/MC/PC IDs from `security-checklist.md` |

Total weight = 23. Overall score = `sum(score_i × weight_i) / 23`.

### Report Template

Full project audits use `skills/auditing/references/plugin-report-template.md` — six-layer structure: Decision Brief → Risk Matrix → Findings by Category → Methodology → Appendix. For annotated report examples, see `skills/auditing/references/report-examples.md`.

### Checklists

- **Project checklist:** `skills/auditing/references/plugin-checklist.md` (Categories 1-5, 7-10)
- **Workflow checklist:** `skills/auditing/references/workflow-checklist.md` (Category 6: W1-W11)
- **Security checklist:** `skills/auditing/references/security-checklist.md` (Category 10 detail)

---

## Single Skill Audit

**When to use:** Reviewing a single skill before integration, evaluating a third-party skill for security, quick quality check on a skill you're authoring.

### Via Agent

```
bundles-forge:auditing skills/authoring
```

The agent detects a single skill directory (contains `SKILL.md`, no `skills/` subdirectory) and runs the 4 applicable categories.

### Via Script

```bash
bundles-forge audit-skill <skill-directory>           # markdown report
bundles-forge audit-skill <skill-directory>/SKILL.md   # also works
bundles-forge audit-skill --json <skill-directory>     # JSON output
```

`audit_skill.py` orchestrates:
- `lint_skills.lint_skill()` — quality, structure, and cross-reference checks
- `audit_security` — security scanning scoped to the skill directory

You can also run the sub-scripts individually:

```bash
bundles-forge audit-skill <skill-directory>     # quality + cross-refs + security
bundles-forge audit-security <skill-directory>   # security scan only
```

### 4 Categories

| # | Category | Weight | Key Checks |
|---|----------|--------|------------|
| 1 | Structure | High (3) | S2, S3, S9 — own directory, SKILL.md exists, name matches |
| 2 | Skill Quality | Medium (2) | Q1-Q15 — frontmatter, descriptions, tokens, sections |
| 3 | Cross-References | Medium (2) | X1-X4 — `project:skill` resolution, relative paths, orphan detection |
| 4 | Security | High (3) | SC1, SC9, SC13, AG1, AG6 — sensitive files, overrides, encoding |

Total weight = 10. Categories not applicable at skill scope: Platform Manifests, Version Sync, Hooks, Testing, Documentation.

### Third-Party Skill Scanning

When evaluating skills from external sources:

1. **Download without executing** — clone/download without running hooks or scripts
2. **Run skill audit** — `bundles-forge audit-skill <downloaded-skill-dir>`
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
bundles-forge audit-workflow <target-dir>                          # full workflow audit
bundles-forge audit-workflow --focus-skills skill-a,skill-b <root>   # focused mode
bundles-forge audit-workflow --json <target-dir>                   # JSON output
```

### 3 Layers (W1-W11)

| Layer | Weight | Checks | Automation |
|-------|--------|--------|------------|
| Static Structure | High (3) | W1-W5: cycles, reachability, Inputs/Outputs presence, artifact ID matching | `bundles-forge audit-skill` graph analysis |
| Semantic Interface | Medium (2) | W6-W9: Integration completeness, artifact clarity, Calls/Called by symmetry | `bundles-forge audit-workflow` + agent review |
| Behavioral Verification | Low (1) | W10-W11: chain A/B eval, trigger/exit in context | `evaluator` agent dispatch |

Total weight = 6. Behavioral layer is scored **N/A** (excluded from weighted average) when skipped; the report notes the skip.

### Focus Mode (Incremental Auditing)

When `--focus-skills skill-a,skill-b` is specified:

1. **All checks run on the full graph** — no analysis is skipped
2. **Findings are partitioned** into Focus Area (involving specified skills) and Context (all others)
3. **Report highlights** the focus skills while preserving full-graph visibility

This enables incremental validation after adding new skills without missing cascade effects.

**Typical workflow for adding third-party skills:**

```
1. User or orchestrating skill decides preparation and next steps (e.g. workflow restructuring).
2. Add skills to the project
3. Run: bundles-forge audit-workflow --focus-skills new-skill-a,new-skill-b .
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
bundles-forge:auditing  (security-only mode)
```

Maps to the `bundles-forge:auditing` skill in security-only mode — runs only Category 10 (Security) across all 7 attack surfaces.

### Via Script

```bash
bundles-forge audit-security <target-dir>           # project-wide scan
bundles-forge audit-security <skill-directory>         # single skill scan
bundles-forge audit-security --json <target-dir>     # JSON output
```

### 7 Attack Surfaces

| Surface | Risk Level | Examples |
|---------|-----------|---------|
| SKILL.md content | High | Sensitive file access, destructive commands, safety overrides, encoding tricks |
| Hook scripts | High | Network calls, env-var leakage, system config modification |
| Hook configs (HTTP hooks) | High | Data exfiltration via `type: "http"` hooks sending tool input/output to external URLs |
| OpenCode plugins | High | Dynamic code execution, network access, message manipulation |
| Agent prompts | Medium | Privilege escalation, scope expansion, safety overrides |
| Bundled scripts | Medium | Network calls, system modifications, unsanitized inputs |
| MCP configs | Medium | Path traversal in plugin.json, userConfig sensitive fields, persistent data in plugin root |

> **Platform note:** Claude Code administrators can restrict hooks via `allowManagedHooksOnly` managed policy. Additionally, `prompt` and `agent` hook types invoke LLM calls on every matched event, which may incur significant token costs in intensive sessions.

### Checklist

- **Security checklist:** `skills/auditing/references/security-checklist.md` — full pattern list for all 7 surfaces

---

## After the Audit

Auditing is a **pure diagnostic** scope: it records findings, scores, and go/no-go style signals in the report. It does **not** suggest fixes, delegate work, or route you to other skills — the **user or an orchestrating skill** (e.g. `blueprinting`, `optimizing`, `releasing`) decides what happens next.

| Report Source | Finding Level | What the report gives you |
|--------------|---------------|----------------------------|
| Full project (`audit-report`) | Critical/Warning | Findings by category with severity; use the report as the source of truth for what failed checks showed. |
| Single skill (`skill-report`) | Critical/Warning | Skill-scope findings and verdict vocabularies (self-check / third-party); no prescribed remediation path from auditing. |
| Workflow (`workflow-report`) | W1-W11 findings | Layered workflow findings only; interpretation and next steps sit with the caller. |
| Any scope | Info | Improvement opportunities noted in the report. |
| Any scope | All clear | Pass state in the report; any follow-up (e.g. release prep) is chosen outside auditing. |

**Verification after changes:** After you address issues, a **single** re-audit can confirm whether critical/warning items are resolved. Whether to run further audits is driven by the **caller** (user or orchestrating skill), not by an audit↔optimize loop.

---

## CI Integration

### Script Composition

```bash
# Full pipeline: lint → security → docs → full audit (audit_plugin orchestrates all)
bundles-forge audit-skill --json . > lint.json
bundles-forge audit-security --json . > security.json
bundles-forge audit-docs --json . > docs.json
bundles-forge audit-plugin --json . > audit.json   # orchestrates lint + security + docs + workflow

# Single skill in CI
bundles-forge audit-skill --json skills/my-skill > skill-audit.json

# Workflow check after PR that modifies skills
bundles-forge audit-workflow --json --focus-skills changed-skill . > workflow.json
```

### Exit Code Usage

```bash
bundles-forge audit-plugin . || echo "Audit found issues (exit $?)"

# Fail CI only on critical
bundles-forge audit-plugin . ; [ $? -ne 2 ] || exit 1
```

### JSON Output

All scripts support `--json`. JSON output includes:
- `status` — PASS / WARN / FAIL
- `overall_score` — weighted average (0-10)
- `summary` — `{critical: N, warning: N}`
- `categories` / `layers` — per-category/layer breakdown with findings and scores

---

## Related Skills

| Skill | Relationship |
|-------|-------------|
| `bundles-forge:blueprinting` | Upstream — dispatches auditing as Phase 4 for initial quality check on new projects |
| `bundles-forge:optimizing` | Upstream — dispatches auditing for post-change verification |
| `bundles-forge:releasing` | Upstream — dispatches auditing as pre-release quality and security gate |
| `bundles-forge:authoring` | Upstream — produces the skill and agent content that auditing validates |
