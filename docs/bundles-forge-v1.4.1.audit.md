# Bundles Forge v1.4.1 — Comprehensive Audit Report

**Date:** 2026-04-09
**Scope:** Full project — 8 skills, 3 agents, 6 commands, 5 scripts, 5 platform manifests, 5 tests
**Methodology:** 10-dimension analysis + per-component review

---

## Executive Summary

Bundles Forge is a well-architected project with clean skill quality (0 lint findings), synchronized versions, and good code reuse in scripts. However, it has **structural issues** that matter:

| Dimension | Rating | Key Finding |
|-----------|--------|-------------|
| #1 Boundary Testing | B | Scripts handle missing dirs/files gracefully; YAML parser is fragile; empty skills dir returns exit 0 (should warn) |
| #2 Prompt Conflicts | B+ | No hard contradictions; one tension around "MUST/ALWAYS" usage vs. authoring's own advice against it |
| #3 Circular Dependencies | A | No cycles in skill references; graph is a clean DAG |
| #4 Degradation Paths | C | No explicit fallback instructions in most skills; hook failure = silent degradation |
| #5 Race Conditions | B+ | Agent reports use sequence numbers for collision avoidance; `.bundles-forge/` is shared mutable state |
| #6 Information Density | A- | All skills within budget; bootstrap 112 lines (limit 200); largest body 302 lines (limit 500) |
| #7 Duplicate Information | C+ | Token budgets repeated in 2 skills; description anti-pattern in 3 places; "Use when" guidance in 3 skills |
| #8 Temporal Dependencies | B | Bootstrap → skill → agent is well-defined; Codex has no bootstrap (intentional but undocumented) |
| #9 Cold/Hot Start | B | Hook re-fires on `clear|compact`; no state diff between cold and hot; potential token waste |
| #10 Version Compat | A- | Version sync is robust; .version-bump.json covers all manifests; no backup/rollback on bump |

**Overall: B+** — Sound architecture, needs tightening on degradation paths, deduplication, and test coverage.

---

## #1 Boundary Condition Testing

### Test Results

| Script | Input | Behavior | Exit Code | Verdict |
|--------|-------|----------|-----------|---------|
| `lint_skills.py` | Non-existent path | `error: has no skills/ directory` | 1 | GOOD |
| `lint_skills.py` | Empty skills/ dir | Returns 0 findings, exit 0 | 0 | **WEAK** — should warn |
| `lint_skills.py` | Malformed frontmatter | Reports Q1 critical finding | 2 | GOOD |
| `lint_skills.py` | Missing SKILL.md in dir | Reports Q1 critical finding | 2 | GOOD |
| `lint_skills.py` | Description >250 chars | Reports Q7 warning | 1 | GOOD |
| `scan_security.py` | Non-existent path | `error: has no skills/ directory` | 1 | GOOD |
| `audit_project.py` | Non-existent path | `error: has no skills/ directory` | 1 | GOOD |
| `audit_project.py` | Partial project (no hooks/) | Reports S1 critical for missing dirs | 2 | GOOD |
| `bump_version.py --check` | From correct dir | Reports sync status | 0 | GOOD |
| `bump_version.py --audit` | From correct dir | Scans repo, no undeclared | 0 | GOOD |
| `session-start` | No platform env vars | Defaults to Claude Code format | 0 | GOOD |
| `session-start` | Missing SKILL.md | Outputs "Error reading bootstrap skill" | 0 | **WEAK** — should exit non-zero |

### Issues Found

1. **Empty skills directory returns exit 0** (`lint_skills.py`): When `skills/` exists but has no subdirectories, the linter reports "0 skills checked" and exits cleanly. This should at minimum produce an info-level warning.

2. **YAML parser is custom and fragile** (`lint_skills.py:parse_frontmatter`): Uses regex `^---\s*\n(.*?)\n---\s*\n` instead of a YAML library. Limitations:
   - No support for YAML escape sequences
   - Multiline values only work if continuation lines start with exactly 2+ spaces
   - Quoted values with escaped inner quotes are not parsed correctly
   - No array or object support in frontmatter values

