# Skill-Project Anatomy

Complete reference for every file and directory in a well-engineered skill-project. Use this when scaffolding a new project or auditing an existing one.

## Root Files

### `package.json`

Project identity. Minimal — no dependencies (skill-projects are zero-dependency by design). The `main` field points to the OpenCode plugin entry if OpenCode is a target platform.

```json
{
  "name": "<project-name>",
  "version": "1.0.0",
  "type": "module",
  "main": ".opencode/plugins/<project-name>.js"
}
```

If OpenCode is not a target, omit the `main` field.

### `README.md`

The project's public face. Must contain:
- One-sentence description of what the project provides
- Installation instructions per target platform (separate subsection each)
- Skill catalog — list every skill with its trigger description
- Workflow diagram (if skills chain together)
- Contributing pointer (if open-source)

### `CHANGELOG.md`

Release history. Use [Keep a Changelog](https://keepachangelog.com/) format. Group by version, date, and change type (Added, Changed, Fixed, Removed).

### `LICENSE`

Default to MIT. Match the user's preference.

### `CLAUDE.md`

Contributor guidelines for AI agents working on the project. Covers PR requirements, what changes are accepted/rejected, testing expectations. This is the authority document — `AGENTS.md` points to it.

### `AGENTS.md`

Codex convention. Contents: a single line pointing to `CLAUDE.md`. Codex reads `AGENTS.md` for agent instructions.

```
CLAUDE.md
```

### `GEMINI.md`

Gemini CLI context file. Uses `@` includes to pull in the bootstrap skill and tool mapping:

```
@./skills/using-<project>/SKILL.md
@./skills/using-<project>/references/gemini-tools.md
```

Gemini reads this file on session start (declared via `contextFileName` in `gemini-extension.json`).

### `.version-bump.json`

Declares every file containing the project version, plus audit exclusions:

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

Only include entries for platforms the project actually targets. The `audit.exclude` list prevents false positives when scanning for stale version strings.

### `.gitignore`

Essential entries:

```
node_modules/
.worktrees/
worktrees/
.DS_Store
Thumbs.db
*.log
```

### `gemini-extension.json`

Gemini CLI extension metadata. Only generate if Gemini is a target platform.

```json
{
  "name": "<project-name>",
  "description": "<one-line project description>",
  "version": "1.0.0",
  "contextFileName": "GEMINI.md"
}
```

---

## `.claude-plugin/` — Claude Code

### `plugin.json`

Marketplace metadata for Claude Code. Does NOT declare skills/hooks paths — Claude Code discovers those by convention (skills at `skills/`, hooks at `hooks/hooks.json`).

```json
{
  "name": "<project-name>",
  "description": "<one-line description>",
  "version": "1.0.0",
  "author": {
    "name": "<author>",
    "email": "<email>"
  },
  "homepage": "<repo-url>",
  "repository": "<repo-url>",
  "license": "MIT",
  "keywords": ["skills", "<relevant>", "<keywords>"]
}
```

### `marketplace.json` (optional)

Marketplace listing if publishing to Claude Code's plugin marketplace. Contains a `plugins` array with source paths.

---

## `.cursor-plugin/` — Cursor

### `plugin.json`

Cursor plugin manifest. Unlike Claude Code, Cursor requires explicit path declarations:

```json
{
  "name": "<project-name>",
  "displayName": "<Display Name>",
  "description": "<one-line description>",
  "version": "1.0.0",
  "author": {
    "name": "<author>",
    "email": "<email>"
  },
  "homepage": "<repo-url>",
  "repository": "<repo-url>",
  "license": "MIT",
  "keywords": ["skills"],
  "skills": "./skills/",
  "agents": "./agents/",
  "commands": "./commands/",
  "hooks": "./hooks/hooks-cursor.json"
}
```

Key difference from Claude Code: `skills`, `agents`, `commands`, and `hooks` paths are explicit.

---

## `.codex/` — Codex

### `INSTALL.md`

Manual setup instructions. Codex uses native skill discovery from `~/.agents/skills/`. The install process is: clone the repo, symlink `skills/` into the discovery directory.

Include both Unix and Windows (PowerShell) commands. The symlink/junction is what makes skills visible to Codex.

---

## `.opencode/` — OpenCode

### `INSTALL.md`

Instructions for adding the plugin to `opencode.json`.

### `plugins/<project-name>.js`

ESM module that:
1. Registers the project's `skills/` path in OpenCode's config (so skills are discovered without symlinks)
2. Injects bootstrap content into the first user message of each session
3. Provides tool mapping (OpenCode tool names differ from Claude Code)

The plugin uses OpenCode's hook API: `config` for path registration, `experimental.chat.messages.transform` for bootstrap injection.

---

## `hooks/` — Session Bootstrap

### `session-start`

Bash script that injects the bootstrap skill content as session context. Platform-aware: detects `CURSOR_PLUGIN_ROOT`, `CLAUDE_PLUGIN_ROOT`, and `COPILOT_CLI` environment variables to emit the correct JSON shape.

| Platform | JSON Field |
|----------|-----------|
| Cursor | `additional_context` (snake_case) |
| Claude Code | `hookSpecificOutput.additionalContext` (nested) |
| Copilot CLI / SDK | `additionalContext` (top-level) |

The script reads the bootstrap SKILL.md, JSON-escapes it, and wraps it in `<EXTREMELY_IMPORTANT>` tags. Uses `printf` instead of heredoc to avoid bash 5.3+ heredoc hang issues.

### `run-hook.cmd`

Windows polyglot — a file that is valid both as a Windows `.cmd` batch script and as a bash script. On Windows, it detects Git Bash and delegates to it. If Git Bash is unavailable, exits 0 gracefully so the plugin still loads without bootstrap injection.

### `hooks.json`

Claude Code hook descriptor:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "matcher": "startup|clear|compact",
        "hooks": [
          {
            "type": "command",
            "command": "\"${CLAUDE_PLUGIN_ROOT}/hooks/run-hook.cmd\" session-start",
            "async": false
          }
        ]
      }
    ]
  }
}
```

### `hooks-cursor.json`

Cursor hook descriptor (simpler format):

```json
{
  "version": 1,
  "hooks": {
    "sessionStart": [
      {
        "command": "./hooks/session-start"
      }
    ]
  }
}
```

---

## `skills/` — Skill Content

### Structure

One directory per skill. The directory name must match the `name` field in the skill's YAML frontmatter.

```
skills/
  using-<project>/          # Bootstrap skill (always-loaded)
    SKILL.md
    references/
      codex-tools.md        # Codex tool mapping
      gemini-tools.md       # Gemini CLI tool mapping
  <skill-name>/
    SKILL.md                # Required: frontmatter + body
    <supporting-file>.md    # Optional: heavy reference
    scripts/                # Optional: executable tools
