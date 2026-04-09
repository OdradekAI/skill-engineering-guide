---
name: optimizing
description: "Use when optimizing a bundle-plugin or single skill — improving descriptions for better triggering, reducing token usage, fixing audit findings, or iterating on user feedback about skill behavior. Auto-detects scope (full project vs single skill)"
---

# Optimizing Bundle-Plugins

## Overview

Targeted improvement of a bundle-plugin project or a single skill. Unlike a full audit, optimization focuses on goals: better triggering, lower token cost, tighter workflow chains, and feedback-driven skill refinement.

**Core principle:** Optimize for the agent's experience. Every improvement should make skills easier to discover, faster to load, and clearer to follow.

**Announce at start:** "I'm using the optimizing skill to improve [this project / this skill]."

## Step 1: Resolve Input & Detect Scope

The target can be a local path, a GitHub URL, or a zip file. Normalize the input to a local directory before scope detection.

### Input Normalization

| Input | Action |
|-------|--------|
| Local directory path | Use directly |
| Local SKILL.md file path | Use its parent directory |
| GitHub repo URL (`https://github.com/user/repo`) | `git clone --depth 1` to temp dir |
| GitHub subdirectory URL (`…/tree/main/skills/xxx`) | Clone repo (shallow), extract the subdirectory path |
| Zip/tar.gz file path | Extract to temp directory |
| GitHub release/archive URL (`.zip`/`.tar.gz`) | Download, then extract to temp directory |

### Scope Detection

After normalization, determine the scope from the resolved local path:

| Target | How to Detect | Mode |
|--------|--------------|------|
| Project root | Has `skills/` directory and `package.json` | **Project optimization** — all 6 targets |
| Single skill directory | Contains `SKILL.md` but no `skills/` subdirectory | **Skill optimization** — 4 targets + feedback iteration |
| Single SKILL.md file | Path ends in `SKILL.md` | **Skill optimization** — 4 targets + feedback iteration |

**If the target is a single skill, skip to the Skill Optimization section below.**

---

## Project Optimization

### Script-Assisted Checks

Run the quality linter to identify frontmatter issues, description anti-patterns, and broken references before manual optimization:

```bash
python scripts/lint-skills.py <project-root>        # markdown report
python scripts/lint-skills.py --json <project-root>  # machine-readable
```

The linter automates checks Q1-Q12 and X1-X2 from the skill quality ruleset. Focus manual effort on the subjective targets below.

### Target 1: Skill Description Triggering

The highest-impact optimization. Descriptions are the primary mechanism for skill discovery.

**Rules:**
- Start with "Use when..." — describe triggering conditions only
- Never summarize the skill's workflow in the description
- Include concrete symptoms, situations, and contexts
- Keep under 250 characters (descriptions over 250 are truncated in the skill listing)

**Why workflow summaries are harmful:** Testing revealed that when a description summarizes a skill's process, agents follow the description shortcut instead of reading the full SKILL.md. A description saying "code review between tasks" caused agents to do ONE review, even though the skill's flowchart showed TWO reviews.

```yaml
# BAD: Summarizes workflow — agent may follow this instead of reading skill
description: Use for auditing - scans structure, checks manifests, scores categories, generates report

# GOOD: Triggering conditions only — agent reads the full skill
description: Use when reviewing a bundle-plugin for structural issues, version drift, or before release
```

**Testing approach:** Use A/B eval (see below) to compare triggering accuracy before and after the change.

### A/B Eval for Description Changes

When optimizing a description, never overwrite the original blindly. Use a copy-and-compare approach:

```
1. Copy the skill to a working version (e.g. `<skill-name>-optimized/`)
2. Apply the description change to the copy only
3. Create 5+ realistic test prompts that should trigger this skill
4. Dispatch two `evaluator` agents (`agents/evaluator.md`) in parallel:
   - Evaluator A: label "original", loaded with the ORIGINAL skill → run all test prompts
   - Evaluator B: label "optimized", loaded with the OPTIMIZED skill → run all test prompts
5. Compare: which version triggered correctly on more prompts?
6. Present results to user with side-by-side comparison
7. User decides → adopt optimized version (replace original) or discard
```

**What to compare:**
- Trigger rate: how many of the test prompts correctly activated the skill?
- False negatives: did the optimized description miss cases the original caught?
- False positives: did either version trigger on prompts meant for other skills?

**When to skip A/B eval:** If the change is purely additive (adding triggering conditions that were previously missing) and doesn't modify existing trigger phrases, a simple verification pass is sufficient.

### Target 2: Token Efficiency

Every token in a frequently-loaded skill costs context budget across every session.

**Targets:**
- SKILL.md body < 500 lines
- Bootstrap skill (always loaded) < 200 lines
- Move heavy reference to sibling files under `references/`

**Techniques:**
- Cross-reference other skills (`project:skill-name`) instead of repeating content
- One excellent example beats three mediocre ones
- Move flag documentation to `--help` references
- Eliminate redundancy — don't repeat what's in referenced skills

### Target 3: Progressive Disclosure

Three-level loading system:

| Level | When Loaded | Budget |
|-------|-------------|--------|
| Metadata (name + description) | Always in context | ~100 words |
| SKILL.md body | When skill triggers | < 500 lines |
| Reference files | On demand | Unlimited |

If SKILL.md is approaching 500 lines, extract sections into `references/`.

### Target 4: Workflow Chain Integrity

| Check | What It Catches |
|-------|----------------|
| Every `project:skill-name` reference resolves | Broken links after renames |
| No circular dependencies | Infinite loops |
| Terminal states are clear | Agent doesn't wonder "what's next?" |
| Integration sections are present | Skills document their place in the chain |

