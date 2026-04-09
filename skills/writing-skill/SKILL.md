---
name: writing-skill
description: "Use when writing or improving skill content in a bundle-plugin — SKILL.md structure, frontmatter conventions, description writing for reliable triggering, instruction style, and resource organization. Also use after scaffolding for content guidance"
---

# Writing Skill Content

## Overview

Guide the authoring of effective SKILL.md files and supporting resources within a bundle-plugin. Good skill content is the difference between a skill that agents consistently find, follow, and produce quality results with — and one that gets ignored or misinterpreted.

**Core principle:** Write for the agent's experience. Every instruction should be discoverable (good description), loadable (right size), and followable (clear, motivated instructions).

This skill distills best practices from the [Anthropic skill-creator](https://github.com/anthropics/skills/tree/main/skills/skill-creator) into actionable guidance for bundle-plugin authors.

**Announce at start:** "I'm using the writing-skill skill to help author skill content."

## Skill Anatomy

```
skill-name/
├── SKILL.md (required)
│   ├── YAML frontmatter (name, description — required)
│   └── Markdown body (instructions, examples, templates)
└── Supporting resources (optional)
    ├── scripts/    — Deterministic tools the skill invokes
    ├── references/ — Docs loaded into context on demand
    └── assets/     — Templates, icons, config files used in output
```

## Writing the Frontmatter

### The `name` Field

Kebab-case identifier matching the directory name. Letters, numbers, hyphens only.

```yaml
name: my-skill-name    # matches skills/my-skill-name/
```

### The `description` Field

The description is the **primary triggering mechanism** — it determines whether agents discover and invoke the skill. This is the highest-impact piece of text in any skill.

**Rules and reasoning:**

- **Start with "Use when..."** — this framing helps agents match user intent to skill purpose
- **Describe triggering conditions, not workflow** — testing shows that when descriptions summarize a skill's process, agents follow the description as a shortcut instead of reading the full SKILL.md. A description saying "scans structure, checks manifests, scores categories" caused agents to do exactly that sequence from the description alone, skipping the detailed instructions
- **Be slightly pushy** — agents tend to under-trigger skills. Include related scenarios, edge cases, and alternative phrasings. If there's even a chance the skill applies, the description should hint at it
- **Keep under 250 characters** — descriptions over 250 are truncated in the skill listing, losing trigger keywords
- **Scope appropriately** — if the skill is for bundle-plugins specifically, say so. Don't let the description match unrelated contexts

```yaml
# BAD: Summarizes workflow — agent shortcuts to this
description: "Scans project structure, validates manifests, checks version sync, scores 9 categories, generates report"

# BAD: Too vague — triggers on unrelated contexts
description: "Use when auditing any project for quality"

# GOOD: Triggering conditions, properly scoped, pushy
description: "Use when reviewing a bundle-plugin for structural issues, version drift, manifest problems, or skill quality, before releasing a bundle-plugin, or when a user points to a skill folder to review"
```

### Optional Frontmatter Fields

Beyond `name` and `description`, Claude Code supports fields that control invocation, execution context, and tool access. Use these when the defaults don't fit.

| Field | Effect | When to Use |
|-------|--------|-------------|
| `disable-model-invocation: true` | Only the user can invoke via `/name` | Side-effect workflows: deploy, commit, send messages |
| `user-invocable: false` | Hidden from `/` menu, only Claude invokes | Background knowledge that isn't a user action |
| `allowed-tools` | Pre-approve tools without per-use prompts | Skills that need specific tool access (e.g., `Bash(git *)`) |
| `context: fork` | Run in an isolated subagent context | Self-contained tasks that shouldn't consume main context |
| `agent` | Which subagent type to use with `context: fork` | Pair with fork: `Explore` for read-only, `Plan` for planning |
| `argument-hint` | Shown during autocomplete (e.g., `[issue-number]`) | Skills that take arguments |
| `model` | Override the session model | Specialized tasks needing a specific model |
| `effort` | Override reasoning effort (`low`/`medium`/`high`/`max`) | Tasks needing more or less reasoning depth |
| `paths` | Glob patterns limiting when skill auto-activates | Skills tied to specific file types or directories |
| `hooks` | Lifecycle hooks scoped to the skill | Pre/post validation when the skill runs |
| `shell` | `bash` (default) or `powershell` for inline commands | Windows-specific skills |

**Example combining fields:**

```yaml
---
name: deploy
description: "Use when deploying the application to production"
disable-model-invocation: true
allowed-tools: Bash(git *) Bash(npm *)
context: fork
argument-hint: "[environment]"
---
```

## Writing the Body

### Structure

A well-structured SKILL.md typically includes:

1. **Overview** — What the skill does and its core principle (1-3 sentences)
2. **The Process / Instructions** — Step-by-step guidance
3. **Output Format** — Templates or examples of expected output (if applicable)
4. **Common Mistakes** — Table of pitfalls and fixes
5. **Integration** — How this skill relates to others in the project

### Instruction Style

**Explain the why, not just the what.** Today's LLMs are smart — they respond much better to understanding reasoning than to rigid directives. If you find yourself writing MUST or ALWAYS in all caps, that's a signal to reframe: explain the reasoning so the agent understands why the thing matters.

```markdown
# Less effective — rigid rule without reasoning
You MUST ALWAYS check version drift before releasing. NEVER skip this step.

# More effective — explains why, agent understands the stakes
Check version drift before releasing — a single drifted manifest can cause install
failures on specific platforms, and users won't know why the plugin stopped working.
```

**Use the imperative form.** Skills are instructions, not documentation.

```markdown
# Less effective — passive/descriptive
The project structure should be scanned first.

# More effective — imperative
Scan the project structure first.
```

**Give concrete examples over abstract descriptions.** One real example teaches more than three paragraphs of explanation.

### Token Efficiency

Every token in a frequently-loaded skill costs context budget across every session.

| Target | Budget |
|--------|--------|
| Bootstrap skill (always loaded) | < 200 lines |
| Regular skill body | < 500 lines |
| Description (always in context) | < 250 characters |

**Techniques for staying lean:**
- Cross-reference other skills (`project:skill-name`) instead of repeating content
- One excellent example beats three mediocre ones
- Extract heavy reference content (100+ lines) to `references/` files
- Don't include information the agent already knows (standard tool usage, basic git commands)

### Progressive Disclosure

The three-level loading system keeps context budgets manageable:

| Level | When Loaded | What Goes Here |
|-------|-------------|----------------|
| Metadata (name + description) | Always | Triggering conditions only (~100 words) |
| SKILL.md body | When skill triggers | Core instructions, process, examples |
| references/, scripts/, assets/ | On demand | Heavy docs, executable tools, templates |

When the SKILL.md body approaches 500 lines, look for sections to extract:
- API reference tables → a file under `references/`
- Platform-specific details → one file per platform under `references/`
- Long example templates → files under `assets/`

Reference extracted files clearly from the SKILL.md with guidance on when to read them:

```markdown
For platform-specific wiring details, read the relevant file
under references/ and then load the template files from assets/.
```

## Skill Types

Skills generally fall into two categories:

- **Rigid skills** (discipline-enforcing) — Follow exactly, no improvisation. Examples: security scanning, release checklists, TDD loops.
- **Flexible skills** (pattern-based) — Adapt principles to context. Examples: brainstorming, optimization, design interviews.

Declare which type the skill is in the Overview section so the agent knows whether to follow instructions literally or adapt them.

## Supporting Resources

### When to Create References

Create a `references/` file when:
- A section exceeds 100 lines and isn't needed on every invocation
- Content is domain-specific (platform docs, API specs) and only relevant in certain branches
- Multiple skills share the same reference material

### When to Create Scripts

Create a `scripts/` file when:
- Multiple test runs independently produce similar helper scripts
- A task is deterministic and repetitive (JSON validation, file scanning, version bumping)
- The skill needs to produce consistent, programmatic output

### When to Create Assets

Create an `assets/` file when:
- The skill generates files from templates (config files, manifest boilerplate)
- Output requires specific formatting that's easier to template than describe

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Description summarizes workflow | Describe triggering conditions only — agents shortcut to description |
| Piling on MUST/ALWAYS/NEVER | Explain why the rule exists — understanding beats compliance |
| Putting everything in SKILL.md | Extract heavy content to references/ when over 500 lines |
| No examples, only abstract rules | Add at least one concrete example per key instruction |
| Writing for humans, not agents | Use imperative form, clear structure, explicit output formats |
| Description too narrow | Be pushy — list related scenarios, edge cases, alternative phrasings |
| Description too broad | Scope to the right context (e.g., "bundle-plugins" not just "any project") |

## Integration

**Called by:**
- **bundles-forge:scaffolding** — after scaffold, point users here for content guidance

**Pairs with:**
- **bundles-forge:optimizing** — for improving existing skill content
- **bundles-forge:auditing** — audit identifies content quality issues this skill helps fix
