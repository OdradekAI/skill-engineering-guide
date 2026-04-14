---
name: blueprinting
description: "Use when planning new bundle-plugins, splitting complex skills, combining skills into bundles, or when a user has a vague idea about packaging skills"
---

# Blueprinting Bundle-Plugins

## Overview

Turn a vague idea ("I want to package my skills") into a concrete project blueprint through needs exploration, architecture design, and structured review — then orchestrate the full creation pipeline: scaffolding, content authoring, workflow wiring, and initial quality check.

**Core principle:** Understand what you're building — and why — before generating anything. Five minutes of needs exploration saves hours of rework.

**Skill type:** Hybrid — follow the three-phase process rigidly, but question selection, depth, and approach recommendations adapt to user context.

**Announce at start:** "I'm using the blueprinting skill to plan your bundle-plugin."

<HARD-GATE>
Do NOT invoke bundles-forge:scaffolding or any subsequent orchestration phase until the user has approved the design document. Every project — regardless of perceived simplicity — must pass through needs exploration → architecture design → design document review. Quick mode may shorten the process (needs exploration asks only 2 core questions), but it cannot skip it.
</HARD-GATE>

## Three Entry Points

This skill handles three scenarios. All three feed into the same three-phase interview — only the initial context differs.

- **Scenario A: New project from scratch** — Begin with Context Exploration, then the full interview
- **Scenario B: Splitting an existing complex skill** — Context Exploration reads the existing skill via `references/decomposition-analysis.md`, then enters the interview with richer context
- **Scenario C: Composing multiple existing skills** — Context Exploration inventories candidates via `references/composition-analysis.md`, then enters the interview with richer context

If the user has an existing skill they want to break apart, start with Scenario B. If the user has multiple existing skills they want to combine into a **new** unified project, start with Scenario C. Otherwise, start with Scenario A.

> **Adding skills to an existing project?** That's optimization, not blueprinting. Use `bundles-forge:optimizing` (Target 7: Skill & Workflow Restructuring) or invoke `/bundles-optimize`.

## Dialogue Strategy

These strategies apply throughout the entire interview process — all three phases.

### Ask 1-2 Questions at a Time

Do not batch questions. Each message focuses on 1-2 key decisions. Users give higher-quality answers with focused single questions.

### Do Not Accept Vague Answers

When the user answers with "roughly", "whatever", "you decide", or "I guess so" — do not accept it:
- **User knows but hasn't articulated** → keep probing until specific
- **User genuinely doesn't know** → provide 2-3 options with trade-off analysis and a clear recommendation

### Approach Guidance

At key decision points (skill decomposition, platform selection, architecture choice, workflow design), propose 2-3 approaches:
- Approach name + one-sentence summary
- Pros / Cons
- Best-fit scenario
- Explicit recommendation + reasoning

### Periodic Confirmation

After completing each phase, restate the collected information and confirm mutual understanding. If contradictions surface, call them out directly.

### Sufficiency Check

The design document may only be generated when all the following are met:

**Must satisfy** (missing any one blocks document generation):
- Problem scenario is clear (can be stated in one sentence)
- Target users are identified
- Core skills are identified (at least know which skills to include)
- Architecture mode is determined (quick / adaptive)
- At least one target platform selected

**Should satisfy** (mark unmet items as [TBD] in the design document):
- Workflow chain mapping is complete
- Bootstrap strategy is decided
- Advanced component needs are clear
- Success criteria are defined

## Context Exploration

Before asking any questions, gather available context:

### Scenario A (New Project)
1. **Scan the workspace** — look for scattered skill files, existing SKILL.md drafts, or relevant project files that hint at what the user is building
2. If user context is already rich from their initial message, proceed directly to Phase 1

### Scenario B (Decomposition)
1. **Read the existing skill** — follow `references/decomposition-analysis.md` to map responsibilities, identify split points, and propose a decomposition
2. Present the decomposition proposal to the user for approval
3. Proceed to Phase 1 with the decomposition as input context

### Scenario C (Composition)
1. **Inventory candidate skills** — follow `references/composition-analysis.md` to check compatibility, detect conflicts, and design orchestration
2. Present the composition plan to the user for approval
3. Proceed to Phase 1 with the composition analysis as input context

