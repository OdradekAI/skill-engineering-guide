# Optimizing Guide

[中文](optimizing-guide.zh.md)

A user-oriented guide to optimizing bundle-plugins and individual skills with Bundles Forge. Covers quick start, scope detection, the diagnose → delegate → verify pipeline, 8 optimization targets, A/B evaluation, and feedback iteration.

## Overview

Optimizing is the **orchestrator** for iterative improvement in the hub-and-spoke model. It **diagnoses** what needs to change, **delegates** substantive content edits to `bundles-forge:authoring`, and **verifies** outcomes by invoking `bundles-forge:auditing` (one-way: auditing reports only; it does not call back into optimizing).

Unlike auditing (which assesses only), optimizing drives improvement from the hub — fixing descriptions, reducing tokens, tightening workflow chains, and processing user feedback — routing SKILL.md and agent content work to authoring where appropriate.

**Core principle:** Optimize for the agent's experience. Every improvement should make skills easier to discover, faster to load, and clearer to follow.

> **Canonical source:** The full execution protocol (scope detection, target details, A/B eval steps, feedback validation) lives in `skills/optimizing/SKILL.md`. This guide helps you understand *what each target does*, *how to interpret results*, and *when to use which approach*.

---

## Quick Start

The fastest way to improve an existing bundle-plugin or skill:

1. **Run an audit** (optional but recommended) — `bundles-forge:auditing` produces a diagnostic report that optimizing can consume directly
2. **Invoke** `/bundles-optimize` (or ask the agent to optimize your project or skill)
3. **The agent auto-detects scope** — project root or single skill — and selects applicable targets
4. **Review proposed changes** — the agent presents its improvement plan before applying
5. **Verify** — the agent runs `bundles-forge:auditing` after changes to confirm improvement

Optimizing accepts local paths, GitHub URLs, and zip/tar.gz files as input. You don't need to clone a repo first.

---

## Choosing Your Path

Optimizing auto-detects your scope from the path you provide:

| Scope | Detection | Mode | Applicable Targets |
|-------|----------|------|--------------------|
| Project root | Has `skills/` + `package.json` | **Project optimization** | All 8 targets + feedback |
| Single skill directory | Has `SKILL.md`, no `skills/` subdirectory | **Skill optimization** | Core targets (1-4) + feedback |

### Decision Flowchart

```
Are you optimizing an entire project or a single skill?
  ├─ Entire project → Project optimization (all 8 targets)
  │    ├─ Have an audit report? → Feed it as input for prioritized optimization
  │    └─ No audit report? → Optimizing runs its own diagnosis
  └─ Single skill → Skill optimization (targets 1-4 + feedback)
       ├─ Skill triggered but produced wrong results? → Feedback iteration
       └─ Skill needs engineering improvement? → Targets 1-4
```

### Supported Inputs

| Input | Action |
|-------|--------|
| Local directory path | Use directly |
| GitHub repo URL | Shallow clone to temp directory |
| GitHub subdirectory URL | Clone repo, extract subdirectory |
| Zip/tar.gz file path | Extract to temp directory |

If download fails, the skill reports the error and suggests alternatives (provide a local path or zip file).

### Input Sources

Optimizing can consume reports from prior audits. A common pattern is **audit first, then optimize** based on findings — but remember that **`bundles-forge:auditing` is diagnostic only**: it does not invoke optimizing. **You** run optimizing when you want fixes, or another orchestrator (for example **`bundles-forge:releasing`**) sequences auditing and optimizing in its pipeline.

| Input | Source | Use |
|-------|--------|-----|
| `audit-report` | `bundles-forge:auditing` (full project) | Per-skill breakdowns for all 8 targets |
| `skill-report` | `bundles-forge:auditing` (skill mode) | Focused 4-category report for skill optimization |
| `workflow-report` | `bundles-forge:auditing` (workflow mode) | W1-W9 findings for Target 4 |
| `user-feedback` | Direct from user | Behavioral feedback for the iteration process |

---

## The Pipeline: Diagnose → Delegate → Verify

Optimizing follows a **one-way** verification pattern toward auditing, not a mutual skill cycle. Auditing never invokes optimizing; optimizing **calls** auditing when it needs a verification report after changes.

```
optimizing diagnoses → delegates content edits to authoring → verifies via auditing
```

**Important:** If verification still shows issues, present them to the user for a manual decision — do not loop indefinitely. Further passes are a **new** user- or orchestrator-driven run of optimizing (or authoring), not auditing "calling back" into optimizing.

### Recommended Workflow

