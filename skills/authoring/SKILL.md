---
name: authoring
description: "Use when writing, completing, improving, or adapting SKILL.md and agents/*.md in a bundle-plugin — integrating external skills, filling scaffolded stubs, or rewriting for better triggering and token efficiency"
allowed-tools: Python(scripts/lint_skills.py *)
---

# Authoring Skill Content

## Overview

Guide the authoring of effective SKILL.md files, agent definitions (`agents/*.md`), and supporting resources within a bundle-plugin. Good content is the difference between skills that agents consistently find and follow — and ones that get ignored or misinterpreted.

**Core principle:** Write for the agent's experience. Every instruction should be discoverable (good description), loadable (right size), and followable (clear, motivated instructions).

**Skill type:** Hybrid — follow the execution flow rigidly (Entry Detection → Path steps → Validation), but apply writing guidance flexibly based on context. The process is discipline-enforcing; the content decisions are pattern-based.

**Announce at start:** "I'm using the authoring skill to help [write / complete / improve / adapt] [skill / agent] content."

## Entry Detection

Determine the authoring path from context:

| Context | Path |
|---------|------|
| `skill-inventory` from blueprinting, or user requests writing new SKILL.md / agent definition from scratch | **Path 1: New Content** |
| User provides an existing/external skill to add into a project, or asks to adapt a skill to match project conventions | **Path 2: Integrate Content** |
| `scaffold-output` directories exist but SKILL.md body has < 10 non-empty lines | **Path 3: Complete Content** |
| User provides existing in-project `skill-md` to improve, or `optimization-spec` from optimizing with specific changes | **Path 4: Improve Content** |

When the target is an agent definition (`agents/*.md`) rather than a skill, follow the same path logic but use the agent authoring conventions from `references/agent-authoring-guide.md`.

## Step 0: Project Context (all paths)

Before writing any content, check whether you're working within an existing bundle-plugin project:

1. **Detect project root** — look for `skills/` directory + `package.json` above the target
2. **If project exists**, read 2-3 existing SKILL.md files to extract the project's conventions:
   - Description style (verb form after "Use when", scoping patterns)
   - Section structure (which headings, in what order)
   - Cross-reference format (`project:skill-name` prefix)
   - Token efficiency patterns (use of `references/`, line counts)
3. **If no project** (standalone authoring), use the conventions from `references/skill-writing-guide.md` directly

## Path 1: New Content

Write skill or agent content from scratch.

1. **Gather requirements** — from `skill-inventory` (blueprinting), user description, or conversation context. Identify: skill purpose, triggering scenarios, expected inputs/outputs, relationship to other skills
2. **Read writing guide** — load `references/skill-writing-guide.md` for frontmatter reference, description rules, and instruction style guidance
3. **Write frontmatter** — `name` (kebab-case matching directory), `description` (start with "Use when...", under 250 chars, triggering conditions only)
4. **Write Overview** — 1-3 sentences: what the skill does, core principle, skill type declaration (rigid / flexible / hybrid)
5. **Write the process** — step-by-step execution flow. Use imperative form. Explain why, not just what. Include at least one concrete example per key instruction
6. **Write Common Mistakes** — table of pitfalls and fixes (at least 3 entries)
7. **Write Inputs / Outputs / Integration** — declare artifact IDs, calling relationships, and pairing skills
8. **Check external dependencies** — if the skill references MCP tools or CLI commands, read `references/skill-writing-guide.md` "External Tool References" section for declaration syntax, fallback patterns, and CLI vs MCP guidance
9. **Evaluate token budget** — if body exceeds 300 lines, extract heavy sections to `references/`. For agent definitions, read `references/agent-authoring-guide.md` for the different structure
10. **Run validation** (see Post-Action Validation below)

## Path 2: Integrate Content

Adapt an existing/external skill to fit a project's conventions and workflow.

1. **Read the incoming skill** — understand its purpose, triggering scenarios, and current structure
2. **Read project conventions** (from Step 0) — identify gaps between the incoming skill and project patterns
3. **Read writing guide** — load `references/skill-writing-guide.md` for the authoritative convention set
4. **Adapt frontmatter** — rewrite `description` to match project style (verb form, scoping), ensure `name` follows project kebab-case convention
5. **Adapt body structure** — restructure sections to match project patterns (Overview, Process, Common Mistakes, Inputs/Outputs/Integration)
6. **Wire Integration section** — add cross-references to existing project skills, declare Inputs/Outputs that connect to the project's workflow graph
7. **Adapt instruction style** — align with project conventions (imperative form, reasoning over directives, example density)
8. **Evaluate token budget** — ensure the adapted skill fits project token norms
9. **Run validation** (see Post-Action Validation below)

## Path 3: Complete Content

Fill in scaffolded skill stubs with substantive content.

