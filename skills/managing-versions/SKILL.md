---
name: managing-versions
description: "Use when version drift is detected across manifests in a bundles repository, bumping versions in a bundles repository, setting up version sync infrastructure, auditing for stale version strings, before releasing a bundles repository, or after adding a new platform manifest to a bundles repository"
---

# Managing Skill Versions

## Overview

All platform manifests in a bundles repository contain version strings that must stay synchronized. A single version drift can cause install failures or stale caches. This skill manages the infrastructure that keeps versions in sync.

**Core principle:** One source of truth, automated enforcement. Manual version bumping across 5+ files is error-prone — tooling prevents it.

**Announce at start:** "I'm using the managing-versions skill to handle version sync."

## The Infrastructure

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
    "exclude": [
      "CHANGELOG.md",
      "RELEASE-NOTES.md",
      "node_modules",
      ".git",
      ".version-bump.json",
      "scripts/bump-version.sh"
    ]
  }
}
```

Only include entries for platforms the project actually targets.

### `scripts/bump-version.sh`

Three commands:

| Command | What It Does |
|---------|-------------|
| `bump-version.sh 1.2.3` | Update all declared files to new version |
| `bump-version.sh --check` | Detect version drift between files |
| `bump-version.sh --audit` | Check + scan repo for undeclared version strings |

Requires `jq` and `bash`.

## Operations

### Bumping a Version

```bash
scripts/bump-version.sh 2.0.0
```

This updates all declared files and runs an audit to catch any missed files. Always commit after bumping.

### Detecting Drift

```bash
scripts/bump-version.sh --check
```

If drift is detected, output shows which files have which version. Fix by running a bump to the correct version.

### Full Audit

```bash
scripts/bump-version.sh --audit
```

Finds files containing the version string that aren't declared in `.version-bump.json`. Either add them to `files` or to `audit.exclude`.

## Setup (New Projects)

When setting up version infrastructure for the first time:

1. Create `.version-bump.json` with entries for all version-bearing manifests
2. Create `scripts/bump-version.sh` (from scaffold templates)
3. Make script executable: `chmod +x scripts/bump-version.sh`
4. Run `--check` to verify initial sync
5. Run `--audit` to catch any missed files

## When to Trigger

- **After adding a platform** — new manifest needs a `.version-bump.json` entry
- **Before release** — run `--check` to verify sync, `--audit` to catch strays
- **After audit finds drift** — bump to correct version
- **After scaffold** — verify infrastructure is set up correctly

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Forgetting marketplace.json entry | `plugins.0.version` field needs tracking too |
| Excluding too aggressively | Only exclude files where version string is incidental |
| Manual editing without bump script | Always use the script — it runs audit after |
| Missing audit excludes for docs | CHANGELOG.md, RELEASE-NOTES.md mention old versions |

## Integration

**Pairs with:**
- **bundles-forge:scaffolding** — initial infrastructure setup
- **bundles-forge:auditing** — drift detection during audit
- **bundles-forge:adapting-platforms** — new manifest registration
