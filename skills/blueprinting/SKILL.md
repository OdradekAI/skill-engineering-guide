---
name: blueprinting
description: "Use when planning new bundle-plugins, splitting complex skills, combining skills into bundles, or when a user has a vague idea about packaging skills"
---

# Blueprinting Bundle-Plugins

## Overview

Turn a vague idea ("I want to package my skills") into a concrete project blueprint through structured interview, then orchestrate the full creation pipeline: scaffolding, content authoring, workflow wiring, and initial quality check.

**Core principle:** Understand what you're building before generating anything. Five minutes of interview saves hours of rework.

**Skill type:** Hybrid — follow the interview process rigidly, but question selection and depth adapt to user context.

**Announce at start:** "I'm using the blueprinting skill to plan your bundle-plugin."

## Three Entry Points

This skill handles three scenarios:

- **Scenario A: New project from scratch** — Follow the full Interview below
- **Scenario B: Splitting an existing complex skill** — Read `references/decomposition-analysis.md`, then return to the Interview to fill in remaining decisions
- **Scenario C: Composing multiple existing skills** — Read `references/composition-analysis.md`, then return to the Interview to fill in remaining decisions

If the user has an existing skill they want to break apart, start with Scenario B. If the user has multiple existing skills they want to combine into a **new** unified project, start with Scenario C. Otherwise, start with Scenario A.

> **Adding skills to an existing project?** That's optimization, not blueprinting. Use `bundles-forge:optimizing` (Target 7: Skill & Workflow Restructuring) or invoke `/bundles-optimize`.

## The Interview

Ask these one at a time. Wait for the user's answer before moving to the next question.

### 1. Project Complexity

Ask: "Are you packaging a few standalone skills for quick distribution, or building an orchestrated multi-skill project?"

**Quick mode** (quick packaging):
- Target: bundle standalone skills into a plugin with minimal infrastructure
- Skip questions 5 (Workflow Chain), 6 (Bootstrap Strategy), and 4a (Skill Visibility)
- Defaults: no bootstrap, no hooks, Claude Code only
- Jump to a simplified design document after question 4

**Adaptive mode** (adaptive deep interview):
- Full interview with dynamic follow-ups based on answers
- After core questions, conditionally ask about advanced components:
  - External integrations — CLI tools (`bin/`) or MCP servers (`.mcp.json`), chosen via the decision tree in `skills/scaffolding/references/external-integration.md`
  - LSP servers (if skills involve language-specific code intelligence)
  - output-styles/ (if customized output formatting is needed)
  - Entry-point vs internal skill classification (question 4a)

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

Start with what the user actually uses. Others can be added later via `bundles-forge:scaffolding`.

### 4. Skill Inventory

What skills will the project contain? Even a rough list helps structure the scaffold. Gather:
- Skill name (kebab-case)
- One-sentence purpose
- Rigid or flexible type

If the user isn't sure yet, scaffold with a single placeholder skill and the bootstrap.

#### 4a. Skill Visibility (adaptive mode only)

For projects with workflow chains, classify each skill:

- **Entry-point** — users invoke directly. Gets a matching command in `commands/` for discoverability. Description describes user-facing triggering conditions.
- **Internal** — called by other skills as part of a workflow chain, not invoked directly by users. Description should say "Use when called by `<project>:<parent-skill>`, not directly." No matching command needed.

Record the classification in the skill inventory table.

### 5. Workflow Chain

Do skills depend on each other? Map the chain:

```
skill-a → calls → skill-b → calls → skill-c
skill-d (independent)
```

If skills are independent, note that — it simplifies the bootstrap skill.

### 6. Bootstrap Strategy

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

## Design Document

After the interview, compile a design summary using the template in `references/design-document-template.md`. Present to user for approval before proceeding.

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

This phase stays within blueprinting — workflow design is a blueprint-level architectural decision that depends on the full project context gathered during the interview. It requires the blueprint's holistic view of skill relationships and dependency chains, making it inappropriate to delegate to an executor skill that operates on individual content units.

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
| Skipping interview, jumping to scaffold | Agents default to action over inquiry — without the interview gate, they generate a scaffold from the first keyword they see |
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

- `design-document` — structured design summary containing project name, platforms, skill inventory, workflow chain, bootstrap strategy, and advanced components. Consumed by `bundles-forge:scaffolding`

## Integration

**Calls:**
- **bundles-forge:scaffolding** — Phase 1: generate project structure and platform adapters
  - Artifact: `design-document` → `design-document` (direct match)
- **bundles-forge:authoring** — Phase 2: write SKILL.md and agents/*.md content
  - Artifact: `design-document` → `skill-inventory` (indirect — skill inventory extracted from design document)
- **bundles-forge:auditing** — Phase 4: initial quality check on the new project
  - Artifact: `design-document` → `project-directory` (indirect — auditing targets the scaffolded project, not the design document)

**Pairs with:**
- **bundles-forge:optimizing** — complementary scope: blueprinting for new projects, optimizing for existing ones
