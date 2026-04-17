# Security Checklist

Structured criteria for evaluating security risks in a bundle-plugin repository. Each category targets a specific file type with pattern-based checks. Use this during a security scan — work through each category, note findings with file paths and line numbers, and compile the report.

## Risk Levels

- **Critical** — Active threat requiring immediate action. Block usage until resolved.
- **Warning** — Suspicious pattern that could be legitimate. Requires human review.
- **Info** — Minor concern, opportunity to apply least-privilege principles.

## Confidence Levels

Each finding has a confidence level that affects scoring and exit codes:

- **deterministic** — Unambiguous pattern match in executable code. Affects score and exit code directly.
- **suspicious** — Context-sensitive match that may be legitimate (e.g. documentation referencing `.env`). Shown in report, affects exit code (at least exit 1), but flagged as "needs review" in output. JSON output includes a `confidence` field for CI to make fine-grained decisions.

### Suspicious Finding Triage (Stage 2)

Static scanning (Stage 1) flags suspicious findings for semantic review. When the auditor agent runs (Stage 2), it must triage each suspicious finding:

1. **Read context** — examine the flagged line and surrounding 5 lines
2. **Classify** — assign one of three dispositions:
   - **FP** (false-positive): benign pattern (e.g. documentation describing `.env`, YAML `superseded-by:` field). Exclude from score.
   - **Accepted** (accepted-risk): real pattern but mitigated or intentional. Keep in report, no score penalty.
   - **TP** (true-positive): genuine security risk. Retain full severity in score.
3. **Record** — include a Suspicious Triage table in the Security section of the audit report for traceability

If the auditor agent is not dispatched (e.g. CLI-only run), suspicious findings remain in the report at their original severity with "needs review" annotation. CI can use the JSON `confidence` field to distinguish them from deterministic findings.

## Cross-Surface Threat Mapping

The same threat class appears across multiple attack surfaces with surface-specific patterns:

<!-- BEGIN:security/threat_mapping -->
| Threat | SKILL.md | Hooks | OpenCode | Agents | Scripts | MCP | Config |
|--------|-------|-------|-------|-------|-------|-------|-------|
| Network exfiltration | SC2 | HK1-HK4, HK13-HK14 | OC5-OC7 | AG3 | BS1 | MC4 | — |
| Sensitive data access | SC1, SC3-SC4 | HK5-HK6, HK15 | OC8-OC10 | AG2 | BS3 | MC1, MC3 | PC4-PC5 |
| Safety overrides | SC9-SC11 | — | OC11-OC12 | AG1, AG4-AG5 | — | — | — |
| System modification | SC5-SC8 | HK8-HK12 | OC1-OC3 | — | BS2, BS4-BS5 | MC2, MC5 | PC1-PC3 |
| Encoding/obfuscation | SC12-SC15 | — | — | — | — | — | — |
<!-- END:security/threat_mapping -->

---

## Category 1: SKILL.md Content Safety (Weight: High)

Scan every `SKILL.md` and every markdown file in `references/` directories.

<!-- BEGIN:security/skill_content -->

### Data Exfiltration Patterns

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| SC1 | Critical | Instructions to read `.env`, `.ssh/`, `credentials`, `secrets`, `tokens`, `api_key` files | `audit_security.py` (suspicious) |
| SC2 | Critical | Instructions to include file contents in responses or outputs sent externally | `audit_security.py` (suspicious) |
| SC3 | Warning | References to reading `~/.config/`, `~/.aws/`, `~/.kube/` or similar config directories | `audit_security.py` (suspicious) |
| SC4 | Warning | Instructions to access `process.env`, `$ENV`, or environment variables beyond documented needs | `audit_security.py` (suspicious) |

