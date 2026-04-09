# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bundles Forge is a bundle-plugin engineering toolkit supporting 5 platforms: Claude Code, Cursor, Codex, OpenCode, and Gemini CLI. It contains 8 skills covering the full lifecycle of bundle-plugin development (design, scaffold, author, audit, optimize, port, release). The project itself is a bundle-plugin — it uses its own patterns to build and validate itself.

## Commands

### Testing

```bash
bash tests/run-all.sh                              # all test suites (shell + Python)
bash tests/test-bootstrap-injection.sh             # session-start hook output
bash tests/test-skill-discovery.sh                 # skill frontmatter validation
bash tests/test-version-sync.sh                    # version consistency across manifests
python tests/test_scripts.py -v                    # Python script tests (unittest)
python -m pytest tests/test_scripts.py -v          # same, via pytest
python -m pytest tests/test_scripts.py -v -k test_lint_runs_without_error  # single test
```

### Quality & Security

```bash
python scripts/lint_skills.py [project-root]       # skill frontmatter/quality lint
python scripts/scan_security.py [project-root]     # 5-surface security scan
python scripts/audit_project.py [project-root]     # combined audit (calls lint + scan)
```

All scripts accept `--json` for machine-readable output. Exit codes: 0 = pass, 1 = warnings, 2 = critical.

### Version Management

```bash
python scripts/bump_version.py --check             # detect version drift across manifests
python scripts/bump_version.py --audit             # find undeclared version strings
python scripts/bump_version.py <new-version>       # bump all files declared in .version-bump.json
```

## Architecture

### Directory Layout

- `skills/` — 8 skill directories, each containing `SKILL.md` and optional `references/` subdirectory
- `agents/` — 3 subagent definitions (inspector, auditor, evaluator) as `.md` files
- `commands/` — slash command stubs (`bundles-*.md`) that redirect to skills via `bundles-forge:<skill-name>`
- `hooks/` — session bootstrap: `session-start` reads `using-bundles-forge/SKILL.md` and injects it as platform-appropriate JSON context. `run-hook.cmd` is a polyglot wrapper (Windows cmd + bash)
- `scripts/` — Python tooling sharing `_cli.py` for common argparse/exit-code patterns

### Skill Lifecycle Flow

`blueprinting` → `scaffolding` → `authoring` → `auditing` ↔ `optimizing` → `releasing`. `porting` can be invoked at any phase for platform adaptation.

### Session Bootstrap

The `hooks/session-start` script runs on SessionStart, reads the `using-bundles-forge` meta-skill, and emits JSON context. It detects the platform via `CURSOR_PLUGIN_ROOT` vs `CLAUDE_PLUGIN_ROOT` env vars and formats output accordingly (`additional_context` for Cursor, `hookSpecificOutput` for Claude Code).

### Agent Dispatch

Skills dispatch read-only subagents (disallowed from editing files) that write reports to `.bundles-forge/`:
- `inspector` — validates scaffolded structure (dispatched by `scaffolding`)
- `auditor` — runs 9-category audit (dispatched by `auditing`)
- `evaluator` — A/B skill evaluation (dispatched in pairs by `optimizing`)

### Platform Manifests

Version is synchronized across these files (declared in `.version-bump.json`):

| Platform | Manifest |
|----------|----------|
| Claude Code | `.claude-plugin/plugin.json` |
| Cursor | `.cursor-plugin/plugin.json` |
| Codex | `.codex/INSTALL.md` |
| OpenCode | `.opencode/plugins/bundles-forge.js` |
| Gemini CLI | `gemini-extension.json` |

## Key Conventions

- **Skill naming:** lowercase with hyphens; directory name must match frontmatter `name` field
- **Descriptions:** must start with "Use when..." and describe triggering conditions, not workflow steps
- **Descriptions:** stay under 250 characters; total frontmatter under 1024 characters
- **Heavy reference content:** extract to `references/` subdirectory (threshold: 100+ lines)
- **Cross-references:** use `bundles-forge:<skill-name>` format
- **Version bumps:** never edit version numbers manually — use `bump_version.py`
- **Pre-commit:** run `python scripts/bump_version.py --check` to detect version drift
- **Pre-release:** run `bundles-forge:auditing` for full quality + security check

## Security Rules

- No network calls (`curl`, `wget`) in hook scripts
- No references to sensitive files (`.env`, `.ssh/`) in SKILL.md instructions
- No `eval()` or `child_process` in plugin code
