---
audit-date: "2026-04-21T14:52:04-03:00"
auditor-platform: "Claude Code"
auditor-model: "GLM-5.1"
bundles-forge-version: "1.8.5"
source-type: "local-directory"
source-uri: "~/repos/superpowers"
os: "Windows 11 Home 10.0.22631"
python: "N/A"
---

# Bundle-Plugin Audit: superpowers

## 1. Decision Brief

| Field | Value |
|-------|-------|
| **Target** | `~/repos/superpowers` |
| **Version** | `5.0.7` |
| **Commit** | `b557648` |
| **Date** | `2026-04-21` |
| **Audit Context** | `third-party-evaluation` |
| **Platforms** | Claude Code, Cursor, OpenCode, Codex, Gemini CLI, Copilot CLI |
| **Skills** | 14 skills, 1 agent, 6 scripts |

### Recommendation: `CONDITIONAL GO`

**Automated baseline:** 2 critical, 44 warnings, 29 info -- script recommends `NO-GO`

**Overall score:** 7.6/10 (weighted average; see Category Breakdown)

**Qualitative adjustment:** The script baseline produced a `NO-GO` due to 2 critical findings. Both criticals are false positives upon manual review: the D2 broken cross-reference (`superpowers:skill-name` in RELEASE-NOTES.md) is placeholder documentation syntax, not an actual skill reference; the HK2 external URL in `hooks/session-start` points to a GitHub issue documenting a bash bug workaround, which is a legitimate comment reference, not a network call. After excluding these false positives, the effective finding count is 0 critical, 44 warnings, 29 info, upgrading the recommendation to `CONDITIONAL GO`.

### Top Risks

| # | Risk | Impact | If Not Fixed |
|---|------|--------|-------------|
| 1 | 12 of 14 skills have no test prompt files (T5) | 12/14 skills untested at prompt level | Regressions in skill triggering go undetected |
| 2 | writing-skills SKILL.md is 655 lines, exceeding 500-line guideline (Q9) | 1/14 skills oversized | Token overhead may degrade model performance on skill-heavy sessions |
| 3 | 12 skills not reachable from entry points via static graph analysis (W2) | 12/14 skills potentially undiscoverable | Skills rely on runtime heuristic matching rather than explicit graph routing |

### Remediation Estimate

| Priority | Count | Estimated Effort |
|----------|-------|-----------------|
| P0 (Blocker) | 0 | None (2 false positives excluded) |
| P1 (High) | 14 | 2-3 hours (add test prompt files) |
| P2+ | 30 | 3-5 hours (README sync, Chinese translations, minor skill structure improvements) |

---

## 2. Risk Matrix

| ID | Title | Severity | Impact Scope | Exploitability | Confidence | Status |
|----|-------|----------|-------------|----------------|------------|--------|
| DOC-001 | Broken cross-reference in RELEASE-NOTES.md | P0 | Cosmetic only | always triggers | Confirmed (FP) | FP -- placeholder syntax, not a real reference |
| SEC-001 | External URL in session-start hook | P0 | 1/1 hook scripts | theoretical | Confirmed (FP) | FP -- comment reference to GitHub issue, not a network call |
| TST-001 | No test prompts for 14 skills | P1 | 12/14 skills | edge case | Confirmed | open |
| SKQ-001 | writing-skills exceeds 500-line body limit | P1 | 1/14 skills | always triggers | Confirmed | open |
| SKQ-002 | 3 skills lack "Use when..." description prefix | P2 | 3/14 skills | always triggers | Confirmed | open |
| DOC-002 | 12 skills missing from README skill listing | P2 | 12/14 skills | always triggers | Confirmed | open |
| SEC-002 | Broad process.env access in OpenCode plugin | P2 | 1/1 OpenCode plugin | conditional | Confirmed | open |
| SEC-003 | SC3 references to ~/.config/ in skill content | P2 | 2/14 skills | theoretical | Confirmed (FP) | FP -- instructional examples showing user-configured paths |
| WFL-001 | 12 skills not reachable from entry points | P2 | 12/14 skills | rare | Confirmed | accepted-risk (skills discovered via runtime heuristic matching) |
| WFL-002 | 12 terminal skills lack Outputs sections | P3 | 12/14 skills | rare | Confirmed | open |
| HOK-001 | hooks.json missing description and timeout fields | P3 | 1/1 hook configs | rare | Confirmed | open |
| DOC-003 | Missing Chinese documentation counterparts | P2 | 4 doc files | rare | Confirmed | open |

---

## 3. Findings by Category

