---
name: releasing
description: "Use when releasing a bundle-plugin, bumping versions, fixing version drift across manifests, setting up version sync infrastructure, updating CHANGELOG, publishing to marketplaces, or checking release readiness"
allowed-tools: Bash(bundles-forge bump-version *) Bash(bundles-forge audit-plugin *) Bash(bundles-forge audit-docs *)
---

# Releasing Bundle-Plugins

## Overview

Orchestrate the complete release workflow for a bundle-plugin: verify quality, scan for security risks, check documentation consistency, review change coherence, test locally, bump versions, update documentation, and publish to target platforms.

**Core principle:** Release is a checkpoint, not a formality. Every release deserves the full pipeline — even "minor" version bumps can introduce drift or break platform installs. Users should complete all agent, skill, and workflow development before invoking this skill.

**Skill type: Rigid** — follow every step exactly. Releases have no room for improvisation.

For version management infrastructure details (`.version-bump.json` schema, script usage, version setup for new projects), read `references/version-infrastructure.md`. For distribution strategy options, read `references/distribution-strategy.md`.

**Announce at start:** "I'm using the releasing skill to prepare this project for release."

## Entry Detection

| Context | Path |
|---------|------|
| User wants to release a version, provides a project directory | **Path 1: Standard release** — run the full pipeline below |
| Urgent fix with small changes | **Path 2: Hotfix release** — run the abbreviated pipeline (see Hotfix Releases) |
| Project needs version infrastructure for the first time | **Path 3: Version setup** — read `references/version-infrastructure.md` § Version Setup |

## The Release Pipeline

```
0. Prerequisites  →  1. Pre-flight Checks  →  2. Address Findings
→  3. Change Review & Doc Sync  →  4. Local Testing
→  5. Version Bump  →  6. Release Notes
→  7. Final Verification  →  8. Publish
```

### Step 0: Prerequisites

Verify all conditions before entering the pipeline. Hard requirements block the pipeline; soft requirements trigger warnings.

**Hard requirements (must pass):**
- The project is a bundle-plugin (has `skills/` directory and `package.json`)
- Working tree is clean — `git status` shows no uncommitted or unstaged changes. All development work (agents, skills, workflows) must be committed before releasing.
- The user knows the target version number (or wants help deciding)

**Soft requirements (warn if missing):**
- A recent audit report exists in `.bundles-forge/audits/` — if not, releasing runs a full audit in Step 1
- The current branch is `main` or `master` — if not, warn the user and ask for confirmation before proceeding
- The target version tag does not already exist — run `git tag -l v<version>` to verify

```bash
git status
git tag -l v<version>
git branch --show-current
```

If the working tree is dirty, instruct the user to commit all development work first. If the tag already exists, ask the user to choose a different version. If on a non-main branch, warn and ask for confirmation.

### Step 1: Pre-flight Checks

Run all automated checks. If any critical issues are found, resolve them before continuing.

```bash
bundles-forge bump-version <target-dir> --check
bundles-forge audit-docs <target-dir>
```

**Plugin validation (Claude Code only):** If running in a Claude Code environment, run `claude plugin validate` (or `/plugin validate` in a session) to verify `plugin.json` schema, skill/agent/command frontmatter, and `hooks/hooks.json` validity. Skip this step on other platforms — the inspector agent covers equivalent structural checks.

**Full audit:** Invoke `bundles-forge:auditing` (preferred — includes qualitative assessment via auditor subagent with 10-category scoring). Fallback: `bundles-forge audit-plugin <target-dir>` (automated checks only, no qualitative scoring).

If audit status is FAIL, resolve critical issues before releasing. If security findings are critical, block the release.

### Step 2: Address Findings

Present all findings to the user grouped by severity:
- **Critical** — must fix before release (broken cross-references, missing skills, security issues)
- **Warning** — recommend fixing, but user decides (documentation drift, missing from tables)
- **Info** — note for future, don't block release

