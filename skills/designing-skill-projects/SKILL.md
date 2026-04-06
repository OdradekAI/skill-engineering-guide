---
name: designing-skill-projects
description: "Use when planning a new skill project, splitting or decomposing a complex skill into a structured skill project, combining or composing multiple existing skills into a unified project, deciding which skills to include and how they chain together, mapping platform targets, choosing a bootstrap strategy, or when a user has a vague idea about packaging or organizing their skills — always use this before any scaffolding or code generation to avoid costly rework"
---

# Designing Skill Projects

## Overview

Turn a vague idea ("I want to package my skills") into a concrete project blueprint through structured interview. The output is a design document that `seg:scaffolding-skill-projects` consumes to generate the actual project.

**Core principle:** Understand what you're building before generating anything. Five minutes of interview saves hours of rework.

**Announce at start:** "I'm using the designing-skill-projects skill to plan your skill project."

## Three Entry Points

This skill handles three scenarios:

- **Scenario A: New project from scratch** — Follow the full Interview below
- **Scenario B: Splitting an existing complex skill** — Follow the Decomposition Analysis first, then the Interview to fill in remaining decisions
- **Scenario C: Composing multiple existing skills** — Follow the Composition Analysis first, then the Interview to fill in remaining decisions

If the user has an existing skill they want to break apart, start with Scenario B. If the user has multiple existing skills they want to combine into a unified project, start with Scenario C. Otherwise, start with Scenario A.

## Scenario B: Decomposition Analysis

When the user wants to split a complex skill into a skill project, analyze the existing skill before designing the new project.

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

When the user wants to combine multiple existing skills into a unified skill project, analyze compatibility and design the orchestration before scaffolding.

### C1. Inventory Existing Skills

Collect all candidate skills. For each one, record:
- Source (local file, git repo, marketplace, another skill project)
- Current structure (standalone SKILL.md, has references/, has scripts/)
- Frontmatter quality (has name/description? follows conventions?)
- Rigid or flexible type

### C2. Analyze Compatibility

Check for issues that need resolution before combining:

| Check | What to Look For |
|-------|-----------------|
| Naming conflicts | Two skills with the same or confusingly similar names |
| Description style | Inconsistent patterns (some start with "Use when...", some don't) |
| Overlapping responsibilities | Skills that do similar things — merge, deduplicate, or clearly scope each |
| Shared dependencies | Multiple skills referencing the same tools, scripts, or external resources |
| Cross-reference conventions | Mismatched project prefixes or reference styles |

Classify each skill as:
- **Ready** — can be included as-is
- **Needs adaptation** — rename, rewrite description, adjust references
- **Needs merge** — overlaps with another skill, combine into one

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
| Copilot CLI | Shares Claude Code hooks | Env detection |
| Gemini CLI | `gemini-extension.json` | Context file |

Start with what the user actually uses. Others can be added later via `seg:adapting-skill-platforms`.

### 3. Skill Inventory

What skills will the project contain? Even a rough list helps structure the scaffold. Gather:
- Skill name (kebab-case)
- One-sentence purpose
- Rigid or flexible type

If the user isn't sure yet, scaffold with a single placeholder skill and the bootstrap.

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
- Single skill project
- Skills are fully independent utilities

## Design Document

After the interview, compile a design summary:

```markdown
## Skill Project Design: <project-name>

**Platforms:** <list>
**Bootstrap:** yes/no

### Skills
| Name | Purpose | Type | Dependencies |
|------|---------|------|--------------|
| ... | ... | rigid/flexible | ... |

### Workflow Chain
<description or "independent">

### Notes
<any special requirements or constraints>
```

Present to user for approval before proceeding.

## Transition

After the user approves the design:

**"Design approved. Invoking scaffolding-skill-projects to generate the project structure."**

**REQUIRED:** Invoke `seg:scaffolding-skill-projects` with the approved design.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping interview, jumping to scaffold | Always interview first — assumptions cause rework |
| Asking all questions at once | One question at a time — reduces cognitive load |
| Over-scoping platforms | Start with what the user actually uses today |
| Forgetting workflow chain mapping | Chains determine bootstrap skill content |
| Dumping skills into one folder without analyzing compatibility | Audit each skill first — naming conflicts and overlapping responsibilities cause confusion |

## Integration

**Calls:**
- **seg:scaffolding-skill-projects** — after design approval

**Pairs with:**
- **seg:adapting-skill-platforms** — for adding platforms later
