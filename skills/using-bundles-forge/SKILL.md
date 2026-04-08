---
name: using-bundles-forge
description: "Use when starting any conversation involving bundles — designing, scaffolding, auditing, optimizing, adapting platforms, writing skill content, or releasing. Also use when splitting a complex skill into a project, or when unsure which bundles-forge skill applies"
---

<SUBAGENT-STOP>
If you were dispatched as a subagent to execute a specific task, skip this skill.
</SUBAGENT-STOP>

## Pre-flight Check

Before invoking any bundles-forge skill on a target directory, verify the target is a bundles project:
- Does it have a `skills/` directory?
- Does it have a `package.json`?

If neither exists, inform the user: "This directory doesn't appear to be a bundles project. Bundles Forge skills are designed for bundles (repositories where skills are the primary content). Would you like to create new bundles here, or did you mean to point to a different directory?"

Exception: `bundles-forge:auditing` and `bundles-forge:optimizing` can also operate on individual skill folders or files — they don't require a full bundles project.

## Instruction Priority

1. **User's explicit instructions** (CLAUDE.md, GEMINI.md, AGENTS.md, direct requests) — highest priority
2. **Bundles Forge skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

## How to Access Skills

**In Claude Code:** Use the `Skill` tool. When you invoke a skill, its content is loaded — follow it directly.

**In Cursor:** Use the `Skill` tool.

**In Gemini CLI:** Skills activate via the `activate_skill` tool. See `references/gemini-tools.md` for tool mapping.

**In Codex:** Skills are discovered from `~/.agents/skills/`. See `references/codex-tools.md` for tool mapping.

## Platform Adaptation

Skills use Claude Code tool names as the default. Non-Claude-Code platforms: see the tool mapping references in this directory for equivalents.

## The Rule

**Invoke relevant skills BEFORE any response or action** when working with bundles. If there's even a small chance a skill applies, invoke it to check.

```
User message about bundles
  → Might any skill apply?
    → yes → Invoke Skill tool → Follow skill → Respond
    → no  → Respond directly
```

## Available Skills

| Skill | When to Use |
|-------|-------------|
| `bundles-forge:designing` | Planning new bundles, splitting a complex skill into a project |
| `bundles-forge:scaffolding` | Generating project structure, manifests, hooks, bootstrap skill |
| `bundles-forge:writing-skill` | Writing or improving individual SKILL.md files and supporting resources |
| `bundles-forge:auditing` | Reviewing a project for quality issues, security risks, or before release |
| `bundles-forge:optimizing` | Engineering optimization, feedback iteration, descriptions, token efficiency |
| `bundles-forge:adapting-platforms` | Adding platform support (Claude Code, Cursor, Codex, OpenCode, Gemini CLI) |
| `bundles-forge:releasing` | Version management, release pipeline: audit, version bump, publish |

## Skill Priority

When multiple skills could apply:

1. **Design first** — if creating something new or splitting a complex skill, start with `designing`
2. **Write content after scaffold** — use `writing-skill` to fill in SKILL.md files
3. **Audit before optimize** — understand the full picture before targeted fixes
4. **Platform adapt after scaffold** — structure must exist before adding platforms
5. **Optimize includes feedback** — use `optimizing` for both engineering improvements and user feedback iteration
6. **Release as the final step** — use `releasing` to orchestrate audit, version bump, and publish

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
| "Just a quick audit" | The audit checklist has 50+ checks including security. Use the skill. |
| "I'll just add the manifest" | Platform adaptation involves version sync, hooks, docs. |
| "Version bump is simple" | Drift detection and audit catch what you'd miss. |
| "This project is too small for all this" | Small projects grow. Set up right from the start. |
| "This skill is from a trusted source" | Trust but verify. Auditing includes security scanning. |
| "I'll just apply the feedback directly" | Unvalidated changes may harm the skill. Use the optimizing skill. |
