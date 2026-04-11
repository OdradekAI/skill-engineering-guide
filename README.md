# Bundles Forge

[中文](README.zh.md)

A toolkit for building **bundle-plugins** — AI coding plugins organized around collaborative skill workflows — across Claude Code, Cursor, Codex, OpenCode, and Gemini CLI.

## What is a Bundle-Plugin?

A single skill (`SKILL.md`) does one thing — an AI agent discovers it by its `description` field and loads it on demand. A **bundle-plugin** takes this further: multiple skills reference each other and form a workflow, where one skill's output feeds the next.

```mermaid
graph LR
    A["Skill A"] -->|output feeds| B["Skill B"]
    B -->|output feeds| C["Skill C"]
    C -->|validates| A
```

bundles-forge itself is a bundle-plugin — `blueprinting` produces a design, `scaffolding` generates a project from it, `auditing` validates the result, and `optimizing` iterates on issues found.

**If your plugin has 3+ skills that form a workflow, you're building a bundle-plugin.** This toolkit gives you scaffolding, quality gates, and multi-platform publishing for that pattern.

## Quick Start

### Install (Claude Code)

```bash
claude plugin install bundles-forge
```

For development (any platform):

```bash
git clone https://github.com/odradekai/bundles-forge.git
cd bundles-forge
claude plugin link .
```

