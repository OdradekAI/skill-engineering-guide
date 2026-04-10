---
name: auditing
description: "Use when reviewing a bundle-plugin for structural issues, version drift, skill quality, workflow integration, or security risks — before releasing, after changes, or after adding skills. Auto-detects scope (full project vs skill vs workflow)"
allowed-tools: Bash(python scripts/*)
---

# Auditing Bundle-Plugins

## Overview

Systematically evaluate a bundle-plugin project or a single skill across applicable quality categories — including security scanning — score each, and produce an actionable report.

**Core principle:** Measure before you fix. A scored audit prevents both under-reaction and over-engineering.

**This skill includes security scanning.** Category 9 performs a security scan of skill content, hook scripts, plugin code, agent prompts, and bundled scripts. No need to invoke a separate security skill.

**Announce at start:** "I'm using the auditing skill to audit [this project / this skill]."

### Security-Only Mode

When invoked via `bundles-scan` or when the user explicitly requests a security-only scan, run only Category 9 (Security) and the `scan_security.py` script. Skip Categories 1-8. Report in the same format but with only the Security category scored. This provides a quick security check without the overhead of a full 10-category audit.

## Step 1: Resolve Input & Detect Scope

The target can be a local path, a GitHub URL, or a zip file. Normalize the input to a local directory before scope detection.

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
| Project root | Has `skills/` directory and `package.json` | **Full audit** — all 10 categories |
| Project root + workflow request | User explicitly requests workflow audit, or specifies `--focus-skills` | **Workflow audit** — 3-layer workflow checks (W1-W12) |
| Single skill directory | Contains `SKILL.md` but no `skills/` subdirectory | **Skill audit** — 4 applicable categories |
| Single SKILL.md file | Path ends in `SKILL.md` | **Skill audit** — 4 applicable categories |

**If the target is a single skill, skip to the Skill Audit section below.**
**If a workflow audit is requested, skip to the Workflow Audit section below.**

---

## Full Project Audit

### The Process

```
Scan project root
  → Run 10-category checks (including security scan)
  → Score each category
  → Compile report
  → Present findings
  → Critical/Warning? → Apply fixes → Suggest optimization
  → Info only?        → Suggest optimization
```

### Script Shortcuts

```bash
python scripts/audit_project.py <project-root>        # full audit with status
python scripts/audit_project.py --json <project-root>  # machine-readable

python scripts/audit_workflow.py <project-root>                          # workflow-only audit
python scripts/audit_workflow.py --focus-skills skill-a,skill-b <root>   # focused workflow audit
python scripts/audit_workflow.py --json <project-root>                   # workflow JSON output

python scripts/scan_security.py <project-root>         # security-only scan
python scripts/scan_security.py --json <project-root>  # security JSON output
```

`audit_project.py` orchestrates `scan_security.py` (security), `lint_skills.py` (skill quality), and `audit_workflow.py` (workflow integration), then adds structure, manifest, version-sync, hook, and documentation checks.

Dispatch the `auditor` agent (`agents/auditor.md`) for automated assessment if subagents are available. The auditor runs read-only and returns a scored report.

**If subagent dispatch is unavailable:** Ask the user — "Subagents are not available. I can run the audit checks inline (same checks, same report format, but within this conversation context). Proceed inline?" If confirmed, perform the 10-category checks directly using the audit checklist, workflow checklist, and security checklist references, then compile the report in the same format the auditor would produce.

### Step 2: Scan

Read the project root. Identify:
- Which platforms are targeted (by manifest presence)
- How many skills exist
- Whether hooks, version sync, and bootstrap are present

### Step 3: Check

Run all 10 categories from `references/audit-checklist.md` and `references/workflow-checklist.md`. The checklists have 60+ individual checks with severity levels (Critical / Warning / Info).

**Categories:**

| Category | Weight | What It Checks |
|----------|--------|----------------|
| Structure | High | Directory layout, required files |
| Platform Manifests | Medium | Format, valid paths, metadata |
| Version Sync | High | Drift, `.version-bump.json` completeness |
| Skill Quality | Medium | Frontmatter, descriptions, token efficiency |
| Cross-References | Medium | `project:skill-name` resolution, broken links (X1-X3) |
| Workflow | High | Workflow graph topology, integration symmetry, artifact handoff (W1-W12) |
| Hooks | Medium | Bootstrap injection, platform detection |
| Testing | Medium | Test directory, test prompts, A/B eval results |
| Documentation | Low | README, install docs, CHANGELOG |
| Security | High | 5 attack surfaces — see Security Scan below |

### Security Scan (Category 9)

Scans 5 attack surfaces. See `references/security-checklist.md` for the full pattern list.

| Target | Risk Level | What to Look For |
|--------|-----------|------------------|
| SKILL.md content | High | Data-leak instructions, destructive commands, safety overrides, encoding tricks |
| Hook scripts | High | Network calls, env-var leakage, system config modification |
| OpenCode plugins | High | Dynamic code execution, network access, message manipulation |
| Agent prompts | Medium | Privilege escalation, scope expansion, safety overrides |
| Bundled scripts | Medium | Network calls, system modifications, unsanitized inputs |

**Third-party skill scanning:** When scanning skills from external sources, clone/download without executing hooks, run the audit, and review critical findings with the user before installation. Never auto-install without scanning.

### Step 4: Score

Each category: 0-10 scale. Scripts compute baseline via `max(0, 10 - (critical × 3 + warning × 1))`. The auditor may adjust by ±2 with rationale. Overall = weighted average (High=3, Medium=2, Low=1).

### Step 5: Report

Compile findings into the six-layer report format defined in `references/report-template.md`. The template structures the report as a **decision document** — Layer 1 enables a 30-second Go/No-Go decision, deeper layers provide evidence and methodology.

**Report layers:**

1. **Decision Brief** — Go/No-Go recommendation, top 3 risks, remediation estimate
2. **Risk Matrix** — all findings in one table with quantified impact, exploitability, and confidence
3. **Findings by Category** — 10 categories as sections, each listing component-level findings with inline evidence
4. **Methodology** — scope, tools, limitations, out-of-scope declaration
5. **Appendix** — per-skill breakdown, component inventory, raw script outputs

**Go/No-Go logic:** Scripts provide an automated baseline (Critical → `NO-GO`, Warning-only → `CONDITIONAL GO`, clean → `GO`). The auditor may adjust the recommendation but must record the rationale.

**Key rules:**
- Every finding gets a category-prefixed ID (e.g. `SEC-001`, `STR-002`) for cross-referencing
- Every finding includes severity (P0–P3), confidence (Confirmed/Likely/Suspected), and quantified impact
- Categories with no findings still appear with "No findings. All checks pass." — readers need to distinguish "checked and clean" from "not checked"
- Qualitative summaries (Verdict / Strengths / Key Issues) per skill go in the Appendix, not the main body

**Qualitative summaries** are produced by the auditor agent or inline by the main agent. Scripts output per-skill findings and counts but not qualitative judgments.

**Audit context adaptation:** The template has conditional sections for pre-release (release readiness), post-change (regression check), and third-party evaluation (install safety). Choose the context that matches the audit trigger.

### Step 6: Fix or Optimize

- **Critical issues:** Offer to fix immediately
- **Warnings:** Offer to fix or suggest `bundles-forge:optimizing`
- **Workflow findings (W1-W12):** Route to `bundles-forge:optimizing` Target 4 (Workflow Chain Integrity)
- **Info:** Note for future consideration

**Termination rule:** After fixing critical/warning issues, run one re-audit to verify. Do not loop more than once — if the re-audit still has issues, present them to the user for manual decision.

---

## Skill Audit (Lightweight Mode)

When the target is a single skill directory or SKILL.md file, run only the 4 categories that apply at skill scope. This is auto-detected — no special flags needed.

### Applicable Categories

| Category | Checks Run | What It Catches |
|----------|-----------|----------------|
| Structure | S2, S3, S9 | Skill has own directory, contains SKILL.md, directory name matches frontmatter `name` |
| Skill Quality | Q1–Q15 (all) | Frontmatter validity, description conventions, token budget, allowed-tools deps, section structure, conditional block reachability |
| Cross-References | X1, X2, X3 | Outgoing `project:skill-name` refs resolve, relative paths exist, referenced subdirectories exist |
| Security | SEC1, SEC5, SEC8, SEC9, SEC10 | Sensitive file access, safety overrides, encoding tricks, scope constraints, error handling |

**Skipped categories:** Platform Manifests, Version Sync, Hooks, Testing, Documentation — these require project-level context.

### Script Shortcuts

```bash
python scripts/audit_skill.py <skill-directory>          # combined 4-category skill audit
python scripts/audit_skill.py <path>/SKILL.md            # also accepts SKILL.md path
python scripts/audit_skill.py --json <skill-directory>   # JSON output

python scripts/lint_skills.py <skill-directory>          # skill quality only
python scripts/scan_security.py <skill-directory>        # security scan on skill files
```

### Process

```
Read target skill
  → Run 4-category checks (Structure, Quality, Cross-Refs, Security)
  → Produce qualitative summary (Verdict, Strengths, Key Issues)
  → Score each category
  → Compile report
  → Present findings
```

### Report Format

Use the **Single Skill Audit Report** template from `references/skill-report-template.md`. It provides a three-layer structure (Decision Brief, Findings by Category, Skill Profile) with its own decision vocabulary, optimized for the 4-category skill scope.

**Qualitative summary guidelines:**
- **Verdict** — one sentence capturing the skill's overall quality and fitness for purpose
- **Strengths** — what the skill does well (max 3, be concise)
- **Key Issues** — the most impactful problems found (max 3, be specific and objective)
- Do not include actionable fix suggestions — that is `bundles-forge:optimizing`'s responsibility

### Third-Party Skill Scanning

When auditing a skill from an external source (marketplace, git, shared file):

1. Clone/download the skill **without executing** any hooks or scripts
2. Run the skill audit on the downloaded content
3. Pay special attention to Security checks — third-party skills are the primary threat vector
4. Review all critical/warning findings with the user before installation
5. Never auto-install a skill that has unresolved critical security findings

---

## Workflow Audit

When the user explicitly requests a workflow audit, or when the Full audit's Cross-References category (X1-X3) or Workflow category (W1-W12) has warnings, run a dedicated workflow audit. This evaluates how skills connect, hand off artifacts, and compose into coherent chains.

### When to Trigger

- User explicitly requests "audit the workflow" or "check workflow integration"
- After adding third-party skills to an existing project (via `bundles-forge:blueprinting` Scenario D)
- After modifying Integration sections, Inputs/Outputs, or adding new skills to a chain
- When the Full audit's Workflow category shows warnings — suggest: "Workflow issues detected. Run a focused workflow audit with `--focus-skills` for detailed diagnostics."

### Script Shortcuts

```bash
python scripts/audit_workflow.py <project-root>                          # full workflow audit
python scripts/audit_workflow.py --focus-skills skill-a,skill-b <root>   # focused on specific skills
python scripts/audit_workflow.py --json <project-root>                   # machine-readable
```

Dispatch the `auditor` agent (`agents/auditor.md`) in Workflow Audit Mode for automated assessment if subagents are available.

### Three-Layer Checks

Checks are defined in `references/workflow-checklist.md` (W1-W12):

| Layer | Weight | Checks | Automation |
|-------|--------|--------|------------|
| Static Structure | High | W1-W5 (cycles, reachability, Inputs/Outputs presence, artifact ID matching) | `lint_skills.py` graph analysis |
| Semantic Interface | Medium | W6-W10 (Integration completeness, artifact clarity, Calls/Called by symmetry) | `audit_workflow.py` + agent review |
| Behavioral Verification | Low | W11-W12 (Chain A/B Eval, trigger/exit in context) | `evaluator` agent dispatch |

### Focus Mode

When `--focus-skills skill-a,skill-b` is specified, all checks run on the full graph but the report partitions findings into **Focus Area** (directly involving specified skills) and **Context** (remaining findings). This enables incremental validation after adding new skills without missing cascade effects.

### Report Format

Use the **Workflow Audit Report** template from `references/workflow-report-template.md`. It provides a three-layer structure (Decision Brief, Findings by Layer, Skill Integration Map) with workflow-specific Go/No-Go logic.

### Fix or Optimize

Route workflow findings to `bundles-forge:optimizing` Target 4 (Workflow Chain Integrity). The optimizing skill consumes the `workflow-report` and applies targeted fixes to Integration sections, Inputs/Outputs, and artifact IDs.

---

## Severity Levels

- **Critical** — skill/project will not work correctly, or contains active security threats
- **Warning** — works but has quality issues or suspicious patterns needing review
- **Info** — improvement opportunities

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping version sync check | Always run `python scripts/bump_version.py --check` (full audit) |
| Not checking description anti-patterns | Descriptions that summarize workflow cause agents to shortcut |
| Ignoring cross-reference resolution | Broken `project:skill-name` refs = broken workflow chains |
| Running full 10-category audit on a single skill | Let scope auto-detection handle it — 6 categories don't apply |
| Skipping workflow audit after adding third-party skills | New skills need workflow integration validation — use `--focus-skills` |
| Skipping security because "I wrote it myself" | Accidental vulnerabilities are common — always scan |
| Only scanning SKILL.md, ignoring hooks | Hooks are the highest-risk executable code (full audit) |

## Inputs

- `project-directory` (required) — bundle-plugin project root, single skill directory, or SKILL.md file path (local, GitHub URL, or archive)

## Outputs

- `audit-report` — scored report with findings across 10 categories (full project), written to `.bundles-forge/` by the auditor agent. Contains per-skill breakdowns. Consumed by `bundles-forge:optimizing` for targeted fixes
- `skill-report` (skill mode) — 4-category scored report (Structure, Quality, Cross-Refs, Security) for a single skill, written to `.bundles-forge/`. Consumed by `bundles-forge:optimizing` (Skill Optimization)
- `workflow-report` (workflow mode) — workflow-specific report with W1-W12 findings across static/semantic/behavioral layers, with focus/context partitioning. Consumed by `bundles-forge:optimizing` Target 4

## Integration

<!-- cycle:auditing,optimizing -->

**Called by:**
- **bundles-forge:scaffolding** — post-scaffold verification
- **bundles-forge:optimizing** — post-change verification after applying optimizations
- **bundles-forge:releasing** — pre-release quality and security check
- **bundles-forge:porting** — verify after platform adaptation

**Calls:**
- **bundles-forge:optimizing** — when findings need targeted fixes or user feedback iteration

**Pairs with:**
- **bundles-forge:releasing** — version drift checks, pre-release verification
