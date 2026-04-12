---
name: releasing
description: "Use when releasing a bundle-plugin, bumping versions, fixing version drift across manifests, setting up version sync infrastructure, updating CHANGELOG, or publishing to marketplaces. Orchestrates the full pre-release verification pipeline"
allowed-tools: Python(scripts/bump_version.py *) Python(scripts/audit_project.py *) Python(scripts/check_docs.py *)
---

# Releasing Bundle-Plugins

## Overview

Orchestrate the complete release workflow for a bundle-plugin: verify quality, scan for security risks, check documentation consistency, review change coherence, bump versions, update documentation, and publish to target platforms. This skill also owns version management infrastructure — keeping all platform manifests in sync.

**Core principle:** Release is a checkpoint, not a formality. Every release deserves the full pipeline — even "minor" version bumps can introduce drift or break platform installs. Users should complete all agent, skill, and workflow development before invoking this skill.

**Announce at start:** "I'm using the releasing skill to prepare this project for release."

## Version Management Infrastructure

All platform manifests contain version strings that must stay synchronized. A single drift causes install failures or stale caches.

### `.version-bump.json`

Declares every file and JSON path containing the version:

```json
{
  "files": [
    { "path": "package.json", "field": "version" },
    { "path": ".claude-plugin/plugin.json", "field": "version" },
    { "path": ".claude-plugin/marketplace.json", "field": "plugins.0.version" },
    { "path": ".cursor-plugin/plugin.json", "field": "version" },
    { "path": "gemini-extension.json", "field": "version" }
  ],
  "audit": {
    "exclude": ["CHANGELOG.md", "node_modules", ".git", ".version-bump.json", "scripts/bump_version.py"]
  }
}
```

Only include entries for platforms the project actually targets.

### `scripts/bump_version.py`

Three commands (requires Python 3):

| Command | What It Does |
|---------|-------------|
| `python scripts/bump_version.py 1.2.3` | Update all declared files to new version |
| `python scripts/bump_version.py --check` | Detect version drift between files |
| `python scripts/bump_version.py --audit` | Check + scan repo for undeclared version strings |

### When to Check Versions

- **After adding a platform** — new manifest needs a `.version-bump.json` entry
- **Before release** — run `--check` to verify sync, `--audit` to catch strays
- **After audit finds drift** — bump to correct version

## Prerequisites

Before starting the release process, verify these conditions. Hard requirements block the pipeline; soft requirements trigger warnings.

**Hard requirements (must pass):**
- The project is a bundle-plugin (has `skills/` directory and `package.json`)
- Working tree is clean — `git status` shows no uncommitted or unstaged changes. All development work (agents, skills, workflows) must be committed before releasing.
- The user knows the target version number (or wants help deciding)

**Soft requirements (warn if missing):**
- A recent audit report exists in `.bundles-forge/` — if not, releasing runs a full audit in Step 1
- The current branch is `main` or `master` — if not, warn the user and ask for confirmation before proceeding
- The target version tag does not already exist — run `git tag -l v<version>` to verify

If the working tree is dirty, stop immediately and ask the user to commit or stash changes. Do not proceed with a dirty tree.

## The Release Pipeline

```
0. Prerequisites
   ├── git status clean (hard — blocks pipeline)
   ├── .bundles-forge/ audit report exists (soft — will run audit if missing)
   ├── Branch check (soft — warn if not main)
   └── Tag conflict check (soft — warn if tag exists)
         │
1. Pre-flight checks
   ├── Version drift check (bump_version.py --check)
   ├── Full audit: bundles-forge:auditing (preferred) or audit_project.py (fallback)
   ├── Documentation consistency (check_docs.py)
   ├── Cross-reference validity (check_docs.py)
   └── Git tag conflict check (git tag -l v<version>)
         │
2. Address findings
   ├── Original audit findings + documentation consistency findings
   └── Categorized by severity: Critical / Warning / Info
         │
3. Documentation sync
   ├── AI review of change coherence (tag..HEAD diff)
   │   ├── Contradictions between changed files
   │   ├── Redundant content across skills/docs
   │   ├── Over-engineered abstractions
   │   └── Missing registrations (new skill not in routing, etc.)
   ├── Fix docs/ content if outdated
   ├── Sync CLAUDE.md and AGENTS.md with project state
   └── Sync README.md and README.zh.md
         │
4. Version bump
   └── python scripts/bump_version.py <new-version>
         │
5. Documentation update
   ├── Update CHANGELOG.md (what changed, migration notes)
   ├── Validate CHANGELOG format, version number, date, no duplicates
   └── Update README.md if needed (new skills, changed workflows)
         │
6. Final verification
   ├── Re-run bump_version.py --check (confirm no drift)
   ├── Re-run bump_version.py --audit (catch stray version strings)
   └── Re-run check_docs.py (confirm documentation consistency)
         │
7. Publish
   ├── Commit all changes
   ├── Tag the release (git tag v<version>)
   └── Publish per platform (see Platform Publishing below)
```

### Step 0: Prerequisites

Verify all hard requirements before entering the pipeline.

```bash
# Working tree must be clean
git status

# Check if target tag already exists
git tag -l v<version>

# Check current branch
git branch --show-current
```

If the working tree is dirty, instruct the user to commit all development work first. If the tag already exists, ask the user to choose a different version. If on a non-main branch, warn and ask for confirmation.

### Step 1: Pre-flight Checks

Run all automated checks. If any critical issues are found, resolve them before continuing.

```bash
# Version drift
python scripts/bump_version.py --check

# Documentation consistency (skill lists, cross-refs, manifests, READMEs)
python scripts/check_docs.py <project-root>
```