3. **session-start outputs error string but exits 0**: When `using-bundles-forge/SKILL.md` is missing, the hook emits "Error reading bootstrap skill" wrapped in JSON but exits 0. The agent receives a meaningless bootstrap injection with no error signal.

4. **No backup/rollback in bump_version.py**: If writing to one manifest succeeds but another fails (disk full, permissions), there's no rollback. Files that were already written retain the new version while others remain on the old version — creating the exact drift the tool aims to prevent.

5. **scan_security.py false-positive storm**: The security scanner flags its own rule definitions as critical findings (10 critical in `scan_security.py` itself). The `audit-checklist.md` and `security-checklist.md` reference files also trigger 14+ critical findings because they document attack patterns. These are all false positives caused by context-unaware regex matching.

### Improvement Recommendations

- **P1:** Add allowlist for self-referencing files in `scan_security.py` (or at minimum exclude `scripts/` and `references/` from scan, since these are tooling/documentation)
- **P2:** Make `session-start` exit non-zero when bootstrap SKILL.md is missing
- **P2:** Add warning when `lint_skills.py` finds zero skills to check
- **P3:** Add atomic write or backup mechanism to `bump_version.py`

---

## #2 Prompt Conflict Detection

### Methodology

Extracted all imperative instructions (MUST, NEVER, ALWAYS, REQUIRED) from all 8 SKILL.md files and cross-compared for contradictions.

### Findings

**No hard contradictions found.** All skills are internally consistent and cross-referencing correctly.

**One meta-level tension:**

| File | Line | Instruction |
|------|------|-------------|
| `authoring/SKILL.md` | 109 | "If you find yourself writing MUST or ALWAYS in all caps, that's a signal to reframe: explain the reasoning" |
| `authoring/SKILL.md` | 113 | Shows BAD example: "You MUST ALWAYS check version drift before releasing. NEVER skip this step." |
| `optimizing/SKILL.md` | 269 | "Adding MUST/ALWAYS/NEVER instead of explaining why" listed as Common Mistake |
| `auditing/SKILL.md` | 215 | "**Never** auto-install a skill that has unresolved critical security findings" |
| `auditing/SKILL.md` | 229 | "**Always** run `python scripts/bump_version.py --check`" |
| `releasing/SKILL.md` | 211 | "**Always** run full pipeline" |

**Analysis:** The authoring and optimizing skills explicitly advise against using MUST/ALWAYS/NEVER directives, recommending "explain the reasoning" instead. Yet the auditing and releasing skills use exactly these patterns. This isn't a functional conflict — the auditing/releasing rules are concrete safety constraints where absolute directives are appropriate. But the authoring guidance doesn't distinguish between "reasoning-based instructions" and "hard safety boundaries," making it look like the project violates its own advice.

**Recommendation:** Authoring should acknowledge that absolute directives are appropriate for safety boundaries (security scanning, version checks) while discouraging them for behavioral guidance.

### Agent Prompt Consistency

| Agent | Constraint | Matches Skill? |
|-------|-----------|----------------|
| `auditor.md` | `disallowedTools: Edit` | Yes — auditing says "never modify files" |
| `evaluator.md` | `disallowedTools: Edit` | Yes — optimizing says agents are read-only |
| `inspector.md` | `disallowedTools: Edit` | Yes — scaffolding says validation only |

All agent constraints are consistent with their dispatching skills.

### AG4 Warning Analysis

The security scanner flags all 3 agents with AG4 "Overly broad permission claims." This is a **false positive** — the agents don't claim permissions; the `disallowedTools` field restricts them. The scanner's regex likely matches on wording about what agents "can" or "will" do.

---

## #3 Circular Dependency Detection

### Dependency Graph (from cross-references)

```
blueprinting ──→ scaffolding ──→ auditing ──→ optimizing
     │                │              │              │
     │                │              └──→ releasing  │
     │                │                      │       │
     │                └──→ authoring         │       │
     │                                       │       │
     └──→ porting ←─────────────────────────┘       │
                                                     │
     optimizing ──→ auditing (one cycle, gate-limited)
     releasing  ──→ auditing
     releasing  ──→ optimizing
```

