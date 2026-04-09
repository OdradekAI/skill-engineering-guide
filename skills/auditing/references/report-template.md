# Audit Report Template

Six-layer report structure for bundle-plugin audits. Each layer serves a distinct audience depth — Layer 1 enables a 30-second decision, Layer 6 provides raw data for deep dives.

This template covers three audit contexts: **pre-release** (version gate), **post-change** (regression check), and **third-party evaluation** (install decision). Conditional sections are marked with `<!-- IF context: ... -->`.

## Finding ID Scheme

Each finding gets a unique, category-prefixed ID for cross-referencing:

| Prefix | Category |
|--------|----------|
| `STR-NNN` | Structure |
| `MAN-NNN` | Platform Manifests |
| `VER-NNN` | Version Sync |
| `SKQ-NNN` | Skill Quality |
| `XRF-NNN` | Cross-References |
| `HOK-NNN` | Hooks |
| `TST-NNN` | Testing |
| `DOC-NNN` | Documentation |
| `SEC-NNN` | Security |

Numbering is sequential within each category, starting at 001.

## Severity Scale

| Level | Label | Definition |
|-------|-------|------------|
| P0 | Blocker | Project/skill will not function, or contains an active security threat |
| P1 | High | Degraded experience on one or more platforms, or suspicious pattern requiring review |
| P2 | Medium | Works but deviates from conventions; may cause problems at scale |
| P3 | Low | Improvement opportunity; no functional impact |

## Confidence Scale

| Level | Label | Meaning |
|-------|-------|---------|
| Confirmed | ✅ | Verified by script output or manual reproduction |
| Likely | ⚠️ | Strong evidence but not fully verified (e.g. pattern match without runtime test) |
| Suspected | ❓ | Suspicious pattern that warrants investigation |

## Go/No-Go Rules

**Automated baseline** (derived from script output):

| Condition | Recommendation |
|-----------|---------------|
| Any Critical finding | `NO-GO` |
| Warnings only, no Critical | `CONDITIONAL GO` |
| All checks pass | `GO` |

**Qualitative adjustment** — the auditor may override the baseline recommendation, but must record the rationale in the `Qualitative Adjustment` field. Examples:

- **Upgrade**: Warning involves an exploitable security surface → escalate to `NO-GO`
- **Downgrade**: Critical is a confirmed false positive or has an active mitigation → reduce to `CONDITIONAL GO`
- **Defer**: Audit scope is insufficient to support a conclusion → `NEEDS MORE INFO`

---

## Full Project Audit Report

