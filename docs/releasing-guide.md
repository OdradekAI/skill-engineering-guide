# Releasing Guide

[中文](releasing-guide.zh.md)

Comprehensive guide to releasing bundle-plugins with Bundles Forge. Covers the full pipeline from pre-flight checks through publishing, including documentation consistency verification and change coherence review.

## Overview

The release pipeline is designed as a quality gate — not a formality. It ensures that every release is internally consistent, well-documented, and free of known defects. Users should complete all agent, skill, and workflow (plugin) development before starting the release process.

> **Canonical source:** The full execution protocol (prerequisites, pre-flight checks, version bump, publish steps) lives in `skills/releasing/SKILL.md`. This guide helps you understand *the release pipeline* and *what to expect at each phase* — the skill itself handles execution.

| Phase | Steps | Tools | Blocking? |
|-------|-------|-------|-----------|
| Prerequisites | Clean git status, branch check, tag check | `git status`, `git tag -l` | Yes (dirty tree blocks) |
| Pre-flight | Version drift, full audit, documentation consistency | `bundles-forge bump-version`, `bundles-forge audit-plugin`, `bundles-forge audit-docs` | Yes (critical findings block) |
| Address findings | Review and fix critical/warning issues | Manual + `bundles-forge:optimizing` | Yes (critical must resolve) |
| Change Review & Doc Sync | Change coherence review, doc updates | AI review + `bundles-forge audit-docs` | Yes (contradictions block) |
| Version bump | Update all manifests | `bundles-forge bump-version` | — |
| Release Notes | CHANGELOG, README | Manual | — |
| Final verification | Re-run all checks | `bundles-forge bump-version`, `bundles-forge audit-docs` | Yes (must pass) |
| Publish | Commit, tag, push, platform publish | `git`, `gh`, platform CLIs | — |

---

## Before You Start

### Development Must Be Complete

The **releasing** skill is the **release pipeline orchestrator** in the hub-and-spoke model: it sequences diagnostics, remediation, version bumps, and publishing. It does not replace earlier design and implementation work. Before invoking it, ensure:

- All skill content is written and reviewed (`bundles-forge:authoring`)
- Quality issues are on track to resolution. **Releasing** orchestrates **`bundles-forge:auditing`** for diagnostics and directs you to **`bundles-forge:optimizing`** (and authoring as needed) for fixes — **auditing does not automatically route to optimizing**; the release pipeline (or you) decides that sequence.
- Platform adapters are in place (`bundles-forge:scaffolding`)
- All changes are committed — `git status` shows a clean working tree

### Choosing a Version Number

| Change Type | Version Bump | Examples |
|-------------|-------------|---------|
| Breaking changes to skill behavior or structure | **Major** (X.0.0) | Renamed skills, changed workflow chain, removed skills |
| New skills, new platform support, significant improvements | **Minor** (0.X.0) | Added a skill, added Gemini support, new agent |
| Bug fixes, description improvements, doc updates | **Patch** (0.0.X) | Fixed description, updated README, typo fixes |
| Testing a major release before stabilizing | **Pre-release** (X.Y.Z-beta.N) | `2.0.0-beta.1`, `2.0.0-rc.1` |

The bump script accepts any valid semver string — pre-release versions work the same as stable ones across all manifests.

---

## The Pipeline Step by Step

### Step 0: Prerequisites

```bash
# Working tree must be clean
git status

# Verify target tag doesn't exist
git tag -l v<version>

# Check current branch
git branch --show-current
```

| Check | Requirement | If Failed |
|-------|------------|-----------|
| Working tree clean | Hard — pipeline blocked | Commit or stash all changes |
| Target tag free | Soft — warning | Choose a different version number |
| On main branch | Soft — warning | Confirm with user before proceeding |

### Step 1: Pre-flight Checks

Run all automated checks before proceeding:

```bash
# Version drift detection
bundles-forge bump-version <target-dir> --check

# Documentation consistency (9 checks)
bundles-forge audit-docs <target-dir>
```

**Plugin validation (Claude Code only):** If running in a Claude Code environment, run `claude plugin validate` (or `/plugin validate` in a session) to verify `plugin.json` schema, skill/agent/command frontmatter, and `hooks.json` validity. On other platforms, the inspector agent covers equivalent structural checks.

**Full audit:** Invoke `bundles-forge:auditing` (preferred — includes qualitative assessment via auditor subagent with 10-category scoring). Fallback: `bundles-forge audit-plugin .` (automated checks only, no qualitative scoring).

**`bundles-forge audit-docs` checks (D1–D9):**

