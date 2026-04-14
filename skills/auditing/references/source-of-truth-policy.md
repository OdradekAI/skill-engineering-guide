# Source of Truth Policy

Defines the authority hierarchy for bundle-plugin projects. When two sources contradict each other, the higher-ranked source wins.

## Authority Hierarchy

| Priority | Layer | Role | Authoritative For |
|:--------:|-------|------|--------------------|
| 1 | `SKILL.md` | Behavior definition | Orchestration logic, triggering conditions, process steps, scope detection, dispatch decisions |
| 2 | `agents/*.md` | Delegated execution | Scoring formulas, report formats, qualitative criteria — only for the specific protocol the skill delegates |
| 3 | `references/` | Standard registry | Check IDs, checklists, severity definitions, this policy — structured criteria that skills and agents reference |
| 4 | `scripts/` | Automation implementation | Executes the standards defined in layers 1-3. Does not define standards; divergence from higher layers is a bug |
| 5 | `CLAUDE.md` / `AGENTS.md` | Route index + project-level rules | Routing agents to the right skill/agent/reference. **Exception:** cross-skill project-level rules (Security Rules, Commands, Key Conventions) are authoritative at this layer |
| 6 | `docs/` | User teaching | Guides, examples, design rationale. Must declare a `> **Canonical source:**` pointing to the skill or agent it summarizes |
| 7 | `README` / `CHANGELOG` | Project overview | Lowest priority — orienting summaries only. Must not contradict higher layers |

## Contradiction Resolution Protocol

When the auditor (or any reviewer) encounters conflicting information between two sources:

1. **Identify** the two sources and the specific claim each makes
2. **Rank** each source using the hierarchy table above
3. **Rule** the higher-ranked source correct — the lower-ranked source must be updated
4. **Tag** the finding as `[Source Conflict]` in the audit report with:
   - The two conflicting claims (quoted)
   - Which source wins and why (layer number)
   - Recommended fix (update the lower-ranked source)
5. **Severity** assignment:
   - **Warning** for hard contradictions (different numbers, opposite behaviors, missing declarations)
   - **Info** for soft contradictions (tone differences, implication gaps, summary oversimplifications)

## Layer Responsibilities

### Layer 1 — SKILL.md (Behavior Definition)

The skill is the first-class citizen of a bundle-plugin project. It defines:
- When the skill triggers (description field)
- What scope it detects and how
- Which agents/scripts it dispatches and under what conditions
- How it interprets and composes results
- What it outputs and who consumes it

Skills own the "what" and "when." When a skill says auditing is "pure diagnostic" but a lower-ranked source says it "orchestrates fixes," the skill wins.

### Layer 2 — agents/*.md (Delegated Execution)

Agent files are **delegated sources**: they hold authority only for the specific execution protocol a skill explicitly delegates to them. The skill decides whether to dispatch the agent and how to use its output. If a skill and its agent disagree on scope or dispatch conditions, the skill wins. If they disagree on scoring formula or report format (execution details), the agent wins — because the skill explicitly delegates those details.

### Layer 3 — references/ (Standard Registry)

Checklists, registries (`audit-checks.json`), and policy files (this document) define the standards that skills, agents, and scripts reference. They are the structured truth — when a script implements a check differently from what the registry says, the registry is correct and the script must be updated.

Within `references/`, `audit-checks.json` is the machine source from which checklist markdown tables are generated. Edit the JSON first, then regenerate.

### Layer 4 — scripts/ (Implementation)

Scripts implement the standards defined in layers 1-3. They are not sources of truth. When a script uses `severity="warning"` but `audit-checks.json` says `severity: "critical"` for the same check ID, the script has a bug.

Fix direction: always update the script to match the higher layer, never the reverse. If the higher layer's rule proves impractical, update the higher layer first (with rationale), then update the script.

### Layer 5 — CLAUDE.md / AGENTS.md (Index Layer)

These files serve as routing indexes: they tell AI agents where to find information. They should summarize, not define. **Exception:** content that spans multiple skills and has no natural single-skill home — Security Rules, Commands, Key Conventions — is authoritative at this layer.

Architecture descriptions in CLAUDE.md (e.g., "hub-and-spoke model") should be kept minimal and link to the relevant skills for detail. If CLAUDE.md's architecture summary drifts from the skills' actual behavior, the skills are correct.

### Layer 6 — docs/ (User Teaching)

Every guide in `docs/` must include a `> **Canonical source:**` declaration near the top, pointing to the skill or agent it summarizes. Guides explain concepts and provide examples — they do not override the execution details in their canonical source.

### Layer 7 — README / CHANGELOG (Overview)

README provides project orientation for new users. It must not make behavioral claims that contradict skills. CHANGELOG records historical changes — it is exempt from cross-reference validation (D2) since it may reference renamed skills.

## Scoring Formula Note

The project-level and single-skill scoring formulas intentionally differ:
- **Project-level** (`plugin-checklist.md`): capped warning penalty per check ID — `capped_warning_penalty = sum(min(count_per_check_id, 3))`
- **Single-skill** (`skill-checklist.md`): uncapped — `critical × 3 + warning × 1`

This is by design, not a contradiction. Project audits encounter many findings per check ID across multiple skills, so capping prevents a single repetitive issue from dominating the score. Single-skill audits have fewer findings, making capping unnecessary.

## Automated Enforcement

Two checks in `audit_docs.py` support this policy:

- **D8** — Canonical source declaration: each `docs/*.md` guide must have a `> **Canonical source:**` line pointing to an existing skill or agent file
- **D9** — Numeric cross-validation: key numbers extracted from skills/agents and their corresponding guides must match (e.g., "N attack surfaces", "N categories", "N targets")

The auditor agent applies this policy during qualitative assessment (±2 adjustment), tagging soft contradictions as `[Source Conflict]` info items.
