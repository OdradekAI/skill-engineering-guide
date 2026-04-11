# Optimizing Guide

[中文](optimizing-guide.zh.md)

A user-oriented guide to optimizing bundle-plugins and individual skills with Bundles Forge. Covers scope detection, the 6 optimization targets, A/B evaluation, feedback iteration, and the audit-optimize cycle.

## Overview

Optimizing is the iterative improvement skill. Unlike auditing (which assesses), optimizing takes action — fixing descriptions, reducing tokens, tightening workflow chains, and processing user feedback.

**Core principle:** Optimize for the agent's experience. Every improvement should make skills easier to discover, faster to load, and clearer to follow.

> **Canonical source:** The full execution protocol (scope detection, target details, A/B eval steps, feedback validation) lives in `skills/optimizing/SKILL.md`. This guide helps you understand *what each target does*, *how to interpret results*, and *when to use which approach*.

---

## Scope Detection

Optimizing auto-detects whether you're working on a full project or a single skill:

| Target | Detection | Mode | Targets |
|--------|----------|------|---------|
| Project root | Has `skills/` + `package.json` | Project optimization | All 6 targets |
| Single skill directory | Has `SKILL.md`, no `skills/` subdirectory | Skill optimization | 4 targets + feedback |

You don't need to specify the mode — the skill detects it from the path you provide.

### Input Sources

Optimizing can consume reports from prior audits. This is the recommended workflow — audit first, then optimize based on findings:

| Input | Source | Use |
|-------|--------|-----|
| `audit-report` | `bundles-forge:auditing` (full project) | Per-skill breakdowns for all 6 targets |
| `skill-report` | `bundles-forge:auditing` (skill mode) | Focused 4-category report for skill optimization |
| `workflow-report` | `bundles-forge:auditing` (workflow mode) | W1-W12 findings for Target 4 |
| `user-feedback` | Direct from user | Behavioral feedback for the iteration process |

---

## The 6 Optimization Targets

### Target 1: Skill Description Triggering

**The highest-impact optimization.** Descriptions are the primary mechanism for skill discovery — when a user says something, the agent matches intent against description fields.

**The critical rule:** Descriptions must state *triggering conditions*, not *workflow summaries*.

| | Bad (workflow summary) | Good (triggering conditions) |
|---|---|---|
| **Pattern** | "Use for auditing — scans structure, checks manifests, scores categories, generates report" | "Use when reviewing a bundle-plugin for structural issues, version drift, or before release" |
| **Problem** | Agent follows the description shortcut instead of reading the full SKILL.md | Agent reads the full skill for execution details |
| **Result** | Skipped steps, incomplete execution | Full execution as designed |

**Additional rules:**
- Always start with "Use when..."
- Keep under 250 characters (truncated in skill listings beyond this)
- Include concrete symptoms, situations, and contexts
- Never mention the skill's internal steps

#### How to Verify Description Quality

Run the linter to catch mechanical issues:

```bash
python scripts/lint_skills.py <project-root>
```

Checks Q1-Q12 cover description format, length, and anti-patterns. For *behavioral* quality (does the right prompt trigger the right skill?), use A/B eval.

### Target 2: Token Efficiency

Every token in a frequently-loaded skill costs context budget across every session. This matters most for the bootstrap skill (loaded every session) and commonly-triggered skills.

**Targets:**
- SKILL.md body < 500 lines
- Bootstrap skill (`using-*`) < 200 lines
- Move heavy reference material to `references/`

**Techniques:**

| Technique | Example |
|-----------|---------|
| Cross-reference instead of repeating | `See bundles-forge:authoring` instead of duplicating rules |
| One excellent example over three mediocre | Remove redundant examples that teach the same concept |
| Move flag docs to --help | Reference `python scripts/lint_skills.py --help` instead of listing all flags |
| Eliminate intra-project redundancy | Don't repeat what's in another skill's `references/` |

### Target 3: Progressive Disclosure

The three-level loading system ensures minimal context usage:

| Level | When Loaded | Budget |
|-------|-------------|--------|
| Metadata (name + description) | Always in context | ~100 words |
| SKILL.md body | When skill triggers | < 500 lines |
| Reference files (`references/`) | On demand | Unlimited |

