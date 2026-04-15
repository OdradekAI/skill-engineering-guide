# Decomposition Analysis

When the user wants to split a complex skill into a bundle-plugin, analyze the existing skill before blueprinting the new project.

## B1. Read the Existing Skill

Read the full SKILL.md (and any supporting files). Map out:
- What distinct responsibilities does this skill handle?
- Are there sections that could operate independently?
- Does the skill have branching logic that suggests separate workflows?

## B2. Identify Responsibility Boundaries

Look for natural split points:

| Signal | Suggests Separate Skill |
|--------|------------------------|
| "If X, do this; if Y, do that" with large branches | Each branch is a candidate skill |
| Sections with their own input/output formats | Independent responsibility |
| Steps that could be skipped entirely in some cases | Optional skill in a chain |
| Heavy reference material for a specific subtask | Subtask skill with its own references/ |

## B3. Propose a Decomposition

Present the user with:
- Which pieces become independent skills
- Which pieces become shared `references/` or `scripts/`
- How the skills chain together (workflow dependencies)
- Whether a bootstrap skill is needed to orchestrate them

Get user approval on the decomposition before proceeding to Phase 1: Needs Exploration to finalize project details.

## Example: Splitting an Audit Skill

Consider a monolithic `auditing` skill that handles structural checks, security scanning, and report generation in one file (~600 lines with heavy branching).

**B1 findings:**
- Three distinct responsibilities: quality checks (frontmatter, body, cross-refs), security scanning (7 surfaces), report generation (scoring, output formatting)
- Each section has its own input format: quality checks read SKILL.md files, security reads hook scripts and plugin code, reporting consumes findings from both
- Quality checks can run independently of security scanning

**B2 split points:**

| Section | Signal | Decision |
|---------|--------|----------|
| Quality checks (Q1-Q15) | Own input/output, skippable when only security matters | Candidate skill: `auditing` (focused on skill quality) |
| Security scanning (S1-S7) | Own input/output, skippable when only quality matters | Candidate skill: `security-scanning` |
| Report generation | Shared by both, heavy formatting logic | Shared `scripts/` — a Python script both skills invoke |
| Audit check definitions | Reference data, not execution logic | Shared `references/audit-checks.json` |

**B3 decomposition proposal:**

```
auditing (quality checks)
  └── scripts/audit_skill.py (shared report generator)
  └── references/audit-checks.json (shared check definitions)

security-scanning (security surface analysis)
  └── scripts/audit_security.py (shared report generator)
  └── references/audit-checks.json (shared check definitions)

using-audit-tools (bootstrap)
  └── routes to auditing + security-scanning
```

The bootstrap skill provides a unified entry point, while each executor skill has a single responsibility with clear boundaries.