1. **Read scaffold structure** — identify which directories and stub files exist
2. **Read project conventions** (from Step 0) — match the style of already-completed skills
3. **Read writing guide** — load `references/skill-writing-guide.md` for frontmatter and body conventions
4. **Complete frontmatter** — fill in `description` (triggering conditions, "Use when...", under 250 chars). If `name` is already set, verify it matches directory name
5. **Write Overview** — core principle + skill type declaration
6. **Write the process** — step-by-step flow based on the skill's intended purpose from the design document or user context
7. **Write remaining sections** — Common Mistakes, Inputs/Outputs/Integration
8. **Create supporting resources** if needed — `references/` for heavy content, `assets/` for templates. Read `references/skill-writing-guide.md` "Supporting Resources" section for thresholds
9. **Run validation** (see Post-Action Validation below)

## Path 4: Improve Content

Enhance existing in-project content based on user feedback or optimization specs.

1. **Read existing content** — understand current structure, strengths, and gaps
2. **Identify improvement targets** — from user request, `optimization-spec`, or self-diagnosis:
   - Description not triggering reliably → rewrite following description rules
   - Token budget exceeded → extract to `references/`, cut redundancy
   - Missing sections → add Overview, Common Mistakes, Inputs/Outputs
   - Instruction style issues → reframe directives as reasoning, add examples
3. **Read writing guide** if needed — load `references/skill-writing-guide.md` for specific convention details
4. **Apply changes** — make targeted improvements. Preserve what works; don't rewrite content that already follows conventions
5. **Verify Integration section** — ensure cross-references still resolve after changes, artifact IDs match consuming skills
6. **Run validation** (see Post-Action Validation below)

## Post-Action Validation

After completing any path, validate the authored content:

1. **Run lint** — `python scripts/lint_skills.py <skill-directory>` on each authored/modified skill
2. **Review findings:**
   - **Critical** (Q1-Q3: missing frontmatter/name/description) — fix immediately before delivering
   - **Warning** (Q4-Q9, Q14, X1-X3: naming conventions, description rules, token budget, tool paths, broken references) — fix if straightforward, otherwise report to the user/caller
   - **Info** (Q10-Q13, Q15-Q17, S9: missing sections, heavy inline content, directory name mismatch) — report as improvement suggestions
3. **Report results** — tell the user/calling skill what was validated and any remaining warnings

Read `references/quality-checklist.md` for the full check-by-check reference when investigating specific findings.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Description summarizes workflow | Describe triggering conditions only — agents shortcut to description |
| Piling on MUST/ALWAYS/NEVER | Explain why the rule exists — understanding beats compliance |
| Putting everything in SKILL.md | Extract heavy content (100+ lines) to `references/`; keep body under 500 lines |
| No examples, only abstract rules | Add at least one concrete example per key instruction |
| Writing for humans, not agents | Use imperative form, clear structure, explicit output formats |
| Description too narrow | Be pushy — list related scenarios, edge cases, alternative phrasings |
| Description too broad | Scope to the right context (e.g., "bundle-plugins" not just "any project") |
| Skipping project conventions | Always read existing skills first when working in an established project |
| Not wiring Integration section | Every skill needs Called by / Calls / Pairs with to connect to the workflow graph |
| Forgetting validation | Always run `lint_skills.py` after authoring — catches issues before they propagate |

## Inputs

- `skill-inventory` (optional) — list of skills and agent definitions to write, from `bundles-forge:blueprinting` design document
- `scaffold-output` (optional) — scaffolded skill directories needing content (from blueprinting pipeline or standalone scaffolding)
- `skill-md` (optional) — existing SKILL.md or agent definition to improve, complete, or adapt
- `optimization-spec` (optional) — specific content changes requested by `bundles-forge:optimizing` (e.g., rewrite description, reduce tokens, restructure sections)

## Outputs

- `skill-content` — completed or improved SKILL.md files following authoring conventions (frontmatter, description, body structure, token efficiency)
- `agent-content` (optional) — completed `agents/*.md` definitions following agent authoring conventions

## Integration

**Called by:**
- **bundles-forge:blueprinting** — dispatched as Phase 2 (content writing) in the blueprinting pipeline (write all skills + agent definitions)
- **bundles-forge:optimizing** — content rewriting for description, token, and structural improvements
- User directly — for standalone SKILL.md or agent definition authoring

**Pairs with:**
- **bundles-forge:scaffolding** — scaffolding generates directory structure, authoring fills it with content
- **bundles-forge:auditing** — auditing validates authored content for quality, cross-references, and security

## References

For detailed writing conventions and rules, read the relevant reference on demand:

- **`references/skill-writing-guide.md`** — frontmatter field reference (all 11 fields + Claude Code features like `$ARGUMENTS`, dynamic context injection, skill lifecycle), description writing rules, instruction style, token efficiency, progressive disclosure, skill types, and supporting resource guidance
- **`references/agent-authoring-guide.md`** — agent definition structure, frontmatter fields, body conventions, agent vs skill differences, fallback patterns
- **`references/quality-checklist.md`** — Q1-Q17 and X1-X3 lint checks as a self-review checklist during authoring