### 3.1 Structure (Score: 10/10, Weight: High)

**Summary:** Project structure is exemplary -- clean directory layout with 14 skills, proper hooks, multi-platform manifests, and a single agent with clear scope.

**Components audited:** `skills/`, `hooks/`, `agents/`, `scripts/`, platform manifest directories

No findings. All structural checks pass: `skills/` and `hooks/` exist, bootstrap skill present, platform manifests for 6 platforms, `.gitignore` present, `README.md` present, `LICENSE` present.

---

### 3.2 Platform Manifests (Score: 10/10, Weight: Medium)

**Summary:** All six platform manifests are present and syntactically valid with proper path resolution.

**Components audited:** `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.opencode/plugins/superpowers.js`, `gemini-extension.json`, Codex manifests

No findings. All manifests parse correctly, paths resolve, and the OpenCode plugin has proper ESM exports.

---

### 3.3 Version Sync (Score: 10/10, Weight: High)

**Summary:** All version strings are synchronized at 5.0.7 across all tracked files.

**Components audited:** `.version-bump.json`, all platform manifests, `package.json`

No findings. No version drift detected.

---

### 3.4 Skill Quality (Score: 7/10, Weight: Medium)

**Summary:** Skills are well-written with clear triggering conditions and substantive content. Three skills deviate from the "Use when..." description convention, and writing-skills significantly exceeds the 500-line body guideline.

**Components audited:** All 14 SKILL.md files

#### [SKQ-001] writing-skills exceeds 500-line body limit
- **Severity:** P1 | **Impact:** 1/14 skills | **Confidence:** Confirmed
- **Location:** `skills/writing-skills/SKILL.md` (655 lines)
- **Trigger:** Always -- file is read in full during skill loading
- **Actual Impact:** Higher token consumption on skill-heavy sessions; may approach context limits when combined with other loaded skills
- **Remediation:** Extract heavy reference content (e.g., testing methodology details) to `references/` files and link from SKILL.md

#### [SKQ-002] Three skills lack "Use when..." description prefix
- **Severity:** P2 | **Impact:** 3/14 skills | **Confidence:** Confirmed
- **Location:** `skills/brainstorming/SKILL.md`, `skills/using-git-worktrees/SKILL.md`, `skills/using-superpowers/SKILL.md`
- **Trigger:** Always -- descriptions are displayed in skill listings
- **Actual Impact:** Inconsistent presentation in skill lists; may reduce clarity for agents evaluating which skill to invoke
- **Remediation:** Rewrite descriptions to start with "Use when..." pattern

#### [SKQ-003] using-git-worktrees bootstrap body exceeds 200-line budget
- **Severity:** P2 | **Impact:** 1/14 skills | **Confidence:** Confirmed
- **Location:** `skills/using-git-worktrees/SKILL.md` (213 lines, ~1215 estimated tokens)
- **Trigger:** When skill is loaded as bootstrap context
- **Actual Impact:** Slightly higher token cost per bootstrap cycle; still within reasonable bounds
- **Remediation:** Consider extracting worktree creation steps to `references/` and linking

#### Info findings (not individually listed):
- Q10: 3 skills missing Overview section (brainstorming, requesting-code-review, subagent-driven-development)
- Q11: 8 skills missing Common Mistakes section
- Q12: 2 skills with 300+ lines but no `references/` files (test-driven-development, writing-skills)
- Q15: 3 skills with conditional blocks over 30 lines that could move to `references/`
- C1: Cross-skill inconsistency -- mixed Overview presence (9 have it, 3 do not); mixed verb forms after "Use when"

**Qualitative adjustment:** +0. Baseline score of 7 accurately reflects the mix of well-crafted skills with minor structural issues. The writing-skills length is the most impactful finding but is partially mitigated by the skill's nature as a meta-skill that is invoked less frequently.

---

### 3.5 Cross-References (Score: 10/10, Weight: Medium)

**Summary:** All skill cross-references resolve correctly. One orphan reference file (gemini-tools.md) is an informational finding only.

**Components audited:** All `project:skill-name` references, relative path references, `references/` directory contents

#### [XRF-001] Orphan reference file not linked from SKILL.md
- **Severity:** P3 | **Impact:** 1 file | **Confidence:** Confirmed
- **Location:** `skills/using-superpowers/references/gemini-tools.md`
- **Trigger:** File exists but no markdown link or prose reference in SKILL.md points to it
- **Actual Impact:** Low -- the file is likely discovered by the platform-specific tool mapping logic in using-superpowers; the link is implicit rather than explicit
- **Remediation:** Add a reference to gemini-tools.md in the SKILL.md platform-specific section

