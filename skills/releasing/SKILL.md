---
name: releasing
description: "Use when releasing a bundle-plugin, bumping versions, fixing version drift across manifests, setting up version sync infrastructure, updating CHANGELOG, or publishing to marketplaces. Orchestrates the full pre-release verification pipeline"
---

# Releasing Bundle-Plugins

## Overview

Orchestrate the complete release workflow for a bundle-plugin: verify quality, scan for security risks, bump versions, update documentation, and publish to target platforms. This skill also owns version management infrastructure — keeping all platform manifests in sync.

**Core principle:** Release is a checkpoint, not a formality. Every release deserves the full pipeline — even "minor" version bumps can introduce drift or break platform installs.

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
    { "path": ".cursor-plugin/plugin.json", "field": "version" },
    { "path": "gemini-extension.json", "field": "version" }
  ],
  "audit": {
    "exclude": ["CHANGELOG.md", "node_modules", ".git", ".version-bump.json", "scripts/bump-version.sh"]
  }
}
```

Only include entries for platforms the project actually targets.

### `scripts/bump-version.sh`

Three commands (requires `jq` and `bash`):

| Command | What It Does |
|---------|-------------|
| `bump-version.sh 1.2.3` | Update all declared files to new version |
| `bump-version.sh --check` | Detect version drift between files |
| `bump-version.sh --audit` | Check + scan repo for undeclared version strings |

### When to Check Versions

- **After adding a platform** — new manifest needs a `.version-bump.json` entry
- **Before release** — run `--check` to verify sync, `--audit` to catch strays
- **After audit finds drift** — bump to correct version

## Prerequisites

Before starting the release process, confirm:
- The project is a bundle-plugin (has `skills/` directory and `package.json`)
- All skill content changes are committed
- The user knows the target version number (or wants help deciding)

## The Release Pipeline

```
1. Pre-flight checks
   ├── Version drift check (bump-version.sh --check)
   └── Full audit (audit-project.py or bundles-forge:auditing)
         │
2. Address findings
   ├── Fix critical issues (block release until resolved)
   └── Review warnings with user (fix or defer)
         │
3. Version bump
   ├── Determine version (major/minor/patch based on changes)
   └── Run bump-version.sh <new-version>
         │
4. Documentation update
   ├── Update CHANGELOG.md (what changed, migration notes)
   └── Update README.md if needed (new skills, changed workflows)
         │
5. Final verification
   ├── Re-run bump-version.sh --check (confirm no drift)
   └── Re-run bump-version.sh --audit (catch stray version strings)
         │
6. Publish
   ├── Commit all changes
   ├── Tag the release (git tag v<version>)
   └── Publish per platform (see Platform Publishing below)
```

### Step 1: Pre-flight Checks

Run all checks before proceeding. If any critical issues are found, resolve them before continuing.

```bash
# Version drift
scripts/bump-version.sh --check

# Full audit (includes security scan + skill quality)
python scripts/audit-project.py <project-root>
```

If audit score is below 7/10, recommend fixing issues before releasing. If security findings are critical, block the release.

### Step 2: Address Findings

Present findings to the user grouped by severity:
- **Critical** — must fix before release
- **Warning** — recommend fixing, but user decides
- **Info** — note for future, don't block release

For fixes, invoke `bundles-forge:optimizing` for quality issues.

### Step 3: Version Bump

Help the user choose the right version increment:

| Change Type | Version Bump | Example |
|-------------|-------------|---------|
| Breaking changes to skill behavior or structure | Major (X.0.0) | Renamed skills, changed workflow chain |
| New skills, new platform support, significant improvements | Minor (0.X.0) | Added a skill, added Gemini support |
| Bug fixes, description improvements, doc updates | Patch (0.0.X) | Fixed description, updated README |

```bash
scripts/bump-version.sh <new-version>
```

This updates all declared files and runs an audit to catch any missed files.

### Step 4: Documentation Update

**CHANGELOG.md** — Add an entry for the new version using [Keep a Changelog](https://keepachangelog.com/) format:

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New skill: `writing-skill` for skill authoring guidance

### Changed
- Improved descriptions for better triggering accuracy

### Fixed
- Version drift in Cursor manifest
```

**README.md** — Update if the release adds/removes skills, changes the workflow, or adds platform support.

### Step 5: Final Verification

After all changes, re-run verification to confirm nothing broke:

```bash
scripts/bump-version.sh --check   # No drift
scripts/bump-version.sh --audit   # No stray versions
```

### Step 6: Publish

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

Generate `CHANGELOG-EXCERPT.md` from the current version's CHANGELOG.md section (the `## [X.Y.Z]` block written in Step 4). Delete the excerpt file after `gh release create` succeeds. If `gh` CLI is unavailable, instruct the user to create the release manually from the GitHub web UI at `https://github.com/<owner>/<repo>/releases/new?tag=v<version>`.

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
2. Run abbreviated pipeline: version drift check + security scan (skip full audit)
3. Bump patch version
4. Update CHANGELOG with `### Fixed` section
5. Publish

## Version Setup (New Projects)

When setting up version infrastructure for the first time:

1. Create `.version-bump.json` with entries for all version-bearing manifests
2. Create `scripts/bump-version.sh` (from scaffold templates)
3. Make script executable: `chmod +x scripts/bump-version.sh`
4. Run `--check` to verify initial sync
5. Run `--audit` to catch any missed files

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Releasing without running audit | Always run full pipeline — "it's just a small change" is how drift happens |
| Forgetting to tag the release | Tags are how git-based platforms identify versions |
| Only pushing a tag without creating a GitHub Release | Tags appear on `/tags` but not `/releases` — use `gh release create` to publish release notes and notify watchers |
| Bumping version before fixing issues | Fix first, bump second — avoid releasing a known-broken version |
| Skipping CHANGELOG update | Users need to know what changed, especially for breaking changes |
| Not re-verifying after fixes | Changes to fix issues can introduce new drift |
| Forgetting marketplace.json entry | `plugins.0.version` field needs tracking too |
| Manual editing without bump script | Always use the script — it runs audit after |

## Integration

**Calls:**
- **bundles-forge:auditing** — pre-release quality and security check
- **bundles-forge:optimizing** — fix quality findings

**Pairs with:**
- **bundles-forge:scaffolding** — initial version infrastructure setup
- **bundles-forge:adapting-platforms** — new platform support often triggers a release and needs version sync
