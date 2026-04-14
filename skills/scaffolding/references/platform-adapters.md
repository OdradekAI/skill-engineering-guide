# Platform Adapters

Documentation for each supported platform's adapter requirements. When adding platform support, read the relevant section for wiring details, then read the actual template files from `assets/platforms/<platform>/`.

All templates use `<project-name>` as a placeholder — replace with the actual project name (kebab-case).

---

## Claude Code

**Template files:** `assets/platforms/claude-code/plugin.json`, `assets/platforms/claude-code/hooks.json`

**Additional shared files:** `hooks/session-start.py` (see `assets/hooks/session-start.py` template)

Claude Code discovers `skills/`, `commands/`, `agents/`, and `hooks/hooks.json` by convention — no path declarations needed in plugin.json. Optional components (`bin/`, `output-styles/`, `.mcp.json`, `.lsp.json`, `settings.json`) are also auto-discovered at their default locations.

**Plugin manifest fields:** `name` (required), `version`, `description`, `author`, `homepage`, `repository`, `license`, `keywords`. Component path overrides: `commands`, `agents`, `skills`, `hooks`, `mcpServers`, `outputStyles`, `lspServers`, `userConfig`, `channels`.

**`userConfig`** declares values prompted at plugin enable time (API keys, endpoints). Keys are available as `${user_config.KEY}` in MCP/LSP/hook configs and (non-sensitive only) in skill/agent content. Sensitive values go to the system keychain. See `references/external-integration.md` for full schema and wiring guide.

**`channels`** declares message channels that inject external content (Telegram, Slack, Discord) into conversations. Each channel binds to a plugin-provided MCP server and can have its own `userConfig` for bot tokens. This is essentially MCP + userConfig scoped to a messaging integration.

**Plugin agent restrictions:** Plugin-shipped agents do not support `hooks`, `mcpServers`, or `permissionMode` frontmatter fields.

**Install method:** Marketplace `claude plugin install` or `/plugin install`. For development: `claude --plugin-dir .`

**Version bump entry:**
```json
{ "path": ".claude-plugin/plugin.json", "field": "version" }
```

---

## Cursor

**Template files:** `assets/platforms/cursor/plugin.json`, `assets/platforms/cursor/hooks-cursor.json`

**Additional shared files:** `hooks/session-start.py`

Unlike Claude Code, Cursor requires explicit `skills`, `agents`, `commands`, and `hooks` path declarations in plugin.json.

Note: Cursor uses `sessionStart` (camelCase), Claude Code uses `SessionStart` (PascalCase).

**Install method:** `/add-plugin <project-name>` in Cursor, or search the plugin marketplace.

**Version bump entry:**
```json
{ "path": ".cursor-plugin/plugin.json", "field": "version" }
```

---

## Codex

**Template files:** `assets/platforms/codex/INSTALL.md`, `assets/platforms/codex/AGENTS.md`

Codex reads `AGENTS.md` for agent instructions. Pointing to `CLAUDE.md` keeps a single source of truth. Codex discovers skills under `~/.agents/skills/` via native skill discovery.

**Install method:** Manual clone + symlink. No plugin marketplace.

**Version bump entry:** None. Codex reads from the git clone directly.

---

## OpenCode

**Template files:** `assets/platforms/opencode/plugin.js`, `assets/platforms/opencode/INSTALL.md`

The plugin is an ESM module that: registers the project's `skills/` path in OpenCode's config, injects bootstrap content into the first user message, and provides tool mapping.

Replace all `<project-name>` occurrences in the plugin template with the actual project name.

**Install method:** Add plugin entry to `opencode.json`. OpenCode clones and loads automatically.

**Version bump entry:** None. Version lives in `package.json`, which is already tracked.

---

## Gemini CLI

**Template files:** `assets/platforms/gemini/extension.json`, `assets/platforms/gemini/GEMINI.md`

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

## Platform-Specific Limitations

