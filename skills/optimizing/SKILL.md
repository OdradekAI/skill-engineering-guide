---
name: optimizing
description: "Use when optimizing a bundle-plugin or single skill — improving descriptions, reducing tokens, fixing audit findings, restructuring workflows, adding skills to fill gaps, or iterating on user feedback"
allowed-tools: Bash(bundles-forge audit-skill *) Bash(bundles-forge audit-security *) Bash(bundles-forge audit-docs *) Bash(bundles-forge audit-plugin *) Bash(bundles-forge audit-workflow *) Bash(bundles-forge checklists *)
---

# Optimizing Bundle-Plugins

## Overview

Orchestrate targeted improvement of a bundle-plugin project or a single skill. Unlike a full audit, optimization focuses on goals: better triggering, lower token cost, tighter workflow chains, and feedback-driven skill refinement. This skill diagnoses issues, decides on improvements, and delegates content changes to `bundles-forge:authoring`.

**Core principle:** Optimize for the agent's experience. Diagnose → decide → delegate → verify.

**Skill type:** Hybrid — follow the execution flow rigidly (diagnose → decide → delegate → verify), but select targets and adapt execution strategies flexibly based on audit findings and user goals.

**Announce at start:** "I'm using the optimizing skill to improve [this project / this skill]."

## Step 1: Resolve Input & Detect Scope

The target can be a local path, a GitHub URL, or a zip file. Normalize the input to a local directory before scope detection.

### Input Normalization

> Canonical source: `bundles-forge:auditing` — `references/input-normalization.md`

Normalize local paths, GitHub URLs, and archives to a local directory. Read the canonical input normalization reference for the full table, security rules, and failure handling.

### Scope Detection

After normalization, determine the scope from the resolved local path:

| Target | How to Detect | Mode |
|--------|--------------|------|
| Project root | Has `skills/` directory and `package.json` | **Project optimization** — all 6 targets |
| Single skill directory | Contains `SKILL.md` but no `skills/` subdirectory | **Skill optimization** — 3 targets + feedback iteration |
| Single SKILL.md file | Path ends in `SKILL.md` | **Skill optimization** — 3 targets + feedback iteration |

**If the target is a single skill, skip to the Skill Optimization section below.**

---

## Project Optimization

### Process

1. **Diagnose** — run audit scripts, assess skill health, detect workflow gaps
2. **Classify & Route** — classify action type, select applicable targets
3. **Apply** — execute selected targets, delegate content changes to authoring
4. **Verify** — re-audit to confirm improvement

### Diagnostic Tools

#### Audit Script Baseline

Run the quality linter to identify frontmatter issues, description anti-patterns, and broken references before manual optimization:

```bash
bundles-forge audit-skill <project-root>        # markdown report
bundles-forge audit-skill --json <project-root>  # machine-readable
```

The linter automates checks Q1-Q15 and X1-X3 from the skill quality ruleset. Focus manual effort on the subjective targets below.

#### Skill Health Assessment

Assess each skill across four qualitative dimensions: trigger confidence, execution clarity, end-to-end completeness, and degradation signals. See `references/optimization-decision-trees.md` for the full assessment framework and signal-to-target mapping.

#### Workflow Gap Detection

When findings reveal structural gaps (not just broken connections but missing capabilities), consider creating new skills via the CAPTURED action type. See `references/optimization-decision-trees.md` for the gap detection signals.

### Routing & Classification

Route findings to targets and classify each action (FIX / DERIVED / CAPTURED) before delegating. See `references/optimization-decision-trees.md` for:
- **Target routing table** — maps Q/W/SC findings and user signals to the 6 targets
- **Action classification** — FIX (repair defect), DERIVED (enhance/specialize), CAPTURED (new skill for gap)
- **Pre-delegation checklist** — classification rationale, impact analysis, scope preservation

### Target 1: Skill Description Triggering

The highest-impact optimization. Descriptions are the primary mechanism for skill discovery.

