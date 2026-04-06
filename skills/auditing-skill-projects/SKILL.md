---
name: auditing-skill-projects
description: "Use when reviewing a skill-project for structural issues, version drift, manifest problems, or skill quality, before releasing a skill-project, after significant changes to a skill-project, when a user points to a specific skill folder or third-party skill to review, or as a periodic skill-project health check — provides systematic 9-category quality assessment with scoring and actionable recommendations"
---

# Auditing Skill Projects

## Overview

Systematically evaluate a skill-project across 9 quality categories, score each, and produce an actionable report. Think of this as a comprehensive health check — it catches everything from missing manifests to security risks.

**Core principle:** Measure before you fix. A scored audit prevents both under-reaction and over-engineering.

**Announce at start:** "I'm using the auditing-skill-projects skill to audit this project."

## The Process

```
Scan project root
  → Run 9-category checks
  → Score each category
  → Compile report
  → Present findings
  → Critical/Warning? → Apply fixes → Suggest optimization
  → Info only?        → Suggest optimization
```

### Script Shortcut

Run the automated audit for a quick project health check:

```bash
python scripts/audit-project.py <project-root>        # markdown report with scores
python scripts/audit-project.py --json <project-root>  # machine-readable
```

The script orchestrates `scan-security.py` (security) and `lint-skills.py` (skill quality), then adds structure, manifest, version-sync, hook, and documentation checks. Use the full manual process below for deeper analysis and scoring nuance.

### Step 1: Scan

Read the project root. Identify:
- Which platforms are targeted (by manifest presence)
- How many skills exist
- Whether hooks, version sync, and bootstrap are present

### Step 2: Check

Run all 9 categories from `references/audit-checklist.md`. The checklist has 50+ individual checks with severity levels (Critical / Warning / Info).

**Categories:**

| Category | Weight | What It Checks |
|----------|--------|----------------|
| Structure | High | Directory layout, required files |
| Platform Manifests | High | Format, valid paths, metadata |
| Version Sync | High | Drift, `.version-bump.json` completeness |
| Skill Quality | Medium | Frontmatter, descriptions, token efficiency |
| Cross-References | Medium | `project:skill-name` resolution, broken links |
| Hooks | Medium | Bootstrap injection, platform detection |
| Testing | Low | Test directory, platform coverage |
| Documentation | Low | README, install docs, CHANGELOG |
| Security | High | Hook scripts, plugin code, agent prompts, instruction patterns |

### Step 3: Score

Each category: 0-10 scale. Overall = weighted average.

### Step 4: Report

Present as:

```
## Skill-Project Audit: <project-name>

### Score: X/10

### Critical (must fix)
- [C1] ...

### Warning (should fix)
- [W1] ...

### Info (consider)
- [I1] ...

### Category Breakdown
| Category | Score | Notes |
|----------|-------|-------|
| Structure | X/10 | ... |
| ...      | ...   | ...   |
```

### Step 5: Fix or Optimize

- **Critical issues:** Offer to fix immediately
- **Warnings:** Offer to fix or suggest `seg:optimizing-skill-projects`
- **Info:** Note for future consideration

## Severity Levels

- **Critical** — project will not work correctly (missing manifests, broken hooks, version drift)
- **Warning** — project works but has quality issues (description anti-patterns, missing .gitignore entries)
- **Info** — improvement opportunities (could add platform, test coverage gaps)

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping version sync check | Always run `bump-version.sh --check` |
| Not checking description anti-patterns | Descriptions that summarize workflow cause agents to shortcut |
| Ignoring cross-reference resolution | Broken `project:skill-name` refs = broken workflow chains |
| Auditing only structure | All 9 categories matter — don't skip quality or security checks |

## Integration

**Called by:**
- **seg:scaffolding-skill-projects** — post-scaffold verification

**Calls:**
- **seg:optimizing-skill-projects** — when findings need targeted fixes
- **seg:scanning-skill-security** — Category 9: Security assessment

**Pairs with:**
- **seg:managing-skill-versions** — version drift checks
