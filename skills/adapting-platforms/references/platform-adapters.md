# Platform Adapters

Documentation for each supported platform's adapter requirements. When adding platform support, read the relevant section for wiring details, then read the actual template files from `assets/<platform>/`.

All templates use `<project-name>` as a placeholder — replace with the actual project name (kebab-case).

---

## Claude Code

**Template files:** `assets/claude-code/plugin.json`, `assets/claude-code/hooks.json`

**Additional shared files:** `hooks/session-start`, `hooks/run-hook.cmd` (see scaffolding assets for templates)

Claude Code discovers `skills/`, `commands/`, `agents/`, and `hooks/hooks.json` by convention — no path declarations needed in plugin.json. Optional components (`bin/`, `output-styles/`, `.mcp.json`, `.lsp.json`, `settings.json`) are also auto-discovered at their default locations.

**Plugin manifest fields:** `name` (required), `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`. Component path overrides: `commands`, `agents`, `skills`, `hooks`, `mcpServers`, `outputStyles`, `lspServers`, `userConfig`, `channels`.

**Plugin agent restrictions:** Plugin-shipped agents do not support `hooks`, `mcpServers`, or `permissionMode` frontmatter fields.

**Install method:** Marketplace `claude plugin install` or `/plugin install`. For development: `claude --plugin-dir .`

**Version bump entry:**
```json
{ "path": ".claude-plugin/plugin.json", "field": "version" }
```

---

## Cursor

**Template files:** `assets/cursor/plugin.json`, `assets/cursor/hooks-cursor.json`

**Additional shared files:** `hooks/session-start`, `hooks/run-hook.cmd`

Unlike Claude Code, Cursor requires explicit `skills`, `agents`, `commands`, and `hooks` path declarations in plugin.json.

Note: Cursor uses `sessionStart` (camelCase), Claude Code uses `SessionStart` (PascalCase).

**Install method:** `/add-plugin <project-name>` in Cursor, or search the plugin marketplace.

**Version bump entry:**
```json
{ "path": ".cursor-plugin/plugin.json", "field": "version" }
```

---

## Codex

**Template files:** `assets/codex/INSTALL.md`, `assets/codex/AGENTS.md`

Codex reads `AGENTS.md` for agent instructions. Pointing to `CLAUDE.md` keeps a single source of truth. Codex discovers skills under `~/.agents/skills/` via native skill discovery.

**Install method:** Manual clone + symlink. No plugin marketplace.

**Version bump entry:** None. Codex reads from the git clone directly.

---

## OpenCode

**Template files:** `assets/opencode/plugin.js`, `assets/opencode/INSTALL.md`

The plugin is an ESM module that: registers the project's `skills/` path in OpenCode's config, injects bootstrap content into the first user message, and provides tool mapping.

Replace all `<project-name>` occurrences in the plugin template with the actual project name.

**Install method:** Add plugin entry to `opencode.json`. OpenCode clones and loads automatically.

**Version bump entry:** None. Version lives in `package.json`, which is already tracked.

---

## Gemini CLI

**Template files:** `assets/gemini/extension.json`, `assets/gemini/GEMINI.md`

Gemini CLI reads `GEMINI.md` on session start and inlines the referenced files. The `@` syntax triggers file inclusion.

**Install method:**
```bash
gemini extensions install <repo-url>
```

**Version bump entry:**
```json
{ "path": "gemini-extension.json", "field": "version" }
```

---

## Platform Differences Summary

| Aspect | Claude Code | Cursor | Codex | OpenCode | Gemini |
|--------|------------|--------|-------|----------|--------|
| Discovery | Convention | Explicit paths | Symlink | Plugin config | Context file |
| Hook format | `hooks.json` (PascalCase) | `hooks-cursor.json` (camelCase) | N/A | JS plugin | N/A |
| Skills path | Auto `skills/` | Declared in manifest | Symlink | Registered in JS | `@` includes |

## Claude Code Hook Events

Claude Code supports 25+ hook events. The most relevant for plugin development:

| Event | Matcher | Use Case |
|-------|---------|----------|
| `SessionStart` | `startup\|resume\|clear\|compact` | Bootstrap injection (use matcher to exclude `resume`) |
| `PreToolUse` | Tool name (regex) | Validate or block tool calls |
| `PostToolUse` | Tool name (regex) | Run linters/formatters after edits |
| `Stop` | (none) | Post-response actions |
| `SubagentStart` / `SubagentStop` | Agent type name | Subagent lifecycle hooks |
| `FileChanged` | Filename (basename) | React to file changes on disk |
| `CwdChanged` | (none) | React to directory changes |

**Hook types:** `command` (shell), `http` (POST to URL), `prompt` (LLM evaluation), `agent` (agentic verifier with tools).

**Environment variables:** Use `${CLAUDE_PLUGIN_ROOT}` for bundled files, `${CLAUDE_PLUGIN_DATA}` for persistent state that survives updates.

## Shared Hook: `session-start`

The `session-start` script is shared across Claude Code and Cursor. It:

1. Determines the plugin root from its own location
2. Reads the bootstrap SKILL.md
3. JSON-escapes the content (backslashes, quotes, newlines, tabs)
4. Wraps in `<EXTREMELY_IMPORTANT>` tags
5. Detects platform via environment variables
6. Emits the correct JSON shape

Use `printf` instead of heredoc to avoid bash 5.3+ hanging issues.

## Shared Hook: `run-hook.cmd`

Windows polyglot wrapper. A file that is simultaneously valid as a Windows `.cmd` batch script and a bash script. The Windows path detects Git Bash and delegates; if Git Bash is unavailable, exits 0 so the plugin loads without bootstrap injection.

Template available at: `scaffolding/assets/hooks/run-hook.cmd`

## Platform Detection Summary

| Environment Variable | Platform |
|---------------------|----------|
| `CURSOR_PLUGIN_ROOT` | Cursor |
| `CLAUDE_PLUGIN_ROOT` | Claude Code |

The `session-start` script checks these in order to determine which JSON format to emit.
