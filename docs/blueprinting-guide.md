# Blueprinting Guide

[中文](blueprinting-guide.zh.md)

A user-oriented guide to planning bundle-plugins with Bundles Forge. Covers scenario selection, the design interview, the automated creation pipeline, and common pitfalls.

## Overview

Blueprinting is the **new-project orchestrator**: it runs a structured design interview and, after you approve the design document, coordinates the full creation pipeline — scaffolding, content authoring, workflow wiring, and initial quality check. It turns a vague idea into a concrete design document before any code or project structure is generated.

**Why it matters:** Five minutes of blueprinting saves hours of rework. Skipping this step is the #1 cause of poorly structured bundle-plugins that need complete restructuring later.

> **Canonical source:** The full execution protocol (interview questions, scenario analysis steps, design document template) lives in `skills/blueprinting/SKILL.md`. This guide helps you decide *which* path to take and *what to expect* — the skill itself handles execution.

---

## Quick Start

The fastest way to start a new bundle-plugin:

1. **Invoke** `/bundles-blueprint` (or ask the agent to plan a new bundle-plugin)
2. **Answer** the structured interview — one question at a time
3. **Review and approve** the design document the agent produces
4. **The agent takes over** — it automatically runs scaffolding → authoring → workflow design → auditing

Two key decisions to make upfront:

- **Quick vs adaptive mode?** Quick is for packaging a few standalone skills quickly (Claude Code only, no bootstrap). Adaptive is for orchestrated multi-skill projects with workflow chains. The agent asks you this as the first question.
- **Already have a project?** Blueprinting creates *new* projects. To add skills, restructure workflows, or improve an existing project, use `/bundles-optimize` instead — see Target 7 in the [optimizing guide](optimizing-guide.md).

For details on each step, read on.

---

## Choosing a Scenario

Blueprinting has three entry points. Pick the one that matches your situation:

| Scenario | Starting Point | When to Use | Output |
|----------|---------------|-------------|--------|
| **A: New project** | No existing code | You're starting from scratch with an idea | Full design document |
| **B: Decomposition** | One large skill | Your SKILL.md has grown too complex | Decomposition plan → design document |
| **C: Composition** | Multiple existing skills | You want to combine independent skills into a workflow | Composition plan → design document |

> **Want to add skills to an existing project?** That's optimization, not blueprinting. Use `/bundles-optimize` — see Target 7 (Skill & Workflow Restructuring) in the [optimizing guide](optimizing-guide.md).

### Decision Flowchart

```
Do you have an existing bundle-plugin project?
  ├─ Yes → You probably need optimizing (add skills, restructure) or auditing, not blueprinting
  └─ No  → Do you have existing skills?
            ├─ Yes → Is it ONE large skill that needs splitting?
            │         ├─ Yes → Scenario B (Decomposition)
            │         └─ No  → Multiple skills to combine?
            │                   ├─ Yes → Scenario C (Composition)
            │                   └─ No  → Scenario A (New project)
            └─ No  → Scenario A (New project)
```

---

## The Interview

**The most common path (Scenario A).** You have an idea for a bundle-plugin and want to plan it properly.

### What to Expect

The skill runs a structured interview, asking one question at a time:

| # | Question | Why It Matters |
|---|----------|---------------|
| 1 | Project complexity | Determines interview depth (quick vs adaptive mode) |
| 2 | Project name | Becomes directory name, package name, and plugin ID everywhere |
| 3 | Target platforms | Determines which manifests to generate |
| 4 | Skill inventory | Defines what capabilities the plugin will have |
| 4a | Skill visibility | Entry-point vs internal — affects commands and descriptions |
| 5 | Workflow chain | Determines how skills connect and the bootstrap content |
| 6 | Bootstrap strategy | Whether to auto-inject skill awareness at session start |
| 7 | Advanced components | MCP servers, LSP servers, bin/ executables, output styles |

Questions 4a, 5, 6, and 7 are only asked in **adaptive mode** (orchestrated multi-skill projects). Quick mode (quick packaging) skips them.

### Quick vs Adaptive Mode

| | Quick | Adaptive |
|---|---|---|
| **Use when** | Bundling standalone skills for distribution | Building an orchestrated workflow |
| **Interview depth** | 4 questions (name, platforms, skills, done) | 7+ questions with conditional follow-ups |
| **Default platform** | Claude Code only | User-selected |
| **Bootstrap** | Skipped (not needed) | Recommended for 3+ skills |
| **Commands** | Not generated | Entry-point skills get matching commands |
| **Duration** | 2-3 minutes | 5-10 minutes |

**Rule of thumb:** If your skills form a chain (output of A feeds into B), use adaptive mode. If they're independent utilities, quick is fine.

### Tips for Good Answers

- **Project name:** Use kebab-case (`my-dev-tools`, not `myDevTools`). This name appears everywhere.
- **Platforms:** Start with what you actually use today. Add others later with `bundles-forge:scaffolding`.
- **Skill inventory:** Even a rough list helps. You can always add skills later.
- **Workflow chain:** Draw it out — "skill-a → skill-b → skill-c". If skills are independent, say so.

---

## Advanced Scenarios

Most users follow the standard interview (Scenario A). These two scenarios handle specialized starting points — both feed into the same interview to finalize project details.

### Scenario B: Decomposition (Splitting a Large Skill)

**You have a SKILL.md that has grown too complex** — too many responsibilities, branching logic, or approaching the 500-line limit.

**Signs you need decomposition:**

