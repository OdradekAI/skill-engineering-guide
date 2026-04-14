---
name: auditing
description: "Use when reviewing a bundle-plugin for structural issues, version drift, skill quality, workflow integration, or security risks — before releasing, after changes, or after adding skills. Auto-detects scope (full project vs skill vs workflow)"
allowed-tools: Bash(bundles-forge audit-skill *) Bash(bundles-forge audit-security *) Bash(bundles-forge audit-docs *) Bash(bundles-forge audit-plugin *) Bash(bundles-forge audit-workflow *) Bash(bundles-forge checklists *) Bash(bundles-forge bump-version *)
---

# Auditing Bundle-Plugins

## Overview

Systematically evaluate a bundle-plugin project or a single skill across applicable quality categories — including security scanning — score each, and produce a diagnostic report. This skill is a pure diagnostic tool: it identifies and reports issues but does not orchestrate fixes.

**Core principle:** Measure and report. A scored audit gives orchestrating skills (blueprinting, optimizing, releasing) the information they need to decide what to fix. When sources contradict, apply the authority hierarchy in `references/source-of-truth-policy.md`.

**This skill includes security scanning.** Category 10 performs a security scan of skill content, hook scripts, plugin code, agent prompts, and bundled scripts. No need to invoke a separate security skill.

**Announce at start:** "I'm using the auditing skill to audit [this project / this skill]."

## Resolve Input & Detect Scope

The target can be a local path, a GitHub URL, or a zip file. Normalize to a local directory, then detect scope. This applies to all three audit modes.

### Input Normalization

| Input | Action |
|-------|--------|
| Local directory path | Use directly |
| Local SKILL.md file path | Use its parent directory |
| GitHub repo URL (`https://github.com/user/repo`) | `git clone --depth 1 --no-checkout` to temp dir, then `git checkout` (avoids running hooks) |
| GitHub subdirectory URL (`…/tree/main/skills/xxx`) | Clone repo (shallow), extract the subdirectory path |
| Zip/tar.gz file path | Extract to temp directory |
| GitHub release/archive URL (`.zip`/`.tar.gz`) | Download, then extract to temp directory |

**Security rule for remote sources:** Always clone/download without executing hooks or scripts. Use `--no-checkout` + selective `git checkout`, or extract archives without running post-install scripts. The audit itself will scan for risks — don't trigger them before scanning.

**If clone/download fails:** Tell the user what failed (network error, 404, auth required, rate limit) and suggest alternatives — provide the repo as a local path or zip file. Do not silently skip the audit or proceed with partial data.

### Scope Detection

After normalization, determine the audit scope from the resolved local path:

| Target | How to Detect | Mode |
|--------|--------------|------|
| Project root | Has `skills/` directory | **Full audit** — all 10 categories |
| Project root + workflow request | User explicitly requests workflow audit, or specifies `--focus-skills` | **Workflow audit** — 3-layer workflow checks (W1-W11) |
| Single skill directory | Contains `SKILL.md` but no `skills/` subdirectory | **Skill audit** — 4 applicable categories |
| Single SKILL.md file | Path ends in `SKILL.md` | **Skill audit** — 4 applicable categories |

**If the target is a single skill, skip to the Skill Audit section below.**
**If a workflow audit is requested, skip to the Workflow Audit section below.**

---

## Full Project Audit

### Script Shortcut

```bash
bundles-forge audit-plugin <project-root>        # full audit with status
bundles-forge audit-plugin --json <project-root>  # machine-readable
```

`audit-plugin` orchestrates `audit-security` (security), `audit-skill` (skill quality), `audit-workflow` (workflow integration), and `audit-docs` (documentation consistency D1-D9), then adds structure, manifest, version-sync, hook, and testing checks.

### Run Script Baseline

Run `bundles-forge audit-plugin --json <project-root>` to collect the deterministic baseline. This ensures script-checkable items (structure, manifests, version sync, skill quality, cross-references, hooks, documentation, security patterns) are verified with reproducible results regardless of agent behavior.

### Dispatch Auditor

Pass the JSON script output to the `auditor` agent (`agents/auditor.md`) as input context. The auditor uses these results as its baseline scores and adds qualitative assessment (±2 score adjustments, narrative evaluation, report compilation). The auditor is the single source of truth for scoring formula, report format, and qualitative assessment criteria.

