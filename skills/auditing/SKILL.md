---
name: auditing
description: "Use when reviewing a bundle-plugin for structural issues, version drift, manifest problems, skill quality, or security risks — before releasing, after changes, or when scanning third-party skills. Auto-detects scope (full project vs single skill)"
allowed-tools: Bash(python scripts/*)
---

# Auditing Bundle-Plugins

## Overview

Systematically evaluate a bundle-plugin project or a single skill across applicable quality categories — including security scanning — score each, and produce an actionable report.

**Core principle:** Measure before you fix. A scored audit prevents both under-reaction and over-engineering.

**This skill includes security scanning.** Category 9 performs a security scan of skill content, hook scripts, plugin code, agent prompts, and bundled scripts. No need to invoke a separate security skill.

**Announce at start:** "I'm using the auditing skill to audit [this project / this skill]."

### Security-Only Mode

When invoked via `bundles-scan` or when the user explicitly requests a security-only scan, run only Category 9 (Security) and the `scan_security.py` script. Skip Categories 1-8. Report in the same format but with only the Security category scored. This provides a quick security check without the overhead of a full 9-category audit.

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

### Scope Detection

After normalization, determine the audit scope from the resolved local path:

| Target | How to Detect | Mode |
|--------|--------------|------|
| Project root | Has `skills/` directory and `package.json` | **Full audit** — all 9 categories |
| Single skill directory | Contains `SKILL.md` but no `skills/` subdirectory | **Skill audit** — 4 applicable categories |
| Single SKILL.md file | Path ends in `SKILL.md` | **Skill audit** — 4 applicable categories |

**If the target is a single skill, skip to the Skill Audit section below.**

---

## Full Project Audit

### The Process

```
Scan project root
  → Run 9-category checks (including security scan)
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

python scripts/scan_security.py <project-root>         # security-only scan
python scripts/scan_security.py --json <project-root>  # security JSON output
```

`audit_project.py` orchestrates `scan_security.py` (security) and `lint_skills.py` (skill quality), then adds structure, manifest, version-sync, hook, and documentation checks.

Dispatch the `auditor` agent (`agents/auditor.md`) for automated assessment if subagents are available. The auditor runs read-only and returns a scored report.

**If subagent dispatch is unavailable:** Ask the user — "Subagents are not available. I can run the audit checks inline (same checks, same report format, but within this conversation context). Proceed inline?" If confirmed, perform the 9-category checks directly using the audit checklist and security checklist references, then compile the report in the same format the auditor would produce.

### Step 2: Scan

Read the project root. Identify:
- Which platforms are targeted (by manifest presence)
- How many skills exist
- Whether hooks, version sync, and bootstrap are present

### Step 3: Check

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

Each category: 0-10 scale. Overall = weighted average.

### Step 5: Report

Present as:

```
## Bundle-Plugin Audit: <project-name>

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

### Step 6: Fix or Optimize

- **Critical issues:** Offer to fix immediately
- **Warnings:** Offer to fix or suggest `bundles-forge:optimizing`
- **Info:** Note for future consideration

**Termination rule:** After fixing critical/warning issues, run one re-audit to verify. Do not loop more than once — if the re-audit still has issues, present them to the user for manual decision.

---

## Skill Audit (Lightweight Mode)

When the target is a single skill directory or SKILL.md file, run only the 4 categories that apply at skill scope. This is auto-detected — no special flags needed.

### Applicable Categories

| Category | Checks Run | What It Catches |
|----------|-----------|----------------|
| Structure | S2, S3, S9 | Skill has own directory, contains SKILL.md, directory name matches frontmatter `name` |
| Skill Quality | Q1–Q12 (all) | Frontmatter validity, description conventions, token efficiency, section structure |
| Cross-References | X1, X2, X3 | Outgoing `project:skill-name` refs resolve, relative paths exist, Integration section present |
| Security | SEC1, SEC5, SEC8, SEC9, SEC10 | Sensitive file access, safety overrides, encoding tricks, scope constraints, error handling |

**Skipped categories:** Platform Manifests, Version Sync, Hooks, Testing, Documentation — these require project-level context.

### Script Shortcuts

```bash
python scripts/lint_skills.py <skill-directory>         # skill quality only
python scripts/scan_security.py <skill-directory>        # security scan on skill files
```

### Process

```
Read target skill
  → Run 4-category checks (Structure, Quality, Cross-Refs, Security)
  → Score each
  → Compile lightweight report
  → Present findings
```

### Report Format

```
## Skill Audit: <skill-name>

### Score: X/10

### Findings
- [C/W/I] <category>.<check>: <description>

### Category Breakdown
| Category | Score | Notes |
|----------|-------|-------|
| Structure | X/10 | ... |
| Skill Quality | X/10 | ... |
| Cross-References | X/10 | ... |
| Security | X/10 | ... |
```

### Third-Party Skill Scanning

When auditing a skill from an external source (marketplace, git, shared file):

1. Clone/download the skill **without executing** any hooks or scripts
2. Run the skill audit on the downloaded content
3. Pay special attention to Security checks — third-party skills are the primary threat vector
4. Review all critical/warning findings with the user before installation
5. Never auto-install a skill that has unresolved critical security findings

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
| Running full 9-category audit on a single skill | Let scope auto-detection handle it — 5 categories don't apply |
| Skipping security because "I wrote it myself" | Accidental vulnerabilities are common — always scan |
| Only scanning SKILL.md, ignoring hooks | Hooks are the highest-risk executable code (full audit) |

## Integration

**Called by:**
- **bundles-forge:scaffolding** — post-scaffold verification

**Calls:**
- **bundles-forge:optimizing** — when findings need targeted fixes or user feedback iteration

**Pairs with:**
- **bundles-forge:releasing** — version drift checks, pre-release verification
