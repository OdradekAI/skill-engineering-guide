# Audit Checklist

> Tables in this file are auto-generated from `audit-checks.json` by `generate_checklists.py`. Do not edit table rows directly.

Structured criteria for evaluating a bundle-plugin. Each category has specific checks with severity levels and automation status. Use this when running an audit — work through each category, note findings, and compile the report.

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

<!-- BEGIN:structure -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| S1 | Critical | `skills/` and `hooks/` directories exist | `audit_plugin.py` |
| S2 | Warning | At least one platform manifest directory present | `audit_plugin.py` |
| S3 | Warning | `.gitignore` exists | `audit_plugin.py` |
| S5 | Warning | `README.md` exists | `audit_plugin.py` |
| S6 | Info | `LICENSE` exists | `audit_plugin.py` |
| S7 | Warning | Bootstrap skill (`using-*`) exists with `SKILL.md` | `audit_plugin.py` |
| S8 | Warning | Skill-agent responsibility boundary: skills handle orchestration (scope detection, dispatch, result composition), agents handle execution (checks, scoring, reporting). No duplication of execution details — agent file is the single source of truth | `agent-only` |
| S9 | Info | Skill directory names match `name` field in SKILL.md frontmatter | `audit_skill.py` |
| S10 | Info | Agent files in `agents/` are self-contained — body includes complete execution protocol (≥5 non-empty body lines), not just a pointer | `audit_skill.py` |
| S11 | Warning | Writable agents (those without `disallowedTools: Edit` or `disallowedTools: Write`) have `isolation: "worktree"` set to prevent main working tree conflicts | `agent-only` |
| S12 | Info | Skill inline fallback blocks (handling "subagent unavailable") reference the corresponding agent file (`agents/*.md`) rather than re-implementing the execution logic | `audit_skill.py` |
<!-- END:structure -->

---

## Category 2: Platform Manifests (Weight: Medium)

Run these checks only for platforms the project claims to support.

<!-- BEGIN:platform_manifests -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| P1 | Critical | Each target platform has its manifest file present | `agent-only` |
| P2 | Critical | Manifest JSON is valid (parseable, no syntax errors) | `audit_plugin.py` |
| P3 | Critical | Cursor manifest paths (`skills`, `hooks`) resolve to existing directories/files | `audit_plugin.py` |
| P4 | Warning | Manifest metadata (name, version, description) is filled in | `agent-only` |
| P5 | Warning | Author and repository fields are populated | `agent-only` |
| P6 | Warning | OpenCode `.js` plugin files contain `module.exports` or `export` statement | `audit_plugin.py` |
| P7 | Info | `claude plugin validate` (or `/plugin validate`) passes without errors — quick schema check for `plugin.json`, frontmatter, and `hooks.json` (Claude Code environments only) | `agent-only` |
<!-- END:platform_manifests -->

**Script ID mapping:** `audit_plugin.py` emits M1 (JSON parse), M2 (path resolve), M3 (OpenCode exports). These map to P2, P3, and OpenCode-specific validation respectively.

**Platform manifest locations:**
- Claude Code: `.claude-plugin/plugin.json`
- Cursor: `.cursor-plugin/plugin.json`
- OpenCode: `.opencode/plugins/<name>.js`
- Codex: `.codex/INSTALL.md`
- Gemini: `gemini-extension.json`

---

## Category 3: Version Sync (Weight: High)

<!-- BEGIN:version_sync -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| V1 | Critical | `.version-bump.json` exists and is valid | `audit_plugin.py` |
| V2 | Warning | All files listed in `.version-bump.json` actually exist | `audit_plugin.py` |
| V3 | Critical | All listed files have the same version string (no drift) | `audit_plugin.py` |
| V5 | Warning | Every platform manifest is listed in `.version-bump.json` | `agent-only` |
| V6 | Info | `bundles-forge bump-version --check` exits 0 | `agent-only` |
| V7 | Info | `bundles-forge bump-version --audit` finds no undeclared version strings | `agent-only` |
<!-- END:version_sync -->

**Quick drift check:**
```bash
bundles-forge bump-version --check
```

---

## Category 4: Skill Quality (Weight: Medium)

Run for every SKILL.md in the project.

