# Blueprinting Guide

[中文](blueprinting-guide.zh.md)

A user-oriented guide to planning bundle-plugins with Bundles Forge. Covers all four entry scenarios, decision-making guidance, real-world examples, and common pitfalls.

## Overview

Blueprinting is the first skill in the bundle-plugin lifecycle. It turns a vague idea into a concrete design document through structured interview — before any code or project structure is generated.

**Why it matters:** Five minutes of blueprinting saves hours of rework. Skipping this step is the #1 cause of poorly structured bundle-plugins that need complete restructuring later.

> **Canonical source:** The full execution protocol (interview questions, scenario analysis steps, design document template) lives in `skills/blueprinting/SKILL.md`. This guide helps you decide *which* path to take and *what to expect* — the skill itself handles execution.

---

## Choosing a Scenario

Blueprinting has four entry points. Pick the one that matches your situation:

| Scenario | Starting Point | When to Use | Output |
|----------|---------------|-------------|--------|
| **A: New project** | No existing code | You're starting from scratch with an idea | Full design document |
| **B: Decomposition** | One large skill | Your SKILL.md has grown too complex | Decomposition plan → design document |
| **C: Composition** | Multiple existing skills | You want to combine independent skills into a workflow | Composition plan → design document |
| **D: Integration** | Existing bundle-plugin project | You want to add skills to a project that already works | Lightweight integration plan |

### Decision Flowchart

```
Do you have an existing bundle-plugin project?
  ├─ Yes → Are you adding new skills to it?
  │         ├─ Yes → Scenario D (Integration)
  │         └─ No  → You probably need auditing or optimizing, not blueprinting
  └─ No  → Do you have existing skills?
            ├─ Yes → Is it ONE large skill that needs splitting?
            │         ├─ Yes → Scenario B (Decomposition)
            │         └─ No  → Multiple skills to combine?
            │                   ├─ Yes → Scenario C (Composition)
            │                   └─ No  → Scenario A (New project)
            └─ No  → Scenario A (New project)
```

---

## Scenario A: New Project from Scratch

**The most common path.** You have an idea for a bundle-plugin and want to plan it properly.

### What to Expect

The skill runs a structured interview, asking one question at a time:

| # | Question | Why It Matters |
|---|----------|---------------|
| 0 | Project complexity | Determines interview depth (minimal vs intelligent mode) |
| 1 | Project name | Becomes directory name, package name, and plugin ID everywhere |
| 2 | Target platforms | Determines which manifests to generate |
| 3 | Skill inventory | Defines what capabilities the plugin will have |
| 3b | Skill visibility | Entry-point vs internal — affects commands and descriptions |
| 4 | Workflow chain | Determines how skills connect and the bootstrap content |
| 5 | Bootstrap strategy | Whether to auto-inject skill awareness at session start |
| 6 | Advanced components | MCP servers, LSP servers, bin/ executables, output styles |

Questions 3b, 4, 5, and 6 are only asked in **intelligent mode** (orchestrated multi-skill projects). Minimal mode (quick packaging) skips them.

### Minimal vs Intelligent Mode

| | Minimal | Intelligent |
|---|---|---|
| **Use when** | Bundling standalone skills for distribution | Building an orchestrated workflow |
| **Interview depth** | 4 questions (name, platforms, skills, done) | 7+ questions with conditional follow-ups |
| **Bootstrap** | Skipped (not needed) | Recommended for 3+ skills |
| **Commands** | Not generated | Entry-point skills get matching commands |
| **Duration** | 2-3 minutes | 5-10 minutes |

**Rule of thumb:** If your skills form a chain (output of A feeds into B), use intelligent mode. If they're independent utilities, minimal is fine.

### Tips for Good Answers

- **Project name:** Use kebab-case (`my-dev-tools`, not `myDevTools`). This name appears everywhere.
- **Platforms:** Start with what you actually use today. Add others later with `bundles-forge:porting`.
- **Skill inventory:** Even a rough list helps. You can always add skills later.
- **Workflow chain:** Draw it out — "skill-a → skill-b → skill-c". If skills are independent, say so.

---

## Scenario B: Decomposition (Splitting a Large Skill)

**You have a SKILL.md that has grown too complex** — too many responsibilities, branching logic, or approaching the 500-line limit.

### Signs You Need Decomposition

| Signal | What It Means |
|--------|--------------|
| SKILL.md > 300 lines with multiple "If X, do this; if Y, do that" branches | Each major branch is a candidate for a separate skill |
| Sections with independent input/output formats | These are distinct responsibilities |
| Steps that can be skipped entirely in some cases | Optional steps should be separate skills in a chain |
| Heavy reference material for specific subtasks | Subtask should be its own skill with its own `references/` |