## Phase 1: Needs Exploration

Understand what the user wants to build and why, before making any architecture decisions. Ask these one at a time, adapting based on answers.

**Quick mode shortcut:** If the project is clearly simple (user explicitly says they just want to package a few standalone skills), ask only questions 1 and 2, then move to Phase 2.

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

After collecting needs exploration answers, restate the understanding:

> "Let me confirm what I understand: You're building [one-sentence summary] for [target users] to solve [problem]. The core capabilities are [list]. The usage flow is [summary]. Does this match your intent?"

Wait for user confirmation before proceeding to Phase 2. If the user corrects anything, update the understanding and re-confirm.

## Phase 2: Architecture Design

With a clear understanding of what and why, now decide how to build it. The agent should actively recommend answers based on Phase 1 context, rather than asking open-ended questions.

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

### 2. Project Name

Kebab-case identifier (e.g., `my-dev-tools`). This becomes the directory name, package name, and plugin ID across all platforms.

**Validation:** lowercase letters, numbers, hyphens only. No underscores, no spaces.

### 3. Target Platforms

Which platforms should the project support?

| Platform | Manifest | Discovery |
|----------|----------|-----------|
| Claude Code | `.claude-plugin/plugin.json` | Convention-based |
| Cursor | `.cursor-plugin/plugin.json` | Explicit paths |
| Codex | `.codex/INSTALL.md` | Symlink to `~/.agents/skills/` |
| OpenCode | `.opencode/plugins/<name>.js` | Plugin config |
| Gemini CLI | `gemini-extension.json` | Context file |

Based on the target users identified in Phase 1, recommend a platform combination with reasoning. When the user is uncertain, present 2-3 platform strategies with trade-offs.

Start with what the user actually uses. Others can be added later via `bundles-forge:scaffolding`.

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

#### 4a. Skill Visibility (adaptive mode only)

For projects with workflow chains, classify each skill:

- **Entry-point** — users invoke directly. Gets a matching command in `commands/` for discoverability. Description describes user-facing triggering conditions.
- **Internal** — called by other skills as part of a workflow chain, not invoked directly by users. Description should say "Use when called by `<project>:<parent-skill>`, not directly." No matching command needed.

Record the classification in the skill inventory table.

### 5. Workflow Chain (adaptive mode only)

Do skills depend on each other? Map the chain:

```
skill-a → calls → skill-b → calls → skill-c
skill-d (independent)
```

If skills are independent, note that — it simplifies the bootstrap skill.

### 6. Bootstrap Strategy (adaptive mode only)

Does the user want an always-loaded meta-skill (`using-<project>`) that teaches agents how to find and use other skills?

**Recommend yes when:**
- Project has 3+ skills
- Skills form a workflow chain
- Multiple platforms targeted

**Skip when:**
- Single bundle-plugin project
- Skills are fully independent utilities

### 7. Advanced Components (adaptive mode — ask only if relevant)

Based on the answers so far, conditionally ask about:

| Component | Ask When | What It Provides |
|-----------|----------|-----------------|
| External integrations (`bin/` or `.mcp.json`) | Skills interact with external tools or services | CLI executables or MCP servers — consult `skills/scaffolding/references/external-integration.md` to decide CLI vs MCP |
| `userConfig` | Skills need user-provided API keys, endpoints, or tokens | User prompts at enable time with optional sensitive storage (Claude Code only) |
| `.lsp.json` servers | Skills involve language-specific code intelligence | Real-time diagnostics, go-to-definition |
| `output-styles/` | Project needs custom output formatting | Output style definitions |
| `settings.json` | Project should activate a default agent | Sets default agent when plugin is enabled |

When external integrations are needed, prefer CLI (`bin/`) for stateless single-shot tools and MCP (`.mcp.json`) for stateful connections or authenticated services. Skip this step entirely if no signals emerged from earlier answers.

## Phase 3: Design Document and Review

### Generate Design Document

After the interview, compile a design summary using the template in `references/design-document-template.md`. This template includes both needs context (project overview, target users, use cases, success criteria) and technical architecture (mode, platforms, skills, workflow, components).

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

### Pipeline Phase 1: Scaffold

**"Design approved. Invoking scaffolding to generate the project structure."**