<!-- BEGIN:skill_quality -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| Q1 | Critical | YAML frontmatter present (between `---` delimiters) | `audit_skill.py` |
| Q2 | Critical | `name` field exists in frontmatter | `audit_skill.py` |
| Q3 | Critical | `description` field exists in frontmatter | `audit_skill.py` |
| Q4 | Warning | `name` uses only letters, numbers, hyphens | `audit_skill.py` |
| Q5 | Warning | `description` starts with "Use when..." | `audit_skill.py` |
| Q6 | Warning | `description` describes triggering conditions, not workflow summary | `audit_skill.py` |
| Q7 | Warning | `description` is under 250 characters (truncated in skill listing beyond this) | `audit_skill.py` |
| Q8 | Warning | Frontmatter total under 1024 characters | `audit_skill.py` |
| Q9 | Warning | SKILL.md body under 500 lines | `audit_skill.py` |
| Q10 | Info | Skill has Overview section | `audit_skill.py` |
| Q11 | Info | Skill has Common Mistakes section | `audit_skill.py` |
| Q12 | Info | Heavy reference content (100+ lines) extracted to supporting files | `audit_skill.py` |
| Q13 | Warning/Info | Token budget: bootstrap skill body ≤ 200 lines (warning); regular skill reports estimated token count when high (info) | `audit_skill.py` |
| Q14 | Warning | `allowed-tools` frontmatter references scripts/paths that actually exist | `audit_skill.py` |
| Q15 | Info | Conditional blocks (`If ... unavailable` etc.) over 30 lines should be in `references/` | `audit_skill.py` |
<!-- END:skill_quality -->

**Description anti-patterns (Q6):**
- Contains step-by-step workflow → agents shortcut to description
- Uses phrases like "first... then... finally..."
- Describes what the skill does instead of when to use it

**Cross-skill consistency (C1):** When ≥2 skills exist, `audit_skill.py` checks structural consistency across skills — mixed Overview presence, inconsistent subagent fallback patterns, and mixed verb forms after "Use when". Reported as a single C1 finding with sub-items.

---

## Category 5: Cross-References (Weight: Medium)

Static link resolution — verifies that references within skill content point to existing targets. For workflow graph analysis (cycles, reachability, artifact handoff), see `references/workflow-checklist.md`.

<!-- BEGIN:cross_references -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| X1 | Warning | All `<project>:<skill-name>` references resolve to existing skills | `audit_skill.py` |
| X2 | Warning | No broken relative-path references to supporting files | `audit_skill.py` |
| X3 | Warning | Text references to subdirectories (`references/`, `templates/`, etc.) match actual skill directory contents | `audit_skill.py` |
| X4 | Info | No orphan files in `references/` — every `.md` and `.json` file is referenced by `SKILL.md` or a sibling reference file | `audit_skill.py` |
<!-- END:cross_references -->

**How to check:**
1. Extract all `<project>:<name>` patterns from all SKILL.md files
2. Verify each `<name>` matches a directory under `skills/`
3. Extract all relative file references and verify they exist
4. Scan for prose references to subdirectories and verify they exist
5. Run `bundles-forge audit-skill --json` — X1-X3 findings are in per-skill results

**Workflow graph checks** have been moved to a dedicated category. See `references/workflow-checklist.md` and run `bundles-forge audit-workflow` for workflow-specific analysis.

---

## Category 6: Workflow (Weight: High)

See `references/workflow-checklist.md` for the full checklist covering three layers: Static Structure (W1-W5), Semantic Interface (W6-W9), and Behavioral Verification (W10-W11).

---

## Category 7: Hooks (Weight: Medium)

Functional correctness checks for session bootstrap hooks. Security-related hook checks (HTTP hooks, env injection, network calls) are in Category 10 via `references/security-checklist.md` (HK13-HK15).

<!-- BEGIN:hooks -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| H1 | Warning | `hooks/` directory exists | `audit_plugin.py` |
| H2 | Warning | `hooks/session-start.py` exists | `audit_plugin.py` |
| H3 | Warning | `session-start.py` references SKILL.md | `audit_plugin.py` |
| H6 | Warning | `session-start.py` handles all target platforms (three-way: CURSOR_PLUGIN_ROOT, CLAUDE_PLUGIN_ROOT, fallback) | `agent-only` |
| H7 | Warning | JSON escaping is correct (backslashes, quotes, newlines, tabs) | `agent-only` |
| H8 | Info | Hook configs invoke `python` with `hooks/session-start.py` (cross-platform; no Git Bash or `.cmd` shim) | `agent-only` |
| H9 | Info | `hooks.json` includes top-level `description` field and per-handler `timeout` | `audit_plugin.py` |
| H12 | Info | `session-start.py` exits 0 on read failure (no-op, does not block session) | `agent-only` |
<!-- END:hooks -->

