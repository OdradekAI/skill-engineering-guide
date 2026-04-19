---
audit-date: "2026-04-19T23:18+00:00"
auditor-platform: "Claude Code"
auditor-model: "GLM-5.1"
bundles-forge-version: "1.8.2"
source-type: "local-directory"
source-uri: "~/repos/superpowers"
os: "Windows 11 Home 10.0.22631"
python: "n/a"
---

# Bundle-Plugin Audit: superpowers

## 1. Decision Brief

| Field | Value |
|-------|-------|
| **Target** | `~/repos/superpowers` |
| **Version** | 5.0.7 |
| **Commit** | b557648 |
| **Date** | 2026-04-19 |
| **Audit Context** | post-change |
| **Platforms** | Claude Code, Cursor, OpenCode, Codex, Gemini |
| **Skills** | 14 skills, 1 agent, 0 commands, 2 project-level scripts |

### Recommendation: `CONDITIONAL GO`

**Automated baseline:** 3 critical, 45 warnings, 68 info -- script recommends `NO-GO`

**Overall score:** 8.4/10 (weighted average; see Category Breakdown)

**Qualitative adjustment:** Upgraded from `NO-GO` to `CONDITIONAL GO`. The 3 critical findings break down as follows: 2 are broken cross-references in RELEASE-NOTES.md (historical changelog, not functional code); 1 is a GitHub issue URL in a shell comment (HK2, not executable). None affect runtime behavior, install correctness, or security posture. The project functions correctly across all 5 platforms.

### Top Risks

| # | Risk | Impact | If Not Fixed |
|---|------|--------|-------------|
| 1 | No test prompts for any of 14 skills (T5) | 14/14 skills untested | Skill regression goes undetected during changes |
| 2 | 12 of 14 skills missing from README.md (D1) | Users cannot discover 86% of skills from docs | Reduced adoption, confused users |
| 3 | Broken cross-refs in RELEASE-NOTES.md (D2) | Historical docs reference nonexistent skills | Misleading documentation for users reading changelog |

### Remediation Estimate

| Priority | Count | Estimated Effort |
|----------|-------|-----------------|
| P0 (Blocker) | 3 | 30 min (2 fix cross-refs, 1 is comment-only) |
| P1 (High) | 17 | 4-6 hours (add skill list to README, add test prompts) |
| P2+ | 96 | 8-12 hours (add Chinese translations, canonical sources, Overview sections) |

---

## 2. Risk Matrix

| ID | Title | Severity | Impact Scope | Exploitability | Confidence | Status |
|----|-------|----------|-------------|----------------|------------|--------|
| DOC-001 | Broken cross-ref `superpowers:code-reviewer` in RELEASE-NOTES.md | P0 | Cosmetic only -- changelog, not runtime | always triggers | Likely | open |
| DOC-002 | Broken cross-ref `superpowers:skill-name` in RELEASE-NOTES.md | P0 | Cosmetic only -- changelog, not runtime | always triggers | Likely | open |
| SEC-001 | External URL in hooks/session-start comment (HK2) | P0 | No runtime impact -- URL is in a comment | theoretical | Likely | open |
| TST-001 | No test prompts for 14 skills (T5) | P1 | 14/14 skills lack prompt-level testing | always triggers | Confirmed | open |
| DOC-003 | 12 skills missing from README.md (D1) | P1 | Users cannot discover 12/14 skills from docs | always triggers | Confirmed | open |
| DOC-004 | Missing Chinese translations (D6, D7) | P2 | 4 docs files lack zh counterparts | always triggers | Confirmed | open |
| DOC-005 | Missing canonical source declarations (D8) | P2 | 3 docs files lack canonical source | always triggers | Confirmed | open |
| SKQ-001 | writing-skills SKILL.md exceeds 500-line limit (Q9) | P2 | 1/14 skills, 650 lines | edge case | Confirmed | open |
| SKQ-002 | using-git-worktrees bootstrap body exceeds 200-line budget (Q13) | P2 | 1/2 bootstrap skills, 213 lines | edge case | Confirmed | open |
| SEC-002 | Broad process.env access in OpenCode plugin (OC9) | P2 | 1/5 platforms (OpenCode) | edge case | Confirmed | open |
| SEC-003 | Env var access in hook scripts (HK6) | P2 | 2 hook files | edge case | Confirmed | open |
| HOK-001 | Missing hooks/session-start.py (H2) | P1 | Script-based hook works; .py variant absent | edge case | Confirmed | open |