### Destructive Operation Patterns

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| SC5 | Critical | Instructions containing `rm -rf`, `rmdir /s`, `del /f` on broad paths | `audit_security.py` |
| SC6 | Critical | Instructions for `git push --force`, `git reset --hard` on main/master | `audit_security.py` |
| SC7 | Critical | Instructions containing `DROP TABLE`, `DELETE FROM` without WHERE clause | `audit_security.py` |
| SC8 | Warning | Instructions to modify or overwrite files outside the project directory | `audit_security.py` |

### Safety Override Patterns

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| SC9 | Critical | Phrases like "ignore previous instructions", "override safety", "disable verification" | `audit_security.py` |
| SC10 | Critical | Instructions to skip git hooks (`--no-verify`), bypass linters, or disable tests | `audit_security.py` |
| SC11 | Warning | Instructions that conflict with `using-<project>` instruction priority (claiming higher priority than user instructions) | `audit_security.py` (suspicious) |

### Encoding and Obfuscation

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| SC12 | Warning | Use of `<EXTREMELY_IMPORTANT>` or similar emphasis tags outside the bootstrap skill | `audit_security.py` |
| SC13 | Critical | Unicode homoglyphs, zero-width characters, right-to-left override characters | `audit_security.py` |
| SC14 | Warning | Base64-encoded content that decodes to instructions or commands | `agent-only` |
| SC15 | Info | Excessively long line (>500 chars) — may indicate obfuscated or machine-generated content | `audit_security.py` |
<!-- END:security/skill_content -->

---

## Category 2: Hook Script Safety (Weight: High)

Scan `hooks/session-start.py` and any other hook scripts or configs in `hooks/`.

<!-- BEGIN:security/hook_scripts -->

### Network Exfiltration

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| HK1 | Critical | `curl`, `wget`, `nc`, `ncat`, `telnet`, `ssh` calls to external hosts | `audit_security.py` |
| HK2 | Critical | Any URL or IP address that is not localhost/127.0.0.1 | `audit_security.py` |
| HK3 | Critical | Piping environment variables or file contents to network commands | `audit_security.py` |
| HK4 | Warning | DNS lookups (`dig`, `nslookup`, `host`) that could encode data in queries | `audit_security.py` |

### Environment Variable Access

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| HK5 | Critical | Reading `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GITHUB_TOKEN`, or similar secrets | `audit_security.py` |
| HK6 | Warning | Reading environment variables beyond `CLAUDE_PLUGIN_ROOT`, `CURSOR_PLUGIN_ROOT` | `audit_security.py` |
| HK7 | Info | Shell hook scripts not using `set -euo pipefail` (missing error handling); not reported for Python-only hooks | `audit_security.py` |

### System Modification

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| HK8 | Critical | Writing to `.bashrc`, `.zshrc`, `.profile`, `.bash_profile`, or shell config files | `audit_security.py` |
| HK9 | Critical | Creating cron jobs, systemd services, or launchd agents | `audit_security.py` |
| HK10 | Critical | Modifying PATH, installing global packages (`npm -g`, `pip install --user`) | `audit_security.py` |
| HK11 | Warning | Creating files outside the project directory or `~/.config/<project>/` | `audit_security.py` |
| HK12 | Warning | Running `chmod` with setuid/setgid bits | `audit_security.py` |

### HTTP Hook Exfiltration

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| HK13 | Critical | `type: "http"` in hooks.json — HTTP hooks send tool input/output to external URLs | `audit_security.py` |
| HK14 | Critical | External URLs in hook config (not localhost/127.0.0.1) | `audit_security.py` |

### Environment Variable Injection

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| HK15 | Warning | Writing to `CLAUDE_ENV_FILE` — injects env vars (including PATH) into all subsequent Bash commands | `audit_security.py` |
<!-- END:security/hook_scripts -->

### Legitimate Hook Baseline

A legitimate `session-start.py` hook should only:
1. Determine plugin root path
2. Read a single SKILL.md file
3. JSON-escape the content
4. Emit platform-appropriate JSON to stdout
5. Exit 0 on failure (no-op, does not block session)

Anything beyond this baseline is suspicious and needs justification.

---

## Category 3: OpenCode Plugin Safety (Weight: High)

