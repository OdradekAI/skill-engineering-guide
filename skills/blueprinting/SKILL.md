---
name: blueprinting
description: "Use when planning new bundle-plugins, splitting complex skills, combining skills into bundles, or exploring a vague idea about packaging skills"
---

# Blueprinting Bundle-Plugins

## Overview

Turn a vague idea ("I want to package my skills") into a concrete project blueprint through needs exploration, architecture design, and structured review — then orchestrate the full creation pipeline: scaffolding, content authoring, workflow wiring, and initial quality check.

**Core principle:** Understand what you're building — and why — before generating anything. Five minutes of needs exploration saves hours of rework.

**Skill type:** Hybrid pattern — follow the three-phase process rigidly, but question selection, depth, and approach recommendations adapt to user context.

**Announce at start:** "I'm using the blueprinting skill to plan your bundle-plugin."

<HARD-GATE>
Do NOT invoke bundles-forge:scaffolding or any subsequent orchestration phase until the user has approved the design document. Every project — regardless of perceived simplicity — must pass through needs exploration → architecture design → design document review. Quick mode may shorten the process (needs exploration asks only 2 core questions), but it cannot skip it.
</HARD-GATE>

| Agent Reasoning | Reality |
|-----------------|---------|
| "The user's requirements are already clear" | Seemingly clear requirements often miss platform, workflow, and visibility architecture decisions |
| "This is just packaging a few existing skills" | Even simple packaging requires compatibility verification, cross-reference validation, and workflow chain mapping |
| "Moving fast through the process is more efficient" | Five minutes of exploration saves hours of rework from missing architecture decisions |

## Three Entry Points

This skill handles three scenarios. All three feed into the same three-phase interview — only the initial context differs.

- **Scenario A: New project from scratch** — Begin with Context Exploration, then the full interview
- **Scenario B: Splitting an existing complex skill** — Context Exploration reads the existing skill via `references/decomposition-analysis.md`, then enters the interview with richer context. Splitting produces a new project. To refactor skills within an existing project, use `bundles-forge:optimizing` (Skill & Workflow Restructuring target).
- **Scenario C: Composing multiple existing skills** — Context Exploration inventories candidates via `references/composition-analysis.md`, then enters the interview with richer context

If the user has an existing skill they want to break apart, start with Scenario B. If the user has multiple existing skills they want to combine into a **new** unified project, start with Scenario C. Otherwise, start with Scenario A.

> **Adding skills to an existing project?** That's optimization, not blueprinting. Use `bundles-forge:optimizing` (Skill & Workflow Restructuring target) or invoke `/bundles-optimize`.

## Dialogue Strategy

Read `references/dialogue-strategies.md` for the full interview protocol. Core principles: ask 1-2 questions at a time, reject vague answers, propose approaches with trade-offs, challenge over-scoping, surface contradictions immediately, and confirm understanding after each phase.

## Context Exploration

Before asking any questions, gather available context:

### Scenario A (New Project)
1. **Scan the workspace** — look for scattered skill files, existing SKILL.md drafts, or relevant project files that hint at what the user is building
2. If user context is already rich from their initial message, proceed directly to Phase 1

### Scenario B (Decomposition)
1. **Read the existing skill** — follow `references/decomposition-analysis.md` to map responsibilities, identify split points, and propose a decomposition
2. Present the decomposition proposal to the user for approval
3. Proceed to Phase 1 with the decomposition as input context. In Phase 1, skip questions already answered by the decomposition analysis. Confirm those answers with the user rather than re-asking.

### Scenario C (Composition)
1. **Inventory candidate skills** — follow `references/composition-analysis.md` to check compatibility, detect conflicts, and design orchestration
2. Present the composition plan to the user for approval
3. Proceed to Phase 1 with the composition analysis as input context. In Phase 1, skip questions already answered by the composition analysis. Confirm those answers with the user rather than re-asking.

## Phase 1: Needs Exploration

Understand what the user wants to build and why, before making any architecture decisions. Ask these one at a time, adapting based on answers.

### 1. Problem Scenario

Ask: "What problem does this skill bundle solve? How are people solving it today?"

Understand the gap between the current state and what the user envisions. This is the foundation for all subsequent decisions.

### 2. Target Users

Ask: "Who will use this skill bundle? What's their background — what type of developers, what workflows, what platforms?"

The answer shapes platform selection, skill complexity, and documentation style.

### 3. Core Capabilities

Ask: "What capabilities must this skill bundle provide? If you had to remove one, which one would make it pointless?"

This identifies the non-negotiable skills vs nice-to-haves. The agent should actively propose a skill decomposition based on the answer — present 2-3 decomposition approaches with trade-offs when the boundaries aren't obvious.

### 4. Usage Flow

Ask: "Walk me through how someone would use this — from installing the plugin to completing their task."

This reveals workflow dependencies, entry points, and the natural sequence of operations.

### 5. Existing Alternatives (if relevant)

Ask: "Are there similar skill bundles or tools out there? What's different about yours?"

Skip this if the user has already addressed it or if the domain is clearly novel.