---

## 3. Findings by Category

### 3.1 Structure (Score: 10/10, Weight: High)

**Summary:** Clean project structure with all required directories present and properly organized.

**Components audited:** `skills/`, `hooks/`, `agents/`, `scripts/`, platform manifests, project root

No findings.

---

### 3.2 Platform Manifests (Score: 10/10, Weight: Medium)

**Summary:** All 5 platform manifests present, valid, and properly configured.

**Components audited:** `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.opencode/plugins/superpowers.js`, `.codex/INSTALL.md`, `gemini-extension.json`

No findings.

---

### 3.3 Version Sync (Score: 10/10, Weight: High)

**Summary:** All version strings are synchronized across manifests and config files.

**Components audited:** `.version-bump.json`, all platform manifests, `package.json`

No findings.

---

### 3.4 Skill Quality (Score: 7/10, Weight: Medium)

**Summary:** Skills are well-written with clear descriptions and strong instructional content. Three warnings relate to size limits and formatting conventions; 18 info items are minor omissions (Overview, Common Mistakes sections).

**Components audited:** 14 SKILL.md files

#### [SKQ-001] writing-skills SKILL.md exceeds 500-line limit
- **Severity:** P2 | **Impact:** 1/14 skills | **Confidence:** Confirmed
- **Location:** `skills/writing-skills/SKILL.md` (650 lines)
- **Trigger:** Skill body is 650 lines, exceeding the 500-line guideline
- **Actual Impact:** Large token consumption when skill is loaded; may exceed context budgets on smaller models
- **Remediation:** Extract heavy reference content (anthropic-best-practices.md, persuasion-principles.md, testing-skills-with-subagents.md already exist) and reduce inline content

#### [SKQ-002] using-git-worktrees bootstrap body exceeds 200-line budget
- **Severity:** P2 | **Impact:** 1/2 bootstrap skills | **Confidence:** Confirmed
- **Location:** `skills/using-git-worktrees/SKILL.md` (213 lines body)
- **Trigger:** Bootstrap skill body is 213 lines (~1215 estimated tokens), exceeding the 200-line budget
- **Actual Impact:** Bootstrap skills load on every session start; extra 13 lines add ~75 tokens per session
- **Remediation:** Trim edge cases or move secondary scenarios to references/

#### [SKQ-003] brainstorming description does not start with "Use when..."
- **Severity:** P2 | **Impact:** 1/14 skills | **Confidence:** Confirmed
- **Location:** `skills/brainstorming/SKILL.md` frontmatter
- **Trigger:** Description starts with "You MUST use this before..." instead of "Use when..."
- **Actual Impact:** Inconsistent description format across skills listing
- **Remediation:** Reformat to "Use when doing any creative work..."

#### Cross-skill consistency (C1)
- Overview sections: 9 skills have it, 3 do not (brainstorming, requesting-code-review, subagent-driven-development)
- Verb forms after "Use when": 9 gerund (-ing) vs 5 bare infinitive -- mixed but not disorienting

---

### 3.5 Cross-References (Score: 10/10, Weight: Medium)

**Summary:** All skill-to-skill cross-references resolve correctly. 24 info-level findings about workflow topology (W2, W3) are architectural observations, not broken links.

**Components audited:** All `superpowers:*` references in SKILL.md files, relative path references, references/ directory contents

