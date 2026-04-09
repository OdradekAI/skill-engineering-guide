# Audit Checklist

Structured criteria for evaluating a bundle-plugin. Each category has specific checks with severity levels. Use this when running an audit — work through each category, note findings, and compile the report.

## Scoring

Each category is scored 0-10:
- **10** — All checks pass, exemplary implementation
- **7-9** — Minor issues only (info-level)
- **4-6** — Has warnings that should be addressed
- **1-3** — Critical issues that prevent correct operation
- **0** — Category entirely missing

**Overall score** = weighted average of category scores.

---

## Category 1: Structure (Weight: High)

| Check | Severity | Criteria |
|-------|----------|----------|
| S1 | Critical | `skills/` directory exists with at least one skill |
| S2 | Critical | Each skill has its own directory under `skills/` |
| S3 | Critical | Every skill directory contains a `SKILL.md` |
| S4 | Warning | `package.json` exists at project root |
| S5 | Warning | `README.md` exists and is not empty |
| S6 | Warning | `.gitignore` exists and covers essentials (node_modules, .worktrees, OS files) |
| S7 | Info | `CHANGELOG.md` exists |
| S8 | Info | `LICENSE` exists |
| S9 | Info | Skill directory names match `name` field in SKILL.md frontmatter |

---

## Category 2: Platform Manifests (Weight: High)

Run these checks only for platforms the project claims to support.

| Check | Severity | Criteria |
|-------|----------|----------|
| P1 | Critical | Each target platform has its manifest file present |
| P2 | Critical | Manifest JSON is valid (parseable, no syntax errors) |
| P3 | Critical | Cursor manifest paths (`skills`, `hooks`) resolve to existing directories/files |
| P4 | Warning | Manifest metadata (name, version, description) is filled in |
| P5 | Warning | Author and repository fields are populated |
| P6 | Info | Manifest keywords are relevant |

**Platform manifest locations:**
- Claude Code: `.claude-plugin/plugin.json`
- Cursor: `.cursor-plugin/plugin.json`
- OpenCode: `.opencode/plugins/<name>.js`
- Codex: `.codex/INSTALL.md`
- Gemini: `gemini-extension.json`

---

## Category 3: Version Sync (Weight: High)

| Check | Severity | Criteria |
|-------|----------|----------|
| V1 | Critical | `.version-bump.json` exists |
| V2 | Critical | All files listed in `.version-bump.json` actually exist |
| V3 | Critical | All listed files have the same version string (no drift) |
| V4 | Warning | Every platform manifest is listed in `.version-bump.json` |
| V5 | Warning | `scripts/bump-version.sh` exists and is executable |
| V6 | Info | `bump-version.sh --check` exits 0 |
| V7 | Info | `bump-version.sh --audit` finds no undeclared version strings |

**Quick drift check:**
```bash
scripts/bump-version.sh --check
```

---

## Category 4: Skill Quality (Weight: Medium)

Run for every SKILL.md in the project.

| Check | Severity | Criteria |
|-------|----------|----------|
| Q1 | Critical | YAML frontmatter present (between `---` delimiters) |
| Q2 | Critical | `name` field exists in frontmatter |
| Q3 | Critical | `description` field exists in frontmatter |
| Q4 | Warning | `name` uses only letters, numbers, hyphens |
| Q5 | Warning | `description` starts with "Use when..." |
| Q6 | Warning | `description` describes triggering conditions, not workflow summary |
| Q7 | Warning | `description` is under 250 characters (truncated in skill listing beyond this) |
| Q8 | Warning | Frontmatter total under 1024 characters |
| Q9 | Warning | SKILL.md body under 500 lines |
| Q10 | Info | Skill has Overview section |
| Q11 | Info | Skill has Common Mistakes section |
| Q12 | Info | Heavy reference content (100+ lines) extracted to supporting files |

**Description anti-patterns (Q6):**
- Contains step-by-step workflow → agents shortcut to description
- Uses phrases like "first... then... finally..."
- Describes what the skill does instead of when to use it

---

## Category 5: Cross-References (Weight: Medium)

| Check | Severity | Criteria |
|-------|----------|----------|
| X1 | Warning | All `<project>:<skill-name>` references resolve to existing skills |
| X2 | Warning | No broken relative-path references to supporting files |
| X3 | Info | Skills with dependencies document them in an Integration section |
| X4 | Info | Workflow chain has no circular dependencies |
| X5 | Info | Terminal skills (end of chain) are clearly marked |

**How to check:**
1. Extract all `<project>:<name>` patterns from all SKILL.md files
2. Verify each `<name>` matches a directory under `skills/`
3. Extract all relative file references and verify they exist

