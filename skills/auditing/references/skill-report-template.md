# Skill Audit Report Template

Three-layer report for single skill audits (auto-detected by scope). Lighter than the full project template — no Risk Matrix, Methodology, or Appendix as separate layers. Evidence is inline in each finding; scope and tools are captured in the Skill Profile.

This template is for **agent-authored reports** (dispatched via `agents/auditor.md`). For CLI/CI summary output, use `bundles-forge audit-skill` (produces compact Markdown or JSON).

For full project audits (10 categories), use `references/plugin-report-template.md` instead.

## Finding ID Scheme

Single skill audits use 4 of the 10 category prefixes:

| Prefix | Category |
|--------|----------|
| `STR-NNN` | Structure |
| `SKQ-NNN` | Skill Quality |
| `XRF-NNN` | Cross-References |
| `SEC-NNN` | Security |

Numbering is sequential within each category, starting at 001.

## Severity Scale

| Level | Label | Definition |
|-------|-------|------------|
| P0 | Blocker | Skill will not function, or contains an active security threat |
| P1 | High | Degraded experience or suspicious pattern requiring review |
| P2 | Medium | Works but deviates from conventions; may cause problems at scale |
| P3 | Low | Improvement opportunity; no functional impact |

## Confidence Scale

| Level | Label | Meaning |
|-------|-------|---------|
| Confirmed | ✅ | Verified by script output or manual reproduction |
| Likely | ⚠️ | Strong evidence but not fully verified (e.g. pattern match without runtime test) |
| Suspected | ❓ | Suspicious pattern that warrants investigation |

## Decision Vocabulary

Two vocabularies based on audit context:

| Context | Positive | Conditional | Negative |
|---------|----------|-------------|----------|
| Self-check (author reviewing own skill) | `PASS` | `PASS WITH NOTES` | `FAIL` |
| Third-party evaluation (install decision) | `SAFE TO INSTALL` | `REVIEW REQUIRED` | `DO NOT INSTALL` |

**Automated baseline** (derived from script output):

| Condition | Recommendation |
|-----------|---------------|
| Any Critical finding | Negative |
| Warnings only, no Critical | Conditional |
| All checks pass | Positive |

**Qualitative adjustment** — the auditor may override the baseline recommendation, but must record the rationale. Examples:

- **Upgrade**: Warning involves an exploitable security surface → escalate to negative
- **Downgrade**: Critical is a confirmed false positive or has an active mitigation → reduce to conditional
- **Defer**: Audit scope is insufficient to support a conclusion → use "NEEDS MORE INFO" in either context

---

## Template

```markdown
---
audit-date: "<YYYY-MM-DDTHH:mm±HH:mm>"       # ISO 8601 with timezone
auditor-platform: "<Cursor / Claude Code / Codex / OpenCode / Gemini CLI>"
auditor-model: "<model-name or unknown>"       # if available; use "unknown" when the platform does not expose model info
bundles-forge-version: "<version>"
source-type: "<local-directory / git-repo / archive / marketplace>"
source-uri: "<original URL or local path>"
os: "<e.g. Windows 10, macOS 14, Ubuntu 22.04>"
python: "<version>"
---

# Skill Audit: <skill-name>

## 1. Decision Brief

| Field | Value |
|-------|-------|
| **Skill** | `<skill-name>` |
| **Target** | `<path/to/skill-directory-or-url>` |
| **Date** | `<YYYY-MM-DD>` |
| **Audit Context** | `self-check` / `third-party-evaluation` |

<!-- IF context: self-check -->
### Recommendation: `PASS` / `PASS WITH NOTES` / `FAIL`
<!-- END IF -->

<!-- IF context: third-party-evaluation -->
### Recommendation: `SAFE TO INSTALL` / `REVIEW REQUIRED` / `DO NOT INSTALL`
<!-- END IF -->

**Automated baseline:** <N> critical, <N> warnings, <N> info → `<recommendation>`

**Qualitative adjustment:** <None — agrees with baseline> / <Adjusted from X to Y because: rationale>

### Top Risks

<!-- List up to 3. If no findings, write "No risks identified." -->

| # | Risk | Impact | If Not Fixed |
|---|------|--------|-------------|
| 1 | <one-line risk title> | <quantified: e.g. "breaks frontmatter parsing", "triggers false positive in agent discovery"> | <worst-case outcome> |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |

<!-- IF context: third-party-evaluation -->
**Trust assessment:** <Skill content follows legitimate patterns / Contains suspicious patterns requiring manual review>

**Third-party trust signals:**
- [ ] No sensitive file access patterns
- [ ] No safety override instructions
- [ ] No encoding tricks or obfuscation
- [ ] Scope constraints are explicit
- [ ] Description matches actual behavior
<!-- END IF -->

---

## 2. Findings by Category

<!-- 4 categories, each with the same finding format as the full project template. -->
<!-- Categories with no findings still get a section header + "No findings. All checks pass." -->

### 2.1 Structure (Score: X/10)

**Summary:** <one-sentence category assessment>

**Checks run:** S2 (own directory), S3 (contains SKILL.md), S9 (directory name matches frontmatter `name`)

<!-- Repeat the finding block below for each finding. If none: "No findings. All checks pass." -->

#### [STR-001] <Finding title>
- **Severity:** P0/P1/P2/P3 | **Impact:** <quantified> | **Confidence:** ✅/⚠️/❓
- **Location:** `<file/path:line>`
- **Trigger:** <what condition causes this issue>
- **Actual Impact:** <what goes wrong if not fixed>
- **Remediation:** <specific fix direction>
- **Verification:** <how to confirm the fix works>
- **Evidence:**
  ```
  <key evidence snippet>
  ```

---

### 2.2 Skill Quality (Score: X/10)

**Summary:** <one-sentence category assessment>

**Checks run:** Q1–Q15 (frontmatter validity, description conventions, token budget, allowed-tools deps, section structure, conditional block reachability)

<!-- findings or "No findings. All checks pass." -->

---

### 2.3 Cross-References (Score: X/10)

**Summary:** <one-sentence category assessment>

**Checks run:** X1 (outgoing `project:skill-name` refs resolve), X2 (relative paths exist), X3 (referenced subdirectories exist)

<!-- findings or "No findings. All checks pass." -->

---

### 2.4 Security (Score: X/10)

**Summary:** <one-sentence category assessment>

**Checks run:** SC1 (sensitive file access), SC9 (safety overrides), SC13 (encoding tricks), AG1 (agent safety overrides), AG6 (scope constraints)

<!-- findings or "No findings. All checks pass." -->

---

## 3. Skill Profile

### Files

| File | Lines | Estimated Tokens |
|------|-------|-----------------|
| `SKILL.md` | <N> | ~<N> |
| `references/<file>` | <N> | — |
| ... | ... | ... |

### Tools Used

| Tool | Purpose |
|------|---------|
| `bundles-forge audit-skill` | Frontmatter validation, description conventions, cross-reference resolution |
| `bundles-forge audit-security` | Security pattern scanning on SKILL.md content |
| Manual/AI review | Qualitative assessment of instruction clarity, description anti-patterns |

### Out of Scope

Single skill audit covers 4 categories: Structure, Skill Quality, Cross-References, Security. The following 5 categories require project-level context and are not applicable:

- Platform Manifests — no manifests at skill level
- Version Sync — version tracked at project level
- Hooks — hook scripts are project infrastructure
- Testing — test suites are project-level
- Documentation — README/CHANGELOG are project-level

Findings are diagnostic. The calling context decides follow-up actions.
```