For fixes, invoke `bundles-forge:optimizing` for quality issues.

### Step 3: Change Review & Doc Sync

This step requires AI judgment — it cannot be fully automated.

**Change coherence review:**

Read the diff from the last release tag to HEAD:

```bash
git diff $(git describe --tags --abbrev=0)..HEAD --stat
git diff $(git describe --tags --abbrev=0)..HEAD
```

If no prior tags exist, use `git log --oneline` to identify the scope of changes.

Review all changed files for:

| Check | What to Look For | Severity |
|-------|-----------------|----------|
| Contradictions | File A says "supports 5 platforms", file B says "supports 4 platforms" | Critical |
| Redundancy | Two SKILL.md files with large duplicated sections | Warning |
| Over-engineering | Complex abstraction for a simple feature, unnecessary indirection layers | Warning |
| Missing registrations | New skill added but not in bootstrap routing, AGENTS.md, or README tables | Critical |
| Stale references | Renamed skill but old name still used in prose | Critical |

Present findings as a blocking report using the same Critical/Warning/Info severity model as Step 2. Critical items must be resolved before proceeding.

**Documentation update:**

After resolving coherence issues, sync project documentation:

1. **`docs/` directory** — Check each document references accurate skill names, script commands, and architecture descriptions. Fix any outdated content.
2. **`CLAUDE.md`** — Verify: skill count in Directory Layout, skill names in Lifecycle Flow, scripts in Commands section, agents in Agent Dispatch, platform manifests table.
3. **`AGENTS.md`** — Verify: Available Skills table matches `skills/` directory.
4. **`README.md` and `README.zh.md`** — Verify: Skills table, Agents table, Commands table, code blocks, and file links are consistent between both files and with the project state.

Use `bundles-forge audit-docs` output from Step 1 as a guide for what needs updating. After making fixes, re-run `bundles-forge audit-docs` to confirm all documentation is consistent.

### Step 4: Local Testing

Before bumping the version, invoke `bundles-forge:testing` to verify the plugin works correctly in a real installation scenario:

1. Generate a dev-marketplace and install the plugin locally
2. Verify hook smoke tests pass (SessionStart + any custom hooks)
3. Confirm all components (skills, commands, agents) are discoverable
4. Run cross-platform readiness checks for all target platforms

If testing reveals critical issues, resolve them before proceeding to version bump.

For abbreviated hotfix releases, this step may be reduced to hook smoke tests only.

### Step 5: Version Bump

Help the user choose the right version increment:

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| Breaking changes to skill behavior or structure | Major (X.0.0) | Renamed skills, changed workflow chain |
| New skills, new platform support, significant improvements | Minor (0.X.0) | Added a skill, added Gemini support |
| Bug fixes, description improvements, doc updates | Patch (0.0.X) | Fixed description, updated README |
| Testing a major release before stabilizing | Pre-release (X.Y.Z-beta.N) | `2.0.0-beta.1`, `2.0.0-rc.1` |

Pre-release versions follow semver pre-release syntax. The bump script accepts any valid version string — pre-release versions work the same as stable ones across all manifests.

```bash
bundles-forge bump-version <target-dir> <new-version>
```

This updates all declared files and runs an audit to catch any missed files. For the full command reference, read `references/version-infrastructure.md`.

### Step 6: Release Notes

