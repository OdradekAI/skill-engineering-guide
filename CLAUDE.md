# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Bundles Forge is a bundle-plugin engineering toolkit supporting 5 platforms: Claude Code, Cursor, Codex, OpenCode, and Gemini CLI. It contains 7 skills covering the full lifecycle of bundle-plugin development (design, scaffold, author, audit, optimize, release). The project itself is a bundle-plugin — it uses its own patterns to build and validate itself.

## Commands

### Testing

```bash
bash tests/run-all.sh                              # all Python test suites
python tests/test_scripts.py -v                    # auditing/releasing script tests (unittest)
python tests/test_integration.py -v                # structure, hooks, version sync, skill discovery
python -m pytest tests/test_scripts.py -v          # same, via pytest
python -m pytest tests/test_scripts.py -v -k test_project_mode_runs_without_error  # single test
```

### Quality & Security

```bash
python skills/auditing/scripts/audit_skill.py [project-root]       # project-level skill quality audit (auto-detects mode)
python skills/auditing/scripts/audit_skill.py [skill-dir]          # single skill audit (4 categories)
python skills/auditing/scripts/audit_skill.py --all [project-root] # force project-level mode
python skills/auditing/scripts/audit_security.py [project-root]     # 7-surface security scan
python skills/auditing/scripts/audit_plugin.py [project-root]     # combined audit (calls audit_skill + audit_security + workflow)
python skills/auditing/scripts/audit_workflow.py [project-root]    # workflow integration audit (W1-W11)
python skills/auditing/scripts/audit_docs.py [project-root]        # documentation consistency (9 checks: D1-D9)
python skills/auditing/scripts/generate_checklists.py [project-root]        # regenerate checklist tables from audit-checks.json registry
python skills/auditing/scripts/generate_checklists.py --check [project-root] # detect checklist drift (exit 1 if stale)
```

All scripts accept `--json` for machine-readable output. Exit codes: 0 = pass, 1 = warnings, 2 = critical.

### Version Management

```bash
python skills/releasing/scripts/bump_version.py --check             # detect version drift across manifests
python skills/releasing/scripts/bump_version.py --audit             # find undeclared version strings
python skills/releasing/scripts/bump_version.py <new-version>       # bump all files declared in .version-bump.json
```

## Architecture

### Directory Layout

- `skills/` — 7 skill directories, each containing `SKILL.md` and optional `references/` subdirectory
- `agents/` — 3 subagent definitions (inspector, auditor, evaluator) as `.md` files
- `commands/` — slash command stubs (`bundles-*.md`) that redirect to skills via `bundles-forge:<skill-name>`
- `hooks/` — session bootstrap: `session-start.py` reads `using-bundles-forge/SKILL.md` and injects it as platform-appropriate JSON context (Python for cross-platform compatibility)
- `docs/` — guides (concepts, blueprinting, scaffolding, authoring, auditing, optimizing, releasing) with `*.zh.md` Chinese translations; checked by D7
- `skills/auditing/scripts/` — audit, security scan, documentation checks, and checklist generation (shares `_cli.py` for argparse/exit-code patterns)
- `skills/releasing/scripts/` — version bump tooling (`bump_version.py`)
- `scripts/` — `bump-version.sh` wrapper for CLI convenience (forwards to `skills/releasing/scripts/bump_version.py`)

### Skill Architecture: Hub-and-Spoke Model

Skills are organized into two layers:

**Orchestration layer** (hub) — diagnose, decide, delegate:
- `blueprinting` — new-project pipeline: interview → scaffolding → authoring → workflow design → auditing
- `optimizing` — existing-project improvement: diagnose → delegate to authoring/scaffolding → verify via auditing
- `releasing` — release pipeline: auditing → optimizing (if needed) → version bump → publish

**Execution layer** (spoke) — single-responsibility workers:
- `scaffolding` — generate project structure, platform adaptation, inspector self-check
- `authoring` — write/improve SKILL.md and agents/*.md content
- `auditing` — pure diagnostics: check, score, report (does not orchestrate fixes)

Pipeline stages: `blueprinting` → `optimizing` → `releasing`. Each orchestrator dispatches executors as needed. Users can also invoke any executor directly for standalone tasks.

### Session Bootstrap

The `hooks/session-start.py` script runs on SessionStart (matcher: `startup|clear|compact`, excluding `resume` since resumed sessions retain context). It reads the `using-bundles-forge` meta-skill and emits JSON context. Platform detection is three-way: `CURSOR_PLUGIN_ROOT` → Cursor format (`additional_context`), `CLAUDE_PLUGIN_ROOT` → Claude Code format (`hookSpecificOutput`), neither → plain text fallback. On read failure, the script warns to stderr and exits 0 (no-op). Written in Python for cross-platform compatibility (Windows/Mac/Linux).

The `hooks/hooks.json` includes a top-level `description` (shown in Claude Code's `/hooks` menu) and per-handler `timeout: 10` to prevent slow hooks from blocking session start.

### Agent Dispatch

Skills dispatch read-only subagents (disallowed from editing files) as diagnostic tools. Subagents write reports to `.bundles-forge/`:
- `inspector` — validates scaffolded structure and platform adaptation (dispatched by `scaffolding`)
- `auditor` — runs 10-category audit (dispatched by `auditing`)
- `evaluator` — A/B skill evaluation and chain verification (dispatched by `optimizing` and `auditing`)

**Design pattern:** Each agent file in `agents/` is a self-contained executor — it holds the complete execution protocol (what to check, how to score, how to report). Skills handle scope detection, dispatch, result composition, and fallback. When subagents are unavailable, skills fall back to reading the agent file inline. This ensures a single source of truth with zero duplication between skills and agents.

### Platform Manifests

Version is synchronized across these files (declared in `.version-bump.json`):

| Platform | Manifest | Version-synced |
|----------|----------|:--------------:|
| Claude Code | `.claude-plugin/plugin.json` | Yes |
| Cursor | `.cursor-plugin/plugin.json` | Yes |
| Codex | `.codex/INSTALL.md` | No (install guide) |
| OpenCode | `.opencode/plugins/bundles-forge.js` | No (plugin loader) |
| Gemini CLI | `gemini-extension.json` | Yes |

## Key Conventions

- **Skill naming:** lowercase with hyphens; directory name must match frontmatter `name` field
- **Descriptions:** must start with "Use when..." and describe triggering conditions, not workflow steps
- **Descriptions:** stay under 250 characters; total frontmatter under 1024 characters
- **Heavy reference content:** extract to `references/` subdirectory (threshold: 100+ lines)
- **Cross-references:** use `bundles-forge:<skill-name>` format
- **Version bumps:** never edit version numbers manually — use `bump_version.py`
- **Pre-commit:** run `python skills/releasing/scripts/bump_version.py --check` to detect version drift
- **Pre-commit:** run `python skills/auditing/scripts/generate_checklists.py --check` to detect checklist drift
- **Pre-release:** run `bundles-forge:auditing` for full quality + security check
- **Pre-release:** run `python skills/auditing/scripts/audit_docs.py` to verify documentation consistency (9 checks: D1-D9)
- **Source of truth:** Skills are first-class citizens — see `skills/auditing/references/source-of-truth-policy.md` for the full hierarchy and contradiction resolution protocol

## Security Rules

- No network calls (`curl`, `wget`) in hook scripts
- No references to sensitive files (`.env`, `.ssh/`) in SKILL.md instructions
- No `eval()` or `child_process` in plugin code