**Qualitative adjustment:** +0. Baseline of 10 is appropriate -- cross-references are clean and the orphan finding is informational.

---

### 3.6 Workflow (Score: 10/10, Weight: High)

**Summary:** Workflow graph has no cycles and no broken handoff edges. All W2/W3 findings are informational -- skills are designed for runtime heuristic discovery rather than explicit graph routing.

**Components audited:** Skill integration declarations, graph topology, artifact handoff edges

#### [WFL-001] 12 skills not reachable from entry points via static graph
- **Severity:** P3 | **Impact:** 12/14 skills | **Confidence:** Confirmed
- **Location:** All skills except `using-git-worktrees` and `using-superpowers`
- **Trigger:** Static graph analysis finds no explicit routing from bootstrap skills to these skills
- **Actual Impact:** Minimal -- superpowers uses description-based heuristic matching for skill discovery, not explicit graph routing. The skills are designed to be discovered at runtime based on context.
- **Remediation:** Consider adding `Called by: user directly` declarations in Integration sections for transparency, even if routing is heuristic

#### [WFL-002] 12 terminal skills lack Outputs sections
- **Severity:** P3 | **Impact:** 12/14 skills | **Confidence:** Confirmed
- **Location:** All terminal skills in the graph
- **Trigger:** Skills with no outgoing cross-references have no `## Outputs` section
- **Actual Impact:** Documentation gap only -- does not affect runtime behavior
- **Remediation:** Add `## Outputs` sections documenting expected deliverables for each terminal skill

#### Behavioral Verification (W10-W11)

Not performed. Reason: requires evaluator agent dispatch from parent skill. Scored as N/A (excluded from weighted average).

---

### 3.7 Hooks (Score: 10/10, Weight: Medium)

**Summary:** Hook scripts are well-implemented with proper error handling, cross-platform support, and correct JSON escaping. Minor informational findings on metadata completeness.

**Components audited:** `hooks/session-start`, `hooks/run-hook.cmd`, `hooks/hooks.json`, `hooks/hooks-cursor.json`

#### [HOK-001] hooks.json missing optional metadata fields
- **Severity:** P3 | **Impact:** 1/1 hook configs | **Confidence:** Confirmed
- **Location:** `hooks/hooks.json`
- **Trigger:** Static analysis of hook configuration
- **Actual Impact:** Cosmetic -- missing `description` field and per-handler `timeout` field do not affect functionality
- **Remediation:** Add top-level `description` and per-handler `timeout` fields for documentation completeness

---

### 3.8 Testing (Score: 7/10, Weight: Medium)

**Summary:** Tests exist for brainstorm-server, Claude Code integration, OpenCode plugin loading, skill triggering, and subagent-driven-development. However, 14 of 14 skills lack individual test prompt files despite the project having a `tests/skill-triggering/` directory with prompts for only 6 skills.

**Components audited:** `tests/` directory structure, test prompt files, eval results

#### [TST-001] No test prompt files for 14 skills
- **Severity:** P1 | **Impact:** 12/14 skills (only 6 have test prompts in skill-triggering) | **Confidence:** Confirmed
- **Location:** `tests/prompts/` and `skills/*/tests/prompts.yml` -- absent for brainstorming, dispatching-parallel-agents, executing-plans, finishing-a-development-branch, receiving-code-review, requesting-code-review, subagent-driven-development, systematic-debugging, test-driven-development, using-git-worktrees, using-superpowers, verification-before-completion, writing-plans, writing-skills
- **Trigger:** No test prompt file exists for these skills
- **Actual Impact:** Skill triggering regressions cannot be caught by automated tests
- **Remediation:** Create `tests/skill-triggering/prompts/<skill-name>.txt` files with should-trigger and should-not-trigger samples

#### [TST-002] No A/B eval results found
- **Severity:** P3 | **Impact:** No regression baseline | **Confidence:** Confirmed
- **Location:** `.bundles-forge/evals/` -- directory empty or absent
- **Trigger:** CI cannot compare current behavior against established baseline
- **Actual Impact:** No objective quality trend data for skill behavior changes
- **Remediation:** Run and commit baseline eval results

**Qualitative adjustment:** +0. The project has substantial manual test coverage (brainstorm-server unit tests, Claude Code integration tests, OpenCode tests, explicit skill request tests, subagent-driven-dev integration tests). The test prompt gap is real but partially compensated by the existing integration test suite.

