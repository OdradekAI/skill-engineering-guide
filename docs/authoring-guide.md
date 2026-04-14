# Authoring Guide

[中文](authoring-guide.zh.md)

User-oriented guide to writing, completing, improving, and adapting SKILL.md and agent definitions in a bundle-plugin with Bundles Forge. Covers path selection, writing conventions, agent authoring, validation, and common pitfalls.

## Overview

Authoring handles the content layer of a bundle-plugin: writing SKILL.md files, agent definitions (`agents/*.md`), and supporting resources (`references/`). It is an **executor** in the execution layer — a single-responsibility worker for content creation and improvement. Orchestrators (`blueprinting`, `optimizing`) dispatch it as part of a pipeline, or you can invoke it directly for standalone content work.

**Why it matters:** A well-authored skill is the difference between agents that consistently find, load, and follow your instructions — and ones that get ignored or misinterpreted. The description determines discoverability; the body determines execution quality.

> **Canonical source:** The full execution protocol (entry detection, path steps, validation checklist) lives in `skills/authoring/SKILL.md`. This guide helps you decide *which path applies* and *what to expect* — the skill itself handles execution.

---

## Choosing a Path

Authoring supports four paths. The right one depends on your starting point:

| Context | Path | When to Use |
|---------|------|-------------|
| Skill inventory from blueprinting, or writing from scratch | **Path 1: New Content** | You need a brand-new SKILL.md or agent definition |
| External/existing skill to bring into a project | **Path 2: Integrate Content** | Adapting a third-party or standalone skill to match project conventions |
| Scaffolded directories with empty stubs | **Path 3: Complete Content** | Filling in SKILL.md files that scaffolding created but left mostly blank |
| Existing in-project skill needing improvement | **Path 4: Improve Content** | Rewriting descriptions, reducing tokens, fixing structure, or applying optimization specs |

### Decision Flowchart

```
Are you coming from blueprinting with a skill inventory?
  ├─ Yes → Path 1: New Content (write all skills + agents)
  └─ No  → Does a SKILL.md already exist?
            ├─ No  → Is there a scaffolded stub directory?
            │         ├─ Yes → Path 3: Complete Content
            │         └─ No  → Path 1: New Content
            ├─ Yes, from outside this project → Path 2: Integrate Content
            └─ Yes, in this project → Path 4: Improve Content
```

---

## Path 1: New Content

Best for: writing skills or agent definitions from scratch, either as part of a blueprinting pipeline or standalone.

**What you provide:** A description of what the skill should do — its purpose, triggering scenarios, expected inputs/outputs, and relationship to other skills.

**What you get:** A complete SKILL.md with frontmatter, description, execution flow, common mistakes, and Integration section — all following the project's conventions (or default conventions if standalone).

**Key steps the agent follows:**
1. Gathers requirements from your description or the blueprinting skill inventory
2. Reads existing project skills (if any) to match conventions
3. Writes frontmatter with a "Use when..." description under 250 characters
4. Writes the full body: Overview, process steps, Common Mistakes, Inputs/Outputs/Integration
5. Checks external dependencies — if the skill references MCP tools or CLI commands, follows declaration syntax and fallback patterns from the writing guide
6. Evaluates token budget — extracts to `references/` if body exceeds 500 lines or heavy sections pass 100 lines
7. Runs `audit_skill.py` validation

**For agent definitions:** The same path applies, but the agent follows conventions from `references/agent-authoring-guide.md` instead — different frontmatter fields (`maxTurns`, `disallowedTools`), report-oriented body, and `.bundles-forge/` output format.

---

## Path 2: Integrate Content

Best for: adapting an external or third-party skill to fit your project's conventions and workflow graph.

**What you provide:** The skill to integrate (a file path, URL, or pasted content) and optionally which project to integrate it into.

**What you get:** The skill rewritten to match your project's description style, section structure, cross-reference format, and Integration wiring.

**Key steps the agent follows:**
1. Reads the incoming skill and your project's existing conventions
2. Rewrites frontmatter (description style, name convention)
3. Restructures body to match project patterns
4. Wires the Integration section with cross-references to existing skills
5. Evaluates token budget
6. Runs validation

**When to use this vs Path 4:** Use Path 2 when the skill comes from *outside* the project. Use Path 4 when improving a skill that's already *inside* the project.

---

## Path 3: Complete Content

Best for: filling in scaffolded stub directories that have the right structure but minimal content.

**What you provide:** A scaffolded project (from `bundles-forge:scaffolding`) with skill directories containing near-empty SKILL.md files.

**What you get:** Fully authored SKILL.md files for each stub, following the project's conventions and the design document's intended purpose for each skill.

