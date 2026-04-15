# Workflow Audit Report Template

Three-layer report for workflow audits. Evaluates how skills connect, hand off artifacts, and compose into coherent chains. Lighter than the full project template — focused on workflow topology, semantic interfaces, and behavioral verification.

This template is for **agent-authored reports** (dispatched via `agents/auditor.md`). For CLI/CI summary output, use `bundles-forge audit-workflow` (produces compact Markdown or JSON).

For full project audits (10 categories), use `references/plugin-report-template.md` instead.
For single skill audits (4 categories), use `references/skill-report-template.md` instead.

## Finding ID Scheme

Workflow audits use the `WFL-NNN` prefix:

| Prefix | Category |
|--------|----------|
| `WFL-NNN` | Workflow (covers W1-W11 checks) |

Numbering is sequential, starting at 001.

## Severity Scale

| Level | Label | Definition |
|-------|-------|------------|
| P0 | Blocker | Workflow chain is broken — skills cannot hand off to each other |
| P1 | High | Degraded handoff quality or missing integration declarations |
| P2 | Medium | Works but conventions are incomplete; may cause confusion at scale |
| P3 | Low | Improvement opportunity; no functional impact on workflow |

## Confidence Scale

| Level | Label | Meaning |
|-------|-------|---------|
| Confirmed | ✅ | Verified by script output or manual reproduction |
| Likely | ⚠️ | Strong evidence but not fully verified |
| Suspected | ❓ | Suspicious pattern that warrants investigation |

## Go/No-Go Rules

**Automated baseline** (derived from script + agent output):

| Condition | Recommendation |
|-----------|---------------|
| Any W1-W5 finding at critical severity | `NO-GO` |
| Any W9-W11 finding at warning severity | `CONDITIONAL GO` |
| All checks pass | `GO` |

**Qualitative adjustment** — the auditor may override the baseline recommendation but must record the rationale.

---

## Template

```markdown
---
audit-date: "<YYYY-MM-DDTHH:mm±HH:mm>"
auditor-platform: "<Cursor / Claude Code / Codex / OpenCode / Gemini CLI>"
auditor-model: "<model-name or unknown>"
bundles-forge-version: "<version>"
source-type: "<local-directory / git-repo / archive>"
source-uri: "<original URL or local path>"
focus-skills: "<comma-separated list, or 'all'>"
os: "<e.g. Windows 10, macOS 14, Ubuntu 22.04>"
python: "<version>"
---

# Workflow Audit: <project-name>

## 1. Decision Brief

| Field | Value |
|-------|-------|
| **Target** | `<repo-url-or-path>` |
| **Version** | `<version>` |
| **Date** | `<YYYY-MM-DD>` |
| **Audit Trigger** | `post-integration` / `pre-release` / `workflow-change` / `on-demand` |
| **Focus Skills** | <list, or "all (full workflow audit)"> |
| **Total Skills** | <N> skills in project, <N> in focus |
| **Workflow Edges** | <N> total edges, <N> involving focus skills |

### Recommendation: `GO` / `CONDITIONAL GO` / `NO-GO`

**Automated baseline:** <N> critical, <N> warnings, <N> info → script recommends `<recommendation>`

**Qualitative adjustment:** <None — agrees with baseline> / <Adjusted from X to Y because: rationale>

### Top Risks

<!-- List up to 3. If no findings, write "No workflow risks identified." -->

| # | Risk | Impact | If Not Fixed |
|---|------|--------|-------------|
| 1 | <one-line risk title> | <quantified: e.g. "breaks skill-A → skill-B handoff"> | <worst-case outcome> |
| 2 | ... | ... | ... |
| 3 | ... | ... | ... |

---

## 2. Findings by Layer

<!-- IF --focus-skills was specified, split each layer into Focus Area and Context. -->
<!-- IF no focus, present all findings together. -->

### 2.1 Static Structure (Score: X/10, Weight: High)

**Summary:** <one-sentence layer assessment>

**Checks run:** W1 (cycles), W2 (reachability), W3 (terminal outputs), W4 (referenced inputs), W5 (artifact matching)

<!-- IF focus mode -->
#### Focus Area
<!-- Findings directly involving focus skills -->

#### Context
<!-- Remaining findings from full graph analysis -->
<!-- END IF -->

#### [WFL-001] <Finding title>
- **Severity:** P0/P1/P2/P3 | **Impact:** <quantified> | **Confidence:** ✅/⚠️/❓
- **Check:** W1-W5
- **Skills involved:** `<skill-a>`, `<skill-b>`
- **Trigger:** <what condition causes this issue>
- **Actual Impact:** <what goes wrong if not fixed>
- **Remediation:** <specific fix direction>
- **Evidence:**
  ```
  <key evidence: e.g. cycle path, missing artifact IDs>
  ```

---

### 2.2 Semantic Interface (Score: X/10, Weight: Medium)

**Summary:** <one-sentence layer assessment>

**Checks run:** W6 (integration docs), W7 (cycle rationale), W8 (artifact clarity), W9 (integration symmetry)

<!-- findings or "No findings. All checks pass." -->

---

### 2.3 Behavioral Verification (Score: X/10, Weight: Low)

**Summary:** <one-sentence layer assessment, or "Skipped — evaluator agents unavailable">

**Checks run:** W10 (chain eval), W11 (trigger/exit in context)

<!-- IF skipped -->
Behavioral verification was not performed. Reason: <evaluator agents unavailable / quick check mode / static+semantic layers clean>.

This does not affect the Go/No-Go recommendation for static and semantic layers.
<!-- END IF -->

<!-- findings or "No findings. All checks pass." -->

---

## 3. Skill Integration Map

### Workflow Graph

<!-- Text representation of the workflow graph. For focus mode, mark focus skills. -->

| Skill | Calls | Called By | Terminal | Focus |
|-------|-------|----------|----------|-------|
| <skill-a> | <skill-b>, <skill-c> | — | No | ★ |
| <skill-b> | <skill-d> | <skill-a> | No | |
| <skill-d> | — | <skill-b> | Yes | ★ |

### Per-Skill Integration Status

<!-- For each focus skill (or all skills if no focus), summarize integration health. -->

#### <skill-name> ★

| Dimension | Status |
|-----------|--------|
| Integration section | Present / Missing |
| Calls declared | <list or "none"> |
| Called by declared | <list or "none"> |
| Inputs section | Present / Missing / Empty |
| Outputs section | Present / Missing / Empty |
| Artifact ID overlap | <N matches with upstream, N matches with downstream> |
| Symmetry | All declarations symmetric / Asymmetric: <details> |

### Tools Used

| Tool | Purpose |
|------|---------|
| `bundles-forge audit-workflow` | Workflow audit orchestration, semantic checks (W6, W8, W9) |
| `bundles-forge audit-skill` | Graph analysis (G1-G5 → W1-W5) |
| `evaluator` agent | Chain A/B eval (W10-W11), if available |

Findings are diagnostic. The calling context decides follow-up actions.
```