### What to Expect

1. The skill reads your existing SKILL.md and maps its responsibilities
2. It identifies natural split points based on the signals above
3. It proposes a decomposition: which pieces become skills, which become shared resources
4. After you approve, it transitions into the Scenario A interview for remaining project details

### Common Decomposition Patterns

| Pattern | Before | After |
|---------|--------|-------|
| **Branch split** | One skill with 3 major if/else branches | 3 skills, each handling one branch, orchestrated by a parent |
| **Pipeline extract** | One skill with sequential phases | Phase skills chained via workflow |
| **Reference extraction** | One skill with inline reference tables | Core skill + reference files in `references/` (not a separate skill) |

**Important:** Not every large skill needs decomposition. If the skill is long but has a single clear responsibility, extract to `references/` instead of splitting into multiple skills.

---

## Scenario C: Composition (Combining Multiple Skills)

**You have several independent skills and want them to work as a coordinated bundle-plugin.**

### What to Expect

1. The skill inventories all candidate skills (source, structure, quality, license)
2. It checks compatibility (naming conflicts, overlapping responsibilities, style consistency)
3. For third-party skills, it asks about integration intent:
   - **Repackage as-is** — bundle without modification (source attribution added)
   - **Integrate into workflow** — adapt descriptions, cross-references, and handoffs
4. It designs the orchestration (workflow chains, glue skills, shared resources, bootstrap)
5. After you approve, it transitions into the Scenario A interview for remaining details

### Third-Party Skill Handling

| Step | Required? | Purpose |
|------|:-:|---------|
| License check | Yes | Ensure license compatibility before copying |
| Security audit | Yes | Run `bundles-forge:auditing` on imported content |
| Source attribution | Yes | Add provenance header to copied SKILL.md |
| Description rewrite | Only for Intent B | Adapt triggering conditions to new context |
| Cross-reference rewrite | Only for Intent B | Change `old-project:skill` → `new-project:skill` |

**Never auto-install third-party skills with unresolved critical security findings.**

---

## Scenario D: Integration (Adding to Existing Project)

**Your bundle-plugin already works, and you want to add new skills to it.** This is lighter than Scenarios A-C — it produces an integration plan, not a full design document.

### What to Expect

1. The skill reads your existing project (skills, workflow graph, bootstrap routing)
2. It inventories the new skills being added (same analysis as Scenario C)
3. It checks compatibility against the *existing project* (not a blank slate)
4. It designs insertion points: where do new skills connect to the workflow?
5. After you approve, it applies changes and suggests a focused workflow audit

### Integration Plan vs Design Document

| | Design Document (A/B/C) | Integration Plan (D) |
|---|---|---|
| **Scope** | Entire project | Only what changes |
| **Includes** | Name, platforms, all skills, full workflow | New skills, insertion points, updated edges |
| **Leads to** | `scaffolding` → `authoring` | Direct changes + workflow audit |
| **Duration** | Full lifecycle | Quick iteration |

### Post-Integration Verification

After integration, always run a focused workflow audit:

```bash
python scripts/audit_workflow.py --focus-skills new-skill-a,new-skill-b .
```

This verifies that new skills integrate correctly without breaking existing workflow chains.

---

## The Design Document

All scenarios except D produce a design document with this structure:

```markdown
## Bundle-Plugin Design: <project-name>

**Mode:** minimal / intelligent
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

## After Blueprinting

| What Happens Next | Triggered By |
|-------------------|-------------|
| `bundles-forge:scaffolding` | Design document approved (automatic chain) |
| `bundles-forge:authoring` | After scaffolding generates the project structure |
| `bundles-forge:porting` | If multi-platform targets were selected |

The transition to scaffolding is automatic — the agent invokes it with your approved design document.

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| Agent jumps to scaffolding without interviewing | Skill wasn't loaded or user said "just generate it" | Explicitly invoke `/bundles-blueprint` |
| Interview asks too many questions | Intelligent mode for a simple project | Answer "quick packaging" at question 0 |
| Interview asks too few questions | Minimal mode for a complex project | Restart and answer "orchestrated multi-skill" at question 0 |
| Design document has wrong platform | Answered platform question too quickly | Edit the design document before approving |
| Third-party skill fails security audit | Imported skill has risky patterns | Fix the issues or exclude the skill |
| Not sure which scenario to pick | Multiple apply | Follow the decision flowchart above |