### Codex: No Bootstrap Routing Table

Codex has no hook-based bootstrap injection. It reads `AGENTS.md` (which points to `CLAUDE.md`) for guidelines, but neither file contains the full skill routing table. Codex users rely entirely on description-based matching for skill discovery. This is a deliberate design choice — Codex's native skill discovery mechanism uses directory symlinks and does not support the same hook lifecycle as Claude Code or Cursor.

### Cursor: No Re-injection on Context Clear

Cursor's `hooks-cursor.json` only fires on `sessionStart` — there is no equivalent to Claude Code's `clear|compact` matcher. If a Cursor user clears context mid-session, the bootstrap is not re-injected. The agent loses the routing table until a new session starts. This is a platform limitation, not a bundles-forge issue.

## Platform Differences Summary

| Aspect | Claude Code | Cursor | Codex | OpenCode | Gemini |
|--------|------------|--------|-------|----------|--------|
| Discovery | Convention | Explicit paths | Symlink | Plugin config | Context file |
| Hook format | `hooks.json` (PascalCase) | `hooks-cursor.json` (camelCase) | N/A | JS plugin | N/A |
| Skills path | Auto `skills/` | Declared in manifest | Symlink | Registered in JS | `@` includes |

## Claude Code Hook Handler Types

Claude Code supports four hook handler types. Scaffolded projects use `command` by default; the others are available for advanced use cases.

| Type | Description | When to use |
|------|-------------|-------------|
| `command` | Runs a shell command. Receives JSON on stdin, returns via exit code + stdout. | Default for all scaffolded hooks. Simple, portable, no dependencies. |
| `http` | Sends HTTP POST to a URL. Response body uses the same JSON format as command hooks. | Remote validation services, centralized logging, webhook integrations. |
| `prompt` | Sends a prompt to a Claude model for single-turn yes/no evaluation. | Policy enforcement without writing scripts (e.g., "Is this command safe?"). |
| `agent` | Spawns a subagent with access to Read, Grep, and Glob tools to verify conditions. | Complex verification that requires inspecting files or project state. |

**Security note:** `http` hooks can transmit data to external services — audit any plugin that uses them. See the [auditing guide](../../../docs/auditing-guide.md) for HTTP hook risk assessment.

## Claude Code Hook Events

Claude Code supports 25+ hook events across three cadences:

**Session-level (once per session):**

| Event | Matcher filters | Can block? | Description |
|-------|----------------|------------|-------------|
| `SessionStart` | `startup`, `resume`, `clear`, `compact` | No | Session begins or resumes. Only `command` type supported. |
| `SessionEnd` | `clear`, `resume`, `logout`, `prompt_input_exit`, `other` | No | Session terminates. |
| `InstructionsLoaded` | `session_start`, `nested_traversal`, `path_glob_match`, `include`, `compact` | No | CLAUDE.md or rule file loaded. |

**Turn-level (once per user prompt):**

| Event | Matcher filters | Can block? | Description |
|-------|----------------|------------|-------------|
| `UserPromptSubmit` | (none) | Yes | Before Claude processes a prompt. Can add context or block. |
| `Stop` | (none) | Yes | Claude finishes responding. Exit 2 prevents stopping. |
| `StopFailure` | `rate_limit`, `authentication_failed`, `billing_error`, `server_error`, `unknown` | No | Turn ends due to API error. |
| `TeammateIdle` | (none) | Yes | Agent team member about to go idle. |

**Agentic loop (per tool call):**

