---
name: releasing
description: "Use when preparing to release or publish a bundles, bumping to a new version, creating a release checklist, updating CHANGELOG, or publishing to platform marketplaces — orchestrates the full pre-release verification and publishing workflow for bundles"
---

# Releasing Bundles

## Overview

Orchestrate the complete release workflow for a bundles: verify quality, scan for security risks, bump versions, update documentation, and publish to target platforms. Releasing without this process risks shipping broken manifests, version drift, or security vulnerabilities.

**Core principle:** Release is a checkpoint, not a formality. Every release deserves the full pipeline — even "minor" version bumps can introduce drift or break platform installs.

**Announce at start:** "I'm using the releasing skill to prepare this project for release."

## Prerequisites

Before starting the release process, confirm:
- The project is a bundles (has `skills/` directory and `package.json`)
- All skill content changes are committed
- The user knows the target version number (or wants help deciding)

## The Release Pipeline

```
1. Pre-flight checks
   ├── Version drift check (bump-version.sh --check)
   ├── Full audit (audit-project.py or bundles-forge:auditing)
   └── Security scan (scan-security.py or bundles-forge:scanning-security)
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

Run all three checks before proceeding. If any critical issues are found, resolve them before continuing.

```bash
# Version drift
scripts/bump-version.sh --check

# Full audit (includes security + skill quality)
python scripts/audit-project.py <project-root>

# Deep security scan
python scripts/scan-security.py <project-root>
```

If audit score is below 7/10, recommend fixing issues before releasing. If security scan has critical findings, block the release.

### Step 2: Address Findings

Present findings to the user grouped by severity:
- **Critical** — must fix before release
- **Warning** — recommend fixing, but user decides
- **Info** — note for future, don't block release

For fixes, invoke the appropriate skill:
- Quality issues → `bundles-forge:optimizing`
- Security issues → `bundles-forge:scanning-security` for detailed analysis
- Version drift → `bundles-forge:managing-versions`

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

**Git:**
```bash
git add -A
git commit -m "release: v<version>"
git tag v<version>
git push origin main --tags
```

**Platform-specific publishing:**

| Platform | Command |
|----------|---------|
| Claude Code | `claude plugin publish` (if marketplace-ready) |
| Cursor | Submit through Cursor plugin marketplace |
| Codex | Users pull from git — tag is sufficient |
| OpenCode | Users pull from git — tag is sufficient |
| Copilot CLI | `copilot plugin publish` (shares Claude Code infra) |
| Gemini CLI | Users install from git URL — tag is sufficient |

## Hotfix Releases

For urgent fixes between planned releases:

1. Fix the issue on main (or a hotfix branch)
2. Run abbreviated pipeline: security scan + version drift check (skip full audit)
3. Bump patch version
4. Update CHANGELOG with `### Fixed` section
5. Publish

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Releasing without running audit | Always run full pipeline — "it's just a small change" is how drift happens |
| Forgetting to tag the release | Tags are how git-based platforms identify versions |
| Bumping version before fixing issues | Fix first, bump second — avoid releasing a known-broken version |
| Skipping CHANGELOG update | Users need to know what changed, especially for breaking changes |
| Not re-verifying after fixes | Changes to fix issues can introduce new drift |

## Integration

**Calls:**
- **bundles-forge:auditing** — pre-release quality check
- **bundles-forge:scanning-security** — pre-release security scan
- **bundles-forge:managing-versions** — version bump and drift check
- **bundles-forge:optimizing** — fix quality findings

**Pairs with:**
- **bundles-forge:adapting-platforms** — new platform support often triggers a release
