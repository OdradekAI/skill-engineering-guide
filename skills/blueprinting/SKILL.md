---
name: blueprinting
description: "Use when planning new bundle-plugins, splitting complex skills, combining skills into bundles, or when a user has a vague idea about packaging skills. Use before scaffolding to avoid rework"
---

# Blueprinting Bundle-Plugins

## Overview

Turn a vague idea ("I want to package my skills") into a concrete project blueprint through structured interview, then orchestrate the full creation pipeline: scaffolding, content authoring, workflow wiring, and initial quality check.

**Core principle:** Understand what you're building before generating anything. Five minutes of interview saves hours of rework.

**Announce at start:** "I'm using the blueprinting skill to plan your bundle-plugin."

## Three Entry Points

This skill handles three scenarios:

- **Scenario A: New project from scratch** — Follow the full Interview below
- **Scenario B: Splitting an existing complex skill** — Follow the Decomposition Analysis first, then the Interview to fill in remaining decisions
- **Scenario C: Composing multiple existing skills** — Follow the Composition Analysis first, then the Interview to fill in remaining decisions

If the user has an existing skill they want to break apart, start with Scenario B. If the user has multiple existing skills they want to combine into a **new** unified project, start with Scenario C. Otherwise, start with Scenario A.

> **Adding skills to an existing project?** That's optimization, not blueprinting. Use `bundles-forge:optimizing` (Target 7: Skill & Workflow Restructuring) or invoke `/bundles-optimize`.

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

### C2.5. Integration Intent & Security Audit (for third-party skills)

For each skill classified as **Needs import**, follow the third-party integration process in `skills/optimizing/references/third-party-integration.md` (shared with `bundles-forge:optimizing`). This covers:

- Integration intent classification (repackage as-is vs integrate into workflow)
- Source attribution template
- Mandatory security audit via `bundles-forge:auditing`
- Intent B adaptation steps (rewrite description, cross-references, workflow declarations)

### C3. Design the Orchestration

With the inventory and compatibility analysis in hand, design how the skills work together:

- **Workflow chains** — which skills call or depend on each other? Map the full dependency graph
- **Independent skills** — which skills stand alone with no dependencies?
- **Glue skills** — do you need new skills to bridge gaps between existing ones (e.g., a skill that coordinates the handoff between two unrelated skills)?
- **Shared resources** — extract common scripts, reference docs, or templates into project-level `scripts/` or shared `references/` files
- **Bootstrap routing** — design the `using-<project>` skill's routing table to cover all composed skills

Present the composition plan to the user. Get approval before proceeding to the Interview (Scenario A) to finalize project details like name, platforms, and bootstrap strategy.

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
  - External integrations — CLI tools (`bin/`) or MCP servers (`.mcp.json`), chosen via the decision tree in `skills/scaffolding/references/external-integration.md`
  - LSP servers (if skills involve language-specific code intelligence)
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

Start with what the user actually uses. Others can be added later via `bundles-forge:scaffolding`.

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
| External integrations (`bin/` or `.mcp.json`) | Skills interact with external tools or services | CLI executables or MCP servers — consult `skills/scaffolding/references/external-integration.md` to decide CLI vs MCP |
| `userConfig` | Skills need user-provided API keys, endpoints, or tokens | User prompts at enable time with optional sensitive storage (Claude Code only) |
| `.lsp.json` servers | Skills involve language-specific code intelligence | Real-time diagnostics, go-to-definition |
| `output-styles/` | Project needs custom output formatting | Output style definitions |
| `settings.json` | Project should activate a default agent | Sets default agent when plugin is enabled |

When external integrations are needed, prefer CLI (`bin/`) for stateless single-shot tools and MCP (`.mcp.json`) for stateful connections or authenticated services. Skip this step entirely if no signals emerged from earlier answers.

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
<list any: bin/, .mcp.json, userConfig, .lsp.json, output-styles/, settings.json — or "none">

### Third-Party Sources (if applicable)
| Skill | Source | License | Integration Intent |
|-------|--------|---------|-------------------|
| ... | ... | ... | repackage / integrate |

### Notes
<any special requirements or constraints>
```

Present to user for approval before proceeding.

## Orchestration Pipeline

After the user approves the design, orchestrate the full project creation pipeline. Execute each phase in order — do not skip or reorder phases.

### Phase 1: Scaffold

**"Design approved. Invoking scaffolding to generate the project structure."**

Invoke `bundles-forge:scaffolding` with the approved design. Wait for scaffolding to complete (including its inspector self-check) before proceeding.

### Phase 2: Author Content

**"Structure generated. Invoking authoring to write skill and agent content."**

Invoke `bundles-forge:authoring` with the full skill inventory from the design document. Authoring handles:
- All SKILL.md files listed in the design
- All agent definitions (`agents/*.md`) if the design specifies subagents

Pass the complete list in one invocation — authoring processes them in sequence.

### Phase 3: Workflow Design

**"Content authored. Designing workflow integration."**

This phase stays within blueprinting — it is an architectural decision, not a content task.

1. For each skill pair with a dependency in the Workflow Chain, write the `## Integration` section:
   - `**Calls:**` and `**Called by:**` declarations must be symmetric (A calls B ⟹ B is called by A)
   - Artifact IDs in `## Outputs` must match downstream `## Inputs`
2. Update the bootstrap skill's routing table to reflect all entry-point and internal skills
3. If the design specifies agent dispatch, add dispatch instructions to the orchestrating skill and `Dispatched by:` to the agent file

### Phase 4: Initial Quality Check

**"Workflow wired. Running initial audit."**

Invoke `bundles-forge:auditing` on the project root for a baseline quality check. Present findings to the user — critical issues should be addressed before considering the project ready for development iteration.

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
| Using blueprinting to add skills to an existing project | Blueprinting creates new projects; use `bundles-forge:optimizing` (Target 7) for existing ones |

## Inputs

- `user-requirements` (required) — conversational input gathered through the structured interview process

## Outputs

- `design-document` — structured design summary containing project name, platforms, skill inventory, workflow chain, bootstrap strategy, and advanced components. Consumed by `bundles-forge:scaffolding`

## Integration

**Calls:**
- **bundles-forge:scaffolding** — Phase 1: generate project structure and platform adapters
  - Artifact: `design-document` → `design-document` (direct match)
- **bundles-forge:authoring** — Phase 2: write SKILL.md and agents/*.md content
  - Artifact: `design-document` → `skill-inventory` (indirect — skill inventory extracted from design document)
- **bundles-forge:auditing** — Phase 4: initial quality check on the new project
  - Artifact: `design-document` → `project-directory` (indirect — auditing targets the scaffolded project, not the design document)
