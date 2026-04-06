# Skill Engineering Guide — Contributor Guidelines

## Project Overview

This is a skill-project engineering toolkit (`seg`) supporting 6 platforms: Claude Code, Cursor, Codex, OpenCode, Copilot CLI, and Gemini CLI. It contains 10 skills covering the full lifecycle of skill-project development.

## Development Workflow

1. Make changes to skills under `skills/`
2. Keep platform manifests in sync — run `scripts/bump-version.sh --check` before committing
3. Run tests with `bash tests/run-all.sh`
4. Use `seg:auditing-skill-projects` for quality checks

## Key Conventions

- **Skill naming:** lowercase with hyphens, directory name must match frontmatter `name` field
- **Descriptions:** must start with "Use when..." and describe triggering conditions, not workflow steps
- **Descriptions:** stay under 500 characters, frontmatter under 1024 characters total
- **Heavy reference content:** extract to `references/` subdirectory (threshold: 100+ lines)
- **Cross-references:** use `seg:<skill-name>` format

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
| OpenCode | `.opencode/plugins/skill-engineering-guide.js` |
| Copilot CLI | (shares Claude Code hooks) |
| Gemini CLI | `gemini-extension.json` |

## Hooks

Session bootstrap hooks live in `hooks/`. The `session-start` script reads `skills/using-skill-engineering-guide/SKILL.md` and injects it as session context. It auto-detects the platform via environment variables.

## Security

- Never add network calls (`curl`, `wget`) to hook scripts
- Never reference sensitive files (`.env`, `.ssh/`) in SKILL.md instructions
- Never use `eval()` or `child_process` in plugin code
- Run `seg:scanning-skill-security` before releases
