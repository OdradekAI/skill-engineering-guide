# Blueprinting Guide

[中文](blueprinting-guide.zh.md)

A user-oriented guide to planning bundle-plugins with Bundles Forge. Covers the three-phase interview (needs exploration, architecture design, design review), the automated creation pipeline, and common pitfalls.

## Overview

Blueprinting is the **new-project orchestrator**: it runs a structured three-phase interview — first understanding *what* you're building and *why*, then designing the technical architecture, and finally producing a design document for your approval. After approval, it coordinates the full creation pipeline: scaffolding, content authoring, workflow wiring, and initial quality check.

**Why it matters:** Five minutes of needs exploration saves hours of rework. Skipping this step is the #1 cause of poorly structured bundle-plugins that need complete restructuring later.

> **Canonical source:** The full execution protocol (interview phases, dialogue strategy, design document template) lives in `skills/blueprinting/SKILL.md`. This guide helps you decide *which* path to take and *what to expect* — the skill itself handles execution.

---

## Quick Start

The fastest way to start a new bundle-plugin:

1. **Invoke** `/bundles-blueprint` (or ask the agent to plan a new bundle-plugin)
2. **Answer** the three-phase interview — needs first, then architecture, one question at a time
3. **Review and approve** the design document the agent produces (including self-review checks)
4. **The agent takes over** — it automatically runs scaffolding → authoring → workflow design → auditing

Key things to know upfront:

- **Needs come first.** The agent will ask what problem you're solving and who will use it *before* any technical questions. Even for simple projects, this takes only 2 questions.
- **The agent recommends, you decide.** For key decisions (quick vs adaptive mode, skill decomposition, platform selection), the agent proposes 2-3 approaches with trade-offs and a recommendation.
- **The agent pushes back when needed.** If your answers contradict each other or your requested scope seems disproportionate to the problem, the agent will name the issue and propose a simpler alternative. This is by design.
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

## The Three-Phase Interview

### Phase 1: Needs Exploration

**The agent starts by understanding your problem, not your technical preferences.**

| # | Question | Why It Matters |
|---|----------|---------------|
| 1 | Problem scenario | What gap exists and how people solve it today |
| 2 | Target users | Shapes platform selection, complexity, and documentation style |
| 3 | Core capabilities | Identifies non-negotiable skills vs nice-to-haves |
| 4 | Usage flow | Reveals workflow dependencies and entry points |
| 5 | Existing alternatives | Clarifies differentiation (asked only if relevant) |

For **quick mode** projects (simple skill packaging), the agent asks only questions 1 and 2 before moving on.

After collecting answers, the agent restates its understanding and asks you to confirm before proceeding to architecture design.

### Phase 2: Architecture Design

**Now the agent makes technical recommendations based on your needs.**

| # | Question | How It Works |
|---|----------|-------------|
| — | Assumptions gate | Agent states key assumptions from Phase 1 — you confirm or correct before architecture begins |
| 1 | Project complexity | Agent *recommends* quick vs adaptive mode based on Phase 1 — you confirm |
| 2 | Project name | Kebab-case identifier used everywhere |
| 3 | Target platforms | Agent recommends based on target users — you confirm or adjust |
| 4 | Skill inventory | Agent *proposes* a decomposition with trade-offs — you confirm or adjust |
| 4a | Skill visibility | Entry-point vs internal — affects commands and descriptions (adaptive only) |
| 5 | Workflow chain | How skills connect (adaptive only) |
| 6 | Bootstrap strategy | Whether to auto-inject skill awareness (adaptive only) |
| 7 | Advanced components | MCP servers, LSP servers, bin/ executables, output styles (adaptive only, only when you mention a matching need) |

Questions 4a, 5, 6, and 7 are only asked in **adaptive mode**. Quick mode skips them.

### Phase 3: Design Document and Review

1. The agent compiles a design document from the interview
2. It runs a self-review (placeholder scan, consistency check, scope check, ambiguity check)
3. It presents the document for your approval
4. You can request changes — the agent updates and re-reviews
5. Only after your explicit approval does the creation pipeline begin

### Quick vs Adaptive Mode

| | Quick | Adaptive |
|---|---|---|
| **Use when** | Bundling standalone skills for distribution | Building an orchestrated workflow |
| **Needs exploration** | 2 questions (problem + users) | 5 questions (full needs exploration) |
| **Architecture depth** | 5 steps (assumptions, mode, name, platforms, skills) | 8+ questions with conditional follow-ups |
| **Default platform** | Claude Code only | User-selected |
| **Bootstrap** | Skipped (not needed) | Recommended for 3+ skills |
| **Commands** | Not generated | Entry-point skills get matching commands |
| **Duration** | 3-5 minutes | 8-15 minutes |

