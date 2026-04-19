# Agent Authoring Guide

Reference for writing agent definitions (`agents/*.md`) in a bundle-plugin. Agents are self-contained execution protocols for read-only subagents dispatched by skills.

## Agent Anatomy

```
agents/
└── <role>.md
    ├── YAML frontmatter (name, description, model, maxTurns, disallowedTools, + optional: effort, tools, skills, memory, background, isolation)
    └── Markdown body (execution protocol, scoring, report format)
```

## Agent Frontmatter

### Core Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `name` | Yes | Role identifier (e.g., `inspector`, `auditor`, `evaluator`) |
| `description` | Yes | When to dispatch this agent (starts with "Use when...") |
| `model` | No | `inherit` (default) or specific model override |
| `maxTurns` | Yes | Upper bound on agent turns (prevents runaway) |
| `disallowedTools` | Yes (read-only) | Include `Edit` for read-only agents — the default and recommended pattern |

### Advanced Fields

| Field | Required | Purpose |
|-------|----------|---------|
| `effort` | No | Reasoning depth: `low`, `medium`, `high`. Controls the trade-off between agent quality and cost/speed |
| `tools` | No | Explicit tool whitelist (more precise than `disallowedTools`). When set, the agent can only use listed tools |
| `skills` | No | List of skills the agent can invoke. Enables agent-to-skill delegation |
| `memory` | No | Persistent memory across sessions. Agent retains context between invocations |
| `background` | No | If true, agent runs asynchronously in the background |
| `isolation` | No | `"worktree"` — agent runs in an isolated git worktree. Required for writable agents to prevent conflicts |

**Platform restriction:** `hooks`, `mcpServers`, and `permissionMode` are not supported for plugin-shipped agents.

**Example:**

```yaml
---
name: inspector
description: |
  Use when validating scaffolded bundle-plugin structure and platform adaptation.
  Dispatched by scaffolding after project generation or platform changes.
model: inherit
disallowedTools: Edit
maxTurns: 20
---
```

## Agent Body Structure

1. **Role & Constraints** — what the agent does, what it cannot do (no editing, no chaining)
2. **Execution Protocol** — step-by-step checks, scoring formulas, decision logic
3. **Report Format** — exact template the agent writes to the appropriate `.bundles-forge/` subdirectory (`audits/`, `evals/`, or `blueprints/`)

### Dispatch Context

Which skill(s) dispatch this agent and under what conditions belongs in the YAML `description` field, not in a separate body section — this is where platforms read it for automatic delegation decisions.

### Report Conventions

Agent reports go to `.bundles-forge/<subdirectory>/` in the workspace root:
- Subdirectory by agent type: `audits/` (auditor), `evals/` (evaluator), `blueprints/` (inspector)
- Filename pattern: `<project-name>-v<version>-<report-type>.YYYY-MM-DD[.<lang>].md`
- Read name and version from `package.json`
- Append `.<lang>` when not English
- Never modify or overwrite existing files — append sequence number if name collision
- Create the subdirectory if it does not exist

## Key Differences from Skills

| Aspect | SKILL.md | agents/*.md |
|--------|----------|-------------|
| Who invokes | Users or other skills | Only the dispatching skill |
| Can edit files | Yes | No (`disallowedTools: Edit`) |
| Can chain to skills | Yes | No (subagents cannot invoke skills) |
| Output | Direct file changes or guidance | Reports to `.bundles-forge/<subdirectory>/` |
| Fallback | N/A | Dispatching skill reads agent file inline |

## Standard Fallback Pattern

When a skill dispatches an agent, include this fallback block:

> **If subagent dispatch is unavailable:** Ask — "Subagents are not available. Run \<action\> inline?" If confirmed, read `agents/<name>.md` and follow its instructions within this conversation.

Skills may override this template when the eval scenario has specific requirements (e.g., optimizing's A/B eval offers "sequential inline with randomized order" vs "skip A/B" to address ordering bias).

## When to Write an Agent vs a Skill

Write a **read-only agent** (default) when:
- The task is inspection-style work producing a report
- The work should run in isolation from the main conversation
- You want to prevent the executor from editing project files

Write a **writable agent** (advanced) when:
- The task needs file modifications but should run in isolation
- The work could conflict with the main conversation's file changes
- Set `isolation: "worktree"` to run in a git worktree — this prevents the agent from modifying files in the main working tree
- Omit `disallowedTools` (or use `tools` whitelist to specify exactly which tools are allowed)

Write a **skill** when:
- User interaction is needed during execution
- The task orchestrates other skills
- The output is direct file changes in the main working tree

## Agent Quality Checklist

- [ ] `name` field matches the filename stem (`auditor.md` → `name: auditor`)
- [ ] `description` starts with "Use when..." and lists dispatch conditions
- [ ] `disallowedTools: Edit` is present for read-only agents
- [ ] Writable agents (no `disallowedTools: Edit`) have `isolation: "worktree"` set
- [ ] `maxTurns` is set to a reasonable bound
- [ ] Body has at least 5 non-empty lines (self-contained protocol)
- [ ] Report format section specifies the `.bundles-forge/<subdirectory>/` filename pattern
- [ ] Dispatching skill has a fallback block for when subagents are unavailable