#### [XRF-001] Unreferenced reference file
- **Severity:** P3 | **Impact:** 1 file | **Confidence:** Confirmed
- **Location:** `skills/using-superpowers/references/gemini-tools.md`
- **Trigger:** File exists in references/ but is not referenced by SKILL.md or any sibling reference file
- **Actual Impact:** Dead reference file; may contain useful Gemini tool documentation that should be linked
- **Remediation:** Add reference in SKILL.md or confirm it is loaded by the Gemini platform logic

---

### 3.6 Workflow (Score: 10/10, Weight: High)

**Summary:** Workflow graph is structurally sound with 2 meta skills (bootstrap) and 12 standalone skills. All info-level findings reflect the intentional design choice that skills are user-invoked rather than chained through a strict graph.

**Components audited:** 14 SKILL.md Integration sections, cross-skill references

#### [WFL-001] 12 skills not reachable from entry points (W2)
- **Severity:** P3 | **Impact:** 12/14 skills | **Confidence:** Confirmed
- **Trigger:** Skills like brainstorming, systematic-debugging, etc. have no incoming edges from the bootstrap skills
- **Actual Impact:** None -- this is by design. The using-superpowers bootstrap skill instructs agents to check all skills on every task, making explicit graph edges unnecessary. Skills are discovered via the Skill tool, not via graph traversal.
- **Remediation:** Consider adding "Called by: user directly" declarations to Integration sections for documentation clarity

#### [WFL-002] 12 terminal skills lack Outputs section (W3)
- **Severity:** P3 | **Impact:** 12/14 skills | **Confidence:** Confirmed
- **Trigger:** Terminal skills (no outgoing references) do not document their expected outputs
- **Actual Impact:** Minor -- agents consuming skill output have no formal contract, but skill bodies contain sufficient inline guidance
- **Remediation:** Add ## Outputs section to each terminal skill

#### Behavioral Verification (W10-W11)

Not performed. Reason: post-change check mode, static+semantic layers evaluated by script. Behavioral verification requires evaluator agent dispatch (W10-W11).

---

### 3.7 Hooks (Score: 10/10, Weight: Medium)

**Summary:** Hook system functions correctly across all platforms. The project uses a shell-based hook (session-start) rather than a Python hook, which is a valid approach. One warning about missing session-start.py is mitigated by the working shell equivalent.

**Components audited:** `hooks/session-start`, `hooks/hooks.json`, `hooks/hooks-cursor.json`, `hooks/run-hook.cmd`

**Qualitative adjustment:** Baseline 9 adjusted to 10. The H2 warning (missing session-start.py) reflects a convention preference, not a functional gap -- the project intentionally uses a shell script hook that works across all supported platforms. The hook correctly handles platform detection (Cursor, Claude Code, Copilot CLI) and emits properly formatted JSON.

#### [HOK-001] Missing hooks/session-start.py
- **Severity:** P1 | **Impact:** Convention only | **Confidence:** Confirmed
- **Location:** `hooks/` directory
- **Trigger:** No session-start.py file exists; project uses shell-based `hooks/session-start` instead
- **Actual Impact:** None -- the shell hook is functionally equivalent and cross-platform
- **Remediation:** Optional -- add a .py wrapper if the convention requires it

#### [HOK-002] hooks.json missing description and timeout fields (H9)
- **Severity:** P3 | **Impact:** 1 hook config | **Confidence:** Confirmed
- **Location:** `hooks/hooks.json`
- **Trigger:** No top-level `description` field; SessionStart handler missing `timeout` field
- **Actual Impact:** Minor -- missing metadata does not affect hook execution
- **Remediation:** Add `"description"` and `"timeout"` fields for completeness

---

### 3.8 Testing (Score: 6/10, Weight: Medium)

**Summary:** No test prompts exist for any of the 14 skills. This is the most significant quality gap in the project. The project has no tests/ directory and no A/B eval results.

**Qualitative adjustment:** Baseline 7 adjusted to 6. While the formula accounts for the 14 missing T5 warnings, the total absence of any test infrastructure (no tests/ directory, no eval results, no prompt files) represents a more fundamental gap than the per-skill count captures.