**Diagnosis** — identify descriptions that summarize workflow, exceed 250 characters, are too narrow/broad, or fail to start with "Use when...".

**Decision** — draft the improved description and rationale. Use A/B eval (see below) to compare triggering accuracy before and after.

**Delegation** — invoke `bundles-forge:authoring` with a precise change spec: the old description verbatim, the new description, the rationale tied to a specific diagnosis (audit finding, health assessment dimension, or user feedback), and the action classification (FIX/DERIVED). Do not ask authoring to "improve the description" — specify the exact change.

**Guiding principle:** Use A/B eval when a change could produce regression effects — when improving one dimension might degrade another. Each eval scenario below defines its own skip conditions based on what kind of regression is possible.

#### A/B Eval for Description Changes

When optimizing a description, never overwrite the original blindly. Use a copy-and-compare approach:

```
1. Copy the skill to a working version (e.g. `<skill-name>-optimized/`)
2. Apply the description change to the copy only
3. Create 5+ realistic test prompts that should trigger this skill
4. Dispatch two `evaluator` agents (`agents/evaluator.md`) in parallel:
   - Evaluator A: label "original", loaded with the ORIGINAL skill → run all test prompts
   - Evaluator B: label "optimized", loaded with the OPTIMIZED skill → run all test prompts
5. Compare: which version triggered correctly on more prompts?
6. Present results to user with side-by-side comparison
7. User decides → adopt optimized version (replace original) or discard
```

**If subagent dispatch is unavailable:** Ask the user which fallback to use:
- **Sequential inline:** Read `agents/evaluator.md` and follow its execution protocol inline. Run both evaluations in sequence within this conversation. Randomize which version runs first (flip a coin) to reduce ordering bias — note the execution order in results so the user can judge accordingly
- **Skip A/B:** Apply the change directly with a simple verification pass instead of comparative evaluation

**What to compare:**
- Trigger rate: how many of the test prompts correctly activated the skill?
- False negatives: did the optimized description miss cases the original caught?
- False positives: did either version trigger on prompts meant for other skills?

**When to skip A/B eval:** If the change is purely additive (adding triggering conditions that were previously missing) and doesn't modify existing trigger phrases, a simple verification pass is sufficient.

### Target 2: Content Optimization

#### Token Budget

> **Canonical source:** Token budgets are defined in `bundles-forge:authoring` (Token Efficiency section).

**Diagnosis** — identify skills exceeding token budgets (SKILL.md body > 500 lines, bootstrap > 200 lines), duplicated content, sections that should be in `references/`.

**Decision** — determine what to extract, merge, or cut. Map specific sections to their target location.

**Delegation** — invoke `bundles-forge:authoring` with a section-level restructuring spec: which sections to extract (source heading → target file in references/), which content to cut (quote the specific lines), and which cross-references to add. Authoring should modify only the named sections, not rewrite the entire SKILL.md.

#### Layer Assignment

**Diagnosis** — verify the three-level loading structure (metadata / SKILL.md body / references) is properly layered. Identify skills where the body contains content that belongs at a different level.

**Decision** — determine which sections to promote (to metadata) or demote (to references/).

**Delegation** — invoke `bundles-forge:authoring` with per-section move instructions: for each section being promoted or demoted, specify the source location, the target level, and the reason (e.g. "move lines 45-80 to references/platform-details.md because this content is only needed during platform adaptation, not on every skill load").

### Target 3: Workflow Chain Integrity

Consume the `workflow-report` from `bundles-forge:auditing` (Workflow mode) to identify and fix workflow issues. If no workflow report is available, run the workflow audit first:

```bash
bundles-forge audit-workflow <project-root>                          # full workflow audit
bundles-forge audit-workflow --focus-skills skill-a,skill-b <root>   # focused on specific skills
```

**Fix by W-check priority:** See `references/optimization-decision-trees.md` for the full W1-W10 fix table.

**After fixes — Chain A/B Eval:**

