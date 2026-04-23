# External Integration: CLI vs MCP

Shared reference for choosing and implementing external service integrations in bundle-plugins. Referenced by `bundles-forge:scaffolding` (optional components), `bundles-forge:blueprinting` (interview phase 6), and `bundles-forge:authoring` (external tool references).

## Decision Tree

When a skill needs to interact with an external tool or service, choose the lightest integration that meets the requirement:

```
Does the skill need external tool access?
├─ No → No integration needed
└─ Yes → Is it stateless, single-execution, with clear input/output?
   ├─ Yes → Level 1: CLI (bin/ executable + allowed-tools)
   └─ No → Does it need persistent connection, rich querying, multi-tool discovery, or authenticated external service?
      ├─ Yes → Level 2: MCP server (.mcp.json or plugin.json mcpServers)
      └─ Both → Level 3: CLI wrapper launching MCP stdio server (npx pattern)
```

### Level 1: CLI — Preferred Default

Use CLI when the tool interaction is **stateless and single-shot**: run a command, get output, done.

| Good fit | Examples |
|----------|---------|
| Linting / validation | `bundles-forge audit-skill` |
| Version management | `bundles-forge bump-version` |
| Data transformation | `jq`, `yq`, format converters |
| File generation | Template rendering, code generation |
| Git operations | `git status`, `git diff` |

**Implementation:**
- Place executables in `bin/` — they are added to `$PATH` while the plugin is enabled
- Declare in frontmatter: `allowed-tools: Bash(bin/my-tool *)` or `Python(scripts/my-tool.py *)`
- No process management, no connection lifecycle, no authentication state

### Handling Missing Dependencies

When a skill depends on external CLI tools that may not be installed, the skill must detect missing tools and provide actionable feedback — not raw shell errors.

```
CLI tool not in PATH?
├─ required → Stop. Print install command. Do not continue.
└─ optional → Warn. Skip dependent feature. Continue execution.
```

**Required tool missing — stop with install guidance:**

```
{tool} is not installed. Install with: {command}. Then retry.
```

**Optional tool missing — warn and degrade gracefully:**

```
{tool} not found — {feature} will be skipped. Install with: {command} for full functionality.
```

Each skill that declares external CLI tools in `allowed-tools` should include a `## Prerequisites` section with a check/install table. See `bundles-forge:authoring` — `references/skill-writing-guide.md` "Prerequisites Writing" for the standard format.

### Level 2: MCP Server — When CLI Falls Short

Use MCP when the integration needs **stateful connections, rich discovery, or authenticated external services**.

| Good fit | Examples |
|----------|---------|
| External SaaS APIs with auth | Sentry, GitHub, Jira, Notion |
| Database querying | PostgreSQL, MySQL via MCP servers |
| Multi-tool discovery | A service exposing many related operations |
| Real-time data streams | Monitoring dashboards, log tailing |
| Browser automation | Playwright MCP |