### Cycle Analysis

**One mutual reference exists:** `auditing ↔ optimizing`
- auditing says: "Warnings? Suggest `bundles-forge:optimizing`"
- optimizing says: "After changes, invoke `bundles-forge:auditing` for post-change verification"

**This is NOT a true cycle** because optimizing explicitly states: "only one audit cycle (no loops)" (`optimizing/SKILL.md:260`). The gate prevents infinite recursion.

**Similarly:** `releasing → auditing → optimizing → auditing` is bounded by the same one-cycle gate.

**Verdict: No unbounded cycles.** The graph is a DAG with one gated bidirectional edge.

### Missing References

All `bundles-forge:xxx` cross-references resolve to actual skill directories. No broken links found (confirmed by lint_skills.py X1 check: 0 findings).

---

## #4 Degradation Path Validation

### Failure Scenarios

| Scenario | Expected Behavior | Actual Behavior | Verdict |
|----------|-------------------|-----------------|---------|
| Bootstrap SKILL.md missing | Hook should fail with clear error | Emits "Error reading bootstrap skill" in JSON, exit 0 | **BAD** — silent degradation |
| Hook script fails | Session should warn user | Depends on platform; Claude Code may silently skip | **UNKNOWN** — no explicit handling |
| Subagent unavailable | Skills should fall back to inline execution | Mentioned in README ("main agent performs same work inline") but NOT in skill instructions | **GAP** — skills lack fallback guidance |
| Script errors (Python not found) | Tests should report failure | `run-all.sh` warns "Python not found — skipping" | **ACCEPTABLE** |
| `.version-bump.json` missing | Should block release operations | `bump_version.py` exits 1 with clear error | **GOOD** |
| Git not available on Windows | Hook should degrade gracefully | `run-hook.cmd` exits 0 silently | **ACCEPTABLE** but should log |

### Critical Gaps

1. **No subagent fallback instructions in skills:** The README documents that agents can fall back to inline execution, but the actual skill files (auditing, optimizing, scaffolding) never instruct the agent what to do when subagent dispatch fails. An agent following the skill literally would try to dispatch, fail, and have no guidance.

2. **Bootstrap failure is invisible:** If the `session-start` hook fails or produces bad output, the agent proceeds without the bundles-forge skill routing table. There's no mechanism for the agent to detect "I should have bundles-forge skills but they're not loaded."

3. **No graceful degradation for missing scripts:** Skills reference `python scripts/audit_project.py`, `python scripts/lint_skills.py`, etc. but never specify what to do if Python is unavailable or the script is missing.

### Improvement Recommendations

- **P1:** Add explicit fallback instructions to auditing, optimizing, and scaffolding: "If subagent dispatch is unavailable, perform the same checks inline."
- **P1:** Make session-start exit non-zero on bootstrap read failure
- **P2:** Add "If Python/scripts are unavailable, perform checks manually using Read and Grep" guidance to skills that reference scripts

---

## #5 Race Condition Analysis

### Parallel Execution Scenarios

| Scenario | Shared State | Risk | Mitigation |
|----------|-------------|------|-----------|
| Two evaluators (A/B test) | `.bundles-forge/` directory | Filename collision | Sequence number append (documented) |
| Inspector + auditor same project | `.bundles-forge/` directory | Different filenames | Low risk — different name patterns |
| Two concurrent audits | `.bundles-forge/` + scripts | Report collision | Sequence number append |
| Concurrent version bumps | `.version-bump.json` + manifest files | Partial write corruption | **No mitigation** |

### Analysis

1. **Agent report filenames** use `<project>-<version>-<type>.YYYY-MM-DD.md` with sequence number collision avoidance. This is well-designed for the common case.

2. **Concurrent version bumps** are the most dangerous scenario. `bump_version.py` reads all manifests, writes them sequentially, with no file locking. If two processes bump simultaneously, manifests could end up with mixed versions. However, this scenario is unlikely in practice (single-agent workflow).