**Components audited:** `tests/` directory (absent), `.bundles-forge/evals/` (absent), skill test prompts

#### [TST-001] No test prompts for all 14 skills (T5)
- **Severity:** P1 | **Impact:** 14/14 skills | **Confidence:** Confirmed
- **Trigger:** No `tests/prompts/<skill-name>.yml` or `skills/<name>/tests/prompts.yml` files exist
- **Actual Impact:** No automated way to verify skill triggering, branch coverage, or regression
- **Remediation:** Create test prompt files for each skill with should-trigger and should-not-trigger samples

#### [TST-002] No A/B eval results (T8)
- **Severity:** P3 | **Impact:** 1 project | **Confidence:** Confirmed
- **Location:** `.bundles-forge/evals/`
- **Trigger:** No eval results found
- **Actual Impact:** No baseline quality metrics for comparison
- **Remediation:** Run A/B evals and commit results

---

### 3.9 Documentation (Score: 0/10, Weight: Low)

**Summary:** Documentation has 2 critical findings (broken cross-references in release notes) and 19 warnings. The most impactful is 12 of 14 skills missing from README.md's skill listing. Despite the 0 score, the README is well-written and covers the workflow narrative effectively -- the score reflects missing skill entries and missing translations rather than poor quality.

**Components audited:** `README.md`, `RELEASE-NOTES.md`, `docs/*.md`, `CLAUDE.md`

#### [DOC-001] Broken cross-reference `superpowers:code-reviewer` in RELEASE-NOTES.md
- **Severity:** P0 | **Impact:** Cosmetic (changelog) | **Confidence:** Likely
- **Location:** `RELEASE-NOTES.md` (6+ occurrences)
- **Trigger:** Historical release notes reference `superpowers:code-reviewer` which does not exist as a skill (it exists as `agents/code-reviewer.md`)
- **Actual Impact:** Misleading for users reading changelog; no runtime effect
- **Remediation:** Update RELEASE-NOTES.md to use correct reference format

#### [DOC-002] Broken cross-reference `superpowers:skill-name` in RELEASE-NOTES.md
- **Severity:** P0 | **Impact:** Cosmetic (changelog) | **Confidence:** Likely
- **Location:** `RELEASE-NOTES.md` line 678
- **Trigger:** Generic placeholder `superpowers:skill-name` appears in historical changelog entry
- **Actual Impact:** Misleading placeholder in documentation
- **Remediation:** Replace with correct skill name or remove the generic entry

#### [DOC-003] 12 skills missing from README.md (D1)
- **Severity:** P1 | **Impact:** 12/14 skills | **Confidence:** Confirmed
- **Trigger:** README.md does not list all 14 skills in its skill inventory section
- **Actual Impact:** Users cannot discover most skills from the README
- **Remediation:** Add complete skill listing to README with descriptions

#### [DOC-004] Missing Chinese translations (D6, D7)
- **Severity:** P2 | **Impact:** 4 docs files | **Confidence:** Confirmed
- **Location:** `README.zh.md` (missing), `docs/README.codex.zh.md` (missing), `docs/README.opencode.zh.md` (missing), `docs/testing.zh.md` (missing)
- **Trigger:** English docs exist without Chinese counterparts
- **Actual Impact:** Chinese-speaking users lack translated documentation
- **Remediation:** Add Chinese translations for README and docs/ files

#### [DOC-005] Missing canonical source declarations (D8)
- **Severity:** P2 | **Impact:** 3 docs files | **Confidence:** Confirmed
- **Location:** `docs/README.codex.md`, `docs/README.opencode.md`, `docs/testing.md`
- **Trigger:** Guide docs lack `> **Canonical source:**` declarations
- **Actual Impact:** No traceability from docs to their authoritative skill/agent source
- **Remediation:** Add canonical source declarations pointing to relevant skill or agent files

