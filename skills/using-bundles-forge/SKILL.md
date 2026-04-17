---
name: using-bundles-forge
description: "Use when starting any conversation involving bundle-plugins — blueprinting, scaffolding, authoring, auditing, testing, optimizing, or releasing. Also use when feeling unsure which bundles-forge skill applies"
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

## Pre-flight Check

Before invoking any bundles-forge skill on a target directory, verify the target is a bundle-plugin project:
- Does it have a `skills/` directory?
- Does it have a `package.json`?

If neither exists, inform the user: "This directory doesn't appear to be a bundle-plugin project. Bundles Forge skills are designed for bundle-plugins (repositories where skills are the primary content). Would you like to create a new bundle-plugin here, or did you mean to point to a different directory?"

Exception: `bundles-forge:auditing` and `bundles-forge:optimizing` can also operate on individual skill folders or files — they don't require a full bundle-plugin project.

## Instruction Priority

1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority
2. **Bundles Forge skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

## How to Access Skills

**In Claude Code:** Use the `Skill` tool. When you invoke a skill, its content is loaded — follow it directly.

**In Cursor:** Use the `Skill` tool.

**In Gemini CLI:** Skills activate via the `activate_skill` tool. See `references/gemini-tools.md` for tool mapping.

**In Codex:** Skills are discovered from `~/.agents/skills/`. See `references/codex-tools.md` for tool mapping.

**In OpenClaw:** Skills auto-load from the bundle's `skills/` directory. See `references/openclaw-tools.md` for tool mapping.

## Platform Adaptation

Skills use Claude Code tool names as the default. Non-Claude-Code platforms: see the tool mapping references in this directory for equivalents.

## The Rule

**Invoke relevant skills BEFORE any response or action** when working with bundle-plugins. If there's even a small chance a skill applies, invoke it to check.

```
User message about bundle-plugins
  → Might any skill apply?
    → yes → Invoke Skill tool → Follow skill → Respond
    → no  → Respond directly
```

## Orchestrators (high-frequency entry points)

These skills diagnose, decide, and delegate. They orchestrate other skills to accomplish multi-step goals.

| Skill | Role | When to Use |
|-------|------|-------------|
| `bundles-forge:blueprinting` | New-project orchestrator | Planning new bundle-plugins, splitting complex skills, or composing skills into bundles. Orchestrates the full creation pipeline: scaffolding → authoring → workflow design → auditing |
| `bundles-forge:optimizing` | Improvement orchestrator | Engineering optimization, feedback iteration, descriptions, tokens, adding skills, restructuring workflows. Delegates content changes to authoring |
| `bundles-forge:releasing` | Release pipeline orchestrator | Version management, release pipeline: audit, test, version bump, publish |

## Executors (single-responsibility workers)

These skills do one thing well. They can be invoked directly by users or dispatched by orchestrators.

| Skill | Role | When to Use |
|-------|------|-------------|
| `bundles-forge:scaffolding` | Structure generator | Generating project structure, adding or removing platform support |
| `bundles-forge:authoring` | Content writer | Writing or improving SKILL.md content and agent definitions (agents/*.md) |
| `bundles-forge:auditing` | Diagnostic reporter | Reviewing a project for quality issues, security risks — outputs reports, does not orchestrate fixes |
| `bundles-forge:testing` | Dynamic verifier | Testing a plugin locally — dev-marketplace setup, hook smoke tests, component discovery, cross-platform readiness |

## Meta-skill

| Skill | Purpose |
|-------|---------|
| `bundles-forge:using-bundles-forge` | Bootstrap meta-skill — you're reading it now (auto-loaded by hooks) |

## Skill Priority

When multiple skills could apply, prefer orchestrators over executors:

1. **New project** → `bundles-forge:blueprinting` (orchestrates scaffolding, authoring, auditing)
2. **Improve existing project** → `bundles-forge:optimizing` (orchestrates authoring, scaffolding, auditing)
3. **Release** → `bundles-forge:releasing` (orchestrates auditing, testing, optimizing)
4. **Standalone content writing** → `bundles-forge:authoring` (when you just need to write/improve a SKILL.md)
5. **Standalone structure** → `bundles-forge:scaffolding` (when you just need to add/remove a platform)
6. **Standalone audit** → `bundles-forge:auditing` (when you just need a diagnostic report)
7. **Standalone testing** → `bundles-forge:testing` (when you just need to verify a plugin works locally)

## Naming Conventions

- **Project name**: kebab-case, descriptive (`dev-workflows`, `data-tools`)
- **Skill directories**: kebab-case matching the `name` frontmatter field
- **Cross-references**: `<project>:<skill-name>`
- **Bootstrap skill**: `using-<project>`
- **Agent prompts**: `agents/<role>.md`
- **Commands**: `commands/<action>.md`

## Skill Types

- **Rigid skills** (discipline-enforcing) — follow exactly, no adaptation. Examples: TDD, verification.
- **Flexible skills** (pattern-based) — adapt principles to context. Examples: brainstorming, optimization.

The skill itself declares which type it is.

## Inputs

- (none — bootstrap skill, loaded on demand via Skill tool)

## Outputs

- `routing-context` — skill routing table, platform adaptation guidance, and instruction priority for the current session