Map the complete chain. Verify every link works.

### Target 5: Platform Coverage (project only)

Identify platforms the project doesn't yet support. For adding new platforms, invoke `bundles-forge:adapting-platforms`.

### Target 6: Security Remediation (project only)

Fix security findings from `bundles-forge:auditing` Category 9.

**Targets:**
- Remove unnecessary system access from hook scripts (least privilege)
- Scope OpenCode plugin capabilities to declared needs only
- Remove or justify any network calls in hooks/plugins
- Ensure agent prompts include scope constraints
- Strip encoding tricks or obfuscated content from SKILL.md files

**Process:** Run `bundles-forge:auditing` first, then address security findings by priority — critical before warnings, warnings before info.

### Project Process

1. **Identify target** — what specifically needs improvement?
2. **Measure current state** — how does it perform now?
3. **Apply improvement** — make the change
4. **Verify** — did it actually improve?

For description optimization specifically: create test prompts, verify triggering before and after.

---

## Skill Optimization (Lightweight Mode)

When the target is a single skill, run only the targets that apply at skill scope. This is auto-detected — no special flags needed.

### Applicable Targets

| Target | Applicable | What to Do |
|--------|-----------|------------|
| 1. Description Triggering | **Full** | Evaluate and improve the description's triggering accuracy |
| 2. Token Efficiency | **Full** | Check SKILL.md line count, references extraction |
| 3. Progressive Disclosure | **Full** | Verify the 3-level loading structure |
| 4. Workflow Chain Integrity | **Partial** | Check this skill's outgoing references resolve |
| 5. Platform Coverage | **Skip** | Project-level concern |
| 6. Security Remediation | **Partial** | Fix security issues within this skill's content |
| Feedback Iteration | **Full** | Process user feedback with 3-question validation |

### Skill Process

```
Read target skill
  → Determine goal: engineering optimization or feedback iteration?
  → Engineering: run applicable targets (1-4, partial 6)
  → Feedback: run feedback process (below)
  → Apply changes
  → Run bundles-forge:auditing (skill mode) for verification
```

### Script Shortcuts

```bash
python scripts/lint-skills.py <skill-directory>     # quality checks on single skill
```

---

## Feedback Iteration

Process user feedback about a specific skill's behavior or output quality. Use this when a user reports that a skill triggered but produced wrong results, skipped steps, or needs better wording. Works in both project and skill scope.

### Classify the Feedback

| Signal | Action |
|--------|--------|
| "This skill triggered but produced wrong results" | Feedback iteration (below) |
| "The steps in this skill are in the wrong order" | Feedback iteration (below) |
| "Description format doesn't follow conventions" | Use optimization targets 1-3 |
| "Token budget exceeded across the project" | Use optimization targets 2-3 (project mode) |

### The Feedback Process

```
Receive feedback
  → Identify target skill
  → If external skill: fork with `forked-` prefix before modifying
  → Read skill, understand core goal
  → Validate each feedback item (goal alignment, necessity, side effects)
  → Present improvement plan to user
  → USER CONFIRMS ← gate
  → Copy skill to working version (<skill-name>-optimized/)
  → Apply changes to copy only
  → A/B eval: subagent A (original) vs subagent B (optimized) with same input
  → Present comparison to user
  → User adopts → replace original; User rejects → discard copy
  → Run bundles-forge:auditing for post-change verification
```

**Validation framework** — for each feedback item, ask three questions:
1. **Goal alignment:** Does this serve the skill's core goal, or push it toward a different purpose?
2. **Necessity:** Without this change, does the skill have an actual defect (vs. a style preference)?
3. **Side effects:** Could this introduce complexity creep, scope expansion, or regression?

### A/B Eval for Feedback Changes

After applying changes to the copy, verify with a parallel comparison:

```
1. Identify the specific scenario from the user's feedback (the input that produced wrong results)
2. Dispatch two `evaluator` agents (`agents/evaluator.md`) in parallel:
   - Evaluator A: label "original", follows the ORIGINAL skill → processes the scenario
   - Evaluator B: label "optimized", follows the OPTIMIZED skill → processes the scenario
3. Compare outputs side-by-side
4. Present to user: "Original produced X, optimized produced Y — which is better?"
5. User decides → adopt or discard
```

**When to skip A/B eval:** If the feedback is about structural issues (missing section, wrong heading level, broken reference) rather than behavioral differences, a simple verification pass is sufficient — no need for subagent comparison.

**Rules:**
- Never apply feedback without user confirmation of the improvement plan
- For external skills, always fork first (prefix with `forked-`, add provenance header)
- After all changes, invoke `bundles-forge:auditing` for post-change verification — but only one audit cycle (no loops)

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Optimizing everything at once | Pick one target, measure, improve, verify |
| Adding MUST/ALWAYS/NEVER instead of explaining why | Explain the reasoning — agents respond to understanding |
| Splitting skills too aggressively | Only split when there's a genuine responsibility boundary |
| Ignoring token budget for bootstrap | Bootstrap loads every session — every word counts |
| Applying feedback without validation | Every item goes through the 3-question framework |
| Expanding skill scope based on feedback | Feedback should improve what the skill does, not change what it is |
| Running all 6 targets on a single skill | Let scope auto-detection handle it — targets 5-6 don't fully apply |

## Integration

**Called by:**
- **bundles-forge:auditing** — when audit finds optimization opportunities or user feedback issues

**Pairs with:**
- **bundles-forge:releasing** — after optimization, versions may need sync
- **bundles-forge:writing-skill** — reference for content modification guidelines