**CHANGELOG.md** — Add an entry for the new version using [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New skill: `bundles-forge:authoring` for skill authoring guidance

### Changed
- Improved descriptions for better triggering accuracy

### Fixed
- Version drift in Cursor manifest
```

**CHANGELOG validation** — After writing the entry, verify:
- Format follows Keep a Changelog (## [version] - date)
- Version number matches the bumped version
- Date is today's date (YYYY-MM-DD)
- No duplicate version entries exist in the file
- Categories are valid (Added, Changed, Deprecated, Removed, Fixed, Security)

**README.md** — Update if the release adds/removes skills, changes the workflow, or adds platform support.

### Step 7: Final Verification

After all changes, re-run verification to confirm nothing broke:

```bash
bundles-forge bump-version <target-dir> --check
bundles-forge bump-version <target-dir> --audit
bundles-forge audit-docs <target-dir>
```

### Step 8: Publish

**Git + GitHub Release:**
```bash
git add -A
git commit -m "release: v<version>"
git tag v<version>
git push origin main --tags
```

After pushing the tag, create a GitHub Release so the `/releases` page has release notes and notifies watchers:

```bash
gh release create v<version> --title "v<version>" --notes-file CHANGELOG-EXCERPT.md
```

Generate `CHANGELOG-EXCERPT.md` from the current version's CHANGELOG.md section (the `## [X.Y.Z]` block written in Step 6). Delete the excerpt file after `gh release create` succeeds. If `gh` CLI is unavailable, instruct the user to create the release manually from the GitHub web UI at `https://github.com/<owner>/<repo>/releases/new?tag=v<version>`.

**Platform-specific publishing:**

| Platform | Command |
|----------|---------|
| Claude Code | `claude plugin publish` (if marketplace-ready) |
| Cursor | Submit through Cursor plugin marketplace |
| Codex | Users pull from git — GitHub Release is sufficient |
| OpenCode | Users pull from git — GitHub Release is sufficient |
| Gemini CLI | Users install from git URL — GitHub Release is sufficient |

## Hotfix Releases

For urgent fixes between planned releases:

1. Fix the issue on main (or a hotfix branch)
2. Run abbreviated pipeline: version drift check + security scan + documentation consistency check (skip full audit)
3. Bump patch version
4. Update CHANGELOG with `### Fixed` section
5. Publish

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Releasing with uncommitted changes | Always verify `git status` is clean before starting the pipeline |
| Releasing without running audit | Always run full pipeline — "it's just a small change" is how drift happens |
| Skipping documentation consistency check | `bundles-forge audit-docs` catches skill list drift, broken cross-refs, README desync |
| Not reviewing changes for coherence | Read the full diff since last tag — contradictions and missing registrations are invisible to automated checks |
| Forgetting to tag the release | Tags are how git-based platforms identify versions |
| Only pushing a tag without creating a GitHub Release | Tags appear on `/tags` but not `/releases` — use `gh release create` to publish release notes and notify watchers |
| Bumping version before fixing issues | Fix first, bump second — avoid releasing a known-broken version |
| Skipping CHANGELOG update | Users need to know what changed, especially for breaking changes |
| Not re-verifying after fixes | Changes to fix issues can introduce new drift |
| Forgetting marketplace.json entry | `plugins.0.version` field needs tracking too |
| Manual editing without bump command | Always use `bundles-forge bump-version` — it runs audit after |
| Releasing from non-main branch without awareness | Not blocked, but should be an explicit decision |

## Inputs

- `project-directory` (required) — bundle-plugin project root with committed skill content ready for release

## Outputs

- `version-tag` — git tag (`v<version>`) for the release
- `changelog-entry` — CHANGELOG.md update with categorized changes (Added, Changed, Fixed)
- `github-release` (optional) — GitHub Release with release notes, created via `gh release create`

## Integration

**Calls:**
- **bundles-forge:auditing** — pre-release quality and security diagnostics
  - Artifact: `project-directory` → `project-directory` (direct match — releasing passes the project root for audit)
- **bundles-forge:testing** — pre-release dynamic verification (after audit, before version bump)
  - Artifact: `project-directory` → `project-directory` (direct match)
- **bundles-forge:optimizing** — orchestrate fixes for quality findings
  - Artifact: `project-directory` → `audit-report` (indirect — releasing passes audit findings, optimizing consumes them as `audit-report`)

**Pairs with:**
- **bundles-forge:scaffolding** — version infrastructure setup and platform sync