3. **`.bundles-forge/` directory** has no locking mechanism. If two agents write to the same report file simultaneously (unlikely but possible), data corruption could occur. The "never modify existing files" instruction mitigates this.

**Verdict:** Low practical risk. The sequential nature of agent workflows makes concurrent access unlikely. The sequence number mechanism is a reasonable safeguard.

---

## #6 Information Density Evaluation

### Token Budget Compliance

| Skill | Lines | Budget | Est. Tokens | Status |
|-------|-------|--------|-------------|--------|
| `using-bundles-forge` (bootstrap) | 112 | 200 | ~1,412 | WITHIN |
| `blueprinting` | 302 | 500 | ~3,528 | WITHIN |
| `optimizing` | 283 | 500 | ~3,250 | WITHIN |
| `authoring` | 220 | 500 | ~2,692 | WITHIN |
| `auditing` | 245 | 500 | ~2,477 | WITHIN |
| `releasing` | 228 | 500 | ~2,218 | WITHIN |
| `scaffolding` | 158 | 500 | ~1,905 | WITHIN |
| `porting` | 100 | 500 | ~960 | WITHIN |

All skills are within their declared budgets. Good discipline.

### Bootstrap Injection Cost

The session-start hook injects **~6,204 bytes** (~1,550 tokens) on every session start, clear, or compact event. This is the fixed cost of having bundles-forge installed.

### Reference File Sizes

| File | Lines | Purpose |
|------|-------|---------|
| `scaffolding/references/project-anatomy.md` | 447 | Complete file reference for bundle-plugins |
| `auditing/references/audit-checklist.md` | 233 | 9-category quality checklist |
| `auditing/references/security-checklist.md` | 216 | 50+ security pattern checks |
| `porting/references/platform-adapters.md` | 145 | Platform-specific documentation |
| `scaffolding/references/scaffold-templates.md` | 60 | Template file index |
| `using-bundles-forge/references/codex-tools.md` | 15 | Tool mapping |
| `using-bundles-forge/references/gemini-tools.md` | 15 | Tool mapping |

`project-anatomy.md` at 447 lines is the largest reference. It's appropriately extracted — loading it every time scaffolding runs would inflate context significantly.

### Density Assessment

- **High density (good):** `porting` (100 lines, covers 5 platforms), `scaffolding` (158 lines, two modes), `using-bundles-forge` (112 lines, full routing table)
- **Moderate density:** `auditing` (245 lines for 9 categories), `releasing` (228 lines for 6-step pipeline)
- **Lower density:** `blueprinting` (302 lines, includes 3 scenarios with interview questions — hard to compress), `optimizing` (283 lines, includes 6 targets + feedback iteration — also hard to compress)

**Verdict:** No bloat. Blueprinting and optimizing are legitimately complex skills that need their line count.

---

## #7 Duplicate Information Detection

### Repeated Concepts

| Concept | Locations | Verbatim? | Dedup Needed? |
|---------|-----------|-----------|---------------|
| Token budget (200/500/250) | `authoring` (l.138-140), `optimizing` (l.109-110, 126) | Near-verbatim | **Yes** — extract to shared reference |
| "Description starts with Use when" | `authoring` (l.47), `optimizing` (l.64), `blueprinting` (l.83) | Paraphrased | No — each uses it in context |
| Description anti-pattern (agents shortcut) | `authoring` (l.48), `optimizing` (l.69), `auditing` (l.230) | Near-verbatim in 2 | **Yes** — authoring and optimizing repeat the same finding |
| Kebab-case naming | `blueprinting`, `scaffolding`, `using-bundles-forge` | Brief mentions | No — contextual |
| "Never auto-install with critical findings" | `auditing` (l.215), `auditing/references/audit-checklist.md` | Same rule | No — reference elaborates |
| Platform detection (CURSOR_PLUGIN_ROOT) | `porting` (l.67), `porting/references/platform-adapters.md` | Same info | No — reference is canonical |
| Security scan 5 attack surfaces | `auditing/SKILL.md`, `auditing/references/security-checklist.md`, `README.md` | Summarized in SKILL.md | No — appropriate progressive disclosure |