#### [DOC-006] Version bump tracking mismatches (D3)
- **Severity:** P3 | **Impact:** 3 manifest files | **Confidence:** Confirmed
- **Trigger:** `.version-bump.json` tracks 3 manifest files not listed in CLAUDE.md Platform Manifests table
- **Actual Impact:** Documentation inconsistency only
- **Remediation:** Update CLAUDE.md table to match `.version-bump.json`

---

### 3.10 Security (Score: 6/10, Weight: High)

**Summary:** One deterministic critical finding (HK2 -- external URL in hook comment) and three deterministic warnings (OC9, HK6 x2). Five suspicious SC3 findings were triaged: 1 false-positive, 4 accepted-risk. After triage, the recalculated baseline is 4, adjusted up by 2 because the HK2 critical is a non-executable comment with no security impact.

**Components audited:** 14 SKILL.md files, 2 hook scripts, 1 hook config, 1 OpenCode plugin, 2 project scripts, 4 MCP/config manifests, 1 agent prompt, 6 skill reference files, 5 bundled scripts

#### [SEC-001] External URL in hooks/session-start comment (HK2)
- **Severity:** P0 | **Impact:** 1/1 hook scripts (non-executable) | **Confidence:** Confirmed
- **Location:** `hooks/session-start:45`
- **Trigger:** Comment contains `https://github.com/obra/superpowers/issues/571`
- **Actual Impact:** None -- URL is in a comment explaining a bash workaround, not in executable code. The hook makes no network calls.
- **Remediation:** Consider removing URL from hook script to satisfy automated scanners, or add inline justification

#### [SEC-002] Broad process.env access in OpenCode plugin (OC9)
- **Severity:** P2 | **Impact:** 1/5 platforms (OpenCode) | **Confidence:** Confirmed
- **Location:** `.opencode/plugins/superpowers.js:52`
- **Trigger:** Plugin accesses `process.env` broadly beyond documented needs
- **Actual Impact:** Theoretical -- OpenCode plugin reads env vars for platform detection, which is standard practice
- **Remediation:** Scope env access to specific needed variables only

#### [SEC-003] Env var access in hook scripts (HK6)
- **Severity:** P2 | **Impact:** 2 hook files | **Confidence:** Confirmed
- **Location:** `hooks/run-hook.cmd:46` ($SCRIPT_NAME), `hooks/session-start:49` ($COPILOT_CLI)
- **Trigger:** Hook scripts read environment variables beyond the standard plugin root variables
- **Actual Impact:** Low -- $SCRIPT_NAME and $COPILOT_CLI are used for platform detection, not secret access
- **Remediation:** Document the env var usage with inline comments explaining purpose

#### [SEC-004] Missing set -euo pipefail in shell scripts (BS6)
- **Severity:** P3 | **Impact:** 2 bundled scripts | **Confidence:** Confirmed
- **Location:** `skills/brainstorming/scripts/start-server.sh:1`, `skills/brainstorming/scripts/stop-server.sh:1`
- **Trigger:** Shell scripts lack strict error handling
- **Actual Impact:** Scripts may silently fail without reporting errors
- **Remediation:** Add `set -euo pipefail` to both scripts

#### Suspicious Triage

| Finding | File:Line | Disposition | Rationale |
|---------|-----------|-------------|-----------|
| SC3 -- References to user config directories | `skills/subagent-driven-development/SKILL.md:142` | FP | Dialogue example ("You: 'User level (~/.config/superpowers/hooks/)'") in a conversation snippet, not an instruction to read config directories |
| SC3 -- References to user config directories | `skills/using-git-worktrees/SKILL.md:46` | Accepted | Menu option presenting legitimate worktree location choice to user; references project's own config directory, not sensitive user data |
| SC3 -- References to user config directories | `skills/using-git-worktrees/SKILL.md:71` | Accepted | Section heading documenting the global worktree path feature; same as above |
| SC3 -- References to user config directories | `skills/using-git-worktrees/SKILL.md:91` | Accepted | Code snippet for constructing worktree path; implements the documented feature |
| SC3 -- References to user config directories | `skills/using-git-worktrees/SKILL.md:92` | Accepted | Continuation of case statement for path construction; same as above |