> Other platforms: see [Platform Support](#platform-support) below.

### Path A: Build a New Bundle-Plugin

```
/bundles-blueprint
```

This starts a structured interview to design your project — scope, platform targets, skill decomposition. When the design is ready, the agent automatically chains into `scaffolding` (project generation) and then `authoring` (SKILL.md writing).

### Path B: Audit an Existing Project

```
cd your-bundle-plugin-project
/bundles-audit
```

Runs a 10-category quality assessment with security scanning across 5 attack surfaces.

## Concepts

| Concept | What it is |
|---------|------------|
| **Skill** | Atomic capability unit (`SKILL.md`) — discovered by description, loaded on demand |
| **Plugin** | Packaging/distribution unit — bundles skills, agents, hooks, and more |
| **Subagent** | Isolated AI assistant for delegated tasks with its own context window |
| **Hook** | Shell/HTTP/LLM action that fires automatically on lifecycle events |
| **Command** | Slash command entry point (`/audit`) that invokes a skill |
| **MCP** | Open standard connecting Claude to external tools and data sources |

> Full explanations, design decisions, and architecture diagrams → [Concepts Guide](docs/concepts-guide.md)

## Skills

The 8 skills cover the full lifecycle of a bundle-plugin project:

```mermaid
flowchart LR
    Design["blueprinting"] --> Scaffold["scaffolding"]
    Scaffold --> Write["authoring"]
    Write --> Audit["auditing"]
    Audit -->|issues| Optimize["optimizing"]
    Optimize --> Audit
    Audit -->|pass| Release["releasing"]
    Adapt["porting"] -.->|"any phase"| Design
    Adapt -.->|"any phase"| Release
```

| Phase | Skill | What It Does |
|-------|-------|-------------|
| Design | `blueprinting` | Structured interview to determine project scope, platform targets, and skill decomposition. Produces a design document. |
| Scaffold | `scaffolding` | Generates the complete project structure from the design — manifests, hooks, scripts, bootstrap skill, and per-platform files. |
| Write | `authoring` | Guides SKILL.md authoring — frontmatter, "Use when..." descriptions, instructions, and progressive disclosure via `references/`. |
| Audit | `auditing` | 10-category quality assessment including security scanning across 5 attack surfaces. |
| Optimize | `optimizing` | Engineering improvements — description triggering accuracy, token efficiency, workflow chains, and feedback iteration. |
| Adapt | `porting` | Adds or fixes platform support. Generates manifests from templates. |
| Release | `releasing` | Orchestrates the pre-release pipeline: version drift check, audit, documentation consistency, change coherence review, version bump, CHANGELOG update, and publish guidance. |

The bootstrap meta-skill `using-bundles-forge` is injected at session start via hooks — it gives the agent awareness of all available skills and routes tasks automatically.

**Standalone use:** `authoring`, `auditing`, and `optimizing` can be invoked independently on any existing project without going through the full lifecycle.

### Agents

| Agent | Role |
|-------|------|
| `inspector` | Validates scaffolded project structure |
| `auditor` | Executes systematic quality audit with security scanning |
| `evaluator` | Runs one side of an A/B skill evaluation for optimization |

### Commands

| Command | Skill |
|---------|-------|
| `/bundles-forge` | `using-bundles-forge` |
| `/bundles-blueprint` | `blueprinting` |
| `/bundles-audit` | `auditing` |
| `/bundles-optimize` | `optimizing` |
| `/bundles-release` | `releasing` |
| `/bundles-scan` | `auditing` |

Skills without a slash command are invoked **automatically** (the agent matches user intent to the skill's `description` field) or **explicitly** when another skill chains to them via `bundles-forge:<skill-name>` references.

## Auditing

Four audit scopes for different levels of granularity — the agent auto-detects scope from the target path:

| Scope | Command / Script | What It Checks |
|-------|-----------------|----------------|
| Full Project | `/bundles-audit` or `audit_project.py` | 10 categories (structure, manifests, version sync, skill quality, cross-refs, workflow, hooks, testing, docs, security) |
| Single Skill | `/bundles-audit skills/authoring` or `audit_skill.py` | 4 categories (structure, skill quality, cross-refs, security) |
| Workflow | Explicit request or `audit_workflow.py` | 3 layers: static structure, semantic interface, behavioral verification (W1-W12) |
| Security Only | `/bundles-scan` or `scan_security.py` | 5 attack surfaces (skill content, hooks, plugins, agents, scripts) |

### Quick Start (Scripts)

```bash
python scripts/audit_project.py .                                      # full project audit
python scripts/audit_skill.py skills/authoring                         # single skill audit
python scripts/audit_workflow.py .                                     # workflow audit
python scripts/audit_workflow.py --focus-skills new-skill .            # focused workflow audit
python scripts/scan_security.py .                                      # security-only scan
```

Exit codes: `0` = pass, `1` = warnings, `2` = critical findings. All scripts accept `--json` for CI integration.

**After the audit:** Critical findings → fix or invoke `bundles-forge:optimizing`. Ready to publish → invoke `bundles-forge:releasing`.

> For detailed usage, checklists, report templates, and CI integration patterns, see [`docs/auditing-guide.md`](docs/auditing-guide.md).

## Architecture

<details>
<summary>Command execution chains and internal routing</summary>

> For concept explanations see [Concepts Guide](docs/concepts-guide.md). For per-skill details see guides in [`docs/`](docs/).

### Command Execution

Each slash command is a thin pointer to a skill. The real logic lives in the skill — but the execution chains can be deep.

```mermaid
flowchart LR
    subgraph commands [Slash Commands]
        CMD_BP["/bundles-blueprint"]
        CMD_AU["/bundles-audit"]
        CMD_OP["/bundles-optimize"]
        CMD_RE["/bundles-release"]
        CMD_SC["/bundles-scan"]
    end

    CMD_BP --> blueprinting
    CMD_AU --> auditing
    CMD_OP --> optimizing
    CMD_RE --> releasing
    CMD_SC -->|"security focus"| auditing

    blueprinting -->|"design approved"| scaffolding
    scaffolding -->|"structure generated"| authoring
    scaffolding -->|"post-scaffold check"| auditing
    auditing -->|"issues found"| optimizing
    optimizing -->|"verify fixes"| auditing
    releasing -->|"pre-release check"| auditing
    releasing -->|"fix quality"| optimizing
    blueprinting -.->|"platform targets"| porting
    scaffolding -.->|"add platform"| porting
    porting -->|"post-adaptation"| auditing
```

#### `/bundles-blueprint` — Plan a new bundle-plugin

**When to use:** Starting a new project, splitting a monolithic skill into multiple skills, or composing third-party skills into a bundle.

```
User runs /bundles-blueprint
  → blueprinting: structured interview (scope, platforms, skill decomposition)
  → User approves design document
  → scaffolding: generate project structure, manifests, hooks, scripts
    → inspector agent validates scaffold (if subagents available)
  → authoring: guide SKILL.md content for each skill
  → porting: add platform adapters (if multi-platform)
```

#### `/bundles-audit` — Quality assessment

**When to use:** Reviewing a project before release, after significant changes, or when scanning a third-party skill for security risks.

```
User runs /bundles-audit
  → auditing: detect scope (full project vs single skill vs workflow)
  → Full project: 10 categories (structure, manifests, version sync,
    quality, cross-refs, workflow, hooks, testing, docs, security)
    → auditor agent runs checklist (if subagents available)
    → Scripts: audit_project.py, audit_workflow.py, scan_security.py, lint_skills.py
  → Single skill: 4 categories (structure, quality, cross-refs, security)
  → Workflow: 3 layers (static structure, semantic interface, behavioral)
  → Score + report with Critical / Warning / Info findings
  → Critical issues? → Offer to fix → Re-audit once
  → Warnings? → Suggest optimizing skill
```

#### `/bundles-scan` — Security-focused audit

**When to use:** Same as `/bundles-audit` but emphasizes security scanning. Maps to the same `auditing` skill — the 5-surface security scan (SKILL.md content, hook scripts, plugin code, agent prompts, bundled scripts) runs as Category 9.

#### `/bundles-optimize` — Engineering improvements

**When to use:** Improving description triggering accuracy, reducing token usage, fixing workflow chain gaps, or iterating on user feedback about a specific skill.

```
User runs /bundles-optimize
  → optimizing: detect scope (project vs single skill)
  → Project scope: 6 optimization targets
    (descriptions, tokens, progressive disclosure, workflow chain,
     platform coverage, security remediation)
  → Skill scope: targeted optimization + feedback iteration
  → Description A/B test:
    → 2x evaluator agents in parallel (if subagents available)
    → Compare reports → pick winner
  → Verify fixes via auditing
```

#### `/bundles-release` — Version bump and publish

**When to use:** Preparing a release — version drift check, quality gate, documentation consistency, version bump, CHANGELOG update, and publishing guidance.

```
User runs /bundles-release
  → releasing: pre-flight checks
    → bump_version.py --check (version drift)
    → auditing (full quality + security)
    → check_docs.py (documentation consistency)
  → Address critical findings (block release until resolved)
  → Documentation sync (change coherence review + doc updates)
  → bump_version.py <new-version> (update all manifests)
  → Update CHANGELOG.md and README.md
  → Final verification (--check + --audit + check_docs.py)
  → Commit, tag, push, gh release create
```

</details>

## Platform Support

### Cursor

Search for `bundles-forge` in the Cursor plugin marketplace, or use `/add-plugin bundles-forge`.

### Codex

See [`.codex/INSTALL.md`](.codex/INSTALL.md)

### OpenCode

See [`.opencode/INSTALL.md`](.opencode/INSTALL.md)

### Gemini CLI

```bash
gemini extensions install https://github.com/odradekai/bundles-forge.git
```

## Tips for Long Sessions

Skills, audit reports, and script output accumulate in the conversation context over a long session. If you notice the agent slowing down or losing track of earlier context:

- **Start a fresh session** for each major lifecycle phase (blueprinting, authoring, auditing)
- **Use slash commands** (`/bundles-audit`, `/bundles-optimize`) to re-anchor the agent on the current task
- **Prefer script output over inline checks** — `python scripts/audit_project.py .` produces a compact summary instead of the agent reasoning through each check

## Contributing

Contributions welcome. Please follow the existing code style and ensure all platform manifests stay in sync using `python scripts/bump_version.py --check`.

## License

Apache-2.0