Invoke `bundles-forge:scaffolding` with the approved design. Wait for scaffolding to complete (including its inspector self-check) before proceeding.

### Pipeline Phase 2: Author Content

**"Structure generated. Invoking authoring to write skill and agent content."**

Invoke `bundles-forge:authoring` with the full skill inventory from the design document. Pass the complete design document (including project overview, target users, and use cases) so authoring can write more targeted descriptions and overviews. Authoring handles:
- All SKILL.md files listed in the design
- All agent definitions (`agents/*.md`) if the design specifies subagents

Pass the complete list in one invocation — authoring processes them in sequence.

### Pipeline Phase 3: Workflow Design

**"Content authored. Designing workflow integration."**

This phase stays within blueprinting — workflow design is a blueprint-level architectural decision that depends on the full project context gathered during the interview. It requires the blueprint's holistic view of skill relationships and dependency chains, making it inappropriate to delegate to an executor skill that operates on individual content units.

1. For each skill pair with a dependency in the Workflow Chain, write the `## Integration` section:
   - `**Calls:**` and `**Called by:**` declarations must be symmetric (A calls B ⟹ B is called by A)
   - Artifact IDs in `## Outputs` must match downstream `## Inputs`
2. Update the bootstrap skill's routing table to reflect all entry-point and internal skills
3. If the design specifies agent dispatch, add dispatch instructions to the orchestrating skill and `Dispatched by:` to the agent file

### Pipeline Phase 4: Initial Quality Check

**"Workflow wired. Running initial audit."**

Invoke `bundles-forge:auditing` on the project root for a baseline quality check. Present findings to the user — critical issues should be addressed before considering the project ready for development iteration.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping needs exploration, jumping to architecture design | Understand "what and for whom" before deciding "how to build" |
| Accepting vague answers without probing | "Whatever", "you decide", "I guess" are not answers — probe until specific |
| Asking all questions at once | Agents optimize for efficiency and batch questions — but users give higher-quality answers with focused single questions, 1-2 at a time |
| Only asking questions, never offering approaches | When users are stuck, proactively provide 2-3 options with trade-offs and a recommendation |
| Asking all questions at once | Agents optimize for efficiency and batch questions — but users give higher-quality answers with focused single questions |
| Over-scoping platforms | Agents see the full platform table and try to be thorough — but untested platform adapters create maintenance debt |
| Forgetting workflow chain mapping | Chains determine bootstrap skill content — an unmapped chain produces a bootstrap that routes incorrectly |
| Dumping skills into one folder without analyzing compatibility | Audit each skill first — naming conflicts and overlapping responsibilities cause confusion |
| Copying third-party skills without security audit | Always run `bundles-forge:auditing` on imported content |
| Treating all third-party skills as repackage-only | Ask integration intent — workflow integration requires adaptation |
| Using adaptive mode for simple skill packaging | Quick mode exists for a reason — don't over-engineer |
| Forgetting skill visibility classification | Entry-point vs internal determines commands/ and description style |
| Using blueprinting to add skills to an existing project | Blueprinting creates new projects; use `bundles-forge:optimizing` (Target 7) for existing ones |

## Inputs

- `user-requirements` (required) — conversational input gathered through the structured interview process

## Outputs

- `design-document` — structured design summary containing project overview, target users, use cases, success criteria, project name, platforms, skill inventory, workflow chain, bootstrap strategy, and advanced components. Consumed by `bundles-forge:scaffolding` and `bundles-forge:authoring`

## Integration

**Calls:**
- **bundles-forge:scaffolding** — Pipeline Phase 1: generate project structure and platform adapters
  - Artifact: `design-document` → `design-document` (direct match)
- **bundles-forge:authoring** — Pipeline Phase 2: write SKILL.md and agents/*.md content
  - Artifact: `design-document` → `skill-inventory` (indirect — skill inventory extracted from design document)
- **bundles-forge:auditing** — Pipeline Phase 4: initial quality check on the new project
  - Artifact: `design-document` → `project-directory` (indirect — auditing targets the scaffolded project, not the design document)

**Pairs with:**
- **bundles-forge:optimizing** — complementary scope: blueprinting for new projects, optimizing for existing ones