| Check | What It Verifies |
|-------|-----------------|
| D1 — Skill list sync | `skills/` directory matches CLAUDE.md, AGENTS.md, README.md, README.zh.md |
| D2 — Cross-reference validity | All `bundles-forge:<name>` references point to existing `skills/<name>/` |
| D3 — Platform manifest sync | CLAUDE.md Platform Manifests table matches `.version-bump.json` |
| D4 — Script accuracy | Skill scripts referenced in CLAUDE.md exist at their declared `skills/.../scripts/` paths |
| D5 — Agent list sync | Agents in CLAUDE.md match `agents/` directory |
| D6 — README data sync | Hard data (skill names, commands, links) consistent between README.md and README.zh.md |
| D7 — Guide language sync | Hard data (tables, code blocks, links) consistent between `docs/*.md` and `docs/*.zh.md` |
| D8 — Canonical source declaration | Each `docs/*.md` guide has a `> **Canonical source:**` declaration pointing to an existing skill or agent file |
| D9 — Numeric cross-validation | Key numbers in `docs/*.md` guides match their canonical source (e.g., attack surface count, category count) |

### Step 2: Address Findings

All findings from Step 1 are grouped by severity:

| Severity | Action | Examples |
|----------|--------|---------|
| **Critical** | Must fix before release | Broken cross-references, security vulnerabilities, missing skills |
| **Warning** | Recommend fixing, user decides | Documentation drift, missing table entries |
| **Info** | Note for future | Undocumented scripts, minor inconsistencies |

**Security scan confidence:** Security findings are classified as `deterministic` (matched in executable code — hooks, plugins, scripts) or `suspicious` (matched in natural-language content — SKILL.md, references, agent prompts). Suspicious findings appear in a separate "Needs review" section of the audit report and are excluded from scoring and exit codes. Only deterministic findings block a release.

For quality fixes, invoke `bundles-forge:optimizing` as part of this pipeline. Auditing only surfaces findings; it does not hand off to optimizing automatically — **releasing** (or you) orchestrates that step.

### Step 3: Change Review & Doc Sync

This step combines automated checking with AI judgment.

**Change coherence review:**

Review the diff from the last release to HEAD:

```bash
# Summary of changed files
git diff $(git describe --tags --abbrev=0)..HEAD --stat

# Full diff for review
git diff $(git describe --tags --abbrev=0)..HEAD
```

If no prior tags exist, use `git log --oneline` to identify the scope of changes.

Look for:

| Issue | Example | Severity |
|-------|---------|----------|
| Contradictions | "supports 5 platforms" in one file, "supports 4 platforms" in another | Critical |
| Redundancy | Duplicated paragraphs across two SKILL.md files | Warning |
| Over-engineering | Complex abstraction for a trivial feature | Warning |
| Missing registrations | New skill not added to bootstrap routing, README, AGENTS.md | Critical |
| Stale references | Old skill name used in prose after rename | Critical |

**Documentation update:**

After resolving coherence issues, sync all project documentation:

1. **`docs/`** — Fix outdated references to skills, scripts, architecture
2. **`CLAUDE.md`** — Update skill count, lifecycle flow, commands, agents, manifests
3. **`AGENTS.md`** — Update Available Skills table
4. **`README.md` + `README.zh.md`** — Update Skills table, Agents table, Commands table, code blocks

Re-run `bundles-forge audit-docs` after making changes to confirm consistency.

### Step 4: Version Bump

```bash
bundles-forge bump-version <target-dir> <new-version>
```

This updates all files declared in `.version-bump.json` and runs a post-bump audit to catch any missed files.

### Step 5: Release Notes