| Signal | What It Means |
|--------|--------------|
| SKILL.md > 300 lines with multiple "If X, do this; if Y, do that" branches | Each major branch is a candidate for a separate skill |
| Sections with independent input/output formats | These are distinct responsibilities |
| Steps that can be skipped entirely in some cases | Optional steps should be separate skills in a chain |
| Heavy reference material for specific subtasks | Subtask should be its own skill with its own `references/` |

**What to expect:**

1. The skill reads your existing SKILL.md and maps its responsibilities
2. It identifies natural split points based on the signals above
3. It proposes a decomposition: which pieces become skills, which become shared resources
4. After you approve, it transitions into the standard interview for remaining project details

**Common patterns:** branch split (if/else branches → separate skills), pipeline extract (sequential phases → chained skills), reference extraction (inline tables → `references/` files). Not every large skill needs decomposition — if the skill is long but has a single clear responsibility, extract to `references/` instead.

### Scenario C: Composition (Combining Multiple Skills)

**You have several independent skills and want them to work as a coordinated bundle-plugin.**

**What to expect:**

1. The skill inventories all candidate skills (source, structure, quality, license)
2. It checks compatibility (naming conflicts, overlapping responsibilities, style consistency)
3. For third-party skills, it asks about integration intent:
   - **Repackage as-is** — bundle without modification (source attribution added)
   - **Integrate into workflow** — adapt descriptions, cross-references, and handoffs
4. It designs the orchestration (workflow chains, glue skills, shared resources, bootstrap)
5. After you approve, it transitions into the standard interview for remaining details

**Third-party skill handling:**

| Step | Required? | Purpose |
|------|:-:|---------|
| License check | Yes | Ensure license compatibility before copying |
| Security audit | Yes | Run `bundles-forge:auditing` on imported content |
| Source attribution | Yes | Add provenance header to copied SKILL.md |
| Description rewrite | Only for workflow integration | Adapt triggering conditions to new context |
| Cross-reference rewrite | Only for workflow integration | Change `old-project:skill` → `new-project:skill` |

**Never auto-install third-party skills with unresolved critical security findings.**

---

## The Design Document

All scenarios produce a design document with this structure:

```markdown
## Bundle-Plugin Design: <project-name>

**Mode:** quick / adaptive
**Platforms:** <list>
**Bootstrap:** yes/no

### Skills
| Name | Purpose | Type | Visibility | Dependencies |
|------|---------|------|------------|--------------|

### Workflow Chain
<description or "independent">

### Advanced Components
<list or "none">

### Third-Party Sources (if applicable)
| Skill | Source | License | Integration Intent |
|-------|--------|---------|-------------------|

### Notes
<special requirements or constraints>
```

**Review checklist before approving:**
- [ ] All skills are named in kebab-case
- [ ] Workflow dependencies are mapped (or marked independent)
- [ ] Platform choices match what you actually use
- [ ] Third-party skills have license and security audit noted

---

## The Pipeline: What Happens After Approval

When the design document is approved, **blueprinting orchestrates** a four-phase pipeline. This is not a single automatic handoff only to scaffolding; the orchestrator drives each stage in order:

| Phase | What runs | Purpose |
|-------|-----------|---------|
| **Phase 1** | `bundles-forge:scaffolding` | Generate project structure and platform manifests |
| **Phase 2** | `bundles-forge:authoring` | Author **SKILL.md** and **agents/*.md** — **invoked by blueprinting** after scaffolding (not by scaffolding) |
| **Phase 3** | Workflow design | Wire skills together (chains, bootstrap, commands) per the design |
| **Phase 4** | `bundles-forge:auditing` | Validate quality and security before further iteration |

Later, use `bundles-forge:scaffolding` again if you need to add more platforms.

The agent carries your approved design document through these phases. **Authoring** is called by **blueprinting** as part of this pipeline; scaffolding does not call authoring.

---

## FAQ

**Q: The agent jumps straight to scaffolding without interviewing me. What happened?**

The skill wasn't loaded, or you said something like "just generate it" that bypassed the interview. Explicitly invoke `/bundles-blueprint` to ensure the full interview runs.

**Q: The interview is asking too many questions for my simple project.**

You're in adaptive mode. At question 1, answer "quick packaging" (or "quick mode") to use the shorter interview flow with only 4 questions.

**Q: The interview is too short — it skipped important questions.**

You're in quick mode. Restart and answer "orchestrated multi-skill" at question 1 to get the full adaptive-mode interview with conditional follow-ups.

**Q: The design document has the wrong platform listed.**

Edit the design document before approving — the agent presents it for your review. You can change platforms, skill names, or any other field before giving approval.

**Q: A third-party skill fails the security audit.**

Fix the security issues in the imported skill, or exclude it from the composition. Never approve a design that includes third-party skills with unresolved critical security findings.

**Q: I'm not sure which scenario to pick.**

Follow the decision flowchart in the "Choosing a Scenario" section. When in doubt, start with Scenario A (new project) — the agent can adapt if it turns out you need decomposition or composition.

**Q: I want to add skills to an existing project, not create a new one.**

Use `/bundles-optimize` instead — Target 7 (Skill & Workflow Restructuring) handles adding, replacing, and reorganizing skills in existing projects. Blueprinting is only for creating new projects.

**Q: What's the difference between blueprinting and scaffolding?**

Blueprinting is the *planning* phase — it interviews you and produces a design document. Scaffolding is the *execution* phase — it reads the design and generates the actual project files. For platform adaptation on existing projects, you skip blueprinting entirely and invoke scaffolding directly.

**Q: Can I skip blueprinting and scaffold directly?**

Yes, but only for platform adaptation (adding/removing platform support on an existing project). For new projects, skipping the interview means the agent has to guess your requirements — which leads to rework. Five minutes of blueprinting is almost always worth it.