**When to extract to references/:**
- SKILL.md approaching 500 lines
- Tables or checklists that are only needed during execution (not for understanding the skill's purpose)
- Template content that the agent copies verbatim

### Target 4: Workflow Chain Integrity

Consumes W1-W12 findings from the workflow audit. If no workflow report is available:

```bash
python scripts/audit_workflow.py <project-root>
python scripts/audit_workflow.py --focus-skills skill-a,skill-b <root>
```

**Fix priority guide:**

| Finding | What It Means | How to Fix |
|---------|--------------|-----------|
| W1 (undeclared cycle) | Two skills call each other but the loop isn't declared | Add `<!-- cycle:a,b -->` in `## Integration` if intentional, or restructure |
| W2 (unreachable skill) | Skill exists but nothing chains to it | Add to bootstrap routing, or declare `Called by: user directly` |
| W3/W4 (missing I/O) | Terminal skill has no `## Outputs`, or referenced skill has no `## Inputs` | Add the section with artifact IDs |
| W5 (artifact ID mismatch) | Upstream `## Outputs` and downstream `## Inputs` use different names | Align the backtick artifact IDs |
| W9 (placeholder sections) | Inputs/Outputs exist but are empty or generic | Write meaningful semantic descriptions |
| W10 (asymmetric integration) | Skill A says it calls B, but B doesn't say it's called by A | Add the missing `**Called by:**` declaration |

### Target 5: Platform Coverage (project only)

Identify platforms the project doesn't yet support. For adding new platforms, invoke `bundles-forge:porting` — optimizing doesn't generate platform adapters itself.

### Target 6: Security Remediation (project only)

Fix security findings from `bundles-forge:auditing` Category 10. Common fixes:

| Finding | Fix |
|---------|-----|
| Hook script makes network calls | Remove or justify with comments |
| OpenCode plugin has excessive capabilities | Scope to declared needs |
| Agent prompt lacks scope constraints | Add explicit boundaries |
| SKILL.md contains encoded/obfuscated content | Strip or replace with plain text |

---

## A/B Evaluation

A/B eval is the core quality assurance mechanism for description changes and feedback-driven improvements. It compares original vs optimized versions side-by-side.

### How It Works

```
1. Copy the skill to a working version (<skill-name>-optimized/)
2. Apply changes to the copy only (never overwrite the original first)
3. Create 5+ realistic test prompts that should trigger this skill
4. Dispatch two evaluator agents in parallel:
   - Evaluator A: "original" label → test with original skill
   - Evaluator B: "optimized" label → test with optimized skill
5. Compare results → present to user
6. User decides: adopt optimized version or discard
```

### What to Compare

| Metric | What It Tells You |
|--------|------------------|
| **Trigger rate** | How many prompts correctly activated the skill? |
| **False negatives** | Did the optimized description miss cases the original caught? |
| **False positives** | Did either version trigger on prompts meant for other skills? |
| **Step accuracy** | Did the agent follow all steps, or take shortcuts? |

### When to Skip A/B

| Situation | Skip? | Rationale |
|-----------|:---:|-----------|
| Purely additive change (new trigger phrases, no modifications) | Yes | Simple verification pass is sufficient |
| Structural fix (missing section, broken reference) | Yes | Not a behavioral change |
| Description rewrite changing existing triggers | **No** | Must verify no regressions |
| Feedback-driven behavior change | **No** | Must compare old vs new behavior |

### Chain A/B Eval

For workflow transitions (not individual descriptions), use chain evaluation:

1. Define a realistic end-to-end scenario
2. Dispatch evaluator with "chain" label and ordered skill list
3. Review transition quality ratings at each handoff
4. Focus on "broken" handoffs — these indicate missing artifacts or unclear instructions

**Use chain eval after:** modifying Inputs/Outputs, adding skills to a chain, or when W1-W12 findings indicate workflow issues.

### Subagent Fallback

When subagent dispatch is unavailable, two options:

| Fallback | How | Trade-off |
|----------|-----|-----------|
| Sequential inline | Follow `agents/evaluator.md` protocol inline, randomize order | Slower, possible ordering bias |
| Skip A/B | Apply change directly with simple verification | Faster, no comparison data |

The user chooses which fallback to use.

---

## Feedback Iteration

When a user reports that a skill triggered but produced wrong results, the feedback process provides structured iteration.

### Feedback Classification

| User Says | Action |
|-----------|--------|
| "This skill triggered but produced wrong results" | Feedback iteration |
| "The steps are in the wrong order" | Feedback iteration |
| "Description format doesn't follow conventions" | Optimization targets 1-3 |
| "Token budget exceeded across the project" | Optimization targets 2-3 (project mode) |

### The 3-Question Validation Framework

Before applying any feedback, each item goes through validation:

| Question | Purpose | Red Flag |
|----------|---------|----------|
| **Goal alignment:** Does this serve the skill's core goal? | Prevents scope drift | "This would turn the skill into something different" |
| **Necessity:** Is there an actual defect, or just a style preference? | Prevents unnecessary churn | "The skill works fine, I just prefer a different format" |
| **Side effects:** Could this introduce complexity or regression? | Prevents creep | "This adds 50 lines to handle a rare edge case" |

### Feedback Process Flow

```
Receive feedback
  → Identify target skill
  → If external skill: fork with forked- prefix
  → Read skill, understand core goal
  → Validate each item (3-question framework)
  → Present improvement plan → USER CONFIRMS
  → Copy to working version
  → Apply changes to copy
  → A/B eval (original vs optimized)
  → User decides: adopt or discard
  → Run auditing for post-change verification
```

**Rules:**
- Never apply feedback without user confirmation
- For external skills, always fork first (add provenance header)
- Only one audit cycle after changes (no loops)

---

## The Audit-Optimize Cycle

Optimizing and auditing form a deliberate cycle:

```
auditing finds issues → optimizing fixes them → auditing verifies fixes
                                                  ↑ stop here (one cycle)
```

**Important:** The cycle runs exactly once. If the re-audit still has issues, present them to the user for manual decision — do not loop indefinitely.

### Recommended Workflow

1. Run `bundles-forge:auditing` (full, skill, or workflow mode)
2. Review the report — prioritize critical findings
3. Run `bundles-forge:optimizing` with the audit report as input
4. After fixes, auditing runs automatically for verification
5. Review the verification report — if issues remain, decide manually

---

## Quick Reference

### Scripts

```bash
python scripts/lint_skills.py <path>                    # Quality lint (Q1-Q17, X1-X3)
python scripts/audit_workflow.py <path>                  # Workflow audit (W1-W12)
python scripts/audit_workflow.py --focus-skills a,b <path>  # Focused workflow audit
```

### Target Applicability by Scope

| Target | Project | Skill |
|--------|:---:|:---:|
| 1. Description Triggering | Full | Full |
| 2. Token Efficiency | Full | Full |
| 3. Progressive Disclosure | Full | Full |
| 4. Workflow Chain Integrity | Full | Partial (W9/W10 only) |
| 5. Platform Coverage | Full | Skip |
| 6. Security Remediation | Full | Partial |
| Feedback Iteration | Full | Full |