**Plugin validation (Claude Code only):** If running in a Claude Code environment, run `claude plugin validate` (or `/plugin validate` in a session) to verify `plugin.json` schema, skill/agent/command frontmatter, and `hooks/hooks.json` validity. Skip this step on other platforms — the inspector agent covers equivalent structural checks.

**Full audit:** Invoke `bundles-forge:auditing` (preferred — includes qualitative assessment via auditor subagent with 10-category scoring). Fallback: `python scripts/audit_project.py <project-root>` (automated checks only, no qualitative scoring).

If audit status is FAIL, resolve critical issues before releasing. If security findings are critical, block the release.

### Step 2: Address Findings

Present all findings to the user grouped by severity:
- **Critical** — must fix before release (broken cross-references, missing skills, security issues)
- **Warning** — recommend fixing, but user decides (documentation drift, missing from tables)
- **Info** — note for future, don't block release

For fixes, invoke `bundles-forge:optimizing` for quality issues.

### Step 3: Documentation Sync

This step requires AI judgment — it cannot be fully automated.

**3a. Change coherence review:**

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

**3b. Documentation update:**

After resolving coherence issues, sync project documentation:

1. **`docs/` directory** — Check each document references accurate skill names, script commands, and architecture descriptions. Fix any outdated content.
2. **`CLAUDE.md`** — Verify: skill count in Directory Layout, skill names in Lifecycle Flow, scripts in Commands section, agents in Agent Dispatch, platform manifests table.
3. **`AGENTS.md`** — Verify: Available Skills table matches `skills/` directory.
4. **`README.md` and `README.zh.md`** — Verify: Skills table, Agents table, Commands table, code blocks, and file links are consistent between both files and with the project state.

Use `check_docs.py` output from Step 1 as a guide for what needs updating. After making fixes, re-run `check_docs.py` to confirm all documentation is consistent.

### Step 4: Version Bump

Help the user choose the right version increment:

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| Breaking changes to skill behavior or structure | Major (X.0.0) | Renamed skills, changed workflow chain |
| New skills, new platform support, significant improvements | Minor (0.X.0) | Added a skill, added Gemini support |
| Bug fixes, description improvements, doc updates | Patch (0.0.X) | Fixed description, updated README |
| Testing a major release before stabilizing | Pre-release (X.Y.Z-beta.N) | `2.0.0-beta.1`, `2.0.0-rc.1` |

Pre-release versions follow semver pre-release syntax. The bump script accepts any valid version string — pre-release versions work the same as stable ones across all manifests.

```bash
python scripts/bump_version.py <new-version>
```

This updates all declared files and runs an audit to catch any missed files.

### Step 5: Documentation Update

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

### Step 6: Final Verification

After all changes, re-run verification to confirm nothing broke:

```bash
python scripts/bump_version.py --check   # No drift
python scripts/bump_version.py --audit   # No stray versions
python scripts/check_docs.py .           # Documentation consistent
```

### Step 7: Publish

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

Generate `CHANGELOG-EXCERPT.md` from the current version's CHANGELOG.md section (the `## [X.Y.Z]` block written in Step 5). Delete the excerpt file after `gh release create` succeeds. If `gh` CLI is unavailable, instruct the user to create the release manually from the GitHub web UI at `https://github.com/<owner>/<repo>/releases/new?tag=v<version>`.

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

## Version Setup (New Projects)

When setting up version infrastructure for the first time:

1. Create `.version-bump.json` with entries for all version-bearing manifests
2. Create `scripts/bump_version.py` (from scaffold templates)
3. Run `python scripts/bump_version.py --check` to verify initial sync
4. Run `python scripts/bump_version.py --audit` to catch any missed files

## Distribution Strategy

Choose how users will install the plugin based on the target audience:

| Strategy | Best For | How |
|----------|----------|-----|
| Marketplace (Claude Code) | Public distribution, widest reach | `claude plugin publish` — users install via `claude plugin install` |
| Project scope | Team tooling shared via git | Install with `--scope project` — config committed to `.claude/settings.json` |
| Local scope | Personal project-specific plugins | Install with `--scope local` — gitignored, per-developer |
| Git-based (Codex, OpenCode, Gemini) | Platforms without marketplaces | Users clone the repo and follow per-platform install docs |
| Development mode | Iterating before publishing | `claude --plugin-dir .` — loads current directory, no caching |

For marketplace distribution, ensure `.claude-plugin/marketplace.json` exists with plugin metadata. For development iteration, use `--plugin-dir .` to bypass caching — changes take effect immediately without version bumps.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Releasing with uncommitted changes | Always verify `git status` is clean before starting the pipeline |
| Releasing without running audit | Always run full pipeline — "it's just a small change" is how drift happens |
| Skipping documentation consistency check | `check_docs.py` catches skill list drift, broken cross-refs, README desync |
| Not reviewing changes for coherence | Read the full diff since last tag — contradictions and missing registrations are invisible to automated checks |
| Forgetting to tag the release | Tags are how git-based platforms identify versions |
| Only pushing a tag without creating a GitHub Release | Tags appear on `/tags` but not `/releases` — use `gh release create` to publish release notes and notify watchers |
| Bumping version before fixing issues | Fix first, bump second — avoid releasing a known-broken version |
| Skipping CHANGELOG update | Users need to know what changed, especially for breaking changes |
| Not re-verifying after fixes | Changes to fix issues can introduce new drift |
| Forgetting marketplace.json entry | `plugins.0.version` field needs tracking too |
| Manual editing without bump script | Always use the script — it runs audit after |
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
- **bundles-forge:optimizing** — orchestrate fixes for quality findings
  - Artifact: `project-directory` → `audit-report` (indirect — releasing passes audit findings, optimizing consumes them as `audit-report`)

**Pairs with:**
- **bundles-forge:scaffolding** — version infrastructure setup and platform sync
