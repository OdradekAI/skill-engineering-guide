# Authoring Quality Checklist

> **Canonical source** for check IDs and severity levels: `bundles-forge:auditing` — `references/audit-checks.json`. This checklist adds authoring-oriented Self-Check guidance.

Definitive quality specification for SKILL.md files. `bundles-forge audit-skill` automates these checks. Use during authoring to catch issues before running the linter, or to investigate specific lint findings.

## Frontmatter Checks

| Check | Severity | Rule | Self-Check |
|-------|----------|------|------------|
| Q1 | Critical | SKILL.md must have YAML frontmatter (`---` delimiters) | Open the file — first line must be `---` |
| Q2 | Critical | `name` field must exist in frontmatter | Verify `name:` is present between `---` markers |
| Q3 | Critical | `description` field must exist in frontmatter | Verify `description:` is present between `---` markers |
| Q4 | Warning | `name` must be kebab-case (lowercase, hyphens, numbers) | Check: no uppercase, no underscores, no spaces |
| Q5 | Warning | `description` should start with "Use when..." | Read the first words of the description |
| Q6 | Warning | `description` must not summarize workflow (anti-pattern) | Look for verb chains: "scans, checks, generates" or "first...then...finally" |
| Q7 | Warning | `description` must be under 250 characters | Count characters (descriptions over 250 are truncated in skill listings) |
| Q8 | Warning | Total frontmatter must be under 1024 characters | Keep frontmatter lean — large `allowed-tools` lists can push over budget |

## Body Checks

| Check | Severity | Rule | Self-Check |
|-------|----------|------|------------|
| Q9 | Warning | SKILL.md body should be under 500 lines | Count body lines (below second `---` marker) |
| Q10 | Info | Should have `## Overview` section | Search for the heading (skipped for bootstrap `using-*` skills) |
| Q11 | Info | Should have `## Common Mistakes` section | Search for the heading (skipped for bootstrap `using-*` skills) |
| Q12 | Info | Body over 300 lines should have `references/` files | If body is long, check whether a `references/` directory exists with content |
| Q13 | Warning/Info | Token budget: bootstrap body over 200 lines (warning); regular skill high token count (info) | Estimate tokens: prose ~1.3 tokens/word, code ~1 token/3.5 chars, tables ~1 token/3 chars |
| Q14 | Warning | `allowed-tools` paths must exist in project | Verify that referenced scripts (e.g. `skills/**/scripts/*.py`) actually exist |
| Q15 | Info | Large conditional blocks (30+ lines) should be in `references/` | Check "If...unavailable" guarded sections for excessive length |

## Cross-Reference Checks

| Check | Severity | Rule | Self-Check |
|-------|----------|------|------------|
| X1 | Warning | `project:skill-name` cross-references must resolve | For each backtick cross-ref, verify `skills/<skill-name>/` directory exists |
| X2 | Warning | Relative path references must exist | For each backtick path like `references/foo.md`, verify the file exists in the skill directory or project root |
| X3 | Warning | Referenced subdirectories must exist | If text says "in `references/`" or "under `assets/`", the directory must exist (except in instructional context like "extract to `references/`") |

## Directory Name Check

| Check | Severity | Rule | Self-Check |
|-------|----------|------|------------|
| S9 | Info | Directory name should match frontmatter `name` | Compare `skills/<dirname>/` with the `name:` field value |

## Quick Validation Command

```bash
bundles-forge audit-skill <skill-directory>          # single skill
bundles-forge audit-skill <target-dir>             # all skills
bundles-forge audit-skill --json <target-dir>      # machine-readable
```

## Interpreting Results

- **Critical** findings (Q1-Q3) mean the skill won't be discovered by agents — fix immediately
- **Warning** findings (Q4-Q9, Q13 bootstrap, Q14, X1-X3) mean the skill works but has quality issues — fix before delivery
- **Info** findings (Q10-Q12, Q13 regular, Q15, S9) are improvement opportunities — address if time permits, report otherwise