**CHANGELOG.md** — Use [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New skill: `bundles-forge:authoring` for skill authoring guidance

### Changed
- Improved descriptions for better triggering accuracy

### Fixed
- Version drift in Cursor manifest
```

**Validation checklist:**
- [ ] Format follows `## [version] - YYYY-MM-DD`
- [ ] Version number matches the bumped version
- [ ] Date is today
- [ ] No duplicate version entries
- [ ] Categories are valid (Added, Changed, Deprecated, Removed, Fixed, Security)

### Step 6: Final Verification

```bash
bundles-forge bump-version <target-dir> --check   # No version drift
bundles-forge bump-version <target-dir> --audit   # No stray version strings
bundles-forge audit-docs <target-dir>             # Documentation consistent
```

All three must exit with code 0 (clean) before publishing.

### Step 7: Publish

**Git + GitHub Release:**

```bash
git add -A
git commit -m "release: v<version>"
git tag v<version>
git push origin main --tags
```

**GitHub Release (recommended):**

```bash
gh release create v<version> --title "v<version>" --notes-file CHANGELOG-EXCERPT.md
```

Generate `CHANGELOG-EXCERPT.md` from the current version's section in CHANGELOG.md. Delete the file after the release is created.

**Platform-specific:**

| Platform | Publishing Method |
|----------|------------------|
| Claude Code | `claude plugin publish` |
| Cursor | Submit via Cursor plugin marketplace |
| Codex | GitHub Release (users pull from git) |
| OpenCode | GitHub Release (users pull from git) |
| Gemini CLI | GitHub Release (users install from git URL) |

---

## Distribution Strategy

Choose how users will install the plugin based on the target audience:

| Strategy | Best For | How |
|----------|----------|-----|
| Marketplace (Claude Code) | Public distribution, widest reach | `claude plugin publish` — users install via `claude plugin install` |
| Project scope | Team tooling shared via git | Install with `--scope project` — config committed to `.claude/settings.json` |
| Local scope | Personal project-specific plugins | Install with `--scope local` — gitignored, per-developer |
| Git-based (Codex, OpenCode, Gemini) | Platforms without marketplaces | Users clone the repo and follow per-platform install docs |
| Development mode | Iterating before publishing | `claude --plugin-dir .` — loads current directory, no caching |

For marketplace distribution, ensure `.claude-plugin/marketplace.json` exists with plugin metadata (including a `plugins.0.version` entry tracked in `.version-bump.json`). For development iteration, use `--plugin-dir .` to bypass caching — changes take effect immediately without version bumps.

---

## Hotfix Releases

For urgent fixes between planned releases:

1. Fix the issue on `main` (or a dedicated hotfix branch)
2. Run abbreviated pipeline:
   - `bundles-forge bump-version --check` (version drift)
   - `bundles-forge audit-security .` (security only)
   - `bundles-forge audit-docs .` (documentation consistency)
3. Bump patch version
4. Update CHANGELOG with `### Fixed` section only
5. Publish

Skip the full audit and change coherence review for hotfixes — speed matters. Run the full audit on the next regular release.

---

## Version Infrastructure Setup

For new projects that don't have version management yet:

1. Create `.version-bump.json` with entries for all version-bearing manifests
2. Verify: `bundles-forge bump-version --check`
3. Audit: `bundles-forge bump-version --audit`

See `bundles-forge:scaffolding` for full project setup including version infrastructure.

---

## Troubleshooting

| Problem | Cause | Fix |
|---------|-------|-----|
| `bundles-forge bump-version --check` finds drift | Manual edit or missed file | Run `bundles-forge bump-version [target-dir] <correct-version>` to re-sync |
| `bundles-forge audit-docs` reports broken cross-refs | Skill renamed without updating references | Find-and-replace old name across all `.md` files |
| `bundles-forge audit-docs` reports skill list mismatch | New skill added but docs not updated | Add skill to AGENTS.md table, README tables, CLAUDE.md |
| Tag already exists | Previous release attempt or version collision | Choose a different version or delete the tag with `git tag -d` |
| `gh release create` fails | `gh` CLI not installed or not authenticated | Install with `gh auth login` or create release manually on GitHub web UI |
| CHANGELOG has wrong format | Missing date, wrong version, invalid category | Follow Keep a Changelog format strictly |
| Releasing from wrong branch | Feature branch instead of main | Merge to main first, or confirm with user that branch release is intentional |
| Released without running audit | Skipped pipeline step — "it's just a small change" | Always run the full pipeline; drift happens in small changes too |
| Tag pushed but no GitHub Release | Only ran `git push --tags` | Use `gh release create` — tags appear on `/tags` but not `/releases` |
| Version bumped before fixing issues | Wrong pipeline order | Fix first, bump second — avoid releasing a known-broken version |
| CHANGELOG not updated | Skipped Step 5 | Users need to know what changed, especially for breaking changes |
| New drift after fixes | Fix introduced new inconsistency | Re-run all checks in Step 6 before publishing |
| `marketplace.json` version stale | Not tracked in `.version-bump.json` | Add entry with `plugins.0.version` field path |
| Manual version edit in manifests | Edited JSON directly instead of using CLI | Always use `bundles-forge bump-version` — it runs a post-bump audit |
| Release from non-main branch unintentionally | Feature branch selected by mistake | Merge to main first, or confirm that branch release is intentional |

---

## Quick Reference

### Commands

```bash
bundles-forge bump-version [target-dir] --check     # Detect version drift
bundles-forge bump-version [target-dir] --audit     # Find undeclared version strings
bundles-forge bump-version [target-dir] <version>   # Bump all manifests
bundles-forge audit-docs <target-dir>               # Documentation consistency check
bundles-forge audit-plugin <target-dir>             # Full quality + security audit
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Clean — no issues found |
| 1 | Warnings — review recommended |
| 2 | Critical — must resolve before release |

### Severity Levels

| Level | Release Impact |
|-------|---------------|
| Critical | **Blocks release** — must fix |
| Warning | **Review** — fix recommended, user decides |
| Info | **Note** — no action required for release |
