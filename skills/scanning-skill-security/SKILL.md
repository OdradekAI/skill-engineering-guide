---
name: scanning-skill-security
description: "Use when reviewing a skill-project for security risks, scanning third-party skills before installation, before publishing or releasing a skill-project, after modifying hooks/plugins/scripts, when a user points to a skill folder/file or skill repository URL to review for safety, or when any executable code in a skill-project needs safety verification — even code you wrote yourself, since accidental vulnerabilities are common"
---

# Scanning Skill Security

## Overview

Scan a skill-project's attack surface — SKILL.md instructions, hook scripts, OpenCode plugins, agent prompts, and bundled scripts — for patterns that could exfiltrate data, destroy resources, install backdoors, or override safety controls.

**Core principle:** Trust but verify. Every skill-project that executes code or instructs agents deserves a security scan, whether you wrote it or someone else did.

**This is a rigid skill.** Follow the scan process completely — do not skip categories or rationalize away findings.

**Announce at start:** "I'm using the scanning-skill-security skill to scan this project for security risks."

## Script Shortcut

Run the automated scanner for quick pattern-based checks before doing a manual deep review:

```bash
python scripts/scan-security.py <project-root>        # markdown report
python scripts/scan-security.py --json <project-root>  # machine-readable
```

Exit codes: 0 = clean, 1 = warnings only, 2 = critical findings. The script covers all 5 scan targets with regex-based pattern matching. Use the full manual process below for nuanced review that patterns cannot catch.

## When to Scan

- **Before release** — every skill-project, every time
- **Before installing third-party skills** — scan before trusting
- **After audit flags security concerns** — deep dive on specific findings
- **After modifying hooks or plugins** — any change to executable code

## The 5 Scan Targets

```
Scan project
  ├── 1. SKILL.md content
  ├── 2. Hook scripts
  ├── 3. OpenCode plugins
  ├── 4. Agent prompts
  └── 5. Bundled scripts
        │
  Compile report → Report
```

### Target 1: SKILL.md Content (all skills + references)

Scan every SKILL.md and markdown reference for instructions that direct agents to perform dangerous actions. Skills are agent instructions — a malicious skill can instruct an agent to do anything the agent has access to.

**What to look for:** Instructions to read secrets, exfiltrate data, execute destructive commands, override safety settings, or install persistent changes. See `references/security-checklist.md` for the full pattern list.

### Target 2: Hook Scripts (session-start, run-hook.cmd)

Hook scripts execute on every session start with the user's shell permissions. They are the highest-risk executable code in a skill-project.

**What to look for:** Network calls (`curl`, `wget`, `nc`), environment variable exfiltration, system config modification, package installation, obfuscated commands. The legitimate use case is narrow: read a SKILL.md, JSON-escape it, emit JSON.

### Target 3: OpenCode Plugins (.opencode/plugins/*.js)

OpenCode plugins run as Node.js modules with full filesystem and network access. They can transform messages, modify config, and execute arbitrary code.

**What to look for:** `eval()`, `child_process`, undeclared network requests, `process.env` access beyond what's documented, message transforms that inject hidden content.

### Target 4: Agent Prompts (agents/*.md + skill-local prompts)

Agent prompts define subagent behavior. A malicious prompt can instruct a subagent to perform actions that the dispatching skill didn't intend.

**What to look for:** Privilege escalation instructions, safety override directives, instructions to access resources beyond the stated task scope.

### Target 5: Bundled Scripts (scripts/, skill-local scripts)

Any executable file bundled with the project — shell scripts, Python scripts, Node scripts.

**What to look for:** Same patterns as hook scripts, plus: undeclared dependencies, network calls, system modifications.

## Risk Levels

| Level | Meaning | Action |
|-------|---------|--------|
| **Critical** | Active threat — data exfiltration, backdoor installation, destructive commands | Block usage until resolved |
| **Warning** | Suspicious pattern — could be legitimate but needs human review | Flag for manual review |
| **Info** | Minor concern — overly broad permissions, missing least-privilege | Note for improvement |

## Security Report Format

```
## Security Scan: <project-name>

**Date:** <date>
**Files scanned:** <count>
**Risk summary:** <critical> critical, <warning> warnings, <info> info

### Critical Risks (block until resolved)
- [SEC-C1] <file>:<line> — <description>

### Warnings (needs human review)
- [SEC-W1] <file>:<line> — <description>

### Info (consider improving)
- [SEC-I1] <file>:<line> — <description>

### Files Scanned
| File | Type | Findings |
|------|------|----------|
| hooks/session-start | Hook script | 0 critical, 0 warning |
| ...  | ...  | ... |
```

## Third-Party Skill Scanning

When scanning skills from external sources (marketplace, git repos, shared files):

1. **Clone or download** without executing any hooks
2. **Run full scan** across all 5 targets
3. **Review critical findings** with the user before proceeding
4. **Only install after user approval** of the security report

Never auto-install third-party skills without scanning first.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping scan because "I wrote it myself" | You can introduce vulnerabilities accidentally |
| Only scanning SKILL.md, ignoring hooks | Hooks are the highest-risk executable code |
| Dismissing warnings as false positives | Flag for human review — let the user decide |
| Scanning once and never again | Rescan after every change to executable code |

## Integration

**Called by:**
- **skill-forge:auditing-skill-projects** — Category 9: Security
- **skill-forge:scaffolding-skill-projects** — post-scaffold security baseline

**Calls:**
- **skill-forge:optimizing-skill-projects** — when security fixes overlap with optimization

**Pairs with:**
- **skill-forge:adapting-skill-platforms** — new platform adapters need security review
