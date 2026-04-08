---
name: iterating-feedback
description: "Use when receiving user feedback about a skill and iterating on improvements — covers feedback analysis, suggestion validation against the skill's core goals, internal skill modification, external skill forking with identifiers, automatic post-change auditing, and version/documentation updates. Also use when a user reports that a skill produces incorrect or incomplete results, or when importing and adapting an external skill"
---

# Iterating Skill Feedback

## Overview

Receive user feedback about a skill, validate each suggestion against the skill's core goals, apply confirmed improvements, and hand off to audit for post-change verification. This is the execution arm of the feedback loop — auditing evaluates, this skill executes.

**Core principle:** Confirm first, change second, audit last. Never apply feedback without validating necessity, and never claim improvement without audit evidence.

**Skill type:** Flexible — adapt the validation depth to feedback complexity.

**Announce at start:** "I'm using the iterating-feedback skill to process your feedback and iterate on improvements."

## The Contract

This skill operates under a strict division of labor with `bundles-forge:auditing`:

```
auditing (Evaluator)          iterating (Executor)
─────────────────────         ────────────────────
Evaluates, scores, reports    Validates feedback, applies changes
Never modifies files          Only modifies after user confirmation
Suggests improvements         Executes improvements
                    ↓ user confirms ↓
              iterating receives feedback
              iterating applies changes
              iterating auto-calls auditing
                    ↓
              auditing outputs post-change report
```

**Rules:**
- Auditing never calls this skill directly — it suggests, user decides
- This skill never starts modifications without explicit user confirmation
- After all changes are applied, this skill always invokes `bundles-forge:auditing` to produce the post-change audit report

## Scope Clarification

This skill and `bundles-forge:optimizing` serve different purposes:

| Signal | Use | Why |
|--------|-----|-----|
| "This skill triggered but produced wrong results" | `iterating` | Single-skill effectiveness |
| "Description format doesn't follow conventions" | `optimizing` | Project engineering norms |
| "The steps in this skill are in the wrong order" | `iterating` | Workflow effectiveness |
| "Token budget exceeded across the project" | `optimizing` | Project-level constraint |
| "The prompts in this skill need better wording" | `iterating` | Prompt tuning |
| "Cross-reference chain is broken" | `optimizing` | Project structure |
| "User reports skill X always skips a step" | `iterating` | Feedback-driven improvement |
| "Need to add Gemini support" | `optimizing` | Platform engineering |

**When in doubt:** If the feedback is about a single skill's behavior or output quality, use this skill. If it's about project-wide engineering standards, use `optimizing`.

## The Process

```
Receive feedback
  → Identify target skill
  → Classify source (internal vs external)
  → If external: fork with identifier
  → Read skill, understand core goal
  → For each feedback item:
      → Validate (3-step framework)
      → Accept / Reject / Modify
  → Present improvement plan to user
  → USER CONFIRMS ← gate
  → Apply changes
  → Self-check
  → Auto-invoke auditing
  → Version bump + doc update (if bundles)
```

### Step 1: Receive and Classify

Identify the target skill and classify its source:

| Source | Indicator | Action |
|--------|-----------|--------|
| Internal (bundles) | Skill exists under `skills/` in current project | Modify in place |
| External folder | User points to a directory outside the project | Fork then modify |
| External zip | User provides a `.zip` file | Extract, fork, then modify |
| External GitHub | User provides a repository URL or skill link | Clone/download, fork, then modify |

### Step 2: Fork External Skills

For external skills, create a working copy before any modification. Never modify the original.

**Naming convention:** Prefix the skill directory with `forked-` to clearly distinguish from the original.

```
Original: awesome-skill/SKILL.md
Forked:   forked-awesome-skill/SKILL.md
```

Add a provenance header to the forked SKILL.md, immediately after the frontmatter:

```markdown
<!-- Forked from: <original-source>
     Fork date: <YYYY-MM-DD>
     Reason: <brief description of feedback being addressed> -->
```

Update the `name` field in frontmatter to match the new directory name (`forked-awesome-skill`).

### Step 3: Understand the Skill's Core Goal

Before evaluating any feedback, read the entire skill and identify:

1. **Core goal** — What is this skill fundamentally trying to achieve?
2. **Target audience** — Which agent behaviors does it shape?
3. **Key constraints** — What trade-offs or boundaries does it operate within?