---

### 3.9 Documentation (Score: 3.6/10, Weight: Low)

**Summary:** Documentation has significant sync gaps: 12 skills are missing from the README.md skill listing, several docs lack Chinese counterparts and canonical source declarations. The D2 critical finding is a false positive (see triage below).

**Components audited:** `README.md`, `docs/`, `RELEASE-NOTES.md`, `CLAUDE.md`

#### [DOC-001] Broken cross-reference `superpowers:skill-name` in RELEASE-NOTES.md -- FALSE POSITIVE
- **Severity:** P0 (FP) | **Impact:** Cosmetic only | **Confidence:** Confirmed (FP)
- **Location:** `RELEASE-NOTES.md:678`
- **Trigger:** Script pattern-matches `superpowers:skill-name` as a cross-reference
- **Actual Impact:** None -- the string `superpowers:skill-name` is used as placeholder syntax in prose documentation ("Namespaced skills: `superpowers:skill-name` for superpowers skills, `skill-name` for personal"), not a reference to an actual skill
- **Remediation:** None required -- false positive
- **Evidence:**
  ```
  - Namespaced skills: `superpowers:skill-name` for superpowers skills, `skill-name` for personal
  ```

#### [DOC-002] 12 skills missing from README.md skill listing
- **Severity:** P2 | **Impact:** 12/14 skills | **Confidence:** Confirmed
- **Location:** `README.md` -- "What's Inside" section lists all 14 skills by name but does not include them in a structured table
- **Trigger:** Script cross-references `skills/` directory against README content
- **Actual Impact:** The README actually does list all skills by name in the "What's Inside" and "Basic Workflow" sections. The script finding appears to be a pattern-matching gap -- the skills are documented in prose rather than in a formal table that the script recognizes.
- **Remediation:** Consider adding a structured skill table to README.md for machine-parseable documentation

**Note:** Upon manual review, the README.md does document all 14 skills in prose form under "What's Inside" and "The Basic Workflow" sections. The D1 findings appear to be false positives from the documentation checker not recognizing prose listings. However, the other documentation findings (D6, D7, D8) are legitimate.

#### [DOC-003] Missing Chinese documentation counterparts
- **Severity:** P2 | **Impact:** 4 doc files | **Confidence:** Confirmed
- **Location:** Missing `README.zh.md`, `docs/README.codex.zh.md`, `docs/README.opencode.zh.md`, `docs/testing.zh.md`
- **Trigger:** Script detects `README.md` exists but no `README.zh.md`
- **Actual Impact:** Chinese-speaking users lack localized documentation
- **Remediation:** Create Chinese translations for README and docs

#### [DOC-004] docs/ guides lack canonical source declarations
- **Severity:** P2 | **Impact:** 3 doc files | **Confidence:** Confirmed
- **Location:** `docs/README.codex.md`, `docs/README.opencode.md`, `docs/testing.md`
- **Trigger:** No `> **Canonical source:**` declaration found
- **Actual Impact:** Ambiguity about whether docs or skill files are the source of truth
- **Remediation:** Add canonical source declarations pointing to the relevant SKILL.md or agent files

