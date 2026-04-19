# Hooks Configuration Guide

Practical guide for configuring hook files in bundle-plugin projects. Covers Claude Code (`hooks.json`) and Cursor (`hooks-cursor.json`) formats, with decision guidance for choosing the right events and patterns.

For the complete event reference (all 26 events, matcher filters, blocking behavior), see `platform-adapters.md` — "Claude Code Hook Events". For the official upstream documentation, see [https://code.claude.com/docs/en/hooks](https://code.claude.com/docs/en/hooks).

---

## Which event should I use?

| I want to... | Use this event | Can block? |
|--------------|---------------|:----------:|
| Inject context at session start | `SessionStart` | No |
| Validate or block a tool call before it runs | `PreToolUse` | Yes (exit 2) |
| Run formatting/lint after a write | `PostToolUse` | No |
| React to a tool failure | `PostToolUseFailure` | No |
| Filter or enrich user prompts | `UserPromptSubmit` | Yes (exit 2) |
| Prevent the agent from stopping prematurely | `Stop` | Yes (exit 2) |

These 6 events cover the vast majority of plugin use cases. Claude Code supports 26 events total — see `platform-adapters.md` for the full list including `PermissionRequest`, `SubagentStart/Stop`, `FileChanged`, `ConfigChange`, `WorktreeCreate`, and others.

---

## Configuration schema

### Claude Code — `hooks/hooks.json`

#### Top-level structure

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `description` | string | Recommended | One-line summary shown in Claude Code's `/hooks` menu |
| `hooks` | object | **Yes** | Map of PascalCase event names to handler group arrays |

#### Handler group fields

Each event maps to an array of handler groups. A handler group optionally narrows when the hooks fire:

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `matcher` | string | No | Regex filtering what triggers the hook. What it matches depends on the event (tool name, session source, notification type, etc.) |
| `hooks` | array | **Yes** | Array of handler objects |

#### Handler fields (all types)

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `type` | string | **Yes** | `"command"`, `"http"`, `"prompt"`, or `"agent"` |
| `if` | string | No | Permission rule syntax filter, e.g. `"Bash(git *)"` or `"Edit(*.ts)"`. Only evaluated on tool events (`PreToolUse`, `PostToolUse`, `PostToolUseFailure`, `PermissionRequest`, `PermissionDenied`). On other events a hook with `if` set never runs |
| `timeout` | number | No | Seconds before canceling. Defaults: 600 (command), 30 (prompt), 60 (agent) |
| `statusMessage` | string | No | Custom spinner message while the hook runs |
| `once` | boolean | No | If `true`, runs once per session then is removed. Skills/agents only |

#### Command-specific fields

| Field | Type | Description |
|-------|------|-------------|
| `command` | string | Shell command to execute. Receives JSON on stdin, returns via exit code + stdout |
| `async` | boolean | If `true`, runs in background without blocking |
| `asyncRewake` | boolean | If `true`, runs in background and wakes Claude on exit 2. Implies `async` |
| `shell` | string | `"bash"` (default) or `"powershell"` (Windows) |

#### HTTP-specific fields

| Field | Type | Description |
|-------|------|-------------|
| `url` | string | URL for the POST request. JSON input as body, JSON output in response |
| `headers` | object | Key-value HTTP headers. Values support `$VAR_NAME` interpolation (only vars in `allowedEnvVars`) |
| `allowedEnvVars` | array | Environment variable names allowed for header interpolation |

#### Prompt/Agent-specific fields

| Field | Type | Description |
|-------|------|-------------|
| `prompt` | string | Prompt text sent to a Claude model for single-turn yes/no evaluation |

Agent hooks (`type: "agent"`) spawn a subagent with read-only tools (Read, Grep, Glob) to verify conditions. The subagent returns a JSON decision.

#### Script path rules

- Use `${CLAUDE_PLUGIN_ROOT}` prefix for scripts within the plugin
- Use `python` (not `python3`) for cross-platform compatibility
- Quote paths: `python "${CLAUDE_PLUGIN_ROOT}/hooks/my-script.py"`
- No `../` paths — breaks after marketplace cache install

#### Exit code conventions

| Exit code | Meaning | Effect |
|-----------|---------|--------|
| 0 | Success | Claude Code parses stdout for JSON output |
| 1 | Non-blocking error | Stderr shown as notice in transcript, execution continues |
| 2 | Blocking error | Event-specific: blocks tool call (PreToolUse), rejects prompt (UserPromptSubmit), prevents stopping (Stop), etc. |

Exit code 2 behavior varies by event. The full table is in `platform-adapters.md`. Key rule: only exit code 2 blocks — exit code 1 is always non-blocking.

### Cursor — `hooks/hooks-cursor.json`

Cursor uses a simpler schema. Key differences from Claude Code:

| Aspect | Claude Code | Cursor |
|--------|------------|--------|
| Event casing | PascalCase (`SessionStart`) | camelCase (`sessionStart`) |
| Matcher support | Yes | No |
| Timeout support | Yes | No |
| Handler types | command, http, prompt, agent | command only |
| Top-level `description` | Yes | No |

#### Structure

| Field | Type | Required | Description |
|-------|------|:--------:|-------------|
| `version` | number | **Yes** | Must be `1` |
| `hooks` | object | **Yes** | Map of camelCase event names to handler arrays |

#### Example

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

## Core events for plugin development

### SessionStart

Injects context when a session begins. Most plugins use this for bootstrap prompts listing available skills or project information.

**Input** (stdin): `session_id`, `cwd`, `source` (`"startup"` / `"resume"` / `"clear"` / `"compact"`), `model`, optional `agent_type`.

**Decision control**: stdout text is added as context for Claude. JSON output supports `hookSpecificOutput.additionalContext`. Exit 2 blocks the session from starting. `CLAUDE_ENV_FILE` is available for persisting environment variables.

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
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

### PreToolUse

Validates or blocks tool calls before they execute. The hook receives `tool_name` and `tool_input` on stdin, allowing inspection of the exact parameters Claude is about to use.

**Input** (stdin): `tool_name` (e.g. `"Bash"`, `"Write"`, `"Edit"`), `tool_input` (tool-specific parameters like `command`, `file_path`, `content`), `tool_use_id`.

**Decision control** via `hookSpecificOutput`:

| Field | Description |
|-------|-------------|
| `permissionDecision` | `"allow"` (skip permission prompt), `"deny"` (block), `"ask"` (prompt user), `"defer"` (pause for external UI) |
| `permissionDecisionReason` | For `allow`/`ask`: shown to user. For `deny`: shown to Claude |
| `updatedInput` | Modifies tool input before execution. Replaces entire input object |
| `additionalContext` | String added to Claude's context before the tool executes |

Precedence when multiple hooks disagree: `deny` > `defer` > `ask` > `allow`.

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/guard.py\"",
            "if": "Bash(rm *)",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

### PostToolUse

Runs after a tool completes successfully. Cannot block the tool (it already ran), but can provide feedback or flag issues for Claude to address.

**Input** (stdin): `tool_name`, `tool_input`, `tool_response` (the result the tool returned), `tool_use_id`.

**Decision control**:

| Field | Description |
|-------|-------------|
| `decision` | `"block"` prompts Claude with the `reason` (tool already ran, this is feedback) |
| `reason` | Explanation shown to Claude when `decision` is `"block"` |
| `additionalContext` | Additional context for Claude |

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/format-check.py\"",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

### PostToolUseFailure

Runs when a tool execution fails. Use for error logging, alerts, or providing corrective context to Claude.

**Input** (stdin): `tool_name`, `tool_input`, `tool_use_id`, `error` (string describing the failure), `is_interrupt` (boolean).

**Decision control**: `additionalContext` provides recovery hints to Claude. Cannot block (failure already happened).

```json
{
  "hooks": {
    "PostToolUseFailure": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/on-failure.py\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

### UserPromptSubmit

Runs before Claude processes a user prompt. Can add context, validate input, or block certain prompts entirely.

**Input** (stdin): `prompt` (the user's text).

**Decision control**:

| Field | Description |
|-------|-------------|
| `decision` | `"block"` prevents the prompt from being processed and erases it |
| `reason` | Shown to the user when blocked (not added to context) |
| `additionalContext` | String added to Claude's context |
| `sessionTitle` | Sets the session title (same effect as `/rename`) |

Plain text stdout is also added as context (JSON not required for simple cases).

### Stop

Runs when Claude finishes responding. Can prevent the agent from stopping to enforce completion criteria.

**Input** (stdin): `stop_hook_active` (boolean — `true` if Claude is already continuing due to a prior Stop hook; check to prevent infinite loops), `last_assistant_message` (Claude's final response text).

**Decision control**:

| Field | Description |
|-------|-------------|
| `decision` | `"block"` prevents Claude from stopping |
| `reason` | Required when blocking — tells Claude why it should continue |

---

## Common patterns

### Security guard — block destructive commands

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/block-dangerous.py\"",
            "if": "Bash(rm *)"
          }
        ]
      }
    ]
  }
}
```

Script reads `tool_input.command` from stdin. If dangerous, prints reason to stderr and exits 2. Otherwise exits 0.

### Auto-format after writes

```json
{
  "hooks": {
    "PostToolUse": [
      {
        "matcher": "Write|Edit",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/auto-format.py\"",
            "timeout": 15
          }
        ]
      }
    ]
  }
}
```

Script reads `tool_input.file_path` from stdin, runs the appropriate formatter, and outputs `additionalContext` if formatting changed the file.

### Context injection at session start

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
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Script prints a lightweight prompt listing available skills. Full context is loaded on demand when a skill is first invoked.

### Error recovery hints

```json
{
  "hooks": {
    "PostToolUseFailure": [
      {
        "matcher": "Bash",
        "hooks": [
          {
            "type": "command",
            "command": "python \"${CLAUDE_PLUGIN_ROOT}/hooks/suggest-fix.py\"",
            "timeout": 10
          }
        ]
      }
    ]
  }
}
```

Script reads `error` from stdin, matches against known patterns, and returns `additionalContext` with fix suggestions.