Scan `.opencode/plugins/*.js` files.

<!-- BEGIN:security/opencode_plugins -->

### Code Execution Risks

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| OC1 | Critical | `eval()`, `new Function()`, `vm.runInNewContext()` | `audit_security.py` |
| OC2 | Critical | `child_process.exec()`, `child_process.spawn()`, `execSync()` | `audit_security.py` |
| OC3 | Critical | `require('child_process')` or dynamic `import()` of system modules | `audit_security.py` |
| OC4 | Warning | Dynamic `require()` or `import()` with variable paths | `audit_security.py` |

### Network Access

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| OC5 | Critical | `fetch()`, `http.request()`, `https.request()`, `net.connect()` to external hosts | `audit_security.py` |
| OC6 | Critical | WebSocket connections to external servers | `audit_security.py` |
| OC7 | Warning | Any network-related imports (`http`, `https`, `net`, `dgram`, `dns`) | `audit_security.py` |

### Sensitive Data Access

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| OC8 | Critical | `process.env.ANTHROPIC_API_KEY` or similar secret access | `audit_security.py` |
| OC9 | Warning | Broad `process.env` access beyond documented needs | `audit_security.py` |
| OC10 | Warning | Reading files outside the plugin's own directory tree | `agent-only` |

### Message Manipulation

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| OC11 | Critical | Message transforms that inject content not derived from the project's own SKILL.md files | `agent-only` |
| OC12 | Warning | Message transforms that modify existing user messages (beyond prepending bootstrap) | `agent-only` |
| OC13 | Info | Missing guard against double-injection (checking for `EXTREMELY_IMPORTANT` before injecting) | `agent-only` |
<!-- END:security/opencode_plugins -->

### Legitimate Plugin Baseline

A legitimate OpenCode plugin should only:
1. Register the project's `skills/` path in config
2. Read its own SKILL.md files
3. Prepend bootstrap content to the first user message
4. Provide tool mapping documentation

---

## Category 4: Agent Prompt Safety (Weight: Medium)

Scan `agents/*.md` and any `*-prompt.md` files within skill directories.