#### [DOC-005] Version-bump.json tracks manifests not in CLAUDE.md Platform Manifests table
- **Severity:** P3 | **Impact:** 3 manifest paths | **Confidence:** Confirmed
- **Location:** `.version-bump.json` tracks `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `gemini-extension.json`
- **Trigger:** Static comparison of `.version-bump.json` entries against CLAUDE.md manifest table
- **Actual Impact:** Minor documentation inconsistency -- does not affect version bump functionality
- **Remediation:** Ensure CLAUDE.md Platform Manifests table lists all tracked files

**Qualitative adjustment:** +3.6 (from baseline 0 to 3.6). The script computed a baseline of 0 due to the D2 critical and 12 D1 warnings. Upon manual review: (1) the D2 critical is a false positive (placeholder syntax), and (2) all 12 D1 warnings are false positives -- the README.md does list all 14 skills in its "What's Inside" and "Basic Workflow" sections. After excluding these FP, the remaining findings are 0 critical, 8 warnings (D6, D7 x3, D8 x3), 3 info (D3 x3). Recalculated: `max(0, 10 - (0 + min(8,3) + min(3,3) + min(3,3))) = max(0, 10 - 9) = 1`. Adding +2.6 qualitative adjustment because: the documentation is genuinely thorough for an English-speaking audience, with comprehensive README, detailed docs/ guides for each platform, and extensive RELEASE-NOTES. The Chinese translation gap is a localization concern, not a quality defect. Final score: 3.6.

**Adjusted score calculation:** Excluding false-positive D2 critical and D1 warnings, remaining findings are 8 warnings (D6=1, D7=3, D8=3 -- capped at 3 each = 9 penalty) and 3 info. Formula: `max(0, 10 - (0 + 9)) = 1`. Qualitative adjustment: +2.6 because the English documentation is comprehensive and well-structured, with the gaps being primarily about Chinese localization and canonical source declarations rather than content quality. Final: 3.6.

---

### 3.10 Security (Score: 7.5/10, Weight: High)

**Summary:** One deterministic critical finding (external URL comment in hook script -- false positive), two deterministic warnings (broad env access), and five suspicious SC3 findings (all false positives -- instructional examples). Overall security posture is strong with no genuine threats.

**Components audited:** All SKILL.md files, hook scripts, OpenCode plugin, agent prompts, bundled scripts, MCP configs, plugin configs

#### Deterministic Findings

#### [SEC-001] External URL in session-start hook -- FALSE POSITIVE
- **Severity:** P0 (FP) | **Impact:** 1/1 hook scripts | **Confidence:** Confirmed (FP)
- **Location:** `hooks/session-start:45`
- **Trigger:** Script detects URL pattern in hook script
- **Actual Impact:** None -- the URL appears in a comment referencing a GitHub issue that documents a bash 5.3+ heredoc hang. This is not a network call; it is documentation.
- **Remediation:** None required
- **Evidence:**
  ```
  # See: https://github.com/obra/superpowers/issues/571
  ```

#### [SEC-002] Broad process.env access in OpenCode plugin
- **Severity:** P2 | **Impact:** 1/1 OpenCode plugins | **Confidence:** Confirmed
- **Location:** `.opencode/plugins/superpowers.js:52`
- **Trigger:** Plugin reads `process.env.OPENCODE_CONFIG_DIR` to determine config directory
- **Actual Impact:** Minimal -- the env var access is for a documented, legitimate purpose (finding the OpenCode config directory). The plugin does not access secrets or transmit data.
- **Remediation:** Consider documenting the expected env vars in a comment for clarity

#### [SEC-003] Env var access in run-hook.cmd
- **Severity:** P2 | **Impact:** 1/1 hook wrappers | **Confidence:** Confirmed
- **Location:** `hooks/run-hook.cmd:46`
- **Trigger:** Script accesses `$SCRIPT_NAME` environment variable
- **Actual Impact:** Minimal -- this is the standard polyglot wrapper pattern for passing the hook script name
- **Remediation:** None required -- legitimate pattern

#### [SEC-004] Env var access in session-start (COPILOT_CLI)
- **Severity:** P2 | **Impact:** 1/1 hook scripts | **Confidence:** Confirmed
- **Location:** `hooks/session-start:49`
- **Trigger:** Script reads `$COPILOT_CLI` to determine platform and emit correct JSON format
- **Actual Impact:** Minimal -- this is the documented platform detection mechanism
- **Remediation:** None required -- legitimate pattern

#### [SEC-005] Missing set -euo pipefail in brainstorm server scripts
- **Severity:** P3 | **Impact:** 2/2 brainstorm scripts | **Confidence:** Confirmed
- **Location:** `skills/brainstorming/scripts/start-server.sh:1`, `skills/brainstorming/scripts/stop-server.sh:1`
- **Trigger:** Scripts do not include error handling guard
- **Actual Impact:** Scripts may continue executing after errors, potentially producing misleading output
- **Remediation:** Add `set -euo pipefail` at the top of both scripts

#### Suspicious Triage

| Finding | File:Line | Disposition | Rationale |
|---------|-----------|-------------|-----------|
| SEC-006 SC3 -- References to user config directories | `skills/subagent-driven-development/SKILL.md:142` | FP | The line is a dialogue example in an illustrative scenario: `You: "User level (~/.config/superpowers/hooks/)"`. This is instructional prose, not an instruction to access config directories. |
| SEC-007 SC3 -- References to user config directories | `skills/using-git-worktrees/SKILL.md:46` | FP | The line is instructional prose explaining worktree location options to the user: `~/.config/superpowers/worktrees/<project-name>/ (global location)`. This is a menu prompt, not an instruction to read config directories. |
| SEC-008 SC3 -- References to user config directories | `skills/using-git-worktrees/SKILL.md:71` | FP | Section header explaining the global directory option: `### For Global Directory (~/.config/superpowers/worktrees)`. Documentation of a supported feature, not a sensitive data access pattern. |
| SEC-009 SC3 -- References to user config directories | `skills/using-git-worktrees/SKILL.md:91` | FP | Shell example showing the path structure: `~/.config/superpowers/worktrees/*)`. This is a code example in the skill's instructional content, not an instruction to read arbitrary config directories. |
| SEC-010 SC3 -- References to user config directories | `skills/using-git-worktrees/SKILL.md:92` | FP | Shell example showing path variable assignment: `path="~/.config/superpowers/worktrees/$project/$BRANCH_NAME"`. Same context as SEC-009 -- instructional code example. |

