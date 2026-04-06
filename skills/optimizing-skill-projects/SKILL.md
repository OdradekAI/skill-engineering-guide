---
name: optimizing-skill-projects
description: "Use when performing engineering optimization on an existing skill project — improving skill descriptions for better triggering, reducing token usage across skills, optimizing workflow chains between skills, fixing audit findings, enhancing progressive disclosure, adding multi-platform support, or auditing skill/agents/commands folder structure for quality"
---

# Optimizing Skill Projects

## Overview

Targeted improvement of specific aspects of a skill project. Unlike a full audit, optimization focuses on goals: better triggering, lower token cost, tighter workflow chains.

**Core principle:** Optimize for the agent's experience. Every improvement should make skills easier to discover, faster to load, and clearer to follow.

**Announce at start:** "I'm using the optimizing-skill-projects skill to improve your project."

## Optimization Targets

### Script-Assisted Checks

Run the quality linter to identify frontmatter issues, description anti-patterns, and broken references before manual optimization:

```bash
python scripts/lint-skills.py <project-root>        # markdown report
python scripts/lint-skills.py --json <project-root>  # machine-readable
```

The linter automates checks Q1–Q12 and X1–X2 from the skill quality ruleset. Focus manual effort on the subjective targets below.

### 1. Skill Description Triggering

The highest-impact optimization. Descriptions are the primary mechanism for skill discovery.

**Rules:**
- Start with "Use when..." — describe triggering conditions only
- Never summarize the skill's workflow in the description
- Include concrete symptoms, situations, and contexts
- Keep under 500 characters

**Why workflow summaries are harmful:** Testing revealed that when a description summarizes a skill's process, agents follow the description shortcut instead of reading the full SKILL.md. A description saying "code review between tasks" caused agents to do ONE review, even though the skill's flowchart showed TWO reviews.

```yaml
# BAD: Summarizes workflow — agent may follow this instead of reading skill
description: Use for auditing - scans structure, checks manifests, scores categories, generates report

# GOOD: Triggering conditions only — agent reads the full skill
description: Use when reviewing a skill project for structural issues, version drift, or before release
```

**Testing approach:** Create 5+ realistic prompts that should trigger the skill. Verify triggering accuracy.

### 2. Token Efficiency

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

### 3. Progressive Disclosure

Three-level loading system:

| Level | When Loaded | Budget |
|-------|-------------|--------|
| Metadata (name + description) | Always in context | ~100 words |
| SKILL.md body | When skill triggers | < 500 lines |
| Reference files | On demand | Unlimited |

If SKILL.md is approaching 500 lines, extract sections into `references/`.

### 4. Workflow Chain Integrity

| Check | What It Catches |
|-------|----------------|
| Every `project:skill-name` reference resolves | Broken links after renames |
| No circular dependencies | Infinite loops |
| Terminal states are clear | Agent doesn't wonder "what's next?" |
| Integration sections are present | Skills document their place in the chain |

Map the complete chain. Verify every link works.

### 5. Platform Coverage

Identify platforms the project doesn't yet support. For adding new platforms, invoke `seg:adapting-skill-platforms`.

### 6. Security Remediation

Fix security findings from `seg:scanning-skill-security` or audit Category 9.

**Targets:**
- Remove unnecessary system access from hook scripts (least privilege)
- Scope OpenCode plugin capabilities to declared needs only
- Remove or justify any network calls in hooks/plugins
- Ensure agent prompts include scope constraints
- Strip encoding tricks or obfuscated content from SKILL.md files

**Process:** Run a security scan first, then address findings by priority — critical before warnings, warnings before info.

## Process

1. **Identify target** — what specifically needs improvement?
2. **Measure current state** — how does it perform now?
3. **Apply improvement** — make the change
4. **Verify** — did it actually improve?

For description optimization specifically: create test prompts, verify triggering before and after.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Optimizing everything at once | Pick one target, measure, improve, verify |
| Adding MUST/ALWAYS/NEVER instead of explaining why | Explain the reasoning — agents respond to understanding |
| Splitting skills too aggressively | Only split when there's a genuine responsibility boundary |
| Ignoring token budget for bootstrap | Bootstrap loads every session — every word counts |

## Integration

**Called by:**
- **seg:auditing-skill-projects** — when audit finds optimization opportunities

**Pairs with:**
- **seg:managing-skill-versions** — after optimization, versions may need sync
- **seg:scanning-skill-security** — security findings feed into remediation