**Key steps the agent follows:**
1. Reads scaffold structure to identify stubs (< 10 non-empty lines)
2. Matches the style of already-completed skills in the project
3. Writes full content for each stub
4. Creates supporting resources (`references/`) if needed
5. Runs validation

---

## Path 4: Improve Content

Best for: targeted improvements to existing in-project skills based on user feedback or optimization specs from `bundles-forge:optimizing`.

**What you provide:** The skill to improve and either a specific request ("rewrite the description") or an `optimization-spec` from the optimizing skill.

**What you get:** Targeted changes that preserve what works and fix what doesn't — not a full rewrite.

**Common improvement targets:**
- Description not triggering reliably → rewrite following description rules
- Token budget exceeded → extract heavy sections to `references/`
- Missing sections → add Overview, Common Mistakes, Inputs/Outputs
- Instruction style issues → reframe directives as reasoning, add examples

**Key steps the agent follows:**
1. Reads and understands the existing content
2. Identifies specific improvement targets
3. Makes targeted changes (preserves working content)
4. Verifies Integration section still resolves
5. Runs validation

---

## Writing Conventions at a Glance

These are the key conventions the authoring skill enforces. For the full reference, see `skills/authoring/references/skill-writing-guide.md`.

### Description Rules

- Start with "Use when..." — describe triggering conditions, not workflow steps
- Stay under 250 characters
- Be pushy — list related scenarios, edge cases, alternative phrasings
- Scope appropriately (e.g., "bundle-plugins" not just "any project")
- Include keywords agents would search for: error messages, symptoms, synonyms, tool names

### Body Structure

Agents read skills in a predictable sequence: description match → Overview scan → Process execution → references on-demand. Front-load critical instructions in the first half of the body.

A well-structured SKILL.md follows this pattern:

1. **Frontmatter** — `name`, `description`, optional fields (`allowed-tools`, etc.)
2. **Overview** — 1-3 sentences: what the skill does, core principle, skill type
3. **Entry Detection** (if multiple paths) — table mapping context to execution path
4. **Process** — step-by-step execution flow in imperative form
5. **Common Mistakes** — table of pitfalls and fixes (at least 3 entries)
6. **Inputs / Outputs** — artifact IDs with descriptions
7. **Integration** — Called by / Calls / Pairs with

For non-obvious decision points, use Mermaid flowcharts or ASCII decision trees instead of long prose.

### Token Efficiency

| Target | Line Budget | Word Budget |
|--------|-------------|-------------|
| Bootstrap skill (always loaded) | < 200 lines | < 150 words |
| Regular skill body | < 500 lines | < 500 words |
| Description (always in context) | — | < 250 characters |
| Total frontmatter | — | < 1024 characters |

At 300+ lines, lint (Q12) suggests extracting heavy sections to `references/` — this is a soft threshold, not a hard limit. Extract reference content (100+ lines) to keep the main file scannable. Use progressive disclosure: core instructions in SKILL.md, details in references.

### Instruction Style

- Use imperative form ("Read the file", not "You should read the file")
- Explain *why*, not just *what* — understanding beats compliance
- Include at least one concrete example per key instruction
- Avoid piling on MUST/ALWAYS/NEVER without reasoning
- For rigid/hybrid skills, add defensive instructions — explicit loophole closers and rationalization tables (see Defensive Writing in `skill-writing-guide.md`)

### Advanced Features

The writing guide covers several advanced capabilities. Each is detailed in `skills/authoring/references/skill-writing-guide.md`:

- **String Substitutions** — use `$ARGUMENTS`, `$0`/`$1`, `${CLAUDE_SKILL_DIR}`, and `${CLAUDE_SESSION_ID}` to inject dynamic values into the skill body at invocation time
- **Dynamic Context Injection** — the `` !` `` syntax runs shell commands before the skill loads; the agent receives the command output, not the command itself (useful for injecting git state, API responses, or environment data)
- **Skill Content Lifecycle** — skills load once into conversation and persist; auto-compaction keeps the first 5,000 tokens per skill when context fills up. Front-load critical instructions for compaction survivability
- **Frontmatter Hooks** (Claude Code only) — define lifecycle hooks (`PreToolUse`, `Stop`, etc.) scoped to a skill's invocation directly in YAML frontmatter
- **User Configuration** (`userConfig`) — reference non-sensitive plugin config values via `${user_config.KEY}` in skill content; sensitive values are restricted to MCP/hook/script environments only
- **External Tool References** — declare CLI tools via `allowed-tools: Bash(...)` or `Python(...)`, MCP tools via `mcp__server__tool`; include a fallback block when an MCP server may not be available

---

## Agent Authoring

When authoring agent definitions (`agents/*.md`), the same four paths apply, but with different conventions:

| Aspect | SKILL.md | agents/*.md |
|--------|----------|-------------|
| Frontmatter | `name`, `description`, optional fields | `name`, `description`, `model`, `maxTurns`, `disallowedTools`, + advanced: `effort`, `tools`, `skills`, `memory`, `background`, `isolation` |
| Body | Execution flow for interactive use | Execution protocol for autonomous inspection |
| Output | Direct file changes or guidance | Reports to `.bundles-forge/` |
| Can chain | Yes (Calls other skills) | Default no; enable via `skills` frontmatter field for agent-to-skill delegation |

### Agent Types

| Type | Key Frontmatter | Use Case |
|------|----------------|----------|
| **Read-only** (default) | `disallowedTools: Edit` | Inspection, auditing, reporting — cannot modify files |
| **Writable** | omit `disallowedTools`, set `isolation: "worktree"` | File modifications in an isolated git worktree to prevent conflicts |
| **With skill delegation** | add `skills` field | Agent can invoke listed skills, enabling agent-to-skill dispatch |

For the full agent authoring reference, see `skills/authoring/references/agent-authoring-guide.md`.

---

## Validation

After authoring, the skill always runs `python skills/auditing/scripts/audit_skill.py` to validate the result.

### What Gets Checked

| Severity | Checks | Action |
|----------|--------|--------|
| **Critical** | Q1-Q3: missing frontmatter, name, description | Fix immediately |
| **Warning** | Q4-Q9, Q14, X1-X3: naming conventions, description rules, token budget, tool paths, broken references | Fix if straightforward |
| **Info** | Q10-Q13, Q15, S9: missing sections, heavy inline content, directory name mismatch | Report as suggestions |

For the full check-by-check reference, see `skills/authoring/references/quality-checklist.md`.

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Description summarizes workflow | Writing for humans, not agents | Describe triggering conditions only — agents shortcut to description |
| Piling on MUST/ALWAYS/NEVER | Wanting to be thorough | Explain why the rule exists — understanding beats compliance |
| Putting everything in SKILL.md | Not knowing about `references/` | Extract heavy content (100+ lines) to `references/`; keep body under 500 lines |
| No examples, only abstract rules | Rushing through authoring | Add at least one concrete example per key instruction |
| Skipping project conventions | Working in isolation | Always read 2-3 existing skills first when in an established project |
| Not wiring Integration section | Treating skills as standalone | Every skill needs Called by / Calls / Pairs with for the workflow graph |
| Forgetting validation | Assuming content is correct | Always run `audit_skill.py` — catches issues before they propagate |
| Description too narrow | Being too specific | Be pushy — list related scenarios and edge cases |
| Description too broad | Being too vague | Scope to the right context (e.g., "bundle-plugins" not "any project") |

---

## FAQ

**Q: I have a standalone skill not in any project. Can I still use authoring?**

Yes. Invoke authoring directly — it detects there's no project root and uses default conventions from the writing guide. You'll get a well-structured SKILL.md following best practices.

**Q: What's the difference between authoring and optimizing?**

Authoring is the *content writer* — it creates and improves SKILL.md files. Optimizing is the *orchestrator* — it diagnoses issues, decides what to fix, and delegates content changes to authoring. If you know exactly what to write or fix, use authoring directly. If you need diagnosis first, use optimizing.

**Q: How do I write an agent definition instead of a skill?**

Use the same authoring paths. When the target is `agents/*.md`, the agent automatically switches to agent conventions — different frontmatter fields, report-oriented body, and read-only constraints. See `references/agent-authoring-guide.md` for details.

**Q: My skill is approaching the line budget. Is that a problem?**

The hard limit is 500 lines (Q9 warning). At 300+ lines, lint (Q12) suggests extracting to `references/` — this is a soft recommendation, not a blocker. Orchestrators with complex flows (like `blueprinting` or `releasing`) may legitimately be longer. But if your skill has heavy reference content (tables, templates, examples), extract sections over 100 lines to `references/` to keep the main file scannable. Bootstrap skills (`using-*`) have a stricter budget of 200 lines.

**Q: Can I run authoring as part of a pipeline?**

Yes. Blueprinting dispatches authoring as Phase 2 (after scaffolding). Optimizing dispatches authoring for content changes. In both cases, authoring receives context from the orchestrator and returns authored content for the next phase.

---

## Related Skills

| Skill | Relationship |
|-------|-------------|
| `bundles-forge:blueprinting` | Upstream — dispatches authoring as Phase 2 of the new-project pipeline |
| `bundles-forge:optimizing` | Upstream — dispatches authoring for content rewriting and improvements |
| `bundles-forge:scaffolding` | Upstream — generates directory structure that authoring fills with content |
| `bundles-forge:auditing` | Downstream — validates authored content for quality and security |
