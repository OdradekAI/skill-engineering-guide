# Audit Report Template

Six-layer report structure for bundle-plugin audits. Each layer serves a distinct audience depth — Layer 1 enables a 30-second decision, Layer 6 provides raw data for deep dives.

This template is for **agent-authored reports** (dispatched via `agents/auditor.md`). For CLI/CI summary output, use `bundles-forge audit-plugin` (produces compact Markdown or JSON).

This template covers three audit contexts: **pre-release** (version gate), **post-change** (regression check), and **third-party evaluation** (install decision). For worked examples of each context, see `references/report-examples.md`.

## Finding ID Scheme

Each finding gets a unique, category-prefixed ID for cross-referencing:

| Prefix | Category |
|--------|----------|
| `STR-NNN` | Structure |
| `MAN-NNN` | Platform Manifests |
| `VER-NNN` | Version Sync |
| `SKQ-NNN` | Skill Quality |
| `XRF-NNN` | Cross-References |
| `WFL-NNN` | Workflow |
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

**Qualitative adjustment** — the auditor may override the baseline recommendation (±2 score adjustment allowed) but must record the rationale in the `Qualitative Adjustment` field.

---

## Full Project Audit Report

```markdown
---
audit-date: "<YYYY-MM-DDTHH:mm±HH:mm>"
auditor-platform: "<Cursor / Claude Code / Codex / OpenCode / Gemini CLI>"
auditor-model: "<model-name or unknown>"
bundles-forge-version: "<version>"
source-type: "<local-directory / git-repo / archive / marketplace>"
source-uri: "<original URL or local path>"
os: "<e.g. Windows 10, macOS 14, Ubuntu 22.04>"
python: "<version>"
---

# Bundle-Plugin Audit: <project-name>

## 1. Decision Brief

| Field | Value |
|-------|-------|
| **Target** | `<repo-url-or-path>` |
| **Version** | `<version>` |
| **Commit** | `<short-sha>` |
| **Date** | `<YYYY-MM-DD>` |
| **Audit Context** | `pre-release` / `post-change` / `third-party-evaluation` |
| **Platforms** | <list of target platforms> |
| **Skills** | <N> skills, <N> agents, <N> commands, <N> scripts |

### Recommendation: `GO` / `CONDITIONAL GO` / `NO-GO` / `NEEDS MORE INFO`

**Automated baseline:** <N> critical, <N> warnings, <N> info → script recommends `<recommendation>`

**Overall score:** <X.X>/10 (weighted average; see Category Breakdown)

**Qualitative adjustment:** <None — agrees with baseline> / <Adjusted from X to Y because: rationale>

### Top Risks

| # | Risk | Impact | If Not Fixed |
|---|------|--------|-------------|
| 1 | <one-line risk title> | <quantified> | <worst-case outcome> |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |

### Remediation Estimate

| Priority | Count | Estimated Effort |
|----------|-------|-----------------|
| P0 (Blocker) | <N> | <effort> |
| P1 (High) | <N> | <effort> |
| P2+ | <N> | <effort> |

---

## 2. Risk Matrix

| ID | Title | Severity | Impact Scope | Exploitability | Confidence | Status |
|----|-------|----------|-------------|----------------|------------|--------|
| <CAT-NNN> | <title> | P0-P3 | <quantified scope> | <see below> | ✅/⚠️/❓ | open/fixed/accepted-risk |

**Impact Scope** — use the most relevant quantification:
- Platform: `N/M platforms affected`
- Workflow: `blocks <skill-a> → <skill-b> chain`
- Component: `N/M skills`, `N/M agents`, `N/M scripts`
- Functional: `breaks install`, `breaks runtime`, `cosmetic only`

**Exploitability:**
- Security: `direct` / `conditional` / `theoretical`
- Quality: `always triggers` / `edge case` / `rare`

---

## 3. Findings by Category

<!-- Repeat for each of the 10 categories. Categories with no findings still appear. -->

### 3.N <Category Name> (Score: X/10, Weight: <H/M/L>)

**Summary:** <one-sentence category assessment>

**Components audited:** <list>

#### [CAT-NNN] <Finding title>
- **Severity:** P0-P3 | **Impact:** <quantified> | **Confidence:** ✅/⚠️/❓
- **Location:** `<file/path:line>`
- **Trigger:** <what condition causes this issue>
- **Actual Impact:** <what goes wrong if not fixed>
- **Remediation:** <specific fix direction>
- **Evidence:**
  ```
  <key evidence snippet>
  ```

---

## 4. Methodology

> Audit environment metadata is recorded in the report frontmatter.

### Scope

| Dimension | Covered |
|-----------|---------|
| **Directories** | `skills/`, `agents/`, `commands/`, `hooks/`, `scripts/`, platform manifests, project root |
| **Check categories** | 10 categories, 60+ individual checks |
| **Total files scanned** | <N> |

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
| `bundles-forge bump-version --check` | Version drift detection |

### Limitations

- Security scanning uses regex — false positives possible on negated contexts; may miss obfuscated patterns
- Skill quality linting uses a lightweight YAML parser — complex YAML edge cases may be missed
- Token estimation uses heuristic rates (prose ~1.3×words, code ~chars/3.5, tables ~chars/3.0); actual counts vary by model

---

## 5. Appendix

### A. Per-Skill Breakdown

#### <skill-name>
**Verdict:** <one-sentence characterization>
**Strengths:** <up to 3 bullet points>
**Key Issues:** <up to 3 bullet points, or "None.">

| Category | Score |
|----------|-------|
| Structure | X/10 |
| Skill Quality | X/10 |
| Cross-References | X/10 |
| Security | X/10 |

### B. Component Inventory

| Component Type | Name | Path | Lines |
|---------------|------|------|-------|
| Skill | <name> | `skills/<name>/SKILL.md` | <N> |
| Agent | <name> | `agents/<name>.md` | <N> |
| Script | <name> | `skills/<bundled-skill>/scripts/<name>.py` | <N> |
| Hook | <name> | `hooks/<name>` | <N> |
| Manifest | <platform> | `<path>` | <N> |

### C. Script Outputs

<details><summary>bundles-forge audit-plugin output</summary>
<raw output>
</details>

<details><summary>bundles-forge audit-security output</summary>
<raw output>
</details>

<details><summary>bundles-forge audit-skill output</summary>
<raw output>
</details>

<details><summary>bundles-forge bump-version --check output</summary>
<raw output>
</details>
```

---

## Single Skill Audit Report

For single skill audits, use the dedicated template in `references/skill-report-template.md`. It provides a three-layer structure (Decision Brief, Findings by Category, Skill Profile) optimized for the 4-category skill scope, with its own decision vocabulary and inline shared rules.
