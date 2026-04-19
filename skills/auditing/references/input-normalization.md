# Input Normalization

> **Canonical source** for input normalization across all skills that accept external targets.

The target can be a local path, a GitHub URL, or a zip file. Normalize to a local directory, then proceed with the skill's work.

## Workspace Resolution

The **workspace** is the directory where all `.bundles-forge/` outputs are written. Resolve it as:

1. `$CLAUDE_PROJECT_DIR` or `$CURSOR_PROJECT_DIR` (plugin mode — whichever is set)
2. Current working directory (direct invocation fallback)

All generated artifacts — reports, eval results, downloaded repos — go under `<workspace>/.bundles-forge/`.

## Output Directory Structure

```
<workspace>/.bundles-forge/
├── audits/        # Audit reports (full/skill/workflow) + script JSON baselines
├── evals/         # A/B eval + chain eval results (evaluator agent)
├── blueprints/    # Design documents (blueprinting) + inspection reports (inspector agent)
└── repos/         # Cloned/extracted external targets (GitHub URLs, zip/tar.gz archives)
```

Skills and agents write to the appropriate subdirectory based on artifact type. Create the subdirectory if it does not exist.

## Input Normalization Table

| Input | Action | Read from | Reports written to |
|-------|--------|-----------|-------------------|
| Local directory path | Use directly | Target path | `<workspace>/.bundles-forge/audits/` |
| Local SKILL.md file path | Use its parent directory | Parent of target | `<workspace>/.bundles-forge/audits/` |
| GitHub repo URL (`https://github.com/user/repo`) | `git clone --depth 1 --no-checkout` to `<workspace>/.bundles-forge/repos/<owner>__<repo>/`, then `git checkout` | Clone directory | `<workspace>/.bundles-forge/audits/` |
| GitHub subdirectory URL (`…/tree/main/skills/xxx`) | Clone repo (shallow) to `repos/`, extract the subdirectory path | Subdirectory within clone | `<workspace>/.bundles-forge/audits/` |
| Zip/tar.gz file path | Extract to `<workspace>/.bundles-forge/repos/<archive-name>/` | Extracted directory | `<workspace>/.bundles-forge/audits/` |
| GitHub release/archive URL (`.zip`/`.tar.gz`) | Download and extract to `<workspace>/.bundles-forge/repos/<owner>__<repo>/` | Extracted directory | `<workspace>/.bundles-forge/audits/` |

### repos/ Naming Convention

Directories under `.bundles-forge/repos/` follow this naming scheme:

| Source | Directory name | Example |
|--------|---------------|---------|
| GitHub URL | `<owner>__<repo>[__<version>][__<timestamp>]` | `alice__cool-plugin__v1.2.0__20260419` |
| Zip/tar.gz file | `<archive-name>[__<timestamp>]` | `cool-plugin__20260419` |

- Use double underscores (`__`) as separators
- `<version>` comes from the GitHub tag/branch if identifiable, otherwise omit
- `<timestamp>` (YYYYMMDD format) is appended when the directory already exists to avoid collisions
- No automatic cleanup — users manage `repos/` contents manually

## Security Rules

**Remote sources:** Always clone/download without executing hooks or scripts. Use `--no-checkout` + selective `git checkout`, or extract archives without running post-install scripts. The audit itself will scan for risks — don't trigger them before scanning.

**If clone/download fails:** Tell the user what failed (network error, 404, auth required, rate limit) and suggest alternatives — provide the repo as a local path or zip file. Do not silently skip the audit or proceed with partial data.