Use chain evaluation to verify end-to-end handoff quality after workflow changes. Follow the same dispatch and fallback pattern as Description A/B Eval, with these differences:

1. Define a realistic end-to-end scenario (e.g. "design and scaffold a new bundle-plugin")
2. Dispatch `evaluator` with label "chain" and the ordered skill list
3. Review transition quality ratings — focus on "broken" handoffs
4. Address broken handoffs by improving `## Inputs` / `## Outputs` declarations

**When to use:** After modifying Inputs/Outputs sections, adding new skills to a workflow chain, or when audit findings indicate workflow integrity issues (W1-W4). Chain eval is sequential by nature (traces a pipeline), so ordering bias is not a concern.

### Target 4: Security Remediation (project only)

Fix security findings from `bundles-forge:auditing` Category 10.

**Targets:**
- Remove unnecessary system access from hook scripts (least privilege)
- Scope OpenCode plugin capabilities to declared needs only
- Remove or justify any network calls in hooks/plugins
- Ensure agent prompts include scope constraints
- Strip encoding tricks or obfuscated content from SKILL.md files

**Process:** Run security scan first, then address findings by priority — critical before warnings, warnings before info:

```bash
bundles-forge audit-security <project-root>
```

Alternatively, invoke `bundles-forge:auditing` for a full audit that includes security (Category 10).

### Target 5: Skill & Workflow Restructuring (project only)

Structural changes to achieve user goals: adding skills, replacing skills, reorganizing workflow chains, or converting skills to subagents.

#### 5a. Adding Skills

When the project has a workflow gap or the user needs new capability:

1. **Read existing project** — list all skills, map the workflow graph (`## Integration` sections), identify the bootstrap skill's routing table
2. **Inventory new skills** — for each skill being added, record source, structure, frontmatter quality
3. **Compatibility analysis** — check naming conflicts, description style, overlapping responsibilities, cross-reference conventions against the existing project
4. **For third-party skills** — follow `references/third-party-integration.md` (inventory checklist, compatibility checks, integration intent, security audit)
5. **Design insertion** — identify where new skills connect to the existing workflow graph, map new `**Calls:**` / `**Called by:**` declarations, update bootstrap routing if needed
6. **Apply** — copy skills into `skills/`, adapt per integration intent, update existing skills' `## Integration` sections
7. **Verify** — run `bundles-forge:auditing` in Workflow mode with `--focus-skills <new-skills>` to verify workflow integrity

For Intent B (integrate into workflow) third-party skills, invoke `bundles-forge:authoring` after adaptation for content quality validation.

#### 5b. Replacing Skills

When a better alternative exists for an existing skill:

1. Analyze the replacement skill's compatibility (same checks as 5a)
2. Map all references to the old skill across the project (cross-references, Integration sections, routing table)
3. Replace and update all references
4. Verify with workflow audit

#### 5c. Reorganizing Workflows

When the execution chain needs restructuring:

1. Map the current workflow graph
2. Identify inefficiencies: unnecessary handoffs, missing shortcuts, bottleneck skills
3. Propose new chain — present to user for approval
4. Update `## Integration` sections across affected skills
5. Update bootstrap routing table
6. Verify with Chain A/B Eval (Target 3)

#### 5d. Skill-to-Agent Conversion

When a skill would work better as a read-only subagent:

Candidates for conversion:
- Execution produces verbose temporary context (search results, file contents, logs) that subsequent steps don't need
- Skills that only inspect/validate without modifying files
- Skills that produce structured reports (self-contained output)
- Skills that could run in parallel with other work (optional bonus)

Conversion steps:
1. Extract the skill's execution protocol into `agents/<role>.md`
2. Update the dispatching skill to use subagent dispatch instead of skill invocation
3. Add fallback logic (read agent file inline when subagents unavailable)
4. Remove the original skill directory if fully replaced

Post-conversion verification:
1. Dispatch `evaluator` (label "original") with test prompts to confirm the new agent correctly executes the former skill's responsibilities
2. Run `bundles-forge:auditing` to verify dispatch/fallback logic in the orchestrating skill