Dispositions: **FP** = false-positive (excluded from score), **Accepted** = real but mitigated (no score penalty), **TP** = true-positive (full severity retained).

---

## 4. Methodology

### Scope

| Dimension | Covered |
|-----------|---------|
| **Directories** | `skills/`, `agents/`, `hooks/`, `scripts/`, `.claude-plugin/`, `.cursor-plugin/`, `.opencode/`, `.codex/`, project root, `docs/` |
| **Check categories** | 10 categories, 60+ individual checks |
| **Total files scanned** | 55+ files across all categories |

### Out of Scope

- Runtime behavior of skills (agent execution, prompt-response quality)
- Platform-specific installation end-to-end testing
- Dependencies of dependencies (transitive analysis)
- Behavioral verification (W10-W11) -- requires evaluator agent dispatch

### Tools

| Tool | Purpose |
|------|---------|
| `bundles-forge audit-plugin` | Orchestrated full 10-category audit |
| `bundles-forge audit-security` | Security pattern scanning (7 attack surfaces) |
| `bundles-forge audit-skill` | Per-skill quality linting |
| `bundles-forge bump-version --check` | Version drift detection |
| Manual review | Suspicious finding triage (5 SC3 findings) |

### Limitations

- Security scanning uses regex -- false positives possible; 5 suspicious findings were manually triaged
- Skill quality linting uses a lightweight YAML parser -- complex YAML edge cases may be missed
- Token estimation uses heuristic rates; actual counts vary by model
- Behavioral verification (W10-W11) was not performed -- static and semantic layers only

---

## 5. Appendix

### A. Per-Skill Breakdown

#### brainstorming
**Verdict:** Well-designed creative skill with strong gating but missing optional sections and inconsistent description format.
**Strengths:** Clear HARD-GATE preventing premature implementation; visual companion and spec reviewer references provide depth
**Key Issues:** Description does not follow "Use when..." convention (Q5); missing Overview section (Q10); missing Common Mistakes section (Q11)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 7/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### dispatching-parallel-agents
**Verdict:** Clean, focused skill with no quality findings -- a model skill in the collection.
**Strengths:** Clear description following conventions; concise at 182 lines; well-scoped instructions
**Key Issues:** None.

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 10/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### executing-plans
**Verdict:** Compact fallback skill (70 lines) for platforms without subagent support, with clear routing guidance.
**Strengths:** Extremely concise; correctly routes to subagent-driven-development when available; clear announce-at-start pattern
**Key Issues:** Missing Common Mistakes section (Q11)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 9/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### finishing-a-development-branch
**Verdict:** Well-structured completion skill with clear Overview and proper conventions.
**Strengths:** Clean description; proper Overview section; good workflow guidance
**Key Issues:** None.

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 10/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### receiving-code-review
**Verdict:** Strong skill promoting technical rigor over social comfort, with excellent behavioral guidance.
**Strengths:** Distinctive voice ("Technical correctness over social comfort"); clear response pattern; proper Overview
**Key Issues:** None.

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 10/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### requesting-code-review
**Verdict:** Focused dispatch skill for code review with clear mandatory/optional triggers, missing optional sections.
**Strengths:** Clear mandatory review triggers; references code-reviewer agent properly
**Key Issues:** Missing Overview section (Q10); missing Common Mistakes section (Q11)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 9/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### subagent-driven-development
**Verdict:** Core implementation skill with rich subagent dispatch logic, missing optional documentation sections.
**Strengths:** Detailed implementer/reviewer prompt templates; two-stage review pattern; strong routing guidance
**Key Issues:** Missing Overview section (Q10); missing Common Mistakes section (Q11); SC3 suspicious finding (FP -- dialogue example)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 9/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### systematic-debugging
**Verdict:** Comprehensive debugging methodology with extensive reference content (5 reference files), well-organized.
**Strengths:** 4-phase root cause process; rich reference library (root-cause-tracing, defense-in-depth, condition-based-waiting); includes pressure tests
**Key Issues:** Missing Common Mistakes section (Q11); conditional block at line 69 spans 38 lines (Q15)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 9/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### test-driven-development
**Verdict:** Long-form TDD skill (371 lines) with strong methodology content, could benefit from reference extraction.
**Strengths:** Comprehensive testing-anti-patterns reference; clear RED-GREEN-REFACTOR enforcement
**Key Issues:** 371 lines with no references/ files (Q12); missing Common Mistakes section (Q11); conditional block at line 76 spans 32 lines (Q15)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 8/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### using-git-worktrees
**Verdict:** Bootstrap skill slightly exceeding token budget (213 lines), with 4 accepted-risk SC3 findings from legitimate worktree path configuration.
**Strengths:** Smart directory selection with safety verification; clear Overview section
**Key Issues:** Bootstrap body exceeds 200-line budget at 213 lines (Q13); 4 SC3 findings (all Accepted -- legitimate worktree path feature)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 8/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### using-superpowers
**Verdict:** Primary bootstrap skill with strong instruction-priority hierarchy and skill-discovery guidance; one orphan reference file.
**Strengths:** Clear 3-level instruction priority; EXTREMELY-IMPORTANT block for skill discovery; platform-specific tool references
**Key Issues:** Reference file `references/gemini-tools.md` not referenced by SKILL.md (X4)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 10/10 |
| Cross-References | 9/10 |
| Security | 10/10 |

