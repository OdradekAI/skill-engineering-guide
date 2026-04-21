# Troubleshooting Guide

[中文](troubleshooting-guide.zh.md)

> **Canonical source:** Exit code semantics are defined in `skills/auditing/scripts/_cli.py`. Platform hook behavior is defined in `hooks/session-start` (Bash) + `hooks/run-hook.cmd` (polyglot wrapper). This guide consolidates troubleshooting information from across the project.

Common issues and their solutions when using Bundles Forge. For exit codes and audit-specific behavior, see the [Auditing Guide](auditing-guide.md). For release pipeline issues, see the [Releasing Guide](releasing-guide.md).

## Requirements

| Requirement | Minimum | Notes |
|-------------|---------|-------|
| Python | 3.9+ | `Path.is_relative_to()` and other 3.9+ features are used throughout |
| External dependencies | None | All scripts use stdlib only — no `pip install` required |

### Python Version Errors

**Symptom:** `AttributeError: 'PosixPath' object has no attribute 'is_relative_to'` or similar.

**Cause:** Running with Python 3.8 or earlier. The CLI entry guard will print `bundles-forge requires Python 3.9+` and exit.

**Fix:** Install Python 3.9+ and ensure it is on your PATH. On systems with multiple Python versions, use `python3.9` or `python3` explicitly.

## Exit Codes

All audit scripts follow a consistent exit code convention:

| Code | Meaning | Action |
|------|---------|--------|
| `0` | Clean — no issues | No action needed |
| `1` | Warnings found | Review recommended; not blocking |
| `2` | Critical findings | Must resolve before proceeding |

Scripts that validate configuration (e.g., `checklists --check`, `bump-version --check`) use: `0` = consistent, `1` = drift detected.

## Installation & Setup

### Unknown Command

**Symptom:** `bundles-forge: unknown command 'xxx'`

**Fix:** Check available commands with `bundles-forge -h`. See the [CLI Reference](cli-reference.md) for the full command list.

### Script Not Found

**Symptom:** `bundles-forge: script not found: ...`

**Cause:** Plugin directory structure is incomplete or the binary is not running from the correct location.

**Fix:** Ensure the full `skills/` directory tree is present. Re-clone or re-install if necessary.

### Path Issues on Windows

**Symptom:** Path-related errors or inconsistent output on Windows.

**Notes:** All scripts use `pathlib.Path` for cross-platform compatibility and normalize output paths with forward slashes. If you encounter path issues, ensure you are invoking scripts through `bundles-forge` or `python bin/bundles-forge` rather than directly.

## Audit Issues

### Security Scan False Positives

**Symptom:** Security scan flags legitimate documentation references (e.g., a SKILL.md mentioning `.env` in a "don't do this" context).

**Explanation:** Findings from SKILL.md and references are classified as `suspicious` (not `deterministic`). They appear in a separate "Needs review" section and require manual judgment.

**Action:** Review the flagged line in context. If the reference is a prohibition (e.g., "never access .env files"), it is a false positive. Suspicious findings still count toward exit codes but are clearly labeled.

### Version Drift

**Symptom:** `bump-version --check` reports drift.

**Cause:** A version number was edited manually instead of using the bump script, or a new manifest file was not added to `.version-bump.json`.

**Fix:** Run `bundles-forge bump-version <correct-version>` to re-sync all declared files. If a new file needs tracking, add it to `.version-bump.json` first.

### Checklist Drift

**Symptom:** `checklists --check` exits with code 1.

**Cause:** Audit check definitions in `audit-checks.json` were updated but the generated checklist markdown tables were not regenerated.

**Fix:** Run `bundles-forge checklists .` to regenerate, then commit the updated files.

### Documentation Audit Failures (D1-D9)

**Symptom:** `audit-docs` reports mismatches.

**Common causes:**
- **D1 (CLAUDE.md):** Skill list in CLAUDE.md doesn't match actual `skills/` directories
- **D3 (Platform manifests):** CLAUDE.md Platform Manifests table doesn't match `.version-bump.json`
- **D6 (README sync):** README skill table is stale after adding/removing a skill
- **D7 (Bilingual symmetry):** A guide was updated in one language but not the other

**Fix:** Update the referenced documents to match the current state of `skills/` and manifests.

## Platform-Specific Issues

### Claude Code

- Hook output must be valid JSON with `hookSpecificOutput` wrapper
- If the hook fails, it exits 0 (silent degradation) to avoid blocking IDE startup

### Cursor

- Hook output uses `additional_context` wrapper (different from Claude Code)
- Hook configuration lives in `hooks-cursor.json` (separate schema, no timeout/description fields)

### Codex / OpenCode / Gemini CLI

- These platforms have platform-specific manifests but share the same skill content
- Version sync covers `gemini-extension.json` but not all platform install guides

## See Also

- [CLI Reference](cli-reference.md) — full command documentation
- [Auditing Guide](auditing-guide.md) — audit scopes and workflows
- [Releasing Guide](releasing-guide.md) — release pipeline troubleshooting
- [Concepts Guide](concepts-guide.md) — architecture and terminology