**Implementation:** See [MCP Generation Guide](#mcp-generation-guide) below.

### Level 3: CLI + MCP Hybrid

When a CLI tool *launches* an MCP server via stdio transport. The CLI is the entry point, MCP provides the protocol.

```json
{
  "mcpServers": {
    "my-tool": {
      "command": "npx",
      "args": ["-y", "@scope/my-mcp-server"],
      "env": {}
    }
  }
}
```

This is common with npm-distributed MCP servers. The CLI (`npx`) handles installation, the MCP protocol handles tool discovery and execution.

---

## MCP Generation Guide

### Claude Code: `.mcp.json` (Project-Scope)

The primary MCP configuration for Claude Code. Placed at the project root, auto-discovered by the platform.

Use the template from `assets/mcp-json.md`. Two transport patterns:

**stdio transport** (bundled server — runs as a local process):

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/<server-script>",
      "args": ["--config", "${CLAUDE_PLUGIN_ROOT}/config.json"],
      "env": {
        "API_KEY": "${API_KEY}"
      }
    }
  }
}
```

**http transport** (remote service):

```json
{
  "mcpServers": {
    "<server-name>": {
      "type": "http",
      "url": "https://<service-endpoint>/mcp"
    }
  }
}
```

Key rules:
- Use `${CLAUDE_PLUGIN_ROOT}` for paths to bundled files (survives plugin updates)
- Use `${VAR}` syntax for secrets — never hardcode API keys or tokens
- Use `${VAR:-default}` for optional env vars with sensible defaults
- Prefer `http` transport for remote services (SSE is deprecated)

### Claude Code: `plugin.json` inline `mcpServers`

Alternative to `.mcp.json` — declare MCP servers directly in the plugin manifest. Servers start automatically when the plugin is enabled.

```json
{
  "name": "my-plugin",
  "version": "1.0.0",
  "mcpServers": {
    "plugin-api": {
      "command": "${CLAUDE_PLUGIN_ROOT}/servers/api-server",
      "args": ["--port", "8080"]
    }
  }
}
```

Use this when the MCP server is integral to the plugin (always needed). Use `.mcp.json` when the server is optional or project-specific.

### Cursor: MCP Configuration

Cursor supports MCP through its settings system rather than `.mcp.json`. The configuration lives in `.cursor/mcp.json` or the IDE's MCP settings panel.

```json
{
  "mcpServers": {
    "<server-name>": {
      "command": "npx",
      "args": ["-y", "@scope/my-mcp-server"],
      "env": {}
    }
  }
}
```

Key differences from Claude Code:
- No `${CLAUDE_PLUGIN_ROOT}` — use relative paths or `npx` for portability
- No plugin-provided auto-start — users configure MCP servers via Cursor's settings UI or `.cursor/mcp.json`
- The `.mcp.json` at project root is not auto-discovered by Cursor
- Document Cursor MCP setup instructions in the project README when generating for both platforms

### Platform Comparison

| Capability | Claude Code | Cursor |
|-----------|-------------|--------|
| Config file | `.mcp.json` (project root) | `.cursor/mcp.json` or settings UI |
| Auto-discovery | Yes | No (manual config) |
| Plugin-provided MCP | Yes (`plugin.json mcpServers`) | No |
| Env var expansion | `${VAR}`, `${VAR:-default}` | `${VAR}` |
| Plugin root variable | `${CLAUDE_PLUGIN_ROOT}` | Not available |
| Transport types | stdio, http, sse | stdio, http, sse |

---

## Optional Component Removal

When removing external integrations (MCP servers, CLI executables, or LSP servers) from a bundle-plugin:

### Removing MCP Servers

1. **Delete `.mcp.json`** if it only contained servers being removed; otherwise edit to remove specific entries
2. **Clean `plugin.json`** — remove the `mcpServers` field from any platform manifest that declared inline servers
3. **Update skill references** — find skills that reference the removed MCP tools (search for `mcp__<server-name>` in `allowed-tools` and skill body). Either:
   - Remove the reference entirely
   - Replace with a CLI alternative (downgrade to Level 1)
4. **Update README** — remove MCP setup instructions for affected platforms
5. **Run inspector** — verify structural integrity after removal

### Removing CLI Executables

1. **Delete files** from `bin/` directory
2. **Update `allowed-tools`** — remove `Bash(bin/<tool> *)` from affected skills' frontmatter
3. **Update skill body** — remove or replace instructions that reference the removed tool
4. **Run inspector** — verify structural integrity

### Removing LSP Servers

1. **Delete `.lsp.json`** if it only contained servers being removed; otherwise edit to remove specific entries
2. **Update README** — remove LSP-related documentation
3. **Run inspector** — verify structural integrity

### Downgrading MCP to CLI

When an MCP server is overkill and a CLI tool would suffice:

1. **Create the CLI replacement** in `bin/` or `scripts/`
2. **Update skills** — replace MCP tool references with CLI invocations in `allowed-tools` and body
3. **Remove MCP config** — follow "Removing MCP Servers" steps above
4. **Update README** — replace MCP setup instructions with CLI usage

---

## User Configuration (`userConfig`)

> **Claude Code only.** Other platforms do not support `userConfig`.

When skills need values that vary per user — API keys, endpoints, tokens, team IDs — declare them in `plugin.json` under `userConfig`. Claude Code prompts the user for these values when the plugin is enabled, instead of requiring manual `settings.json` edits.

### When to Use

| Signal | Use `userConfig` |
|--------|-----------------|
| Skill references an API key or token | Yes — declare with `sensitive: true` |
| Skill references a team-specific endpoint or base URL | Yes — declare with `sensitive: false` |
| MCP server needs auth credentials at startup | Yes — reference via `${user_config.KEY}` in env |
| Value is hardcoded `${API_KEY}` in `.mcp.json` | Migrate to `userConfig` for automatic prompting |
| Value is project-specific (not per-user) | No — use standard env vars or `.env` |

### Schema

```json
{
  "userConfig": {
    "api_endpoint": {
      "description": "Your team's API endpoint",
      "sensitive": false
    },
    "api_token": {
      "description": "API authentication token",
      "sensitive": true
    }
  }
}
```

Keys must be valid identifiers (letters, numbers, underscores). Each key is available for substitution as `${user_config.KEY}` in MCP server configs, LSP server configs, hook commands, and (for non-sensitive values only) skill and agent content.

### Storage and Access

- **Non-sensitive values** → `settings.json` under `pluginConfigs[<plugin-id>].options`
- **Sensitive values** → system keychain (or `~/.claude/.credentials.json` as fallback). Keychain storage has ~2 KB total limit — keep sensitive values small
- **Environment variables** → all values are exported to plugin subprocesses as `CLAUDE_PLUGIN_OPTION_<KEY>` (uppercased key)

### Sensitive Value Rules

Mark a field as `sensitive: true` when the value is a secret (token, password, API key, private key). Sensitive values:
- Are stored in the system keychain, not in plaintext config files
- Cannot be referenced via `${user_config.KEY}` in skill or agent content (only in MCP/LSP/hook configs)
- Are available to scripts via the `CLAUDE_PLUGIN_OPTION_<KEY>` environment variable

### Wiring with MCP Servers

Replace hardcoded `${API_KEY}` patterns with `userConfig`-backed values:

```json
{
  "userConfig": {
    "sentry_token": {
      "description": "Sentry API token",
      "sensitive": true
    }
  },
  "mcpServers": {
    "sentry": {
      "command": "npx",
      "args": ["-y", "@sentry/mcp-server"],
      "env": {
        "SENTRY_AUTH_TOKEN": "${user_config.sentry_token}"
      }
    }
  }
}
```

This replaces the previous `"SENTRY_AUTH_TOKEN": "${SENTRY_AUTH_TOKEN}"` pattern. The advantage: users are prompted automatically at plugin enable time, and the value is stored securely in the keychain.

---

## Persistent Data (`${CLAUDE_PLUGIN_DATA}`)

> **Claude Code only.** Other platforms do not provide a persistent data directory.

### The Problem

`${CLAUDE_PLUGIN_ROOT}` points to the plugin's installation directory. When the plugin updates, this path changes — the old directory is orphaned (cleaned up after 7 days) and a fresh copy is made. Any data written to `${CLAUDE_PLUGIN_ROOT}` is lost on update.

### The Solution

`${CLAUDE_PLUGIN_DATA}` is a persistent directory (`~/.claude/plugins/data/{id}/`) that survives plugin updates. Use it for:
- Installed dependencies (`node_modules`, Python virtualenvs)
- Generated caches, databases, compiled assets
- Any file that should persist across plugin versions

The directory is created automatically the first time the variable is referenced. It is deleted when the plugin is uninstalled from all scopes (unless `--keep-data` is passed).

### Dependency Caching Pattern

The canonical pattern for plugins that bundle an MCP server with npm dependencies:

**SessionStart hook** — compares the bundled `package.json` against the cached copy, reinstalls if they differ:

```json
{
  "hooks": {
    "SessionStart": [
      {
        "hooks": [
          {
            "type": "command",
            "command": "diff -q \"${CLAUDE_PLUGIN_ROOT}/package.json\" \"${CLAUDE_PLUGIN_DATA}/package.json\" >/dev/null 2>&1 || (cd \"${CLAUDE_PLUGIN_DATA}\" && cp \"${CLAUDE_PLUGIN_ROOT}/package.json\" . && npm install) || rm -f \"${CLAUDE_PLUGIN_DATA}/package.json\""
          }
        ]
      }
    ]
  }
}
```

The `diff` exits nonzero when the stored copy is missing or differs, covering both first run and dependency-changing updates. If `npm install` fails, the trailing `rm` removes the copy so the next session retries.

**MCP server config** — points `NODE_PATH` to the persisted `node_modules`:

```json
{
  "mcpServers": {
    "my-server": {
      "command": "node",
      "args": ["${CLAUDE_PLUGIN_ROOT}/server.js"],
      "env": {
        "NODE_PATH": "${CLAUDE_PLUGIN_DATA}/node_modules"
      }
    }
  }
}
```

### When to Use Which Directory

| Directory | Use For | Survives Update? |
|-----------|---------|:----------------:|
| `${CLAUDE_PLUGIN_ROOT}` | Bundled code, scripts, templates, config (read-only) | No |
| `${CLAUDE_PLUGIN_DATA}` | Installed deps, caches, generated state (read-write) | Yes |

---

## LSP Servers (`.lsp.json`)

Language Server Protocol servers provide real-time code intelligence: instant diagnostics, go-to-definition, find references, hover info.

### When to Include

Add LSP support when skills involve **language-specific code intelligence** — the plugin works with a specific programming language and users benefit from real-time error checking or navigation.

### Configuration Format

Place `.lsp.json` at the plugin root:

```json
{
  "go": {
    "command": "gopls",
    "args": ["serve"],
    "extensionToLanguage": {
      ".go": "go"
    }
  }
}
```

Can also be declared inline in `plugin.json` under `lspServers`.

### Required Fields

| Field | Description |
|-------|-------------|
| `command` | The LSP binary to execute (must be in user's PATH) |
| `extensionToLanguage` | Maps file extensions to language identifiers |

### Optional Fields

| Field | Description | Default |
|-------|-------------|---------|
| `args` | Command-line arguments | `[]` |
| `transport` | `stdio` or `socket` | `stdio` |
| `env` | Environment variables | `{}` |
| `initializationOptions` | Options passed during LSP initialization | `{}` |
| `settings` | Settings via `workspace/didChangeConfiguration` | `{}` |
| `workspaceFolder` | Workspace folder path | Project root |
| `startupTimeout` | Max startup wait (ms) | Platform default |
| `shutdownTimeout` | Max shutdown wait (ms) | Platform default |
| `restartOnCrash` | Auto-restart on crash | `false` |
| `maxRestarts` | Max restart attempts | Platform default |

### Important: Binary Installation

LSP plugins configure how Claude Code connects to a language server — they do **not** include the server binary itself. Document the required installation command in README:

```markdown
## Prerequisites
Install the Go language server: `go install golang.org/x/tools/gopls@latest`
```

If the binary is missing, users see `Executable not found in $PATH` in the `/plugin` Errors tab.

---

## Output Styles (`output-styles/`)

Output style definitions control how Claude Code formats its responses when a particular style is active.

### When to Include

Add output styles when the plugin needs custom response formatting — terse mode for experienced users, verbose mode for debugging, structured mode for machine consumption.

### Format

Place markdown files in `output-styles/` at the plugin root. Each file defines one named style:

```markdown
---
name: terse
description: Minimal output — code changes only, no explanations
---

Respond with only the essential information:
- Show code changes as diffs
- Skip explanations unless the user asks
- No greetings or sign-offs
```

Can also be placed in a custom directory and pointed to via `"outputStyles": "./styles/"` in `plugin.json`.

---

## Default Settings (`settings.json`)

A `settings.json` file at the plugin root provides default configuration applied when the plugin is enabled.

### When to Include

Add default settings when the plugin should activate a default agent or configure specific behavior on install.

### Current Scope

Only [`agent`](/en/sub-agents) settings are currently supported:

```json
{
  "agent": "my-agent-name"
}
```

This sets the default agent for sessions where the plugin is active. As the settings system expands, additional fields may become available.