```markdown
# Bundle-Plugin Audit: <project-name>

## 1. Decision Brief

| Field | Value |
|-------|-------|
| **Repository** | `<repo-url-or-path>` |
| **Version** | `<version>` |
| **Commit** | `<short-sha>` |
| **Date** | `<YYYY-MM-DD>` |
| **Audit Context** | `pre-release` / `post-change` / `third-party-evaluation` |
| **Platforms** | <list of target platforms> |
| **Skills** | <N> skills, <N> agents, <N> commands, <N> scripts |

### Recommendation: `GO` / `CONDITIONAL GO` / `NO-GO` / `NEEDS MORE INFO`

**Automated baseline:** <N> critical, <N> warnings, <N> info → script recommends `<recommendation>`

**Qualitative adjustment:** <None — agrees with baseline> / <Adjusted from X to Y because: rationale>

### Top Risks

<!-- List up to 3. If no findings, write "No risks identified." -->

| # | Risk | Impact | If Not Fixed |
|---|------|--------|-------------|
| 1 | <one-line risk title> | <quantified: e.g. "affects 3/5 platforms", "blocks release chain"> | <worst-case outcome> |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |

### Remediation Estimate

| Priority | Count | Estimated Effort |
|----------|-------|-----------------|
| P0 (Blocker) | <N> | <e.g. "~2 hours", "1 file change"> |
| P1 (High) | <N> | <effort> |
| P2+ | <N> | <effort> |

<!-- IF context: pre-release -->
**Release decision:** <Ready to release / Block release until P0 items resolved / Needs further review>
<!-- END IF -->

<!-- IF context: third-party-evaluation -->
**Install decision:** <Safe to install / Install with caution (review warnings) / Do not install>
**Trust assessment:** <Skill content follows legitimate patterns / Contains suspicious patterns requiring manual review>
<!-- END IF -->

---

## 2. Risk Matrix

| ID | Title | Severity | Impact Scope | Exploitability | Confidence | Status |
|----|-------|----------|-------------|----------------|------------|--------|
| <CAT-NNN> | <title> | P0/P1/P2/P3 | <quantified scope> | <see below> | ✅/⚠️/❓ | open/fixed/accepted-risk |

**Impact Scope** — use the most relevant quantification dimension(s):
- Platform: `N/M platforms affected` (e.g. `3/5 platforms`)
- Workflow: `blocks <skill-a> → <skill-b> chain` or `N/M workflow stages affected`
- Component: `N/M skills`, `N/M agents`, `N/M scripts`
- Functional: `breaks install`, `breaks runtime`, `breaks version sync`, `cosmetic only`

**Exploitability** (choose the column that applies):

| Security findings | Quality findings |
|-------------------|-----------------|
| `direct` — no prerequisites | `always triggers` — deterministic |
| `conditional` — requires specific setup | `edge case` — unusual inputs |
| `theoretical` — possible but undemonstrated | `rare` — unlikely in practice |

<!-- If no findings exist, replace the table with: "No findings. All 9 categories passed." -->

---

## 3. Findings by Category

<!-- Repeat this section for each of the 9 categories. -->
<!-- Categories with no findings still get a section header + "No findings." -->

### 3.1 Structure (Score: X/10)

**Summary:** <one-sentence category assessment>

**Components audited:** project root, `skills/` directory tree, `package.json`, `.gitignore`, `README.md`, `LICENSE`, `CHANGELOG.md`

<!-- Repeat the finding block below for each finding. If none, write "No findings. All checks pass." -->

#### [STR-001] <Finding title>
- **Severity:** P0/P1/P2/P3 | **Impact:** <quantified> | **Confidence:** ✅/⚠️/❓
- **Location:** `<file/path:line>`
- **Trigger:** <what condition causes this issue>
- **Actual Impact:** <what goes wrong if not fixed>
- **Remediation:** <specific fix direction>
- **Verification:** <how to confirm the fix works>
- **Evidence:**
  ```
  <key evidence snippet — code line, script output excerpt, or pattern match>
  ```

---

### 3.2 Platform Manifests (Score: X/10)

**Summary:** <one-sentence category assessment>

**Components audited:** `.claude-plugin/plugin.json`, `.cursor-plugin/plugin.json`, `.opencode/plugins/<name>.js`, `.codex/INSTALL.md`, `gemini-extension.json`

<!-- findings or "No findings. All checks pass." -->

---

### 3.3 Version Sync (Score: X/10)

**Summary:** <one-sentence category assessment>

**Components audited:** `.version-bump.json`, all declared version-bearing files, `scripts/bump_version.py`

<!-- findings or "No findings. All checks pass." -->

---

### 3.4 Skill Quality (Score: X/10)

**Summary:** <one-sentence category assessment>

**Components audited:** all `skills/*/SKILL.md` files (<N> skills)

<!-- findings or "No findings. All checks pass." -->

---

### 3.5 Cross-References (Score: X/10)

**Summary:** <one-sentence category assessment>

**Components audited:** all `project:skill-name` references, relative path references, subdirectory references across SKILL.md files

<!-- findings or "No findings. All checks pass." -->

---

### 3.6 Hooks (Score: X/10)

**Summary:** <one-sentence category assessment>

**Components audited:** `hooks/session-start`, `hooks/run-hook.cmd`, `hooks/hooks.json`, `hooks/hooks-cursor.json`

<!-- findings or "No findings. All checks pass." -->

---

### 3.7 Testing (Score: X/10)

**Summary:** <one-sentence category assessment>

**Components audited:** `tests/` directory, test files and coverage

<!-- findings or "No findings. All checks pass." -->

---

### 3.8 Documentation (Score: X/10)

**Summary:** <one-sentence category assessment>

**Components audited:** `README.md`, `CHANGELOG.md`, `CLAUDE.md`, `AGENTS.md`, platform-specific install docs

<!-- findings or "No findings. All checks pass." -->

---

### 3.9 Security (Score: X/10)

**Summary:** <one-sentence category assessment>

**Components audited:** (list all scanned files by type)
- **Skill content:** <N> SKILL.md files
- **Hook scripts:** `hooks/session-start`, `hooks/run-hook.cmd`
- **OpenCode plugins:** `.opencode/plugins/<name>.js`
- **Agent prompts:** `agents/inspector.md`, `agents/auditor.md`, `agents/evaluator.md`
- **Bundled scripts:** `scripts/*.py`

<!-- findings or "No findings. All checks pass." -->

<!-- IF context: third-party-evaluation -->
**Third-party trust signals:**
- [ ] No sensitive file access patterns
- [ ] No network calls in hooks or scripts
- [ ] No safety override instructions
- [ ] No encoding tricks or obfuscation
- [ ] Agent prompts have explicit scope constraints
<!-- END IF -->

---

## 4. Methodology

### Scope

| Dimension | Covered |
|-----------|---------|
| **Directories** | `skills/`, `agents/`, `commands/`, `hooks/`, `scripts/`, `.claude-plugin/`, `.cursor-plugin/`, `.codex/`, `.opencode/`, project root |
| **File types** | `.md` (SKILL.md, agent prompts), `.json` (manifests, hooks config), `.py` (scripts), `.js` (OpenCode plugins), `.sh`/`.cmd` (hook scripts) |
| **Check categories** | 9 categories, 50+ individual checks |
| **Total files scanned** | <N> |

### Out of Scope

- Runtime behavior of skills (agent execution, prompt-response quality)
- Platform-specific installation end-to-end testing
- Dependencies of dependencies (transitive analysis)
- <any other explicit exclusions>

### Tools

| Tool | Purpose | Invocation |
|------|---------|------------|
| `audit_project.py` | Orchestrates full audit | `python scripts/audit_project.py <root>` |
| `scan_security.py` | Security pattern scanning | `python scripts/scan_security.py <root>` |
| `lint_skills.py` | Skill quality linting | `python scripts/lint_skills.py <root>` |
| `bump_version.py` | Version drift detection | `python scripts/bump_version.py --check` |
| Manual/AI review | Qualitative assessment | Categories 1-9 checklist walkthrough |

### Limitations

- `scan_security.py` uses regex pattern matching — it can produce false positives on negated contexts (e.g. "do NOT use curl") and may miss obfuscated patterns
- `lint_skills.py` uses a lightweight YAML parser (no PyYAML dependency) — edge cases in complex YAML may be missed
- Security scan covers known attack patterns but cannot detect novel or zero-day techniques
- Qualitative assessments (description anti-patterns, architecture quality) involve judgment and carry `Likely` or `Suspected` confidence

### Environment

| Field | Value |
|-------|-------|
| **OS** | <e.g. Windows 10, macOS 14, Ubuntu 22.04> |
| **Python** | <version> |
| **Git commit** | `<sha>` |
| **Audit date** | `<YYYY-MM-DD>` |

---

## 5. Appendix

### A. Per-Skill Breakdown

<!-- For each skill, provide a qualitative summary and 4-category micro-scores. -->
<!-- This section is reference material — the primary findings are in Layer 3. -->

#### <skill-name>
**Verdict:** <one-sentence characterization>
**Strengths:**
- <up to 3 bullet points>
**Key Issues:**
- <up to 3 bullet points, or "None.">

| Category | Score |
|----------|-------|
| Structure | X/10 |
| Skill Quality | X/10 |
| Cross-References | X/10 |
| Security | X/10 |

<!-- Repeat for each skill -->

### B. Component Inventory

| Component Type | Name | Path | Lines |
|---------------|------|------|-------|
| Skill | <name> | `skills/<name>/SKILL.md` | <N> |
| Agent | <name> | `agents/<name>.md` | <N> |
| Command | <name> | `commands/<name>.md` | <N> |
| Script | <name> | `scripts/<name>.py` | <N> |
| Hook | <name> | `hooks/<name>` | <N> |
| Manifest | <platform> | `<path>` | <N> |

### C. Script Outputs

<details>
<summary>audit_project.py output</summary>

<raw output here>

</details>

<details>
<summary>scan_security.py output</summary>

<raw output here>

</details>

<details>
<summary>lint_skills.py output</summary>

<raw output here>

</details>

<details>
<summary>bump_version.py --check output</summary>

<raw output here>

</details>

### D. Audit Context Guide

This appendix describes how to adapt the report for each audit context.

**Pre-release audit:**
- Layer 1 focuses on release readiness — "Can we ship this version?"
- Include version bump verification (`bump_version.py --check` and `--audit`)
- Decision Brief includes release recommendation
- Pair with `bundles-forge:releasing` for the full release pipeline

**Post-change audit:**
- Layer 1 focuses on regression — "Did this change break anything?"
- Compare findings against the previous audit baseline if available
- Flag any new findings not present in the prior report
- Decision Brief focuses on change safety

**Third-party evaluation:**
- Layer 1 focuses on trust — "Is this safe to install?"
- Security category (3.9) gets elevated attention with a trust checklist
- Decision Brief includes explicit install recommendation
- Critical security findings block installation unconditionally
```

---

## Single Skill Audit Report

For single skill audits, use the dedicated template in `references/skill-report-template.md`. It provides a three-layer structure (Decision Brief, Findings by Category, Skill Profile) optimized for the 4-category skill scope, with its own decision vocabulary and inline shared rules.