### Target 6: Optional Component Management (project only)

Add, adjust, or migrate optional plugin components based on evolving project needs. This target handles the gap between initial scaffolding and the components a project needs as it matures.

**Diagnosis** — identify signals that a component is needed. See `references/optimization-decision-trees.md` for the full signal-to-component mapping table (userConfig, MCP, LSP, output-styles, PLUGIN_DATA, path migration).

**Decision** — read `bundles-forge:scaffolding` — `references/external-integration.md` for the full decision tree (CLI vs MCP, userConfig schema, PLUGIN_DATA patterns, LSP fields, output-styles format, settings.json scope).

**Execution** — invoke `bundles-forge:scaffolding` using its "Adding Optional Components" flow. Scaffolding handles file generation, manifest updates, and inspector validation.

**Verification** — after scaffolding completes, run `bundles-forge:auditing` to confirm structural integrity and security compliance (especially for new MCP servers and userConfig sensitive values).

---

## Single-Skill Optimization

When the target is a single skill, run only the targets that apply at skill scope. This is auto-detected — no special flags needed.

### Applicable Targets

| Target | Applicable | What to Do |
|--------|-----------|------------|
| 1. Description Triggering | **Full** | Evaluate and improve the description's triggering accuracy |
| 2. Content Optimization | **Full** | Check token budget, references extraction, layer assignment |
| 3. Workflow Chain Integrity | **Partial** | Fix this skill's W9/W10 findings (Inputs/Outputs clarity, integration symmetry) |
| 4. Security Remediation | **Partial** | Fix security issues within this skill's content |
| 5. Skill & Workflow Restructuring | **Skip** | Project-level concern |
| 6. Optional Component Management | **Skip** | Project-level concern |
| Feedback Iteration | **Full** | Process user feedback with 3-question validation |

### Skill Process

1. **Read target skill** — consume `skill-report` if available (or extract per-skill findings from `audit-report`)
2. **Determine goal** — engineering optimization or feedback iteration?
3. **Engineering path:** diagnose applicable targets (1-3, partial 4)
4. **Feedback path:** run the Feedback Iteration process (below)
5. **Delegate** content changes to `bundles-forge:authoring`
6. **Verify** — run `bundles-forge:auditing` (skill mode) for post-change verification

### Script Shortcuts

```bash
bundles-forge audit-skill <skill-directory>     # quality checks on single skill
```

---

## Feedback Iteration

Process user feedback about a specific skill's behavior or output quality. This is a cross-cutting concern — available in both project and skill optimization modes. Use this when a user reports that a skill triggered but produced wrong results, skipped steps, or needs better wording.

### Classify the Feedback

| Signal | Action |
|--------|--------|
| "This skill triggered but produced wrong results" | Feedback iteration (below) |
| "The steps in this skill are in the wrong order" | Feedback iteration (below) |
| "Description format doesn't follow conventions" | Use optimization targets 1-2 |
| "Token budget exceeded across the project" | Use optimization target 2 (project mode) |

### The Feedback Process

```
Receive feedback
  → Identify target skill
  → If external skill: fork with `forked-` prefix before modifying
  → Read skill, understand core goal
  → Validate each feedback item (goal alignment, necessity, side effects)
  → Present improvement plan to user
  → USER CONFIRMS ← gate
  → Copy skill to working version (<skill-name>-optimized/)
  → Delegate changes to bundles-forge:authoring on the copy
  → A/B eval: subagent A (original) vs subagent B (optimized) with same input
  → Present comparison to user
  → User adopts → replace original; User rejects → discard copy
  → Run bundles-forge:auditing for post-change verification
```

**Validation framework** — for each feedback item, ask three questions:
1. **Goal alignment:** Does this serve the skill's core goal, or push it toward a different purpose?
2. **Necessity:** Without this change, does the skill have an actual defect (vs. a style preference)?
3. **Side effects:** Could this introduce complexity creep, scope expansion, or regression?