### Phase 1 Checkpoint

After collecting needs exploration answers, restate the understanding and verify completeness:

> "Let me confirm what I understand: You're building [one-sentence summary] for [target users] to solve [problem]. The core capabilities are [list]. The usage flow is [summary]. Does this match your intent?"

**Must verify before proceeding:**
- Problem scenario: expressible as "[user] needs to [action] because [reason]" in one sentence
- Target users: at least one concrete persona with platform + workflow identified

Wait for user confirmation before proceeding to Phase 2. If the user corrects anything, update the understanding and re-confirm.

## Phase 2: Architecture Design

With a clear understanding of what and why, now decide how to build it. The agent should actively recommend answers based on Phase 1 context, rather than asking open-ended questions.

**Before making architecture recommendations:** Explicitly list key assumptions derived from Phase 1 and wait for user confirmation. Template:

> "Based on our needs exploration, I'm operating on these assumptions:
> 1. [Complexity assumption — e.g., 'This is a straightforward packaging project']
> 2. [Platform assumption — e.g., 'Primary platform is Claude Code based on your workflow']
> 3. [Independence assumption — e.g., 'Skills appear independent with no workflow chain']
>
> If any of these are wrong, correct me now — they will shape all architecture decisions."

### 1. Project Complexity

Based on Phase 1 answers, **recommend** quick or adaptive mode:

**Quick mode** (quick packaging):
- Target: bundle standalone skills into a plugin with minimal infrastructure
- Skip questions 5 (Workflow Chain), 6 (Bootstrap Strategy), and 4a (Skill Visibility)
- Defaults: no bootstrap, no hooks, Claude Code only
- Jump to a simplified design document after question 4

**Adaptive mode** (adaptive deep interview):
- Full interview with dynamic follow-ups based on answers
- After core questions, conditionally ask about advanced components

Present the recommendation with reasoning: "Based on what you've described — [reasoning] — I recommend [quick/adaptive] mode. [Quick explanation of what this means]."

Quick mode skips most Phase 1/2 questions and defaults to Claude Code only with independent skills. See `references/dialogue-strategies.md` for the full behavior summary table.

### 2. Project Name

Kebab-case identifier (e.g., `my-dev-tools`). This becomes the directory name, package name, and plugin ID across all platforms.

**Validation:** lowercase letters, numbers, hyphens only. No underscores, no spaces.

### 3. Target Platforms

Which platforms should the project support? See `references/platform-reference.md` for the full platform table and selection strategies.

Based on the target users identified in Phase 1, recommend a platform combination with reasoning. Start with what the user actually uses — others can be added later via `bundles-forge:scaffolding`.

### 4. Skill Inventory

Based on the core capabilities and usage flow from Phase 1, **propose a skill decomposition** rather than asking the user to list skills:

"Based on the capabilities you described, I recommend splitting into these skills: [proposed list with one-sentence purpose each]. Here's why this decomposition makes sense: [reasoning]."

When the decomposition isn't obvious, present 2-3 approaches:
- Approach A: [decomposition] — pros/cons
- Approach B: [decomposition] — pros/cons
- Recommended: [which and why]

For each skill, determine:
- Skill name (kebab-case)
- One-sentence purpose
- Rigid or flexible type

If the user isn't sure yet, scaffold with a single placeholder skill and the bootstrap.

#### 4a–7. Adaptive Mode Questions

Questions 4a (Skill Visibility), 5 (Workflow Chain), 6 (Bootstrap Strategy), and 7 (Advanced Components) apply only in adaptive mode. Quick mode skips them. See `references/adaptive-mode-questions.md` for the full question set.

### Phase 2 Checkpoint

Restate the architecture decisions and verify completeness before generating the design document.

**Must satisfy** (missing any one blocks document generation):
- Core skills: each has a name + one-sentence purpose + type (rigid/flexible)
- Architecture mode: quick or adaptive, with explicit reasoning documented
- Target platform: at least one selected, with rationale tied to target users

**Should satisfy** (mark unmet items as [TBD] in the design document):
- Workflow chain: dependency graph is drawn (or explicitly marked "all independent")
- Bootstrap strategy: yes/no decision with reasoning (or "deferred" with rationale)
- Success criteria: at least one measurable outcome the user can verify post-creation

Wait for user confirmation before proceeding to Phase 3.

## Phase 3: Design Document and Review

### Generate Design Document

After the interview, compile a design summary using the template in `references/design-document-template.md`. This template includes both needs context (project overview, target users, use cases, success criteria) and technical architecture (mode, platforms, skills, workflow, components). Conditional fields: fill `Third-Party Sources` only when Scenario C involves external skills; fill `Notes` for special constraints not captured elsewhere. Leave unused conditional fields out of the document.

### Design Document Self-Review

Before presenting to the user, review the document:

1. **Placeholder scan** — any TBD, TODO, or incomplete [TBD] markers? Fix what can be resolved from interview context
2. **Internal consistency** — does the skill inventory match the workflow chain? Do entry-point skills all have commands/?
3. **Scope check** — is this focused on a single project? Does it need decomposition into sub-projects first?
4. **Ambiguity check** — could any requirement be interpreted two ways? If so, pick one and make it explicit