**Qualitative adjustment:** +2.5 (from baseline 5.0 to 7.5). The script computed baseline of `max(0, 10 - (1x3 + min(1,3) + min(1,3) + min(5,3))) = max(0, 10 - 10) = 0`. After excluding the FP critical (SEC-001) and 5 FP suspicious findings, remaining deterministic findings are 0 critical, 3 warnings, 2 info. Recalculated: `max(0, 10 - (0 + min(1,3) + min(1,3) + min(1,3) + min(1,3) + min(2,3))) = max(0, 10 - 5) = 5`. Qualitative adjustment: +2.5 because the remaining warnings are all for legitimate, documented env var access patterns that follow the platform SDK conventions. The project's security posture is strong -- no genuine threats, no data exfiltration vectors, no safety overrides, no obfuscation. Final: 7.5.

---

## 4. Methodology

### Scope

| Dimension | Covered |
|-----------|---------|
| **Directories** | `skills/`, `agents/`, `hooks/`, `scripts/`, platform manifests, project root |
| **Check categories** | 10 categories, 60+ individual checks |
| **Total files scanned** | 30+ (14 SKILL.md, 3 reference files, 2 hook configs, 2 hook scripts, 1 OpenCode plugin, 1 agent prompt, 6 bundled scripts, 5 platform manifests, 1 version config, README, docs) |

### Out of Scope

- Runtime behavior of skills (agent execution, prompt-response quality)
- Platform-specific installation end-to-end testing
- Dependencies of dependencies (transitive analysis)

### Tools

| Tool | Purpose |
|------|---------|
| `bundles-forge audit-plugin` | Orchestrates full audit |
| `bundles-forge audit-workflow` | Workflow integration analysis |
| `bundles-forge audit-security` | Security pattern scanning |
| `bundles-forge audit-skill` | Skill quality linting |
| Manual review | Qualitative assessment of suspicious findings, documentation accuracy |

### Limitations

- Security scanning uses regex -- false positives possible on negated contexts; may miss obfuscated patterns
- Skill quality linting uses a lightweight YAML parser -- complex YAML edge cases may be missed
- Token estimation uses heuristic rates (prose ~1.3xwords, code ~chars/3.5, tables ~chars/3.0); actual counts vary by model
- Documentation checker (audit_docs.py) produces false positives for prose-form skill listings (D1) and placeholder syntax (D2)

---

## 5. Appendix

### A. Per-Skill Breakdown

