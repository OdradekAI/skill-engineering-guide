---
name: using-<project-name>
description: Use when starting any conversation - establishes how to find and use skills in the <project-name> project
---

# Using <Project Name>

## Instruction Priority

1. **User's explicit instructions** (CLAUDE.md, AGENTS.md, direct requests) — highest priority
2. **<Project Name> skills** — override default system behavior where they conflict
3. **Default system prompt** — lowest priority

## How to Access Skills

**In Claude Code:** Use the `Skill` tool.
**In Cursor:** Use the `Skill` tool.
**In Gemini CLI:** Skills activate via the `activate_skill` tool.

## Platform Adaptation

Skills use Claude Code tool names. For other platforms, see the tool mapping references in this directory.

## The Rule

Invoke relevant skills BEFORE any response or action. Even a 1% chance a skill might apply means you should invoke it.

## Available Skills

<!-- List your project's skills here -->

| Skill | When to Use |
|-------|-------------|
| `<project-name>:<skill-1>` | <trigger description> |
| `<project-name>:<skill-2>` | <trigger description> |