**Quick hook test:**
```bash
CLAUDE_PLUGIN_ROOT="$(pwd)" python hooks/session-start.py | python -m json.tool
```

---

## Category 8: Testing (Weight: Medium)

<!-- BEGIN:testing -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| T1 | Warning | `tests/` directory exists | `audit_plugin.py` |
| T2 | Info | At least one test per target platform | `agent-only` |
| T3 | Info | Tests verify skill discovery (skills appear in available list) | `agent-only` |
| T4 | Info | Tests verify bootstrap injection (`session-start.py` output / content loads) | `agent-only` |
| T5 | Warning | Each skill has a test prompts file (`tests/prompts/<skill-name>.yml` or `skills/<name>/tests/prompts.yml`) | `audit_plugin.py` |
| T6 | Info | Test prompts include both should-trigger and should-not-trigger samples | `agent-only` |
| T7 | Info | Test prompts cover all major branch paths of the skill | `agent-only` |
| T8 | Info | Most recent A/B eval result exists in `.bundles-forge/` | `audit_plugin.py` |
| T9 | Info | Most recent chain eval result exists in `.bundles-forge/` | `audit_plugin.py` |
<!-- END:testing -->

---

## Category 9: Documentation (Weight: Low)

Documentation consistency checks — verifies that project docs stay in sync with actual project state.

<!-- BEGIN:documentation -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| D1 | Warning | Skill names in AGENTS.md / CLAUDE.md / README match skills/ directory | `audit_docs.py` |
| D2 | Critical | Cross-references (`project:skill`) in all .md files resolve to existing skills | `audit_docs.py` |
| D3 | Warning | CLAUDE.md Platform Manifests table matches `.version-bump.json` | `audit_docs.py` |
| D4 | Critical | Skill scripts referenced in CLAUDE.md exist at their declared `skills/.../scripts/` paths | `audit_docs.py` |
| D5 | Warning | Agent names in CLAUDE.md match agents/ directory | `audit_docs.py` |
| D6 | Warning | README.md and README.zh.md hard data (skills, agents, commands, links) in sync | `audit_docs.py` |
| D7 | Warning | docs/*.md and docs/*.zh.md pairs have consistent hard data (tables, commands, links) | `audit_docs.py` |
| D8 | Warning | Each docs/*.md guide has a `> **Canonical source:**` declaration pointing to an existing skill or agent file | `audit_docs.py` |
| D9 | Warning | Key numbers in docs/*.md guides match their canonical source (e.g., attack surface count, category count, target count) | `audit_docs.py` |
<!-- END:documentation -->

---

## Category 10: Security (Weight: High)

Run security checks on all executable code, agent instructions, and hook scripts. See `references/security-checklist.md` for the full pattern list organized by 7 attack surfaces:

1. **SKILL.md Content** (SC1-SC14) — sensitive files, destructive commands, safety overrides, encoding tricks
2. **Hook Scripts** (HK1-HK15) — network calls, env vars, system modification, HTTP hooks, env injection
3. **OpenCode Plugins** (OC1-OC13) — code execution, network access, sensitive data, message manipulation
4. **Agent Prompts** (AG1-AG7) — safety overrides, credentials, network, scope expansion
5. **Bundled Scripts** (BS1-BS6) — network, system modification, sensitive data
6. **MCP Configuration** (MC1-MC5) — hardcoded credentials, command execution, plain HTTP
7. **Plugin Configuration** (PC1-PC7) — path traversal, userConfig, persistent data

Each surface has a legitimate baseline documenting expected behavior.

**Quick check:** Grep for high-risk patterns across all executable files:
```
curl|wget|nc |eval\(|child_process|\.env|api_key|secret|ignore safety|override|bypass
```

---

## Audit Report Templates

After running all checks, compile findings using the appropriate report template:

- **Full project audit:** `references/plugin-report-template.md` — six-layer structure for 10-category audits
- **Single skill audit:** `references/skill-report-template.md` — three-layer structure for 4-category audits (see `references/skill-checklist.md` for the 4-category checklist)
- **Workflow audit:** `references/workflow-report-template.md` — three-layer structure for workflow checks

All templates include Go/No-Go decision logic, quantified impact scales, and confidence levels.
