---
name: blueprinting
description: "Use when planning new bundle-plugins, splitting complex skills, combining skills into bundles, adding skills to an existing project, or when a user has a vague idea about packaging skills. Use before scaffolding to avoid rework"
---

# Blueprinting Bundle-Plugins

## Overview

Turn a vague idea ("I want to package my skills") into a concrete project blueprint through structured interview. The output is a design document that `bundles-forge:scaffolding` consumes to generate the actual project.

**Core principle:** Understand what you're building before generating anything. Five minutes of interview saves hours of rework.

**Announce at start:** "I'm using the blueprinting skill to plan your bundle-plugin."

## Four Entry Points

This skill handles four scenarios:

- **Scenario A: New project from scratch** — Follow the full Interview below
- **Scenario B: Splitting an existing complex skill** — Follow the Decomposition Analysis first, then the Interview to fill in remaining decisions
- **Scenario C: Composing multiple existing skills** — Follow the Composition Analysis first, then the Interview to fill in remaining decisions
- **Scenario D: Adding skills to an existing project** — Follow the Integration Planning analysis, then apply changes directly (no full Interview needed)

If the user has an existing skill they want to break apart, start with Scenario B. If the user has multiple existing skills they want to combine into a **new** unified project, start with Scenario C. If the user wants to add skills to an **existing** bundle-plugin project, start with Scenario D. Otherwise, start with Scenario A.

## Scenario B: Decomposition Analysis

When the user wants to split a complex skill into a bundle-plugin, analyze the existing skill before blueprinting the new project.

### B1. Read the Existing Skill

Read the full SKILL.md (and any supporting files). Map out:
- What distinct responsibilities does this skill handle?
- Are there sections that could operate independently?
- Does the skill have branching logic that suggests separate workflows?

### B2. Identify Responsibility Boundaries

Look for natural split points:

| Signal | Suggests Separate Skill |
|--------|------------------------|
| "If X, do this; if Y, do that" with large branches | Each branch is a candidate skill |
| Sections with their own input/output formats | Independent responsibility |
| Steps that could be skipped entirely in some cases | Optional skill in a chain |
| Heavy reference material for a specific subtask | Subtask skill with its own references/ |

### B3. Propose a Decomposition

Present the user with:
- Which pieces become independent skills
- Which pieces become shared `references/` or `scripts/`
- How the skills chain together (workflow dependencies)
- Whether a bootstrap skill is needed to orchestrate them

Get user approval on the decomposition before proceeding to the Interview (Scenario A) to finalize project details.

## Scenario C: Composition Analysis

When the user wants to combine multiple existing skills into a unified bundle-plugin, analyze compatibility and design the orchestration before scaffolding.

### C1. Inventory Existing Skills

Collect all candidate skills. For each one, record:
- Source (local file, git repo, marketplace plugin, another bundle-plugin project)
- Current structure (standalone SKILL.md, has references/, has scripts/)
- Frontmatter quality (has name/description? follows conventions?)
- Rigid or flexible type

**For third-party skills** (marketplace, GitHub, other bundle-plugins), additionally record:
- License (MIT, Apache-2.0, proprietary, unknown)
- Version or commit hash at time of evaluation
- Maintenance status (actively maintained, archived, unknown)
- Original project name and namespace (for cross-reference rewriting)

### C2. Analyze Compatibility

Check for issues that need resolution before combining:

| Check | What to Look For |
|-------|-----------------|
| Naming conflicts | Two skills with the same or confusingly similar names |
| Description style | Inconsistent patterns (some start with "Use when...", some don't) |
| Overlapping responsibilities | Skills that do similar things — merge, deduplicate, or clearly scope each |
| Shared dependencies | Multiple skills referencing the same tools, scripts, or external resources |
| Cross-reference conventions | Mismatched project prefixes or reference styles |

**For third-party skills**, also check:

| Check | What to Look For |
|-------|-----------------|
| License compatibility | Can this license coexist with the project's license? |
| Security posture | Does the skill invoke external tools, network calls, or eval()? Run `bundles-forge:auditing` |
| Staleness risk | Is the skill actively maintained? Will you need to own updates? |

Classify each skill as:
- **Ready** — can be included as-is
- **Needs adaptation** — rename, rewrite description, adjust references
- **Needs merge** — overlaps with another skill, combine into one
- **Needs import** — third-party skill requiring copy + source attribution

### C2.5. Integration Intent (for third-party skills)

For each skill classified as **Needs import**, ask the user which integration intent applies:

**Intent A: Repackage as-is** — bundle the third-party skill without modification.
- Copy the SKILL.md and any references/ or scripts/ into the project's skills/ directory
- Add a source attribution block at the top of the copied SKILL.md:
  ```
  <!-- Source: <original-repo-or-marketplace> | Version: <version> | License: <license> -->
  ```
- Preserve the original description and instructions unchanged
- Use case: packaging scattered third-party skills for distribution in your own marketplace

**Intent B: Integrate into workflow** — copy and adapt the skill to fit the project's workflow.
- Copy the skill, then modify:
  - Rewrite description to reflect triggering conditions within the new project context
  - Rewrite cross-reference prefixes (`old-project:skill-name` → `new-project:skill-name`)
  - Add workflow connections: declare upstream/downstream skill dependencies in the Integration section
  - Trim standalone-only instructions that don't apply in the orchestrated context
  - Add handoff guidance to/from adjacent skills in the chain
  - Classify as entry-point or internal skill (see Interview step 3b)
- After adaptation, invoke `bundles-forge:authoring` for quality validation
- Use case: building your own orchestrated workflow on top of third-party foundations

### C2.6. Security Audit

Regardless of integration intent, run `bundles-forge:auditing` on all copied third-party content before proceeding. Flag any hook scripts, eval() calls, network requests, or file system access that was not present in your own skills.

### C3. Design the Orchestration

With the inventory and compatibility analysis in hand, design how the skills work together:

- **Workflow chains** — which skills call or depend on each other? Map the full dependency graph
- **Independent skills** — which skills stand alone with no dependencies?
- **Glue skills** — do you need new skills to bridge gaps between existing ones (e.g., a skill that coordinates the handoff between two unrelated skills)?
- **Shared resources** — extract common scripts, reference docs, or templates into project-level `scripts/` or shared `references/` files
- **Bootstrap routing** — design the `using-<project>` skill's routing table to cover all composed skills

Present the composition plan to the user. Get approval before proceeding to the Interview (Scenario A) to finalize project details like name, platforms, and bootstrap strategy.

## Scenario D: Integration Planning

When the user wants to add one or more skills (including third-party) to an **existing** bundle-plugin project. Unlike Scenario C (which creates a new project), Scenario D works within an existing project structure.

### D1. Read Existing Project

Read the existing project to understand the current state:
- List all skills under `skills/` and their workflow connections
- Map the current workflow graph (who calls whom, via `## Integration` sections)
- Identify the bootstrap skill (`using-*`) and its routing table
- Note current platforms, version, and project conventions

### D2. Inventory New Skills

For each skill being added, run the same analysis as Scenario C's C1 (Inventory Existing Skills):
- Source (local file, git repo, marketplace, another bundle-plugin)
- Current structure (standalone SKILL.md, has references/, has scripts/)
- Frontmatter quality (follows project conventions?)

**For third-party skills**, additionally record license, version/commit, maintenance status, and original namespace — same as C1's third-party checklist.

### D3. Compatibility Analysis

Reuse Scenario C's C2 (Analyze Compatibility) checks, but against the **existing project** rather than a blank slate:

| Check | What to Look For |
|-------|-----------------|
| Naming conflicts | New skill name clashes with existing skills |
| Description style | New skill follows project's description conventions |
| Overlapping responsibilities | New skill duplicates or conflicts with existing skills |
| Cross-reference conventions | New skill uses the correct project prefix |

**For third-party skills**, also run C2's license compatibility, security posture, and staleness risk checks.

### D3.5. Integration Intent

For each new skill, determine integration intent — reuse Scenario C's C2.5 logic:

- **Intent A: Repackage as-is** — copy with source attribution, no workflow changes
- **Intent B: Integrate into workflow** — copy, adapt, and wire into existing chains

### D3.6. Security Audit

Run `bundles-forge:auditing` (Skill mode) on each new skill before copying it into the project. For third-party skills, this is mandatory — same as C2.6.

### D4. Design Integration Plan

With the existing project state and new skill analysis in hand, design how the new skills integrate:

- **Insertion points** — where do new skills connect to the existing workflow graph? Which existing skills' `## Integration` sections need updates?
- **New edges** — map all new `**Calls:**` and `**Called by:**` declarations needed
- **Bootstrap updates** — does the `using-*` skill's routing table need new entries?
- **Shared resources** — do new skills bring scripts or references that should be project-level?

Present the integration plan to the user. This is lighter than a full Design Document — it covers only what changes, not the entire project.

### D5. Apply and Verify

After the user approves the integration plan:

1. Copy new skills into `skills/` (with source attribution for third-party)
2. Adapt as needed per integration intent (rewrite cross-refs, add Integration sections)
3. Update existing skills' `## Integration` sections for new connections
4. Update bootstrap skill routing if needed
5. **Suggest workflow audit:** "Integration complete. Run `bundles-forge:auditing` in Workflow mode with `--focus-skills <new-skills>` to verify workflow integrity."

## Scenario A: The Interview

Ask these one at a time. Wait for the user's answer before moving to the next question.

### 0. Project Complexity

Ask: "Are you packaging a few standalone skills for quick distribution, or building an orchestrated multi-skill project?"

**Minimal mode** (quick packaging):
- Target: bundle standalone skills into a plugin with minimal infrastructure
- Skip questions 4 (Workflow Chain), 5 (Bootstrap Strategy), and 3b (Skill Visibility)
- Defaults: no bootstrap, no hooks, Claude Code only
- Jump to a simplified design document after question 3

**Intelligent mode** (adaptive deep interview):
- Full interview with dynamic follow-ups based on answers
- After core questions, conditionally ask about advanced components:
  - MCP servers (if skills need external tool integrations)
  - LSP servers (if skills involve language-specific code intelligence)
  - bin/ executables (if skills invoke CLI tools that should be on PATH)
  - output-styles/ (if customized output formatting is needed)
  - Entry-point vs internal skill classification (question 3b)

### 1. Project Name

Kebab-case identifier (e.g., `my-dev-tools`). This becomes the directory name, package name, and plugin ID across all platforms.

**Validation:** lowercase letters, numbers, hyphens only. No underscores, no spaces.

### 2. Target Platforms

Which platforms should the project support?

| Platform | Manifest | Discovery |
|----------|----------|-----------|
| Claude Code | `.claude-plugin/plugin.json` | Convention-based |
| Cursor | `.cursor-plugin/plugin.json` | Explicit paths |
| Codex | `.codex/INSTALL.md` | Symlink to `~/.agents/skills/` |
| OpenCode | `.opencode/plugins/<name>.js` | Plugin config |
| Gemini CLI | `gemini-extension.json` | Context file |

Start with what the user actually uses. Others can be added later via `bundles-forge:porting`.

### 3. Skill Inventory

What skills will the project contain? Even a rough list helps structure the scaffold. Gather:
- Skill name (kebab-case)
- One-sentence purpose
- Rigid or flexible type

If the user isn't sure yet, scaffold with a single placeholder skill and the bootstrap.

### 3b. Skill Visibility (intelligent mode only)

For projects with workflow chains, classify each skill:

- **Entry-point** — users invoke directly. Gets a matching command in `commands/` for discoverability. Description describes user-facing triggering conditions.
- **Internal** — called by other skills as part of a workflow chain, not invoked directly by users. Description should say "Use when called by `<project>:<parent-skill>`, not directly." No matching command needed.

Record the classification in the skill inventory table.

### 4. Workflow Chain

Do skills depend on each other? Map the chain:

```
skill-a → calls → skill-b → calls → skill-c
skill-d (independent)
```

If skills are independent, note that — it simplifies the bootstrap skill.

### 5. Bootstrap Strategy

Does the user want an always-loaded meta-skill (`using-<project>`) that teaches agents how to find and use other skills?

**Recommend yes when:**
- Project has 3+ skills
- Skills form a workflow chain
- Multiple platforms targeted

**Skip when:**
- Single bundle-plugin project
- Skills are fully independent utilities

### 6. Advanced Components (intelligent mode — ask only if relevant)

Based on the answers so far, conditionally ask about:

| Component | Ask When | What It Provides |
|-----------|----------|-----------------|
| `bin/` executables | Skills reference CLI tools | Adds tools to Bash PATH while plugin is enabled |
| `.mcp.json` servers | Skills need external service integration | MCP servers start automatically with the plugin |
| `.lsp.json` servers | Skills involve language-specific code intelligence | Real-time diagnostics, go-to-definition |
| `output-styles/` | Project needs custom output formatting | Output style definitions |
| `settings.json` | Project should activate a default agent | Sets default agent when plugin is enabled |

Skip this step entirely if no signals emerged from earlier answers.

## Design Document

After the interview, compile a design summary:

```markdown
## Bundle-Plugin Design: <project-name>

**Mode:** minimal / intelligent
**Platforms:** <list>
**Bootstrap:** yes/no

### Skills
| Name | Purpose | Type | Visibility | Dependencies |
|------|---------|------|------------|--------------|
| ... | ... | rigid/flexible | entry-point/internal | ... |

### Workflow Chain
<description or "independent">

### Advanced Components (intelligent mode only)
<list any: bin/, .mcp.json, .lsp.json, output-styles/, settings.json — or "none">

### Third-Party Sources (if applicable)
| Skill | Source | License | Integration Intent |
|-------|--------|---------|-------------------|
| ... | ... | ... | repackage / integrate |

### Notes
<any special requirements or constraints>
```

Present to user for approval before proceeding.

## Transition

After the user approves the design:

**"Design approved. Invoking scaffolding to generate the project structure."**

**REQUIRED:** Invoke `bundles-forge:scaffolding` with the approved design.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping interview, jumping to scaffold | Always interview first — assumptions cause rework |
| Asking all questions at once | One question at a time — reduces cognitive load |
| Over-scoping platforms | Start with what the user actually uses today |
| Forgetting workflow chain mapping | Chains determine bootstrap skill content |
| Dumping skills into one folder without analyzing compatibility | Audit each skill first — naming conflicts and overlapping responsibilities cause confusion |
| Copying third-party skills without security audit | Always run `bundles-forge:auditing` on imported content |
| Treating all third-party skills as repackage-only | Ask integration intent — workflow integration requires adaptation |
| Using intelligent mode for simple skill packaging | Minimal mode exists for a reason — don't over-engineer |
| Forgetting skill visibility classification | Entry-point vs internal determines commands/ and description style |
| Using Scenario C when adding to an existing project | Scenario C creates new projects; Scenario D works within existing ones |
| Skipping workflow audit after Scenario D | Always suggest `--focus-skills` workflow audit after integrating new skills |

## Inputs

- `user-requirements` (required) — conversational input gathered through the structured interview process

## Outputs

- `design-document` — structured design summary containing project name, platforms, skill inventory, workflow chain, bootstrap strategy, and advanced components. Consumed by `bundles-forge:scaffolding`

## Integration

**Calls:**
- **bundles-forge:scaffolding** — after design approval
- **bundles-forge:porting** — when blueprinting includes platform targets