### High-Impact Deduplication Opportunities

1. **Token budgets:** Create `references/token-budgets.md` (5 lines) referenced by both authoring and optimizing. Currently the same three numbers appear in two skills.

2. **Description anti-pattern paragraph:** authoring/SKILL.md:48 and optimizing/SKILL.md:69 contain the same critical finding about description shortcuts. Extract to `authoring/references/description-conventions.md` and cross-reference from optimizing.

### Low-Impact (Leave As-Is)

- "Use when" guidance is appropriately contextual in each skill
- Kebab-case mentions are brief and serve different purposes
- Security surface descriptions are appropriate progressive disclosure (summary in SKILL.md, detail in reference)

---

## #8 Temporal Dependency Analysis

### Loading DAG by Platform

```
┌─────────────────────────────────────────────────────────┐
│                    SESSION START                         │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Claude Code:                                           │
│    SessionStart event                                   │
│    → hooks.json (matcher: startup|clear|compact)        │
│    → run-hook.cmd session-start                         │
│    → session-start (bash)                               │
│    → reads using-bundles-forge/SKILL.md                 │
│    → emits hookSpecificOutput JSON                      │
│    → agent has routing table                            │
│                                                         │
│  Cursor:                                                │
│    sessionStart event                                   │
│    → hooks-cursor.json                                  │
│    → ./hooks/session-start                              │
│    → reads using-bundles-forge/SKILL.md                 │
│    → emits additional_context JSON                      │
│    → agent has routing table                            │
│                                                         │
│  Gemini CLI:                                            │
│    Extension load                                       │
│    → gemini-extension.json                              │
│    → contextFileName: GEMINI.md                         │
│    → @./skills/using-bundles-forge/SKILL.md             │
│    → @./skills/using-bundles-forge/references/gemini..  │
│    → agent has routing table + tool mapping             │
│                                                         │
│  OpenCode:                                              │
│    Plugin load                                          │
│    → .opencode/plugins/bundles-forge.js                 │
│    → registers skills path                              │
│    → message transform (first message)                  │
│    → prepends bootstrap content                         │
│    → agent has routing table + tool mapping             │
│                                                         │
│  Codex:                                                 │
│    Skill discovery                                      │
│    → ~/.agents/skills/bundles-forge (symlink)           │
│    → reads AGENTS.md (points to CLAUDE.md)              │
│    → NO bootstrap injection                             │
│    → agent has guidelines but NO routing table          │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                   SKILL INVOCATION                      │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  User intent / slash command / cross-reference          │
│    → Skill tool (CC/Cursor) / activate_skill (Gemini)  │
│    → SKILL.md loaded into context                       │
│    → references/ loaded on demand                       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│                   AGENT DISPATCH                        │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  Skill instructions → dispatch subagent                 │
│    → agents/<role>.md loaded                            │
│    → agent reads references (audit-checklist, etc.)     │
│    → agent writes report to .bundles-forge/             │
│    → control returns to parent skill                    │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

### Timing Assumptions

1. **Bootstrap must complete before any skill invocation.** If the hook fails silently, the agent has no routing table and skill matching degrades to description-only matching.

2. **Codex has no bootstrap.** AGENTS.md points to CLAUDE.md for guidelines, but neither file contains the full routing table. Codex users rely entirely on description matching for skill discovery — this is a design choice but not documented as intentional.

3. **OpenCode bootstrap is delayed** — injected on first user message via message transform, not at session start. This means the first message has bootstrap context, but if the agent starts processing before the transform fires, there's a brief window without bootstrap.

### Improvement Recommendations

- **P2:** Document Codex's bootstrap-less design as intentional in porting/references/platform-adapters.md
- **P3:** Consider adding a lightweight routing table to AGENTS.md for Codex users

---

## #9 Cold/Hot Start Comparison

### Hook Trigger Analysis

`hooks.json` matcher: `startup|clear|compact`

| Trigger | Context | Behavior |
|---------|---------|----------|
| `startup` | New session | Full bootstrap injection (cold start) |
| `clear` | User runs /clear | Full bootstrap re-injection (hot start) |
| `compact` | Context compression | Full bootstrap re-injection (hot start) |

### Cold vs. Hot Difference

**There is no difference.** The session-start hook always performs the same operation: read SKILL.md, JSON-escape, emit JSON. No cached state, no delta detection.

### Token Waste Analysis

On every `clear` or `compact` event, the full ~1,550 token bootstrap is re-injected. For a session that compresses 5 times, that's ~7,750 tokens spent on bootstrap alone. This is acceptable overhead for a toolkit this size.

### State Persistence

Nothing persists between session events. The agent re-learns the routing table each time. This is **correct** behavior — the bootstrap content could have changed between invocations (e.g., after a skill was added/modified).

### Cursor vs. Claude Code

Cursor's `hooks-cursor.json` has **no matcher** — `sessionStart` fires on every session start. There's no equivalent to `clear|compact` triggers. This means Cursor only injects once per session, while Claude Code re-injects on clear/compact.

**Impact:** If a Cursor user clears context mid-session, the bootstrap won't re-inject. The agent loses the routing table until a new session starts.

---

## #10 Version Compatibility

### Version Sync Coverage

`.version-bump.json` declares 5 files:

| File | Field Path | Exists | In Sync |
|------|-----------|--------|---------|
| `package.json` | `version` | Yes | 1.4.1 |
| `.claude-plugin/plugin.json` | `version` | Yes | 1.4.1 |
| `.claude-plugin/marketplace.json` | `plugins.0.version` | Yes | 1.4.1 |
| `.cursor-plugin/plugin.json` | `version` | Yes | 1.4.1 |
| `gemini-extension.json` | `version` | Yes | 1.4.1 |

**Status: All in sync.** The `--audit` scan found no undeclared version strings.

### Files NOT in version sync

| File | Has Version? | Tracked? | Risk |
|------|-------------|----------|------|
| `.opencode/plugins/bundles-forge.js` | No explicit version | N/A | Low — reads from package.json at runtime |
| `.codex/INSTALL.md` | No version string | N/A | Low — instructions are version-agnostic |
| `CHANGELOG.md` | Contains version strings | Excluded by audit config | Correct exclusion |

### Robustness Analysis

1. **Dotted path traversal** (`plugins.0.version`): Works correctly for `marketplace.json`. However, if the array index doesn't exist, `_resolve_field_path` returns None silently — no error, no warning. Adding a new plugin to the marketplace array could cause this field to resolve incorrectly.

2. **SemVer validation**: Only checks `X.Y.Z` format via regex. Pre-release tags (e.g., `1.4.1-beta.1`) are rejected. This is intentional but limiting for projects that use pre-release versions.

3. **No dry-run mode**: `bump_version.py <version>` writes immediately. There's no `--dry-run` to preview which files would be modified.

---

## Per-Component Review

### Skills

| Skill | Reasonable? | Duplicate? | Complete? | Over-designed? |
|-------|------------|-----------|-----------|----------------|
| `using-bundles-forge` | Yes — essential bootstrap | No | Yes | No — 112 lines, lean |
| `blueprinting` | Yes — prevents rework | No | Yes — 3 scenarios | Slightly — Q0 "Minimal vs Intelligent" adds complexity; could default to intelligent |
| `scaffolding` | Yes — consistent generation | No | Yes — 2 modes | No — modes map to real needs |
| `authoring` | Yes — quality guidance | Partial — token budgets overlap with optimizing | Yes | No — good balance of guidance and examples |
| `auditing` | Yes — essential quality gate | No | Yes — 9 categories + security | Slightly — the Category 9 security scan overlaps heavily with `scan_security.py` script; the skill adds little beyond "run the script" |
| `optimizing` | Yes — feedback loop | Partial — description guidance overlaps with authoring | Yes — 6 targets | Slightly — A/B evaluation with subagents is heavy machinery for description changes that could be validated by eye |
| `porting` | Yes — multi-platform is core | No | **Missing** platform removal/deprecation | No — lean at 100 lines |
| `releasing` | Yes — prevents drift | No | Yes | No |

### Agents

| Agent | Reasonable? | Duplicate? | Complete? | Over-designed? |
|-------|------------|-----------|-----------|----------------|
| `inspector` | Yes — post-scaffold validation | Partially — overlaps with auditor on structure, manifests, version sync | **Missing** functional testing (can skills actually load?) | No |
| `auditor` | Yes — comprehensive assessment | No | Yes — 9 categories with checklists | No |
| `evaluator` | Yes — A/B testing | No | **Missing** comparison logic — only runs one side; human must compare | No |

**Inspector vs. Auditor overlap:** Both validate structure, manifests, and version sync. The inspector runs post-scaffold (quick check), the auditor runs as full assessment (scored). The overlap is intentional — inspector is fast sanity check, auditor is comprehensive. However, inspector could delegate structure/manifest/version checks to auditor to avoid maintaining two validation implementations.

### Commands

| Command | Reasonable? | Duplicate? |
|---------|------------|-----------|
| `bundles-forge` | Yes — bootstrap entry point | No |
| `bundles-blueprint` | Yes — clear entry point | No |
| `bundles-audit` | Yes | **Yes** — functionally identical to `bundles-scan` |
| `bundles-optimize` | Yes | No |
| `bundles-release` | Yes | No |
| `bundles-scan` | **Questionable** | **Yes** — invokes same skill as `bundles-audit` |

**`bundles-scan` is redundant.** It invokes `bundles-forge:auditing` with a "security focus" hint in its description, but the auditing skill always includes security scanning (Category 9). The scan command provides no additional functionality. It exists for "semantic clarity" but adds maintenance burden.

### Scripts

| Script | Reasonable? | Duplicate? | Complete? | Over-designed? |
|--------|------------|-----------|-----------|----------------|
| `_cli.py` | Yes — excellent reuse | No | Yes | No |
| `bump_version.py` | Yes — prevents drift | No | **Missing** dry-run, backup/rollback | No |
| `lint_skills.py` | Yes — automated quality | No | **Missing** frontmatter schema validation beyond basic fields | No |
| `scan_security.py` | Yes — automated scanning | No | **Flawed** — massive false positives on self-referencing files | Slightly — 54 regex rules with no context awareness |
| `audit_project.py` | Yes — comprehensive audit | Partially — orchestrates other scripts but adds own structural checks | Yes | No |

### Tests

| Test | Reasonable? | Complete? |
|------|------------|-----------|
| `test-bootstrap-injection.sh` | Yes | **Failing** — 1 failure (Claude Code platform detection) |
| `test-skill-discovery.sh` | Yes | Yes for its scope |
| `test-version-sync.sh` | Yes | **Failing** — jq path resolution broken on Windows |
| `test_scripts.py` | Yes | **Major gaps** — no error cases, no boundary tests, no individual rule tests, no exit code tests |
| `run-all.sh` | Yes | **3 of 4 suites failing** |

---

## Test Infrastructure Issues

Current test results: **3 of 4 test suites failing**

1. `test-bootstrap-injection.sh`: Fails on "Claude Code platform detection" — the test checks for `hookSpecificOutput` in default (no env var) mode, but the condition may be platform-sensitive.

2. `test-version-sync.sh`: Fails because jq-based file existence checks don't resolve paths correctly. On Windows/Git Bash, paths from jq output may have encoding issues. The script uses `jq -r '.files[].path'` then checks file existence — this works on Unix but breaks on Windows.

3. `test_scripts.py`: Passes (Python tests run successfully).

4. Missing test coverage:
   - No error-case tests (corrupted JSON, missing files, bad YAML)
   - No individual lint rule tests
   - No individual security rule tests
   - No exit code tests
   - No cross-platform tests
   - No negative tests ("should detect X problem")

---

## Prioritized Improvement Recommendations

### Priority 1 — Fix Now (Functional Issues)

| # | Issue | Recommendation | Files |
|---|-------|---------------|-------|
| 1 | Security scanner false positives on own files | Add self-exclusion: skip files under `scripts/` and `skills/*/references/` from bundled_script and skill_content scans respectively, OR add an allowlist for known-safe patterns in scanning context | `scripts/scan_security.py` |
| 2 | 3 of 4 test suites failing | Fix `test-bootstrap-injection.sh` platform detection check; fix `test-version-sync.sh` jq path resolution for Windows | `tests/test-bootstrap-injection.sh`, `tests/test-version-sync.sh` |
| 3 | No subagent fallback in skill instructions | Add "If subagent dispatch is unavailable, perform the same checks inline" to auditing, optimizing, scaffolding | `skills/auditing/SKILL.md`, `skills/optimizing/SKILL.md`, `skills/scaffolding/SKILL.md` |

### Priority 2 — Should Fix (Quality Issues)

| # | Issue | Recommendation | Files |
|---|-------|---------------|-------|
| 4 | session-start exits 0 on bootstrap read failure | Add `|| exit 1` after the cat command | `hooks/session-start` |
| 5 | Token budget duplication | Extract to shared reference, cross-reference from authoring and optimizing | New: `skills/authoring/references/token-budgets.md` |
| 6 | Description anti-pattern duplication | Consolidate into authoring, cross-reference from optimizing | `skills/authoring/SKILL.md`, `skills/optimizing/SKILL.md` |
| 7 | Porting skill missing platform removal | Add Scenario B: platform deprecation/removal guidance | `skills/porting/SKILL.md` |
| 8 | `bundles-scan` command is redundant | Consider removing — `bundles-audit` already includes security scanning | `commands/bundles-scan.md` |
| 9 | Codex bootstrap-less design undocumented | Document in platform-adapters.md that Codex intentionally has no routing table | `skills/porting/references/platform-adapters.md` |

### Priority 3 — Nice to Have (Polish)

| # | Issue | Recommendation | Files |
|---|-------|---------------|-------|
| 10 | bump_version.py lacks dry-run and rollback | Add `--dry-run` flag and backup-before-write | `scripts/bump_version.py` |
| 11 | Empty skills dir returns exit 0 | Add info-level warning | `scripts/lint_skills.py` |
| 12 | Inspector/auditor structural validation overlap | Consider having inspector delegate to auditor or share a validation module | `agents/inspector.md`, `agents/auditor.md` |
| 13 | MUST/ALWAYS usage tension with authoring guidance | Add note to authoring that absolute directives are appropriate for safety boundaries | `skills/authoring/SKILL.md` |
| 14 | test_scripts.py lacks boundary/error tests | Add negative tests: malformed YAML, broken cross-refs, drift scenarios | `tests/test_scripts.py` |
| 15 | Cursor doesn't re-inject on context clear | Document this limitation or explore alternative bootstrap persistence | `skills/porting/references/platform-adapters.md` |

---

## Appendix: File Inventory

### Skills (8 total, 1,648 lines SKILL.md + 1,131 lines references)

| Skill | SKILL.md Lines | Reference Lines | Total |
|-------|----------------|-----------------|-------|
| blueprinting | 302 | 0 | 302 |
| optimizing | 283 | 0 | 283 |
| auditing | 245 | 449 | 694 |
| releasing | 228 | 0 | 228 |
| authoring | 220 | 0 | 220 |
| scaffolding | 158 | 507 | 665 |
| using-bundles-forge | 112 | 30 | 142 |
| porting | 100 | 145 | 245 |

### Scripts (5 total, 1,216 lines)

| Script | Lines |
|--------|-------|
| audit_project.py | 335 |
| scan_security.py | 322 |
| bump_version.py | 265 |
| lint_skills.py | 264 |
| _cli.py | 30 |

### Tests (5 total)

| Test | Type | Status |
|------|------|--------|
| test-bootstrap-injection.sh | Shell | 1 FAIL |
| test-skill-discovery.sh | Shell | PASS |
| test-version-sync.sh | Shell | FAIL (Windows) |
| test_scripts.py | Python | PASS |
| run-all.sh | Orchestrator | 3/4 FAIL |