The auditor executes all 10 categories, scores each on a 0-10 scale, and compiles a layered report. Full execution details — category weights, scoring formula, report format, Go/No-Go logic — are defined in `agents/auditor.md` and supported by checklists in `references/`.

When auditing a project created by `bundles-forge:blueprinting`, the auditor may reference the design document's "Success Criteria" section (if present in `.bundles-forge/` or project root) to evaluate whether the implementation aligns with the original project goals.

**Categories at a glance** (see `references/plugin-checklist.md` for 60+ individual checks):

| Category | Weight |
|----------|--------|
| Structure | High |
| Platform Manifests | Medium |
| Version Sync | High |
| Skill Quality | Medium |
| Cross-References | Medium |
| Workflow | High |
| Hooks | Medium |
| Testing | Medium |
| Documentation | Low |
| Security | High |

**Security Scan (Category 10):** Scans 7 attack surfaces. See `references/security-checklist.md` for the full pattern list.

| Target | Risk Level |
|--------|-----------|
| SKILL.md content | High |
| Hook scripts | High |
| Hook configs (HTTP hooks) | High |
| OpenCode plugins | High |
| Agent prompts | Medium |
| Bundled scripts | Medium |
| MCP configs | Medium |

**If subagent dispatch is unavailable:** Ask the user — "Subagents are not available. I can run the audit checks inline. Proceed inline?" If confirmed, read `agents/auditor.md` and follow its execution instructions within this conversation context, using the script JSON output as baseline. The agent file contains the complete audit protocol — scoring rules, report compilation, and file-saving conventions.

**Third-party skill scanning:** When scanning skills from external sources, clone/download without executing hooks, run the audit, and review critical findings with the user before installation. Never auto-install without scanning.

### Behavioral Verification (Optional)

If subagents are available, dispatch the `evaluator` agent (`agents/evaluator.md`) with label "chain" to run behavioral verification (W10-W11) on workflow chains. This validates that skill handoffs work end-to-end, not just structurally. Append evaluator results to the Workflow category in the audit report.

**When to run:** Pre-release audits, or when the Workflow category (W1-W9) has warnings that suggest structural issues may affect runtime behavior.

**When to skip:** Quick post-change checks, when evaluator dispatch is unavailable, or when static and semantic layers show no issues. Score skipped behavioral layer as **N/A** (excluded from weighted average).

Present all findings grouped by severity (Critical / Warning / Info). The audit report is the final output — the calling context decides what to fix and how.

---

## Skill Audit (Lightweight Mode)

When the target is a single skill directory or SKILL.md file, run only the 4 categories that apply at skill scope. This is auto-detected — no special flags needed.

### Applicable Categories

| Category | Checks Run | What It Catches |
|----------|-----------|----------------|
| Structure | S2, S3, S9 | Skill has own directory, contains SKILL.md, directory name matches frontmatter `name` |
| Skill Quality | Q1–Q15 | Frontmatter validity, description conventions, token budget, allowed-tools deps, section structure, conditional block reachability |
| Cross-References | X1, X2, X3 | Outgoing `project:skill-name` refs resolve, relative paths exist, referenced subdirectories exist |
| Security | SC1, SC9, SC13, AG1, AG6 | Sensitive file access, safety overrides, encoding tricks, scope constraints (IDs from `security-checklist.md`) |

**Skipped categories:** Platform Manifests, Version Sync, Hooks, Testing, Documentation — these require project-level context.

### Script Shortcut

```bash
bundles-forge audit-skill <skill-directory>          # combined 4-category skill audit
bundles-forge audit-skill <path>/SKILL.md            # also accepts SKILL.md path
bundles-forge audit-skill --json <skill-directory>   # JSON output
```

### Process & Report

The auditor (or inline executor) runs the 4-category checks, produces a qualitative summary (Verdict, Strengths, Key Issues), scores each category, and compiles the report using `references/skill-report-template.md`. Full process and report format details are in `agents/auditor.md` (Single Skill Audit Mode section).

### Third-Party Skill Scanning

When auditing a skill from an external source (marketplace, git, shared file):