```

### SKILL.md Requirements

Every SKILL.md must have YAML frontmatter with:
- `name` — kebab-case, letters/numbers/hyphens only, matches directory name
- `description` — starts with "Use when...", triggering conditions only, under 500 chars

The body follows the structure from `superpowers:writing-skills`: Overview, When to Use, Core Pattern, Quick Reference, Common Mistakes.

### Supporting Files

Only create supporting files when content exceeds what fits inline:
- **Heavy reference** (100+ lines) — API docs, syntax guides
- **Reusable scripts** — deterministic tools the skill invokes
- **Templates** — file templates the skill generates

---

## `agents/` — Shared Agent Prompts (optional)

Markdown files used as prompts when dispatching subagents. Referenced by skills via `agents/<role>.md`. Example: `agents/code-reviewer.md` contains the review template.

## `commands/` — Slash Commands (optional)

Markdown files that define slash commands for platforms that support them (Cursor). Each file is one command.

## `scripts/` — Project Tooling

### `bump-version.sh`

Version synchronization tool. Reads `.version-bump.json` and provides:
- `bump-version.sh <version>` — update all declared files
- `bump-version.sh --check` — detect drift between files
- `bump-version.sh --audit` — check + scan repo for undeclared version strings

Requires `jq` and `bash`.

## `tests/` — Integration Tests

Per-platform test scripts that verify skills are discoverable and loadable. Organized by platform:

```
tests/
  claude-code/
    run-skill-tests.sh
  opencode/
    setup.sh
    integration.sh
```

Tests typically use headless invocations (e.g., `claude -p` for Claude Code) to verify skill triggering and content loading.

## `docs/` — Documentation

Platform-specific READMEs, design documents, specs, and plans. Organized as needed — no strict structure required.

```
docs/
  README.codex.md
  README.opencode.md
  specs/
    2025-01-15-feature-design.md
```
