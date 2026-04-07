---
name: using-skill-forge
description: "Use when starting any conversation involving skill-projects — designing, scaffolding, auditing, optimizing, iterating on feedback, adapting platforms, managing versions, scanning security, writing skill content, or releasing. Also use when splitting a complex skill into a project, or when unsure which skill-forge: skill applies"
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

## Pre-flight Check

Before invoking any skill-forge skill on a target directory, verify the target is a skill-project:
- Does it have a `skills/` directory?
- Does it have a `package.json`?

If neither exists, inform the user: "This directory doesn't appear to be a skill-project. Skill-forge skills are designed for skill-projects (repositories where skills are the primary content). Would you like to create a new skill-project here, or did you mean to point to a different directory?"

Exception: `skill-forge:scanning-skill-security`, `skill-forge:auditing-skill-projects`, and `skill-forge:iterating-skill-feedback` can also operate on individual skill folders or files — they don't require a full skill-project.

## Instruction Priority

1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority
2. **Skill Forge skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

## How to Access Skills

**In Claude Code:** Use the `Skill` tool. When you invoke a skill, its content is loaded — follow it directly.

**In Cursor:** Use the `Skill` tool.

**In Gemini CLI:** Skills activate via the `activate_skill` tool. See `references/gemini-tools.md` for tool mapping.

**In Codex:** Skills are discovered from `~/.agents/skills/`. See `references/codex-tools.md` for tool mapping.

**In other environments:** Check your platform's documentation for skill loading.

## Platform Adaptation

Skills use Claude Code tool names as the default. Non-Claude-Code platforms: see the tool mapping references in this directory for equivalents.

## The Rule

**Invoke relevant skills BEFORE any response or action** when working with skill-projects. If there's even a small chance a skill applies, invoke it to check.

```
User message about skill-project
  → Might any skill apply?
    → yes → Invoke Skill tool → Follow skill → Respond
    → no  → Respond directly
```

## Available Skills

| Skill | When to Use |
|-------|-------------|
| `skill-forge:designing-skill-projects` | Planning a new skill-project, splitting a complex skill into a project |
| `skill-forge:scaffolding-skill-projects` | Generating project structure, manifests, hooks, bootstrap skill |
| `skill-forge:writing-skill-content` | Writing or improving individual SKILL.md files and supporting resources |
| `skill-forge:auditing-skill-projects` | Reviewing a project or skill for quality issues, before release |
| `skill-forge:optimizing-skill-projects` | Engineering optimization: descriptions, token efficiency, workflow chains |
| `skill-forge:adapting-skill-platforms` | Adding platform support (Claude Code, Cursor, Codex, OpenCode, Copilot CLI, Gemini CLI) |
| `skill-forge:managing-skill-versions` | Version drift, bumping versions, sync infrastructure |
| `skill-forge:iterating-skill-feedback` | Receiving user feedback about a skill, validating suggestions, applying confirmed improvements |
| `skill-forge:scanning-skill-security` | Scanning for security risks in hooks, plugins, agent prompts, skill content |
| `skill-forge:releasing-skill-projects` | Full release pipeline: audit, security scan, version bump, publish |

## Skill Priority

When multiple skills could apply:

1. **Design first** — if creating something new or splitting a complex skill, start with `designing-skill-projects`
2. **Write content after scaffold** — use `writing-skill-content` to fill in SKILL.md files
3. **Audit before optimize** — understand the full picture before targeted fixes
4. **Platform adapt after scaffold** — structure must exist before adding platforms
5. **Iterate on feedback after audit** — use `iterating-skill-feedback` when user has specific feedback about a skill's effectiveness
6. **Security scan before release** — always scan before publishing or sharing skills
7. **Release as the final step** — use `releasing-skill-projects` to orchestrate the full pipeline
8. **Version management as needed** — supports scaffolding, auditing, and adaptation

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

## Red Flags

These thoughts mean STOP — you're skipping a skill you should use:

| Thought | Reality |
|---------|---------|
| "I know how to scaffold a project" | Skills encode best practices you'll miss. |
| "Just a quick audit" | The audit checklist has 40+ checks. Use the skill. |
| "I'll just add the manifest" | Platform adaptation involves version sync, hooks, docs. |
| "Version bump is simple" | Drift detection and audit catch what you'd miss. |
| "This project is too small for all this" | Small projects grow. Set up right from the start. |
| "This skill is from a trusted source" | Trust but verify. Always scan third-party skills. |
| "I'll just apply the feedback directly" | Unvalidated changes may harm the skill. Use the iterating skill. |