| Event | Matcher filters | Can block? | Description |
|-------|----------------|------------|-------------|
| `PreToolUse` | Tool name | Yes | Before tool executes. Can allow/deny/ask/defer. |
| `PostToolUse` | Tool name | No | After tool succeeds. Can provide feedback. |
| `PostToolUseFailure` | Tool name | No | After tool fails. |
| `PermissionRequest` | Tool name | Yes | Permission dialog appears. Can auto-allow/deny. |
| `PermissionDenied` | Tool name | No | Auto mode denies a tool call. Can signal retry. |
| `SubagentStart` | Agent type | No | Subagent spawned. |
| `SubagentStop` | Agent type | Yes | Subagent finishes. |
| `TaskCreated` | (none) | Yes | Task being created. |
| `TaskCompleted` | (none) | Yes | Task marked complete. |
| `Notification` | Notification type | No | Claude Code sends a notification. |

**Standalone async events:**

| Event | Matcher filters | Can block? | Description |
|-------|----------------|------------|-------------|
| `FileChanged` | Literal filenames to watch | No | Watched file changes on disk. |
| `CwdChanged` | (none) | No | Working directory changes. |
| `ConfigChange` | Config source | Yes | Configuration file changes. |
| `WorktreeCreate` | (none) | Yes | Worktree being created. Hook provides the path. |
| `WorktreeRemove` | (none) | No | Worktree being removed. |
| `PreCompact` | `manual`, `auto` | No | Before context compaction. |
| `PostCompact` | `manual`, `auto` | No | After compaction completes. |
| `Elicitation` | MCP server name | Yes | MCP server requests user input. |
| `ElicitationResult` | MCP server name | Yes | User responds to MCP elicitation. |

## Hook Handler Fields

### Common fields (all types)

| Field | Required | Description |
|-------|----------|-------------|
| `type` | Yes | `"command"`, `"http"`, `"prompt"`, or `"agent"` |
| `if` | No | Permission rule syntax filter, e.g., `"Bash(git *)"`. Only evaluated on tool events. |
| `timeout` | No | Seconds before canceling. Defaults: 600 (command), 30 (prompt), 60 (agent). |
| `statusMessage` | No | Custom spinner message while the hook runs. |
| `once` | No | If `true`, runs only once per session. Skills only, not agents. |

### Command-specific fields

| Field | Required | Description |
|-------|----------|-------------|
| `command` | Yes | Shell command to execute. |
| `async` | No | If `true`, runs in background without blocking. |
| `shell` | No | `"bash"` (default) or `"powershell"`. PowerShell runs directly on Windows without needing `CLAUDE_CODE_USE_POWERSHELL_TOOL`. |

### HTTP-specific fields

| Field | Required | Description |
|-------|----------|-------------|
| `url` | Yes | URL to POST to. |
| `headers` | No | Key-value pairs. Values support `$VAR_NAME` interpolation. |
| `allowedEnvVars` | No | Env vars allowed in header interpolation. |

### Prompt/Agent-specific fields

| Field | Required | Description |
|-------|----------|-------------|
| `prompt` | Yes | Prompt text. Use `$ARGUMENTS` as placeholder for hook input JSON. |
| `model` | No | Model to use. Defaults to a fast model. |

## Hooks in Skill and Agent Frontmatter

> **Claude Code only.** This feature is not available on Cursor, Codex, OpenCode, or Gemini.

Skills and agents can define hooks directly in their YAML frontmatter. These hooks are scoped to the component's lifecycle — active while the skill/agent runs, automatically cleaned up when it finishes.

```yaml
---
name: secure-operations
description: Use when performing operations requiring security checks
hooks:
  PreToolUse:
    - matcher: "Bash"
      hooks:
        - type: command
          command: "./scripts/security-check.sh"
---
```

All hook events are supported. For subagents, `Stop` hooks are automatically converted to `SubagentStop`.

## Environment Variables for Hooks

| Variable | Scope | Description |
|----------|-------|-------------|
| `${CLAUDE_PLUGIN_ROOT}` | Plugin hooks | Plugin installation directory. Changes on each update. |
| `${CLAUDE_PLUGIN_DATA}` | Plugin hooks | Persistent data directory. Survives plugin updates. |
| `$CLAUDE_PROJECT_DIR` | All hooks | Project root directory. |
| `$CLAUDE_ENV_FILE` | SessionStart, CwdChanged, FileChanged | Write `export` statements here to persist env vars for all subsequent Bash commands. |
| `$CLAUDE_CODE_REMOTE` | All hooks | Set to `"true"` in remote web environments. |