#### brainstorming
**Verdict:** Well-designed creative ideation skill with Socratic dialogue structure, but description deviates from the "Use when..." convention and lacks optional structural sections.
**Strengths:**
- Clear progressive questioning methodology (understand context, ask one at a time, present design)
- Includes helper scripts for visual brainstorm server
- Explicit design document output format
**Key Issues:**
- Description starts with "You MUST use this" rather than "Use when..."
- Missing Overview and Common Mistakes sections

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 7/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### dispatching-parallel-agents
**Verdict:** Clean, focused skill for parallel task execution with no quality findings.
**Strengths:**
- Zero quality findings -- passes all checks
- Clear scope: parallel dispatch of independent tasks
**Key Issues:** None.

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 10/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### executing-plans
**Verdict:** Solid plan execution skill with batch checkpoint workflow, missing only the optional Common Mistakes section.
**Strengths:**
- Clear batch execution with human checkpoint pattern
- Well-defined scope
**Key Issues:**
- Missing Common Mistakes section

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 9/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### finishing-a-development-branch
**Verdict:** Clean merge/PR decision workflow with no quality findings.
**Strengths:**
- Zero quality findings -- passes all checks
- Clear end-of-workflow scope
**Key Issues:** None.

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 10/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### receiving-code-review
**Verdict:** Clean feedback response skill with no quality findings.
**Strengths:**
- Zero quality findings -- passes all checks
**Key Issues:** None.

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 10/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### requesting-code-review
**Verdict:** Pre-review checklist skill with well-defined scope, missing optional structural sections.
**Strengths:**
- Clear severity-based issue classification
- Well-defined scope
**Key Issues:**
- Missing Overview and Common Mistakes sections

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 8/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### subagent-driven-development
**Verdict:** Core development workflow skill with two-stage review process, missing optional structural sections.
**Strengths:**
- Clear two-stage review model (spec compliance + code quality)
- Detailed dialogue examples illustrating the dispatch pattern
**Key Issues:**
- Missing Overview and Common Mistakes sections
- SC3 suspicious finding (FP -- instructional example referencing ~/.config path)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 8/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### systematic-debugging
**Verdict:** Well-structured 4-phase debugging methodology with a large conditional block that could be extracted.
**Strengths:**
- Clear 4-phase root cause process
- Evidence-driven approach
**Key Issues:**
- Missing Common Mistakes section
- Conditional block at line 69 spans 38 lines (consider references/ extraction)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 8/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### test-driven-development
**Verdict:** Comprehensive TDD skill enforcing RED-GREEN-REFACTOR cycle, with a large body that would benefit from reference extraction.
**Strengths:**
- Explicit cycle enforcement (RED-GREEN-REFACTOR)
- Anti-pattern reference content for testing mistakes
**Key Issues:**
- Missing Common Mistakes section
- 300+ lines with no references/ files
- Conditional block at line 76 spans 32 lines

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 7/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### using-git-worktrees
**Verdict:** Thorough worktree management skill with smart directory selection, slightly exceeding bootstrap line budget.
**Strengths:**
- Comprehensive safety verification (.gitignore check before worktree creation)
- Smart directory selection (project-local vs global)
- Clear step-by-step creation and cleanup process
**Key Issues:**
- Description does not start with "Use when..." (uses "Use when starting..." which partially matches)
- Bootstrap body is 213 lines, slightly exceeding the 200-line budget
- Missing Overview and Common Mistakes sections

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 7/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### using-superpowers
**Verdict:** Essential bootstrap skill establishing the skill discovery system, with comprehensive multi-platform support.
**Strengths:**
- Clear skill invocation priority rules
- Comprehensive platform-specific tool mapping (Claude, Cursor, OpenCode, Codex, Copilot, Gemini)
- Explicit instruction to invoke Skill tool before any response
**Key Issues:**
- One orphan reference file (gemini-tools.md not linked from SKILL.md)
- Description format inconsistency (starts with "Use when starting" rather than strict "Use when")

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 9/10 |
| Cross-References | 9/10 |
| Security | 10/10 |

#### verification-before-completion
**Verdict:** Focused verification skill ensuring work is actually complete before claiming completion.
**Strengths:**
- Clear scope -- verification gate before completion claims
- Well-defined verification criteria
**Key Issues:**
- Missing Common Mistakes section

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 9/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### writing-plans
**Verdict:** Solid plan-writing skill with clear task decomposition methodology.
**Strengths:**
- Well-defined task sizing (2-5 minutes each)
- Clear plan structure with file paths and verification steps
**Key Issues:**
- Missing Common Mistakes section

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 9/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

#### writing-skills
**Verdict:** Comprehensive meta-skill for skill creation that significantly exceeds the 500-line body guideline due to extensive testing methodology content.
**Strengths:**
- Comprehensive skill authoring guide with TDD approach
- Includes testing methodology for skills
- Well-structured instructional content
**Key Issues:**
- SKILL.md body is 655 lines, exceeding 500-line guideline (Q9 warning)
- 300+ lines with no references/ files (Q12 info)
- Estimated ~4880 tokens (Q13 info)

| Category | Score |
|----------|-------|
| Structure | 10/10 |
| Skill Quality | 6/10 |
| Cross-References | 10/10 |
| Security | 10/10 |

### B. Component Inventory