### A/B Eval for Feedback Changes

Follow the same dispatch and fallback pattern as Description A/B Eval (Target 1), with these differences:

- **Test scenario:** Use the specific scenario from the user's feedback (the input that produced wrong results), not synthetic test prompts
- **What to compare:** Output quality and behavioral correctness, not triggering accuracy
- **When to skip:** If the feedback is about structural issues (missing section, wrong heading level, broken reference) rather than behavioral differences, a simple verification pass is sufficient

**Rules:**
- Never apply feedback without user confirmation of the improvement plan
- For external skills, always fork first (prefix with `forked-`, add provenance header)
- After all changes, invoke `bundles-forge:auditing` for post-change verification — one audit pass only (auditing reports; optimizing decides)

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Optimizing everything at once | Pick one target, measure, improve, verify |
| Adding MUST/ALWAYS/NEVER instead of explaining why | Explain the reasoning — agents respond to understanding |
| Splitting skills too aggressively | Only split when there's a genuine responsibility boundary |
| Ignoring token budget for bootstrap | Bootstrap loads every session — every word counts |
| Applying feedback without validation | Every item goes through the 3-question framework |
| Expanding skill scope during any optimization | Optimization should improve how well a skill fulfills its goal, not shift what the goal is. Verify after every change: does this skill still do the same thing? |
| Running all 6 targets on a single skill | Let scope auto-detection handle it — targets 4-6 don't fully apply |
| Rewriting entire SKILL.md instead of surgical edits | Specify section-level changes in delegation. A FIX to one heading should not trigger a full rewrite — minimize diff surface to reduce regression risk |
| Adding third-party skills without security audit | Always run `bundles-forge:auditing` — see `references/third-party-integration.md` |
| Adding skills without updating Integration sections | Every new connection needs symmetric `Calls` / `Called by` declarations |

## Inputs

- `audit-report` (optional) — findings from `bundles-forge:auditing` (full project mode). Contains per-skill breakdowns — when optimizing a single skill from a full audit, extract the relevant skill's findings from the Per-Skill Breakdown section
- `skill-report` (optional) — findings from `bundles-forge:auditing` (skill mode). More precise input for Skill Optimization — 4-category scored report targeting a single skill
- `workflow-report` (optional) — workflow-specific findings (W1-W11) from `bundles-forge:auditing` (workflow mode), consumed by Target 3
- `user-feedback` (optional) — behavioral feedback about skill quality, triggering issues, or wrong output

## Outputs

- `optimized-skill` — improved SKILL.md content with better descriptions, reduced tokens, or fixed workflow references
- `eval-report` (optional) — optimization record written to `.bundles-forge/`, structured as:
  - **Action type:** FIX, DERIVED, or CAPTURED
  - **Change summary:** one sentence describing what changed and why
  - **Diagnosis basis:** which health dimension, audit finding, or user feedback triggered this optimization
  - **Before/after comparison:** A/B eval results, or verification pass outcome if A/B was skipped

## Integration

**Called by:**
- **bundles-forge:releasing** — fix quality findings during release pipeline
- User directly — standalone optimization of any project or skill

**Calls:**
- **bundles-forge:authoring** — all content changes (descriptions, token optimization, restructuring, third-party adaptation)
  - Artifact: `optimized-skill` → `optimization-spec` (indirect — optimizing formulates the spec, authoring receives it as targeted change instructions)
- **bundles-forge:scaffolding** — Platform Coverage routing for adding new platforms; Optional Component Management target for adding MCP/LSP/userConfig/output-styles
  - Artifact: `optimized-skill` → `project-directory` (indirect — scaffolding operates on the project directory, not the optimization output)
- **bundles-forge:auditing** — post-change verification (one pass, no loops)
  - Artifact: `optimized-skill` → `project-directory` (indirect — auditing targets the project containing the optimized skill)

**Pairs with:**
- **bundles-forge:releasing** — after optimization, versions may need sync