---

## Category 6: Hooks (Weight: Medium)

Run only if the project uses session bootstrap hooks.

| Check | Severity | Criteria |
|-------|----------|----------|
| H1 | Critical | `hooks/session-start` exists and is executable (`chmod +x`) |
| H2 | Critical | `hooks/hooks.json` is valid JSON (if Claude Code targeted) |
| H3 | Critical | `hooks/hooks-cursor.json` is valid JSON (if Cursor targeted) |
| H4 | Critical | `session-start` reads the correct bootstrap SKILL.md path |
| H5 | Warning | `hooks/run-hook.cmd` exists (Windows support) |
| H6 | Warning | `session-start` handles all target platforms (env var detection) |
| H7 | Warning | JSON escaping is correct (backslashes, quotes, newlines, tabs) |
| H8 | Info | Uses `printf` instead of heredoc (bash 5.3+ compatibility) |

**Quick hook test:**
```bash
CLAUDE_PLUGIN_ROOT="$(pwd)" bash hooks/session-start | python3 -m json.tool
```

---

## Category 7: Testing (Weight: Low)

| Check | Severity | Criteria |
|-------|----------|----------|
| T1 | Warning | `tests/` directory exists |
| T2 | Info | At least one test per target platform |
| T3 | Info | Tests verify skill discovery (skills appear in available list) |
| T4 | Info | Tests verify bootstrap injection (session-start content loads) |

---

## Category 8: Documentation (Weight: Low)

| Check | Severity | Criteria |
|-------|----------|----------|
| D1 | Warning | README contains install instructions for each target platform |
| D2 | Warning | README lists all skills with descriptions |
| D3 | Info | Each non-marketplace platform has a dedicated install doc |
| D4 | Info | CLAUDE.md exists with contributor guidelines |
| D5 | Info | AGENTS.md exists and points to CLAUDE.md |

---

## Category 9: Security (Weight: High)

Run security checks on all executable code, agent instructions, and hook scripts. See `references/security-checklist.md` for the full pattern list.

| Check | Severity | Criteria |
|-------|----------|----------|
| SEC1 | Critical | No SKILL.md instructs agents to read sensitive files (`.env`, `.ssh/`, credentials) |
| SEC2 | Critical | No hook script makes external network calls (`curl`, `wget`, `nc`) |
| SEC3 | Critical | No hook script reads or transmits API keys or secrets |
| SEC4 | Critical | No OpenCode plugin uses `eval()`, `child_process`, or undeclared network access |
| SEC5 | Critical | No agent prompt contains safety override instructions ("ignore safety", "bypass") |
| SEC6 | Warning | Hook scripts follow the legitimate baseline (read SKILL.md, JSON-escape, emit JSON) |
| SEC7 | Warning | OpenCode plugins follow the legitimate baseline (register skills, inject bootstrap) |
| SEC8 | Warning | No SKILL.md uses encoding tricks (unicode homoglyphs, zero-width chars) |
| SEC9 | Info | Agent prompts include explicit scope constraints |
| SEC10 | Info | Scripts use error handling (`set -euo pipefail` or equivalent) |

**Quick check:** Grep for high-risk patterns across all executable files:
```
curl|wget|nc |eval\(|child_process|\.env|api_key|secret|ignore safety|override|bypass
```

---

## Audit Report Template

After running all checks, compile findings into this format:

```markdown
## Bundle-Plugin Audit: <project-name>

**Date:** <date>
**Platforms:** <target platforms>
**Skills:** <count> skills

### Overall Score: X/10

### Critical Issues (must fix)
- [C1] <category>.<check>: <description>
- [C2] ...

### Warnings (should fix)
- [W1] <category>.<check>: <description>
- [W2] ...

### Info (consider)
- [I1] <category>.<check>: <description>
- [I2] ...

### Category Breakdown

| Category | Score | Critical | Warning | Info |
|----------|-------|----------|---------|------|
| Structure | X/10 | 0 | 1 | 0 |
| Platform Manifests | X/10 | 0 | 0 | 1 |
| Version Sync | X/10 | 0 | 0 | 0 |
| Skill Quality | X/10 | 0 | 2 | 1 |
| Cross-References | X/10 | 0 | 0 | 0 |
| Hooks | X/10 | 0 | 1 | 0 |
| Testing | X/10 | 0 | 0 | 2 |
| Documentation | X/10 | 0 | 1 | 0 |
| Security | X/10 | 0 | 0 | 0 |

### Recommendations

1. <highest-impact fix>
2. <next priority>
3. ...
```

Order recommendations by impact: critical fixes first, then warnings that affect the most users, then info items.
