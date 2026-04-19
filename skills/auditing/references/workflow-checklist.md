# Workflow Audit Checklist

Structured criteria for evaluating workflow quality — how skills connect, hand off artifacts, and compose into coherent chains. Use this when running a workflow audit, either standalone or as part of a full project audit.

This checklist complements `plugin-checklist.md` (which covers 10 project-level categories, including Workflow). Category 5 (Cross-References) in the project checklist handles static link resolution (X1-X3). This checklist handles the workflow graph, semantic interfaces, and behavioral verification that sit above link resolution.

## Scoring

Each layer is scored 0-10 using the same baseline formula as the project audit:

```
baseline = max(0, 10 - (critical_count × 3 + capped_warning_penalty))
```

where `capped_warning_penalty = sum(min(count_per_check_id, 3))` — warnings from the same check ID are capped at -3 per ID.

**Overall workflow score** = weighted average of the three layers:

| Layer | Weight | What It Measures |
|-------|--------|-----------------|
| Static Structure | 3 | Graph topology, declared dependencies |
| Semantic Interface | 2 | Integration declarations, artifact clarity |
| Behavioral Verification | 1 | End-to-end chain execution quality |

Total weight = 6. The behavioral layer has low weight because it requires evaluator agents and may not always be run. When skipped, it is scored as **N/A** and excluded from the weighted average (denominator reduces to 5).

---

## Layer 1: Static Structure (Weight: High)

Automated checks — produced by `audit_skill.py` graph analysis (G1-G5) and consumed by `audit_workflow.py` as W1-W5.

<!-- BEGIN:workflow/static -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| W1 | Warning/Info | No undeclared circular dependencies in the workflow graph. Cycles declared via `<!-- cycle:a,b -->` in `## Integration` are demoted to Info | `_graph.py` |
| W2 | Info | All skills are reachable from entry points (skills referenced by `using-*` bootstrap). Skills declaring "Called by: user directly" in `## Integration` are exempt | `_graph.py` |
| W3 | Info | Terminal skills (no outgoing cross-references) have an `## Outputs` section documenting final deliverables and are clearly identifiable as workflow endpoints | `_graph.py` |
| W4 | Info | Skills referenced by other skills have an `## Inputs` section declaring expected artifacts | `_graph.py` |
| W5 | Info | For each edge A→B, at least one artifact ID in A's `## Outputs` matches an ID in B's `## Inputs` | `_graph.py` |
<!-- END:workflow/static -->

**How to run:**
```bash
bundles-forge audit-skill --json <target-dir>
```
Inspect the `graph` key in the JSON output for G1-G5 findings, which map directly to W1-W5.

---

## Layer 2: Semantic Interface (Weight: Medium)

Agent or manual checks — verify that Integration sections are complete, artifact descriptions are meaningful, and cross-reference conventions are consistent.

<!-- BEGIN:workflow/semantic -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| W6 | Info | Skills with workflow dependencies document them in an `## Integration` section with `**Calls:**` and/or `**Called by:**` blocks | `audit_workflow.py` (partial) |
| W7 | Info | Workflow chain has no semantically unreasonable circular dependencies — declared cycles (`<!-- cycle:a,b -->`) have a clear rationale (e.g. feedback loop between audit and optimize) | `agent-only` |
| W8 | Warning | `## Inputs` and `## Outputs` sections contain meaningful semantic descriptions — not empty, not placeholder text (e.g. "TBD", "TODO"), each artifact has a name and one-line purpose | `audit_workflow.py` |
| W9 | Warning | For newly added skills: Integration section uses the correct project cross-reference prefix, `**Calls:**` / `**Called by:**` declarations are symmetric with the skills they reference (if A calls B, B should list A in Called by) | `audit_workflow.py` |
<!-- END:workflow/semantic -->

**Symmetry check (W9):** For each edge A→B declared in A's `**Calls:**`, verify that B's `**Called by:**` lists A. Asymmetric declarations indicate incomplete integration.

---

## Layer 3: Behavioral Verification (Weight: Low)

Requires evaluator agent dispatch — validates that workflow chains actually execute correctly end-to-end. Skip this layer when evaluator agents are unavailable or when the audit is a quick check. **When skipped, score as N/A** (excluded from weighted average) rather than a default 10.

<!-- BEGIN:workflow/behavioral -->
| Check | Severity | Criteria | Automation |
|-------|----------|----------|------------|
| W10 | Warning | Chain A/B Eval: for each workflow chain involving focus skills, an end-to-end scenario produces no broken handoffs (evaluator reports all transitions as "smooth" or "acceptable") | `evaluator` agent with label "chain" |
| W11 | Info | Newly added skills can be triggered and exit correctly within their workflow chain context — the skill activates on expected input and produces output consumable by the next skill in the chain | `evaluator` agent (single-skill-in-chain) |
<!-- END:workflow/behavioral -->

**When to run behavioral checks:**
- Pre-release (recommended)
- After major workflow changes (adding/removing skills from a chain)
- When W1-W5 findings indicate structural issues that may affect behavior
- When `--focus-skills` targets skills that were recently added or modified

**When to skip:**
- Quick workflow health checks
- When evaluator agents are unavailable (note this in the report)
- When static and semantic layers show no issues

---

## Focus Mode

When `--focus-skills skill-a,skill-b` is specified, the workflow audit runs all checks but partitions findings into two groups:

| Group | Contents |
|-------|---------|
| **Focus Area** | Findings directly involving the specified skills — W1 cycles containing them, W2 reachability of them, W5 edges from/to them, W6-W9 checks on their Integration/Inputs/Outputs, W10-W11 chain evals involving them |
| **Context** | All other findings from the full graph analysis — included for completeness but clearly separated in the report |

Focus mode does not reduce the analysis scope — it reduces the report noise.