1. Clone/download the skill **without executing** any hooks or scripts
2. Run the skill audit on the downloaded content
3. Pay special attention to Security checks — third-party skills are the primary threat vector
4. Review all critical/warning findings with the user before installation
5. Never auto-install a skill that has unresolved critical security findings

---

## Workflow Audit

When the user explicitly requests a workflow audit, or when the Full audit's Cross-References category (X1-X3) or Workflow category (W1-W11) has warnings, run a dedicated workflow audit. This evaluates how skills connect, hand off artifacts, and compose into coherent chains.

### When to Trigger

- User explicitly requests "audit the workflow" or "check workflow integration"
- After adding skills to an existing project
- After modifying Integration sections, Inputs/Outputs, or adding new skills to a chain
- When the Full audit's Workflow category shows warnings — suggest: "Workflow issues detected. Run a focused workflow audit with `--focus-skills` for detailed diagnostics."

### Script Shortcut

```bash
bundles-forge audit-workflow <project-root>                          # full workflow audit
bundles-forge audit-workflow --focus-skills skill-a,skill-b <root>   # focused on specific skills
bundles-forge audit-workflow --json <project-root>                   # machine-readable
```

Dispatch the `auditor` agent (`agents/auditor.md`) in Workflow Audit Mode for automated assessment if subagents are available. The auditor handles W1-W9 (Static Structure + Semantic Interface) across three layers defined in `references/workflow-checklist.md`. Full workflow audit protocol, focus mode, and report format are in `agents/auditor.md` (Workflow Audit Mode section).

**Phase 2 — Behavioral Verification (W10-W11):**
After the auditor returns the workflow report, dispatch `evaluator` agent (`agents/evaluator.md`) with label "chain" for each workflow chain involving focus skills. Use the chain list and focus skills from the auditor's report. Skip if subagent dispatch is unavailable — score the behavioral layer as **N/A** (excluded from weighted average) and note the skip in the final report. Append evaluator results to the workflow audit report.

**Why two phases:** Subagents cannot dispatch other subagents, so the evaluator must be dispatched from this skill (main conversation), not from within the auditor.

**If subagent dispatch is unavailable:** Ask the user — "Subagents are not available. I can run the workflow checks inline. Proceed?" If confirmed, read `agents/auditor.md` (Workflow Audit Mode section) and follow its execution instructions inline, then handle W10-W11 from `references/workflow-checklist.md`.

### Report Findings

Present workflow findings grouped by severity. The `workflow-report` is consumed by the calling context for targeted fixes.

---

## Security-Only Mode

When invoked via `bundles-scan` or when the user explicitly requests a security-only scan, run only Category 10 (Security) and `bundles-forge audit-security`. Skip Categories 1-8. Report in the same format but with only the Security category scored. This provides a quick security check without the overhead of a full 10-category audit.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping version sync check | Always run `bundles-forge bump-version --check` (full audit) |
| Not checking description anti-patterns | Descriptions that summarize workflow cause agents to shortcut |
| Ignoring cross-reference resolution | Broken `project:skill-name` refs = broken workflow chains |
| Running full 10-category audit on a single skill | Let scope auto-detection handle it — 6 categories don't apply |
| Skipping workflow audit after adding third-party skills | New skills need workflow integration validation — use `--focus-skills` |
| Skipping security because "I wrote it myself" | Accidental vulnerabilities are common — always scan |
| Only scanning SKILL.md, ignoring hooks | Hooks are the highest-risk executable code (full audit) |

## Inputs

- `project-directory` (required) — bundle-plugin project root, single skill directory, or SKILL.md file path (local, GitHub URL, or archive)

## Outputs

- `audit-report` — scored report with findings across 10 categories (full project), written to `.bundles-forge/` by the auditor agent. Contains per-skill breakdowns
- `skill-report` (skill mode) — 4-category scored report (Structure, Quality, Cross-Refs, Security) for a single skill, written to `.bundles-forge/`
- `workflow-report` (workflow mode) — workflow-specific report with W1-W11 findings across static/semantic/behavioral layers, with focus/context partitioning

## Integration

**Called by:**
- **bundles-forge:blueprinting** — Phase 4: initial quality check on new projects
- **bundles-forge:optimizing** — post-change verification after applying optimizations
- **bundles-forge:releasing** — pre-release quality and security check
- User directly — standalone audit of any project or skill