Document these in your working notes. Every feedback item will be validated against them.

### Step 4: Validate Each Feedback Item

Apply the three-step validation framework to every suggestion:

#### 4a: Goal Alignment

Ask: "Does this improvement serve the skill's core goal?"

If the suggestion pushes the skill toward a different purpose — even a useful one — it fails this check. A security-scanning skill should not become a general code reviewer just because someone suggests adding code quality checks.

#### 4b: Necessity

Ask: "Without this change, does the skill have an actual defect?"

Distinguish between:
- **Defect** — the skill produces incorrect or incomplete results → necessary
- **Preference** — a different style that isn't objectively better → not necessary
- **Enhancement** — adds capability the skill wasn't designed for → evaluate scope

For each accepted suggestion, articulate a one-sentence necessity argument: "This change is necessary because [concrete deficiency]."

#### 4c: Side Effect Assessment

Ask: "Could this change introduce new problems?"

Check for:
- **Complexity creep** — does the change make the skill harder to follow?
- **Scope expansion** — does it push the skill beyond its declared responsibility?
- **Conflict** — does it contradict other instructions in the same skill?
- **Regression** — could it break behavior that currently works?

### Step 5: Present the Improvement Plan

After validating all feedback items, present a structured plan to the user:

```
## Improvement Plan for <skill-name>

### Accepted (X items)
1. [Feedback summary] — Necessity: [reason]
   Change: [what will be modified]

### Rejected (Y items)
1. [Feedback summary] — Reason: [why it was rejected]

### Modified (Z items)
1. [Original feedback] → [Adjusted version] — Reason: [why adjusted]
```

**Wait for user confirmation before proceeding.** Do not apply any changes until the user explicitly approves the plan.

### Step 6: Apply Changes

After user confirmation, apply all accepted improvements. Follow these rules:

- Make changes incrementally — one logical change at a time
- For internal skills, modify the original files directly
- For forked skills, modify the forked copy only
- Preserve the skill's existing structure and style conventions
- When modifying instructions, follow `bundles-forge:writing-skill` guidelines

### Step 7: Self-Check

Before handing off to audit, run a lightweight self-check:

| Check | What to Verify |
|-------|---------------|
| Intent match | Do changes accurately reflect the confirmed plan? |
| No accidental duplication | Did any change duplicate content from other skills? |
| Format consistency | Are file format and style consistent with the rest of the project? |

If any issue is found during self-check, fix it before proceeding.

### Step 8: Auto-Invoke Audit

Invoke `bundles-forge:auditing` to produce the post-change audit report. This is not optional — every iteration cycle ends with an audit.

The audit provides an independent evaluation of the changes. If the audit reveals new issues introduced by the changes, present them to the user and offer to address them in a follow-up iteration.

### Step 9: Version and Documentation

For skills within a bundles, after the audit confirms the changes are sound:

1. **Version bump** — Use `bundles-forge:managing-versions` to bump the appropriate version (patch for fixes, minor for new capabilities)
2. **CHANGELOG** — Add an entry describing what feedback was addressed
3. **README** — Update if the skill's purpose or behavior changed significantly

For forked external skills, version and documentation updates apply only to the fork.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Applying feedback without validation | Every item goes through the 3-step framework — no exceptions |
| Skipping user confirmation | The improvement plan must be approved before any file is modified |
| Modifying external skills in place | External skills are always forked first — never touch the original |
| Treating all feedback as equal | Distinguish defects from preferences from enhancements |
| Forgetting the post-change audit | Always invoke auditing after changes — improvement claims need evidence |
| Expanding skill scope based on feedback | Feedback should improve what the skill does, not change what it is |
| Not recording fork provenance | Forked skills need the provenance header to track origin |

## Integration

**Suggested by:**
- **bundles-forge:auditing** — when audit findings indicate single-skill effectiveness issues (requires user confirmation)

**Calls:**
- **bundles-forge:auditing** — automatic post-change audit
- **bundles-forge:writing-skill** — reference for content modification guidelines
- **bundles-forge:managing-versions** — version bump after confirmed changes

**Cross-refers:**
- **bundles-forge:optimizing** — when project-level engineering issues are discovered during iteration, suggest the user invoke optimizing instead