Fix issues inline. Then present the document to the user.

### User Review Gate

Present the design document and ask the user to review:

> "Here's the design document. Please review and let me know if anything needs adjustment before I proceed with the creation pipeline."

If the user requests changes, update the document and re-run the self-review. Only proceed to the Orchestration Pipeline when the user explicitly approves.

The user may request going back to a specific phase to re-discuss decisions — support this without restarting from scratch.

## Orchestration Pipeline

After the user approves the design, orchestrate the full project creation pipeline. Execute each phase in order — do not skip or reorder phases.

### Scaffold

**"Design approved. Invoking scaffolding to generate the project structure."**

Invoke `bundles-forge:scaffolding` with the approved design. Wait for scaffolding to complete (including its inspector self-check) before proceeding.

→ **verify:** inspector self-check passes with 0 critical findings
→ **on fail:** fix structural issues inline, re-run inspector before proceeding

### Author Content

**"Structure generated. Invoking authoring to write skill and agent content."**

Invoke `bundles-forge:authoring` with the full skill inventory from the design document. Pass the complete design document (including project overview, target users, and use cases) so authoring can write more targeted descriptions and overviews. Authoring handles:
- All SKILL.md files listed in the design
- All agent definitions (`agents/*.md`) if the design specifies subagents

Pass the complete list in one invocation — authoring processes them in sequence.

→ **verify:** every skill in the design has a SKILL.md with valid frontmatter (name, description)
→ **on fail:** re-invoke authoring for missing or invalid skills

### Wire Workflow

**"Content authored. Designing workflow integration."**

This step runs within blueprinting — workflow wiring requires the full project context from the interview.

1. For each skill pair with a dependency in the Workflow Chain, write the `## Integration` section:
   - `**Calls:**` and `**Called by:**` declarations must be symmetric (A calls B ⟹ B is called by A)
   - Artifact IDs in `## Outputs` must match downstream `## Inputs`
2. Update the bootstrap skill's routing table to reflect all entry-point and internal skills
3. If the design specifies agent dispatch, add dispatch instructions to the orchestrating skill and `Dispatched by:` to the agent file

→ **verify:** all Calls/Called-by pairs are symmetric; bootstrap routes match skill inventory
→ **on fail:** fix asymmetric links or missing routes before proceeding

### Run Audit

**"Workflow wired. Running initial audit."**

Invoke `bundles-forge:auditing` on the project root for a baseline quality check.

→ **verify:** 0 critical audit findings
→ **on warn:** present to user, proceed if user approves
→ **on critical:** must address before project is considered ready

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping needs exploration, jumping to architecture design (see HARD-GATE above) | Understand "what and for whom" before deciding "how to build" |
| Proposing approaches without trade-off analysis | Each approach needs pros, cons, best-fit scenario, and an explicit recommendation — not just a list of options |
| Forgetting workflow chain mapping | Chains determine bootstrap skill content — an unmapped chain produces a bootstrap that routes incorrectly |
| Dumping skills into one folder without analyzing compatibility | Audit each skill first — naming conflicts and overlapping responsibilities cause confusion |
| Copying third-party skills without security audit | Always invoke `bundles-forge:auditing` on imported content |
| Treating all third-party skills as repackage-only | Ask integration intent — workflow integration requires adaptation |
| Forgetting skill visibility classification | Entry-point vs internal determines commands/ and description style |
| Using blueprinting to add skills to an existing project | Blueprinting creates new projects; use `bundles-forge:optimizing` (Skill & Workflow Restructuring target) for existing ones |

## Inputs

- `user-requirements` (required) — conversational input gathered through the structured interview process
- `existing-skill` (optional) — path to existing SKILL.md for Scenario B (decomposition)
- `candidate-skills` (optional) — list of existing skills for Scenario C (composition)

## Outputs

- `design-document` — structured design summary containing project overview, target users, use cases, success criteria, project name, platforms, skill inventory, workflow chain, bootstrap strategy, and advanced components. Contains `skill-inventory` (consumed by `bundles-forge:authoring`) and `workflow-chain` (consumed during the Wire Workflow step). Consumed by `bundles-forge:scaffolding` and `bundles-forge:authoring`

## Integration

**Calls:**
- **bundles-forge:scaffolding** — Scaffold step: generate project structure and platform adapters
  - Artifact: `design-document` → `design-document` (direct match)
- **bundles-forge:authoring** — Author Content step: write SKILL.md and agents/*.md content
  - Artifact: `design-document` → `skill-inventory` (indirect — skill inventory extracted from design document)
- **bundles-forge:auditing** — Run Audit step: initial quality check on the new project
  - Artifact: `design-document` → `project-directory` (indirect — auditing targets the scaffolded project, not the design document)

**Pairs with:**
- **bundles-forge:optimizing** — complementary scope: blueprinting for new projects, optimizing for existing ones