<!-- BEGIN:security/agent_prompts -->
| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| AG1 | Critical | Instructions to "ignore", "override", or "bypass" safety guidelines or user instructions | `audit_security.py` (suspicious) |
| AG2 | Critical | Instructions to access credentials, secrets, or API keys | `audit_security.py` (suspicious) |
| AG3 | Critical | Instructions to make network requests or exfiltrate data | `audit_security.py` (suspicious) |
| AG4 | Warning | Instructions that expand scope beyond the agent's stated role | `audit_security.py` (suspicious) |
| AG5 | Warning | Instructions that claim elevated permissions ("you have full system access") | `audit_security.py` (suspicious) |
| AG6 | Info | Missing scope constraints (agent prompt doesn't limit what files/actions are in scope) | `agent-only` |
| AG7 | Warning | Agent prompt instructs dispatching other agents/subagents — subagents cannot nest; orchestration must stay in the parent skill | `agent-only` |
<!-- END:security/agent_prompts -->

---

## Category 5: Bundled Script Safety (Weight: Medium)

Scan `scripts/` at the project root and any `scripts/` under skill directories.

<!-- BEGIN:security/bundled_scripts -->
| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| BS1 | Critical | Network calls (`curl`, `wget`, `fetch`) in scripts not documented as needing network | `audit_security.py` |
| BS2 | Critical | System modification patterns (same as HK8-HK12) | `audit_security.py` |
| BS3 | Critical | Reading or transmitting sensitive files or environment variables | `audit_security.py` |
| BS4 | Warning | Scripts that accept unsanitized user input passed to `eval` or command execution | `audit_security.py` |
| BS5 | Warning | Scripts that download and execute remote code | `audit_security.py` |
| BS6 | Info | Scripts missing `set -euo pipefail` or equivalent error handling | `audit_security.py` |
<!-- END:security/bundled_scripts -->

### Legitimate Script Baseline

A version bump script (e.g. `scripts/bump_version.py`) should only:
1. Read `.version-bump.json`
2. Read/write version fields in declared JSON files using `jq`
3. Grep the repo for version strings
4. Output results to stdout

---

## Category 6: MCP Configuration Safety (Weight: Medium)

Scan `.mcp.json`, `.lsp.json`, and MCP server definitions for credential leaks, command execution risks, and transport security.

<!-- BEGIN:security/mcp_config -->
| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| MC1 | Critical | Hardcoded credential in MCP server config (Authorization, api_key, token, secret, password) | `audit_security.py` |
| MC2 | Critical | `headersHelper` field executes arbitrary shell commands | `audit_security.py` |
| MC3 | Warning | Env var value embedded directly instead of using `${VAR}` expansion | `audit_security.py` |
| MC4 | Warning | MCP server URL uses plain HTTP instead of HTTPS | `audit_security.py` |
| MC5 | Info | Absolute path in command field (may not be portable) | `audit_security.py` |
<!-- END:security/mcp_config -->

---

## Category 7: Plugin Configuration Safety (Weight: Medium)

Scan `plugin.json` manifests and hook commands for path and configuration issues.

<!-- BEGIN:security/plugin_config -->

### Path Traversal

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| PC1 | Warning | `../` path references in `plugin.json` component paths, hook commands, or MCP/LSP configs — after marketplace install, the plugin is cached and `../` paths break | `audit_security.py` |
| PC2 | Warning | Absolute paths in plugin configs — installed plugins should use `${CLAUDE_PLUGIN_ROOT}` or relative `./` paths | `audit_security.py` |
| PC3 | Info | Symlinks to external directories — legitimate but should be documented in README | `agent-only` |

### User Configuration

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| PC4 | Warning | `userConfig` field contains key names suggesting secrets (token, key, secret, password, credential, auth) but `sensitive` is not set to `true` | `agent-only` |
| PC5 | Info | `userConfig` sensitive values referenced via `${user_config.KEY}` in skill or agent content — sensitive values should only appear in MCP/LSP/hook configs, not in conversation-visible content | `agent-only` |

### Persistent Data

| Check | Risk | Pattern | Automation |
|-------|------|---------|------------|
| PC6 | Info | Hook scripts or MCP configs write to `${CLAUDE_PLUGIN_ROOT}` — data written here is lost on plugin update; should use `${CLAUDE_PLUGIN_DATA}` instead | `agent-only` |
| PC7 | Info | No dependency caching pattern detected when plugin bundles MCP servers with npm dependencies — consider adding a SessionStart hook for `${CLAUDE_PLUGIN_DATA}` install | `agent-only` |
<!-- END:security/plugin_config -->

---

## Scan Report Template

```markdown
## Security Scan: <project-name>

**Date:** <date>
**Files scanned:** <count>
**Risk summary:** <critical> critical, <warning> warnings, <info> info

### Critical Risks (block until resolved)
- [SEC-C1] <file>:<line> — <check-id>: <description>
- [SEC-C2] ...

### Warnings (needs human review)
- [SEC-W1] <file>:<line> — <check-id>: <description>
- [SEC-W2] ...

### Info (consider improving)
- [SEC-I1] <file>:<line> — <check-id>: <description>

### Files Scanned
| File | Type | Critical | Warning | Info |
|------|------|----------|---------|------|
| hooks/session-start.py | Hook script | 0 | 0 | 0 |
| .opencode/plugins/example.js | OpenCode plugin | 0 | 0 | 1 |
| skills/my-skill/SKILL.md | Skill content | 0 | 0 | 0 |
| agents/example-agent.md | Agent prompt | 0 | 0 | 0 |
| scripts/bump_version.py | Bundled script | 0 | 0 | 0 |

### Recommendations
1. <highest-priority remediation>
2. ...
```

Order recommendations by risk: critical first, then warnings, then info.
