# Bundles Forge — Contributor Guidelines

## Project Overview

This is a bundle-plugin engineering toolkit supporting 5 platforms: Claude Code, Cursor, Codex, OpenCode, and Gemini CLI. It contains 8 skills covering the full lifecycle of bundle-plugin development.

## Development Workflow

1. Make changes to skills under `skills/`
2. Keep platform manifests in sync — run `scripts/bump-version.sh --check` before committing
3. Run tests with `bash tests/run-all.sh`
4. Use `bundles-forge:auditing` for quality checks

## Key Conventions

- **Skill naming:** lowercase with hyphens, directory name must match frontmatter `name` field
- **Descriptions:** must start with "Use when..." and describe triggering conditions, not workflow steps
- **Descriptions:** stay under 250 characters (truncated beyond this), frontmatter under 1024 characters total
- **Heavy reference content:** extract to `references/` subdirectory (threshold: 100+ lines)
- **Cross-references:** use `bundles-forge:<skill-name>` format

## Version Management

All versioned files are declared in `.version-bump.json`. Never edit version numbers manually — use:

```bash
scripts/bump-version.sh <new-version>   # bump all files
scripts/bump-version.sh --check         # detect drift
scripts/bump-version.sh --audit         # find undeclared version strings
```

## Platform Manifests

| Platform | Manifest |
|----------|----------|
| Claude Code | `.claude-plugin/plugin.json` |
| Cursor | `.cursor-plugin/plugin.json` |
| Codex | `.codex/INSTALL.md` |
| OpenCode | `.opencode/plugins/bundles-forge.js` |
| Gemini CLI | `gemini-extension.json` |

## Hooks

Session bootstrap hooks live in `hooks/`. The `session-start` script reads `skills/using-bundles-forge/SKILL.md` and injects it as session context. It auto-detects the platform via environment variables.

## Security

- Never add network calls (`curl`, `wget`) to hook scripts
- Never reference sensitive files (`.env`, `.ssh/`) in SKILL.md instructions
- Never use `eval()` or `child_process` in plugin code
- Run `bundles-forge:auditing` before releases