1. Optionally run `bundles-forge:auditing` (full, skill, or workflow mode) to produce a diagnostic report as input.
2. Review the report — prioritize critical findings.
3. Run `bundles-forge:optimizing` with the audit report (or your goals). It diagnoses, delegates content work to `bundles-forge:authoring` as needed, applies non-content optimizations per its protocol, and **invokes** `bundles-forge:auditing` for post-change verification (**optimizing** triggers this step — auditing does not auto-start optimizing).
4. Review the verification report — if issues remain, decide manually whether to run another optimizing or authoring pass.

---

## Core Targets (1-4)

These targets apply to both project optimization and single-skill optimization.

### Target 1: Skill Description Triggering

**The highest-impact optimization.** Descriptions are the primary mechanism for skill discovery — when a user says something, the agent matches intent against description fields.

**The critical rule:** Descriptions must state *triggering conditions*, not *workflow summaries*.

| | Bad (workflow summary) | Good (triggering conditions) |
|---|---|---|
| **Pattern** | "Use for auditing — scans structure, checks manifests, scores categories, generates report" | "Use when reviewing a bundle-plugin for structural issues, version drift, or before release" |
| **Problem** | Agent follows the description shortcut instead of reading the full SKILL.md | Agent reads the full skill for execution details |
| **Result** | Skipped steps, incomplete execution | Full execution as designed |

**Additional rules:**
- Always start with "Use when..."
- Keep under 250 characters (truncated in skill listings beyond this)
- Include concrete symptoms, situations, and contexts
- Never mention the skill's internal steps

#### How to Verify Description Quality

Run the linter to catch mechanical issues:

```bash
python skills/auditing/scripts/audit_skill.py <project-root>
```

Description-specific checks are **Q3-Q7**: missing description (Q3), "Use when..." prefix (Q5), workflow summary anti-pattern (Q6), and length >250 characters (Q7). The full lint suite covers Q1-Q15 and X1-X3 — see Quick Reference for the complete list.

For *behavioral* quality (does the right prompt trigger the right skill?), use A/B eval.

### Target 2: Token Efficiency

Every token in a frequently-loaded skill costs context budget across every session. This matters most for the bootstrap skill (loaded every session) and commonly-triggered skills.

**Targets:**
- SKILL.md body < 500 lines
- Bootstrap skill (`using-*`) < 200 lines
- Move heavy reference material to `references/`

**Techniques:**

| Technique | Example |
|-----------|---------|
| Cross-reference instead of repeating | `See bundles-forge:authoring` instead of duplicating rules |
| One excellent example over three mediocre | Remove redundant examples that teach the same concept |
| Move flag docs to --help | Reference `python skills/auditing/scripts/audit_skill.py --help` instead of listing all flags |
| Eliminate intra-project redundancy | Don't repeat what's in another skill's `references/` |

### Target 3: Progressive Disclosure

The three-level loading system ensures minimal context usage:

| Level | When Loaded | Budget |
|-------|-------------|--------|
| Metadata (name + description) | Always in context | ~100 words |
| SKILL.md body | When skill triggers | < 500 lines |
| Reference files (`references/`) | On demand | Unlimited |

