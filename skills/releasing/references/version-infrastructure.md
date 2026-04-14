# Version Management Infrastructure

All platform manifests contain version strings that must stay synchronized. A single drift causes install failures or stale caches.

## `.version-bump.json`

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
    "exclude": [
      "CHANGELOG.md",
      "RELEASE-NOTES.md",
      "node_modules",
      ".git",
      ".repos",
      ".version-bump.json",
      "skills/releasing/scripts/bump_version.py"
    ]
  }
}
```

Only include entries for platforms the project actually targets. The script automatically excludes `.git` and `node_modules` during audit scans — listing them in `audit.exclude` is harmless but not required.

## `skills/releasing/scripts/bump_version.py`

Version synchronization tool (requires Python 3):

| Command | What It Does |
|---------|-------------|
| `bump_version.py [project-root] <new-version>` | Update all declared files to new version |
| `bump_version.py [project-root] <new-version> --dry-run` | Preview version bump without writing files |
| `bump_version.py [project-root] --check` | Detect version drift between files |
| `bump_version.py [project-root] --audit` | Check + scan repo for undeclared version strings |

`[project-root]` defaults to the current directory if omitted. Version accepts `X.Y.Z` or pre-release forms like `X.Y.Z-beta.1`.

## When to Check Versions

- **After adding a platform** — new manifest needs a `.version-bump.json` entry
- **Before release** — run `--check` to verify sync, `--audit` to catch strays
- **After audit finds drift** — bump to correct version

## Version Setup (New Projects)

When setting up version infrastructure for the first time:

1. Create `.version-bump.json` with entries for all version-bearing manifests
2. Create `skills/releasing/scripts/bump_version.py` (from scaffold templates)
3. Run `bump_version.py --check` to verify initial sync
4. Run `bump_version.py --audit` to catch any missed files