**Rule of thumb:** If your skills form a chain (output of A feeds into B), use adaptive mode. If they're independent utilities, quick is fine. The agent recommends the mode — you don't need to choose upfront.

### Tips for Good Answers

- **Problem scenario:** Be specific about the pain point. "It's annoying to do X manually" is better than "I want a tool for X."
- **Target users:** Mention their skill level and workflow context. "Backend developers using Claude Code who write Python" is more useful than "developers."
- **Project name:** Use kebab-case (`my-dev-tools`, not `myDevTools`). This name appears everywhere.
- **Platforms:** Start with what you actually use today. Add others later with `bundles-forge:scaffolding`.
- **When the agent proposes approaches:** Read the trade-offs. If none fit, say so — the agent will adjust.

---

## Advanced Scenarios

Most users follow the standard interview (Scenario A). These two scenarios handle specialized starting points — both feed into the same three-phase interview to finalize project details.

### Scenario B: Decomposition (Splitting a Large Skill)

**You have a SKILL.md that has grown too complex** — too many responsibilities, branching logic, or approaching the 500-line limit. Splitting produces a **new** project. To refactor skills within an existing project, use `/bundles-optimize` (Target 7).

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
4. After you approve, it transitions into the standard three-phase interview with richer context

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
5. After you approve, it transitions into the standard three-phase interview with richer context

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

### Project Overview
<One sentence: what this skill bundle is and what problem it solves>

### Target Users
<Who will use it, their background, typical workflows>

### Use Cases
<2-3 concrete scenarios>

### Success Criteria
<How to judge whether this is working well>

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
- [ ] Project overview clearly states the problem being solved
- [ ] Target users are specific (not just "developers")
- [ ] All skills are named in kebab-case
- [ ] Workflow dependencies are mapped (or marked independent)
- [ ] Platform choices match what you actually use
- [ ] Third-party skills have license and security audit noted
- [ ] Success criteria are measurable where possible

---

## The Pipeline: What Happens After Approval

When the design document is approved, **blueprinting orchestrates** a four-step pipeline. This is not a single automatic handoff only to scaffolding; the orchestrator drives each step in order:

| Step | What runs | Purpose |
|------|-----------|---------|
| **Scaffold** | `bundles-forge:scaffolding` | Generate project structure and platform manifests |
| **Author Content** | `bundles-forge:authoring` | Author **SKILL.md** and **agents/*.md** — **invoked by blueprinting** after scaffolding (not by scaffolding) |
| **Wire Workflow** | Workflow design (blueprinting internal) | Wire skills together (chains, bootstrap, commands) per the design |
| **Run Audit** | `bundles-forge:auditing` | Validate quality and security before further iteration |

Each phase includes a verification gate: the agent checks its work (e.g., inspector passes, frontmatter is valid, workflow links are symmetric, no critical audit findings) and loops back to fix issues before proceeding. If the final audit surfaces warnings, the agent presents them and asks whether to proceed.

Later, use `bundles-forge:scaffolding` again if you need to add more platforms.

The agent carries your approved design document through these phases. **Authoring** is called by **blueprinting** as part of this pipeline; scaffolding does not call authoring. The design document's needs context (project overview, target users, use cases) is passed to authoring to help write more targeted skill descriptions.

---

## FAQ

**Q: The agent jumps straight to scaffolding without interviewing me. What happened?**

The skill has a HARD-GATE that prevents this. If it happened, the skill wasn't loaded — explicitly invoke `/bundles-blueprint` to ensure the full interview runs. The agent cannot proceed to scaffolding until you approve a design document.

**Q: The agent keeps asking questions and won't move on. How do I speed this up?**

Each phase has a checkpoint — the agent moves forward once it has verified the required information. If you want the shorter flow, tell the agent you're doing "quick packaging" early on. Quick mode asks only 2 needs questions + 4 architecture questions. You can also say "that's enough detail, let's proceed" and the agent will assess whether it has enough to generate the design document.

**Q: The agent gave me multiple approaches. I don't know which to pick.**

Read the trade-offs the agent provides. The agent always marks one as "recommended" with reasoning. If you're unsure, go with the recommendation — you can adjust later. If none of the approaches fit, tell the agent what's wrong and it will propose alternatives.

**Q: The interview is asking too many questions for my simple project.**

You're likely in adaptive mode. At the architecture phase, the agent should have recommended quick mode for simple projects. If it didn't, tell it explicitly that you want quick mode.

**Q: The design document has something wrong. Can I go back?**

Yes. At the review gate, you can request changes to any part of the design. The agent updates the document and re-runs its self-review. You can also ask to go back to a specific phase to re-discuss a decision without restarting from scratch.

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
