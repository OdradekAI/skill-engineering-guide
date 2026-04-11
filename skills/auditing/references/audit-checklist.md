# Audit Checklist

Structured criteria for evaluating a bundle-plugin. Each category has specific checks with severity levels. Use this when running an audit — work through each category, note findings, and compile the report.

## Scoring

Each category is scored 0-10. Scripts compute a **baseline score** using the formula:

```
baseline = max(0, 10 - (critical_count × 3 + capped_warning_penalty))
```

where `capped_warning_penalty = sum(min(count_per_check_id, 3))` — warnings from the same check ID are capped at -3 penalty per ID. This prevents a single conceptual gap (e.g. missing prompt files for N skills) from producing N × -1 multiplicative punishment.

The auditor agent (or inline auditor) may adjust the baseline by **±2 points** to account for qualitative factors the formula cannot capture (e.g. a critical that is a confirmed false positive, or a warning-free category that still has poor design). Any adjustment must include a one-sentence rationale in the report.

**Interpretation:**
- **10** — All checks pass, exemplary implementation
- **7-9** — Minor issues only (info-level)
- **4-6** — Has warnings that should be addressed
- **1-3** — Critical issues that prevent correct operation
- **0** — Category entirely missing

### Category Weights

| Weight Level | Numeric Value | Categories |
|-------------|--------------|------------|
| High | 3 | Structure, Version Sync, Workflow, Security |
| Medium | 2 | Platform Manifests, Skill Quality, Cross-References, Hooks, Testing |
| Low | 1 | Documentation |

**Overall score** = `sum(score_i × weight_i) / sum(weight_i)` (total weight = 23).

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
| S10 | Info | Agent files in `agents/` are self-contained — body includes complete execution protocol, not just a pointer to an external file |
| S11 | Warning | Skills that dispatch agents do not duplicate the agent's execution details (scoring formulas, report format, process steps). Agent file is the single source of truth |
| S12 | Info | Skill inline fallback blocks (handling "subagent unavailable") reference the corresponding agent file (`agents/*.md`) rather than re-implementing the execution logic |
| S13 | Info | Each skill-agent pair has clear responsibility separation — skill handles orchestration (scope detection, dispatch, result composition), agent handles execution (checks, scoring, reporting) |

---

## Category 2: Platform Manifests (Weight: Medium)

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
| V5 | Warning | `scripts/bump_version.py` exists |
| V6 | Info | `python scripts/bump_version.py --check` exits 0 |
| V7 | Info | `python scripts/bump_version.py --audit` finds no undeclared version strings |

**Quick drift check:**
```bash
python scripts/bump_version.py --check
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
| Q13 | Warning/Info | Token budget: bootstrap skill body ≤ 200 lines (warning); regular skill reports estimated token count when high (info) |
| Q14 | Warning | `allowed-tools` frontmatter references scripts/paths that actually exist |
| Q15 | Info | Conditional blocks (`If ... unavailable` etc.) over 30 lines should be in `references/` |
| Q16 | Info | Non-bootstrap skills have an `## Inputs` section |
| Q17 | Info | Non-bootstrap skills have an `## Outputs` section |

**Description anti-patterns (Q6):**
- Contains step-by-step workflow → agents shortcut to description
- Uses phrases like "first... then... finally..."
- Describes what the skill does instead of when to use it

---

## Category 5: Cross-References (Weight: Medium)

Static link resolution — verifies that references within skill content point to existing targets. For workflow graph analysis (cycles, reachability, artifact handoff), see `references/workflow-checklist.md` (W1-W12).

| Check | Severity | Criteria |
|-------|----------|----------|
| X1 | Warning | All `<project>:<skill-name>` references resolve to existing skills |
| X2 | Warning | No broken relative-path references to supporting files |
| X3 | Warning | Text references to subdirectories (`references/`, `templates/`, etc.) match actual skill directory contents |

**How to check:**
1. Extract all `<project>:<name>` patterns from all SKILL.md files
2. Verify each `<name>` matches a directory under `skills/`
3. Extract all relative file references and verify they exist
4. Scan for prose references to subdirectories and verify they exist
5. Run `python scripts/lint_skills.py --json` — X1-X3 findings are in per-skill results

**Workflow graph checks (W1-W12)** have been moved to a dedicated category. See `references/workflow-checklist.md` and run `python scripts/audit_workflow.py` for workflow-specific analysis.

---

## Category 6: Workflow (Weight: High)

See `references/workflow-checklist.md` for the full W1-W12 checklist covering three layers: Static Structure (W1-W5), Semantic Interface (W6-W10), and Behavioral Verification (W11-W12).

---

## Category 7: Hooks (Weight: Medium)

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

## Category 8: Testing (Weight: Medium)

| Check | Severity | Criteria |
|-------|----------|----------|
| T1 | Warning | `tests/` directory exists |
| T2 | Info | At least one test per target platform |
| T3 | Info | Tests verify skill discovery (skills appear in available list) |
| T4 | Info | Tests verify bootstrap injection (session-start content loads) |
| T5 | Warning | Each skill has a test prompts file (`tests/prompts/<skill-name>.yml` or `skills/<name>/tests/prompts.yml`) |
| T6 | Info | Test prompts include both should-trigger and should-not-trigger samples |
| T7 | Info | Test prompts cover all major branch paths of the skill |
| T8 | Warning | Most recent A/B eval result exists in `.bundles-forge/` |
| T9 | Info | Most recent chain eval result exists in `.bundles-forge/` |

---

## Category 9: Documentation (Weight: Low)

| Check | Severity | Criteria |
|-------|----------|----------|
| D1 | Warning | README contains install instructions for each target platform |
| D2 | Warning | README lists all skills with descriptions |
| D3 | Info | Each non-marketplace platform has a dedicated install doc |
| D4 | Info | CLAUDE.md exists with contributor guidelines |
| D5 | Info | AGENTS.md exists and points to CLAUDE.md |

---

## Category 10: Security (Weight: High)

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

## Audit Report Templates

After running all checks, compile findings using the appropriate report template:

- **Full project audit:** `references/report-template.md` — six-layer structure for 10-category audits
- **Single skill audit:** `references/skill-report-template.md` — three-layer structure for 4-category audits (see `references/skill-checklist.md` for the 4-category checklist)
- **Workflow audit:** `references/workflow-report-template.md` — three-layer structure for W1-W12 workflow checks

All templates include Go/No-Go decision logic, quantified impact scales, and confidence levels.
