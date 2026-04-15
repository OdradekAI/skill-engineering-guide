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
      ".version-bump.json"
    ]
  }
}
```

Only include entries for platforms the project actually targets. The script automatically excludes `.git` and `node_modules` during audit scans — listing them in `audit.exclude` is harmless but not required.

## Version Bump CLI

Version synchronization is provided by the `bundles-forge` CLI (requires Python 3):

| Command | What It Does |
|---------|-------------|
| `bundles-forge bump-version <new-version>` | Update all declared files to new version |
| `bundles-forge bump-version <new-version> --dry-run` | Preview version bump without writing files |
| `bundles-forge bump-version --check` | Detect version drift between files |
| `bundles-forge bump-version --audit` | Check + scan repo for undeclared version strings |

Run from the target project directory, or pass the project root as the first positional argument. Version accepts `X.Y.Z` or pre-release forms like `X.Y.Z-beta.1`.

## When to Check Versions

- **After adding a platform** — new manifest needs a `.version-bump.json` entry
- **Before release** — run `--check` to verify sync, `--audit` to catch strays
- **After audit finds drift** — bump to correct version

## Version Setup (New Projects)

When setting up version infrastructure for the first time:

1. Create `.version-bump.json` with entries for all version-bearing manifests
2. Run `bundles-forge bump-version --check` to verify initial sync
3. Run `bundles-forge bump-version --audit` to catch any missed files