**When to extract to references/:**
- SKILL.md approaching 500 lines
- Tables or checklists that are only needed during execution (not for understanding the skill's purpose)
- Template content that the agent copies verbatim

### Target 4: Workflow Chain Integrity

Consumes workflow audit findings to identify and fix workflow issues. The workflow audit has two layers:

- **Script-automated (W1-W9):** Static graph analysis and semantic checks — run via `python skills/auditing/scripts/audit_workflow.py`
- **Evaluator-only (W10-W11):** Chain evaluation and behavioral verification — requires `evaluator` agent dispatch

If no workflow report is available:

```bash
python skills/auditing/scripts/audit_workflow.py <project-root>
python skills/auditing/scripts/audit_workflow.py --focus-skills skill-a,skill-b <root>
```

**Fix priority guide:**

| Finding | What It Means | How to Fix |
|---------|--------------|-----------|
| W1 (undeclared cycle) | Two skills call each other but the loop isn't declared | Add `<!-- cycle:a,b -->` in `## Integration` if intentional, or restructure |
| W2 (unreachable skill) | Skill exists but nothing chains to it | Add to bootstrap routing, or declare `Called by: user directly` |
| W3/W4 (missing I/O) | Terminal skill has no `## Outputs`, or referenced skill has no `## Inputs` | Add the section with artifact IDs |
| W5 (artifact ID mismatch) | Upstream `## Outputs` and downstream `## Inputs` use different names | Align the backtick artifact IDs |
| W9 (placeholder sections) | Inputs/Outputs exist but are empty or generic | Write meaningful semantic descriptions |
| W10 (asymmetric integration) | Skill A says it calls B, but B doesn't say it's called by A | Add the missing `**Called by:**` declaration |

In single-skill mode, only W9 (placeholder sections) and W10 (asymmetric integration) apply — the rest require project-wide graph analysis.

---

## Project-Only Targets (5-8)

These targets are skipped in single-skill mode. They require project-wide context.

### Target 5: Platform Coverage

Identify platforms the project doesn't yet support. For adding new platforms, invoke `bundles-forge:scaffolding` — optimizing doesn't generate platform adapters itself.

### Target 6: Security Remediation

Fix security findings from `bundles-forge:auditing` Category 10. Common fixes:

| Finding | Fix |
|---------|-----|
| Hook script makes network calls | Remove or justify with comments |
| OpenCode plugin has excessive capabilities | Scope to declared needs |
| Agent prompt lacks scope constraints | Add explicit boundaries |
| SKILL.md contains encoded/obfuscated content | Strip or replace with plain text |

### Target 7: Skill & Workflow Restructuring

Structural changes to the project: adding skills, replacing skills, reorganizing workflow chains, or converting skills to subagents. This was previously part of blueprinting (Scenario D) but belongs in optimizing because it operates on existing projects without producing a design document.

#### When to Use

| User Says | Action |
|-----------|--------|
| "Add a new skill to my project" | Target 7a — add skill, wire into workflow |
| "Replace this skill with a better one" | Target 7b — replace and update references |
| "The workflow chain needs reorganizing" | Target 7c — restructure execution paths |
| "This skill should be a subagent instead" | Target 7d — convert to read-only agent |
| "My project needs better X capability" | Feedback process → may lead to Target 7a |

#### Adding Skills (7a)

The most common restructuring operation. The process:

1. Read the existing project — map skills, workflow graph, bootstrap routing
2. Inventory new skills — source, structure, frontmatter quality
3. Check compatibility against the existing project (naming, responsibilities, conventions)
4. For third-party skills — follow the shared integration reference (`references/third-party-integration.md`) covering license, security audit, and integration intent
5. Design insertion points — where do new skills connect?
6. Apply — copy, adapt, update Integration sections
7. Verify — focused workflow audit with `--focus-skills`

#### Replacing Skills (7b)

Same compatibility analysis as adding, plus:
- Map all references to the old skill
- Update cross-references, Integration sections, and routing table
- Verify with workflow audit

#### Reorganizing Workflows (7c)

When the execution chain has inefficiencies:
- Map the current graph and identify bottlenecks or unnecessary handoffs
- Propose new chain (present to user)
- Update Integration sections and routing
- Verify with Chain A/B Eval

#### Skill-to-Agent Conversion (7d)

Candidates for conversion:
- Execution produces verbose temporary context (search results, file contents, logs) that subsequent steps don't need
- Skills that only inspect/validate without modifying files
- Skills that produce structured reports (self-contained output)
- Skills that could run in parallel with other work (optional bonus)

Conversion extracts the execution protocol into `agents/<role>.md` with fallback logic for when subagents are unavailable. After conversion, dispatch the `evaluator` agent with test prompts to confirm the new agent correctly executes the former skill's responsibilities, then run `bundles-forge:auditing` to verify dispatch/fallback logic.

### Target 8: Optional Component Management

Add, adjust, or migrate optional plugin components based on evolving project needs. This target handles the gap between initial scaffolding and the components a project needs as it matures.

#### When to Use

| Signal | Component | Action |
|--------|-----------|--------|
| Skills hardcode API keys/endpoints as `${VAR}` env vars | `userConfig` | Migrate to `userConfig` for automatic user prompting |
| Audit finds MCP servers without `userConfig`-backed auth | `userConfig` | Add `userConfig` fields with `sensitive: true` |
| Skills reference external SaaS APIs with no integration | `.mcp.json` or `bin/` | Add MCP server or CLI — consult decision tree |
| Skills involve language-specific code intelligence | `.lsp.json` | Add LSP server config |
| Users request custom output formats | `output-styles/` | Add output style definitions |
| Plugin MCP server has npm dependencies | `${CLAUDE_PLUGIN_DATA}` | Add SessionStart dependency install hook |
| Plugin uses `../` paths or writes to `${CLAUDE_PLUGIN_ROOT}` | Path migration | Fix to use relative `./` paths and `${CLAUDE_PLUGIN_DATA}` |

#### How It Works

1. **Diagnose** — identify signals from audit reports, user feedback, or direct inspection
2. **Decide** — consult `skills/scaffolding/references/external-integration.md` for the full decision tree (CLI vs MCP, userConfig schema, PLUGIN_DATA patterns, LSP fields, output-styles format)
3. **Execute** — invoke `bundles-forge:scaffolding` using its "Adding Optional Components" flow
4. **Verify** — run `bundles-forge:auditing` to confirm structural integrity and security compliance (especially for new MCP servers and userConfig sensitive values)

---

## A/B Evaluation

A/B eval is the core quality assurance mechanism for description changes and feedback-driven improvements. It compares original vs optimized versions side-by-side.

### How It Works

```
1. Copy the skill to a working version (<skill-name>-optimized/)
2. Apply changes to the copy only (never overwrite the original first)
3. Create 5+ realistic test prompts that should trigger this skill
4. Dispatch two evaluator agents in parallel:
   - Evaluator A: "original" label → test with original skill
   - Evaluator B: "optimized" label → test with optimized skill
5. Compare results → present to user
6. User decides: adopt optimized version or discard
```

### What to Compare

| Metric | What It Tells You |
|--------|------------------|
| **Trigger rate** | How many prompts correctly activated the skill? |
| **False negatives** | Did the optimized description miss cases the original caught? |
| **False positives** | Did either version trigger on prompts meant for other skills? |
| **Step accuracy** | Did the agent follow all steps, or take shortcuts? |

### When to Skip A/B

| Situation | Skip? | Rationale |
|-----------|:---:|-----------|
| Purely additive change (new trigger phrases, no modifications) | Yes | Simple verification pass is sufficient |
| Structural fix (missing section, broken reference) | Yes | Not a behavioral change |
| Description rewrite changing existing triggers | **No** | Must verify no regressions |
| Feedback-driven behavior change | **No** | Must compare old vs new behavior |

### Chain A/B Eval

For workflow transitions (not individual descriptions), use chain evaluation:

1. Define a realistic end-to-end scenario
2. Dispatch evaluator with "chain" label and ordered skill list
3. Review transition quality ratings at each handoff
4. Focus on "broken" handoffs — these indicate missing artifacts or unclear instructions

**Use chain eval after:** modifying Inputs/Outputs, adding skills to a chain, or when workflow audit findings indicate issues.

### Subagent Fallback

When subagent dispatch is unavailable, two options:

| Fallback | How | Trade-off |
|----------|-----|-----------|
| Sequential inline | Follow `agents/evaluator.md` protocol inline, randomize order | Slower, possible ordering bias |
| Skip A/B | Apply change directly with simple verification | Faster, no comparison data |

The user chooses which fallback to use.

---

## Feedback Iteration

When a user reports that a skill triggered but produced wrong results, the feedback process provides structured iteration.

### Feedback Classification

| User Says | Action |
|-----------|--------|
| "This skill triggered but produced wrong results" | Feedback iteration |
| "The steps are in the wrong order" | Feedback iteration |
| "Description format doesn't follow conventions" | Optimization targets 1-3 |
| "Token budget exceeded across the project" | Optimization targets 2-3 (project mode) |

### The 3-Question Validation Framework

Before applying any feedback, each item goes through validation:

| Question | Purpose | Red Flag |
|----------|---------|----------|
| **Goal alignment:** Does this serve the skill's core goal? | Prevents scope drift | "This would turn the skill into something different" |
| **Necessity:** Is there an actual defect, or just a style preference? | Prevents unnecessary churn | "The skill works fine, I just prefer a different format" |
| **Side effects:** Could this introduce complexity or regression? | Prevents creep | "This adds 50 lines to handle a rare edge case" |

### Feedback Process Flow

```
Receive feedback
  → Identify target skill
  → If external skill: fork with forked- prefix
  → Read skill, understand core goal
  → Validate each item (3-question framework)
  → Present improvement plan → USER CONFIRMS
  → Copy to working version
  → Apply changes to copy
  → A/B eval (original vs optimized)
  → User decides: adopt or discard
  → Optimizing invokes auditing for post-change verification
```

**Rules:**
- Never apply feedback without user confirmation
- For external skills, always fork first (add provenance header)
- At most one verification pass after changes; if issues remain, escalate to the user — do not auto-loop. **Optimizing** triggers re-audit when following this skill's protocol; **auditing** does not auto-trigger optimizing.

---

## Common Mistakes

| Mistake | What Goes Wrong | How to Avoid |
|---------|----------------|--------------|
| Trying to optimize everything at once | Unfocused changes that are hard to verify | Pick one target, measure, improve, verify — then move to the next |
| Rewriting descriptions as workflow summaries | Agent shortcuts the description instead of reading the full SKILL.md | State triggering *conditions* ("Use when reviewing..."), not *steps* ("Scans structure, checks manifests...") |
| Ignoring the bootstrap skill's token budget | The bootstrap skill loads every session, so bloat costs context everywhere | Keep `using-*` under 200 lines — this is the highest-ROI token optimization |
| Applying user feedback without validation | Style preferences masquerade as defect reports, leading to unnecessary churn | Run every feedback item through the 3-question validation framework before accepting |
| Expanding a skill's scope based on feedback | A skill slowly drifts from its original responsibility | Feedback should improve *how* the skill works, not change *what* it is |
| Running all 8 targets on a single skill | Targets 5-8 require project context and produce no useful results at skill scope | Let scope auto-detection handle it — single skills only get targets 1-4 |
| Adding third-party skills without security audit | Imported content may contain encoded prompts, excessive tool access, or network calls | Always run `bundles-forge:auditing` on imported skills — see `references/third-party-integration.md` |
| Adding skills without updating Integration sections | The workflow graph becomes inconsistent, causing W10 (asymmetric integration) findings | Every new skill connection needs symmetric `**Calls:**` and `**Called by:**` declarations |
| Skipping A/B eval for description rewrites | A description that improves one trigger may break another | Always A/B eval when modifying existing trigger phrases — additive-only changes can skip |

---

## FAQ

**Q: What's the difference between auditing and optimizing?**

Auditing is pure diagnostics — it checks, scores, and reports. It never modifies files or calls optimizing. Optimizing is the improvement driver — it reads audit reports (or your goals), diagnoses what to fix, delegates content changes to authoring, and verifies results by calling auditing. Think of it as: auditing tells you what's wrong, optimizing fixes it.

**Q: When should I use optimizing vs authoring directly?**

Use optimizing when you need *diagnosis* — when you don't know exactly what to fix, or you want a structured improvement process with A/B evaluation and verification. Use authoring directly when you already know exactly what content to write or change (e.g., "rewrite this description to X").

**Q: Do I need to run an audit before optimizing?**

No, but it's recommended. Optimizing can run its own diagnosis, but feeding it an audit report gives it a prioritized list of findings to work through. The common pattern is: audit → review report → optimize based on findings.

**Q: Which targets apply when optimizing a single skill?**

Targets 1-4 (description triggering, token efficiency, progressive disclosure, workflow chain integrity) plus feedback iteration. Targets 5-8 are skipped because they require project-wide context. Within Target 4, only W9 (placeholder sections) and W10 (asymmetric integration) apply at skill scope.

**Q: What if the verification audit still shows issues after optimization?**

The agent presents remaining issues to you for a manual decision — it does not loop automatically. You can choose to run another optimizing pass, invoke authoring directly for specific fixes, or accept the current state. This prevents infinite optimize-audit cycles.

**Q: Can I optimize a project hosted on GitHub without cloning it first?**

Yes. Pass a GitHub URL directly — the skill performs a shallow clone automatically. This also works for subdirectory URLs (e.g., `github.com/user/repo/tree/main/skills/my-skill`) and archive URLs (.zip/.tar.gz).

---

## Quick Reference

### Scripts

```bash
python skills/auditing/scripts/audit_skill.py <path>                        # Quality lint (Q1-Q15, X1-X3)
python skills/auditing/scripts/audit_skill.py <skill-dir>                   # Single skill audit (4 categories)
python skills/auditing/scripts/audit_workflow.py <path>                      # Workflow audit (W1-W9, script-automated)
python skills/auditing/scripts/audit_workflow.py --focus-skills a,b <path>   # Focused workflow audit
python skills/auditing/scripts/audit_security.py <path>                       # Security scan (7 surfaces)
```

W10-W11 (chain evaluation and behavioral verification) require `evaluator` agent dispatch and are not produced by the script.

### Target Applicability by Scope

| Target | Project | Skill |
|--------|:---:|:---:|
| 1. Description Triggering | Full | Full |
| 2. Token Efficiency | Full | Full |
| 3. Progressive Disclosure | Full | Full |
| 4. Workflow Chain Integrity | Full | Partial (W9/W10 only) |
| 5. Platform Coverage | Full | Skip |
| 6. Security Remediation | Full | Partial |
| 7. Skill & Workflow Restructuring | Full | Skip |
| 8. Optional Component Management | Full | Skip |
| Feedback Iteration | Full | Full |