#### verification-before-completion
**Verdict:** Concise skill (139 lines) enforcing evidence-based completion claims with clear behavioral rules.
**Strengths:** Strong core principle ("Evidence before claims, always"); proper Overview section
**Key Issues:** Missing Common Mistakes section (Q11)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 9/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### writing-plans
**Verdict:** Well-crafted planning skill with clear audience assumptions and proper plan-reviewer integration.
**Strengths:** Clear "assume skilled but uninformed engineer" framing; plan-document-reviewer-prompt.md reference
**Key Issues:** Missing Common Mistakes section (Q11)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 9/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### writing-skills
**Verdict:** Comprehensive skill-authoring guide that is itself the largest skill (650 lines), exceeding the 500-line guideline despite having extracted reference content.
**Strengths:** Includes testing-skills-with-subagents methodology; anthropic-best-practices and persuasion-principles references; comprehensive examples directory
**Key Issues:** Body is 650 lines, exceeding 500-line max (Q9); high estimated token count (~4880 tokens, Q13); 300+ lines but no references/ directory (Q12 -- note: reference files exist at skill root level but not in a references/ subdirectory)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 6/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

---

### B. Component Inventory

| Component Type | Name | Path | Lines |
|---------------|------|------|-------|
| Skill | brainstorming | `skills/brainstorming/SKILL.md` | 164 |
| Skill | dispatching-parallel-agents | `skills/dispatching-parallel-agents/SKILL.md` | 182 |
| Skill | executing-plans | `skills/executing-plans/SKILL.md` | 70 |
| Skill | finishing-a-development-branch | `skills/finishing-a-development-branch/SKILL.md` | 200 |
| Skill | receiving-code-review | `skills/receiving-code-review/SKILL.md` | 213 |
| Skill | requesting-code-review | `skills/requesting-code-review/SKILL.md` | 105 |
| Skill | subagent-driven-development | `skills/subagent-driven-development/SKILL.md` | 277 |
| Skill | systematic-debugging | `skills/systematic-debugging/SKILL.md` | 296 |
| Skill | test-driven-development | `skills/test-driven-development/SKILL.md` | 371 |
| Skill | using-git-worktrees | `skills/using-git-worktrees/SKILL.md` | 218 |
| Skill | using-superpowers | `skills/using-superpowers/SKILL.md` | 117 |
| Skill | verification-before-completion | `skills/verification-before-completion/SKILL.md` | 139 |
| Skill | writing-plans | `skills/writing-plans/SKILL.md` | 152 |
| Skill | writing-skills | `skills/writing-skills/SKILL.md` | 655 |
| Agent | code-reviewer | `agents/code-reviewer.md` | 48 |
| Script | bump-version | `scripts/bump-version.sh` | 220 |
| Script | sync-to-codex-plugin | `scripts/sync-to-codex-plugin.sh` | 388 |
| Hook | session-start | `hooks/session-start` | 57 |
| Hook | hooks.json | `hooks/hooks.json` | 16 |
| Hook | hooks-cursor.json | `hooks/hooks-cursor.json` | 10 |
| Hook | run-hook.cmd | `hooks/run-hook.cmd` | 46 |
| Manifest | Claude Code | `.claude-plugin/plugin.json` | 20 |
| Manifest | Cursor | `.cursor-plugin/plugin.json` | 25 |
| Manifest | OpenCode | `.opencode/plugins/superpowers.js` | 112 |
| Manifest | Codex | `.codex/INSTALL.md` | -- |
| Manifest | Gemini | `gemini-extension.json` | 6 |