## Windows Support: `shell: "powershell"` Alternative

The `shell: "powershell"` field on command hooks runs the hook command in PowerShell on Windows. Scaffolded projects use a **Python** `session-start.py` invoked via `python .../hooks/session-start.py`, which avoids Git Bash and does not require a separate `.cmd` shim.

| Approach | Pros | Cons |
|----------|------|------|
| `python hooks/session-start.py` (current default) | Cross-platform; single script; standard library | Requires `python` on PATH |
| `shell: "powershell"` + PowerShell script | Native Windows shell | Hook logic must be maintained in PowerShell; platform-specific |

## Shared Hook: `session-start.py`

The `session-start.py` script is shared across Claude Code and Cursor. It:

1. Determines the plugin root from its own location
2. Reads the bootstrap SKILL.md
3. JSON-escapes the content (backslashes, quotes, newlines, tabs)
4. Wraps in `<EXTREMELY_IMPORTANT>` tags
5. Detects platform via environment variables
6. Emits the correct JSON shape

Implementation is Python for portability (Windows, macOS, Linux) without bash or polyglot wrappers.

## Platform Detection Summary

| Environment Variable | Platform | JSON Output Format |
|---------------------|----------|--------------------|
| `CURSOR_PLUGIN_ROOT` | Cursor | `{"additional_context": "..."}` |
| `CLAUDE_PLUGIN_ROOT` | Claude Code | `{"hookSpecificOutput": {"hookEventName": "SessionStart", "additionalContext": "..."}}` |
| Neither set | Unknown/fallback | Plain text context on stdout |

The `session-start.py` script checks `CURSOR_PLUGIN_ROOT` first, then `CLAUDE_PLUGIN_ROOT`, with a plain-text fallback for unknown platforms.

## Claude vs Cursor Hook Format Comparison

| Aspect | Claude Code | Cursor |
|--------|------------|--------|
| Event casing | PascalCase (`SessionStart`) | camelCase (`sessionStart`) |
| Config file | `hooks/hooks.json` | `hooks/hooks-cursor.json` |
| Top-level `description` | Supported | Not documented |
| Top-level `version` | Not used | Required (`1`) |
| Matcher field | Supported (regex or `\|`-separated) | Not supported |
| Handler `type` field | Required (`command`/`http`/`prompt`/`agent`) | Not used |
| Handler `async` field | Supported | Not supported |
| Handler `timeout` field | Supported | Not supported |
| Handler `shell` field | `"bash"` or `"powershell"` | Not supported |
| Handler `if` field | Permission rule syntax | Not supported |
| Manifest hooks path | Convention (`hooks/hooks.json`) | Explicit in `plugin.json` |

> **Note:** The OpenCode `plugin.js` template contains a tool name mapping (e.g., `TodoWrite` → `todowrite`). These mappings should be verified periodically against OpenCode's current tool set.

---

## Plugin Caching & Distribution

> **Claude Code only.** Other platforms install plugins differently (see per-platform sections above).

### How Plugin Caching Works

When a plugin is installed from a marketplace, Claude Code copies it to the local **plugin cache** (`~/.claude/plugins/cache`). The plugin runs from this cached copy, not from the original source.

Each installed version gets its own directory. When updated, the old version is marked as orphaned and automatically removed **7 days later** — this grace period lets concurrent sessions that loaded the old version continue running.

### Path Traversal Limitation

Installed plugins **cannot reference files outside their directory**. Paths like `../shared-utils` will fail after installation because external files are not copied to the cache.