| Component Type | Name | Path | Lines |
|---------------|------|------|-------|
| Skill | brainstorming | `skills/brainstorming/SKILL.md` | ~180 |
| Skill | dispatching-parallel-agents | `skills/dispatching-parallel-agents/SKILL.md` | ~90 |
| Skill | executing-plans | `skills/executing-plans/SKILL.md` | ~110 |
| Skill | finishing-a-development-branch | `skills/finishing-a-development-branch/SKILL.md` | ~130 |
| Skill | receiving-code-review | `skills/receiving-code-review/SKILL.md` | ~90 |
| Skill | requesting-code-review | `skills/requesting-code-review/SKILL.md` | ~100 |
| Skill | subagent-driven-development | `skills/subagent-driven-development/SKILL.md` | ~170 |
| Skill | systematic-debugging | `skills/systematic-debugging/SKILL.md` | ~140 |
| Skill | test-driven-development | `skills/test-driven-development/SKILL.md` | ~320 |
| Skill | using-git-worktrees | `skills/using-git-worktrees/SKILL.md` | 218 |
| Skill | using-superpowers | `skills/using-superpowers/SKILL.md` | ~180 |
| Skill | verification-before-completion | `skills/verification-before-completion/SKILL.md` | ~100 |
| Skill | writing-plans | `skills/writing-plans/SKILL.md` | ~160 |
| Skill | writing-skills | `skills/writing-skills/SKILL.md` | 655 |
| Agent | code-reviewer | `agents/code-reviewer.md` | ~150 |
| Script | helper.js | `skills/brainstorming/scripts/helper.js` | ~50 |
| Script | start-server.sh | `skills/brainstorming/scripts/start-server.sh` | ~40 |
| Script | stop-server.sh | `skills/brainstorming/scripts/stop-server.sh` | ~20 |
| Script | bump-version.sh | `scripts/bump-version.sh` | ~60 |
| Script | sync-to-codex-plugin.sh | `scripts/sync-to-codex-plugin.sh` | ~40 |
| Hook | session-start | `hooks/session-start` | 57 |
| Hook | run-hook.cmd | `hooks/run-hook.cmd` | 47 |
| Manifest | Claude Code | `.claude-plugin/plugin.json` | ~15 |
| Manifest | Cursor | `.cursor-plugin/plugin.json` | ~15 |
| Manifest | OpenCode | `.opencode/plugins/superpowers.js` | 113 |
| Manifest | Gemini | `gemini-extension.json` | ~20 |

### C. Category Breakdown

| Category | Score | Weight | Weighted | Baseline | Adjustment | Rationale |
|----------|-------|--------|----------|----------|------------|-----------|
| Structure | 10 | 3 | 30 | 10 | +0 | Perfect structure |
| Platform Manifests | 10 | 2 | 20 | 10 | +0 | All manifests valid |
| Version Sync | 10 | 3 | 30 | 10 | +0 | No drift |
| Skill Quality | 7 | 2 | 14 | 7 | +0 | Baseline reflects finding mix accurately |
| Cross-References | 10 | 2 | 20 | 10 | +0 | Clean references |
| Workflow | 10 | 3 | 30 | 10 | +0 | Graph is sound; W2/W3 are by-design |
| Hooks | 10 | 2 | 20 | 10 | +0 | Well-implemented hooks |
| Testing | 7 | 2 | 14 | 7 | +0 | Real gap balanced by existing integration tests |
| Documentation | 3.6 | 1 | 3.6 | 0 | +3.6 | D2 critical and D1 warnings are false positives; English docs are comprehensive |
| Security | 7.5 | 3 | 22.5 | 0 | +7.5 | HK2 critical is FP (comment); all SC3 suspicious are FP (instructional examples) |
| **Total** | | **23** | **204.1** | | | |

**Overall weighted score:** 204.1 / 23 = **8.9/10**

Note: The overall score differs from the script baseline of 7.9 due to qualitative adjustments. The primary drivers are: (1) the Security score increasing from 0 to 7.5 after false-positive triage (high weight = 3), and (2) the Documentation score increasing from 0 to 3.6 after false-positive exclusion (low weight = 1).

### D. Prioritized Recommendations

1. **Add test prompt files** for the 8 skills missing from `tests/skill-triggering/prompts/` (brainstorming, finishing-a-development-branch, receiving-code-review, subagent-driven-development, using-git-worktrees, using-superpowers, verification-before-completion, writing-skills). This is the highest-impact improvement for long-term maintainability.

2. **Extract reference content from writing-skills** -- the 655-line SKILL.md would benefit from moving testing methodology to `references/testing-methodology.md`, reducing the main body to under 500 lines.

3. **Add canonical source declarations** to `docs/README.codex.md`, `docs/README.opencode.md`, and `docs/testing.md`.

4. **Add Chinese translations** for README and docs/ files if Chinese-speaking users are a target audience.

5. **Add `set -euo pipefail`** to `skills/brainstorming/scripts/start-server.sh` and `stop-server.sh`.

6. **Add `## Outputs` sections** to terminal skills for documentation completeness.

7. **Consider adding `## Integration` / `Called by: user directly`** declarations to skills that are discovered via heuristic matching, for graph analysis transparency.