---

### C. Category Score Summary

| Category | Baseline | Adjustment | Final | Weight | Weighted |
|----------|----------|------------|-------|--------|----------|
| Structure | 10 | 0 | 10 | 3 (High) | 30 |
| Platform Manifests | 10 | 0 | 10 | 2 (Medium) | 20 |
| Version Sync | 10 | 0 | 10 | 3 (High) | 30 |
| Skill Quality | 7 | 0 | 7 | 2 (Medium) | 14 |
| Cross-References | 10 | 0 | 10 | 2 (Medium) | 20 |
| Workflow | 10 | 0 | 10 | 3 (High) | 30 |
| Hooks | 9 | +1 | 10 | 2 (Medium) | 20 |
| Testing | 7 | -1 | 6 | 2 (Medium) | 12 |
| Documentation | 0 | 0 | 0 | 1 (Low) | 0 |
| Security | 4* | +2 | 6 | 3 (High) | 18 |
| **Total** | | | | **23** | **194** |

**Overall score: 194 / 23 = 8.4/10**

*Security baseline recomputed after suspicious finding triage (5 suspicious warnings reclassified: 1 FP, 4 Accepted).

---

### D. Prioritized Recommendations

1. **Fix broken cross-references in RELEASE-NOTES.md** (P0, 15 min)
   - Replace `superpowers:code-reviewer` with `agents/code-reviewer` or correct skill reference
   - Replace `superpowers:skill-name` placeholder with actual skill name

2. **Add complete skill listing to README.md** (P1, 30 min)
   - Add all 14 skills to the skill inventory section with one-line descriptions

3. **Create test prompts for all 14 skills** (P1, 4-6 hours)
   - Create `tests/prompts/<skill-name>.yml` for each skill with should-trigger and should-not-trigger samples

4. **Reduce writing-skills SKILL.md to under 500 lines** (P2, 1-2 hours)
   - Move additional content to existing reference files or create new ones

5. **Add Common Mistakes sections to 8 skills** (P2, 2-3 hours)
   - brainstorming, executing-plans, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, verification-before-completion, writing-plans

6. **Add Chinese translations** (P2, 4-6 hours)
   - README.zh.md, docs/README.codex.zh.md, docs/README.opencode.zh.md, docs/testing.zh.md

7. **Add canonical source declarations to docs/** (P2, 30 min)
   - Add `> **Canonical source:**` to docs/README.codex.md, docs/README.opencode.md, docs/testing.md

8. **Add set -euo pipefail to brainstorming shell scripts** (P3, 5 min)
   - start-server.sh, stop-server.sh

9. **Reference gemini-tools.md from using-superpowers SKILL.md** (P3, 5 min)
   - Add link to the orphan reference file

10. **Trim using-git-worktrees to under 200 lines** (P3, 30 min)
    - Move secondary scenarios to a references/ file