| Pattern | Works in dev (`--plugin-dir .`)? | Works after install? |
|---------|:-------------------------------:|:--------------------:|
| `./scripts/my-tool.sh` | Yes | Yes |
| `../shared/utils.sh` | Yes | **No** |
| `${CLAUDE_PLUGIN_ROOT}/scripts/tool.sh` | Yes | Yes |

**Workaround:** Create symlinks to external files within the plugin directory. Symlinks are preserved in the cache and resolve at runtime:

```bash
ln -s /path/to/shared-utils ./shared-utils
```

### Implications for Scaffolding

- All file references in `plugin.json`, hook commands, and MCP configs must use relative paths starting with `./` or `${CLAUDE_PLUGIN_ROOT}`
- Never use `../` to reach files outside the plugin root
- When bundling external tools, copy them into the plugin rather than referencing them externally
- Use `${CLAUDE_PLUGIN_DATA}` for generated files that need to survive updates (see `references/external-integration.md`)

---

## Installation Scopes

> **Claude Code only.** Other platforms have their own installation mechanisms.

When installing a plugin, users choose a **scope** that controls visibility and persistence:

| Scope | Settings File | Use Case | Shared via Git? |
|-------|--------------|----------|:---------------:|
| `user` | `~/.claude/settings.json` | Personal plugins across all projects (default) | No |
| `project` | `.claude/settings.json` | Team plugins shared via version control | Yes |
| `local` | `.claude/settings.local.json` | Project-specific plugins, gitignored | No |
| `managed` | Managed settings (read-only) | Enterprise-managed plugins | N/A |

### Choosing a Scope

- **`user`** — Default for individual developers. Plugin available in every project.
- **`project`** — Recommended for team tooling. Plugin config is committed to the repo, so all team members get it automatically.
- **`local`** — When a plugin is needed for one project but shouldn't be committed (e.g., personal workflow tools).
- **`managed`** — For enterprise deployments. Plugins are installed by IT administrators and cannot be modified by users.

### CLI Commands

```bash
claude plugin install my-plugin@marketplace --scope project   # team-shared
claude plugin install my-plugin@marketplace --scope local     # gitignored
claude plugin uninstall my-plugin@marketplace --keep-data     # preserve data dir
claude plugin enable my-plugin@marketplace --scope project    # re-enable
claude plugin disable my-plugin@marketplace                   # disable without uninstall
claude plugin update my-plugin@marketplace                    # update to latest
```

---

## Debugging Plugins

### Quick Validation

Run `claude plugin validate` (or `/plugin validate` in a session) to check:
- `plugin.json` syntax and schema validity
- Skill, agent, and command frontmatter correctness
- `hooks/hooks.json` syntax and schema validity

### Debug Mode

Run `claude --debug` to see detailed plugin loading information:
- Which plugins are discovered and loaded
- Manifest parsing errors
- Skill, agent, and hook registration
- MCP server initialization

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Plugin not loading | Invalid `plugin.json` | Run `claude plugin validate` to identify syntax/schema errors |
| Skills not appearing | Wrong directory structure | Components must be at plugin root, not inside `.claude-plugin/` |
| Hooks not firing | `python` not on PATH or wrong `command` in hooks config | Ensure `python` runs `hooks/session-start.py` as in platform templates; on Unix, `chmod +x` is not required when using `python path/to/script` |
| MCP server fails | Missing `${CLAUDE_PLUGIN_ROOT}` | Use the variable for all plugin paths — hardcoded paths break after install |
| Path errors after install | Absolute or `../` paths | All paths must be relative, starting with `./` |
| LSP `Executable not found` | Language server not installed | Install the binary separately (e.g., `npm install -g typescript-language-server`) |
| Plugin changes not visible | Version not bumped | Claude Code uses the version to detect updates — bump before re-publishing |

### Development Workflow

For iterating on a plugin locally without publishing:

```bash
claude --plugin-dir .    # load current directory as a plugin for this session
```

This bypasses caching — changes take effect immediately. Use this during development, then publish via marketplace for distribution.
