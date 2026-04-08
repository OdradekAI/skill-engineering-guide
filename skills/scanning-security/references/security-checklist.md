# Security Checklist

Structured criteria for evaluating security risks in a bundles repository. Each category targets a specific file type with pattern-based checks. Use this during a security scan — work through each category, note findings with file paths and line numbers, and compile the report.

## Risk Levels

- **Critical** — Active threat requiring immediate action. Block usage until resolved.
- **Warning** — Suspicious pattern that could be legitimate. Requires human review.
- **Info** — Minor concern, opportunity to apply least-privilege principles.

---

## Category 1: SKILL.md Content Safety (Weight: High)

Scan every `SKILL.md` and every markdown file in `references/` directories.

### Data Exfiltration Patterns

| Check | Risk | Pattern |
|-------|------|---------|
| SC1 | Critical | Instructions to read `.env`, `.ssh/`, `credentials`, `secrets`, `tokens`, `api_key` files |
| SC2 | Critical | Instructions to include file contents in responses or outputs sent externally |
| SC3 | Warning | References to reading `~/.config/`, `~/.aws/`, `~/.kube/` or similar config directories |
| SC4 | Warning | Instructions to access `process.env`, `$ENV`, or environment variables beyond documented needs |

### Destructive Operation Patterns

| Check | Risk | Pattern |
|-------|------|---------|
| SC5 | Critical | Instructions containing `rm -rf`, `rmdir /s`, `del /f` on broad paths |
| SC6 | Critical | Instructions for `git push --force`, `git reset --hard` on main/master |
| SC7 | Critical | Instructions containing `DROP TABLE`, `DELETE FROM` without WHERE clause |
| SC8 | Warning | Instructions to modify or overwrite files outside the project directory |

### Safety Override Patterns

| Check | Risk | Pattern |
|-------|------|---------|
| SC9 | Critical | Phrases like "ignore previous instructions", "override safety", "disable verification" |
| SC10 | Critical | Instructions to skip git hooks (`--no-verify`), bypass linters, or disable tests |
| SC11 | Warning | Instructions that conflict with `using-<project>` instruction priority (claiming higher priority than user instructions) |
| SC12 | Warning | Use of `<EXTREMELY_IMPORTANT>` or similar emphasis tags outside the bootstrap skill |

### Encoding and Obfuscation

| Check | Risk | Pattern |
|-------|------|---------|
| SC13 | Critical | Unicode homoglyphs, zero-width characters, right-to-left override characters |
| SC14 | Warning | Base64-encoded content that decodes to instructions or commands |
| SC15 | Info | Excessively long lines that might hide content beyond visible editor width |

---

## Category 2: Hook Script Safety (Weight: High)

Scan `hooks/session-start`, `hooks/run-hook.cmd`, and any other executable in `hooks/`.

### Network Exfiltration

| Check | Risk | Pattern |
|-------|------|---------|
| HK1 | Critical | `curl`, `wget`, `nc`, `ncat`, `telnet`, `ssh` calls to external hosts |
| HK2 | Critical | Any URL or IP address that is not localhost/127.0.0.1 |
| HK3 | Critical | Piping environment variables or file contents to network commands |
| HK4 | Warning | DNS lookups (`dig`, `nslookup`, `host`) that could encode data in queries |

### Environment Variable Access

| Check | Risk | Pattern |
|-------|------|---------|
| HK5 | Critical | Reading `ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, `GITHUB_TOKEN`, or similar secrets |
| HK6 | Warning | Reading environment variables beyond `CLAUDE_PLUGIN_ROOT`, `CURSOR_PLUGIN_ROOT`, `COPILOT_CLI` |
| HK7 | Info | Not using `set -euo pipefail` (missing error handling) |

### System Modification

| Check | Risk | Pattern |
|-------|------|---------|
| HK8 | Critical | Writing to `.bashrc`, `.zshrc`, `.profile`, `.bash_profile`, or shell config files |
| HK9 | Critical | Creating cron jobs, systemd services, or launchd agents |
| HK10 | Critical | Modifying PATH, installing global packages (`npm -g`, `pip install --user`) |
| HK11 | Warning | Creating files outside the project directory or `~/.config/<project>/` |
| HK12 | Warning | Running `chmod` with setuid/setgid bits |

### Legitimate Hook Baseline

A legitimate `session-start` hook should only:
1. Determine plugin root path
2. Read a single SKILL.md file
3. JSON-escape the content
4. Emit platform-appropriate JSON to stdout

Anything beyond this baseline is suspicious and needs justification.

---

## Category 3: OpenCode Plugin Safety (Weight: High)

Scan `.opencode/plugins/*.js` files.

### Code Execution Risks

| Check | Risk | Pattern |
|-------|------|---------|
| OC1 | Critical | `eval()`, `new Function()`, `vm.runInNewContext()` |
| OC2 | Critical | `child_process.exec()`, `child_process.spawn()`, `execSync()` |
| OC3 | Critical | `require('child_process')` or dynamic `import()` of system modules |
| OC4 | Warning | Dynamic `require()` or `import()` with variable paths |

### Network Access

| Check | Risk | Pattern |
|-------|------|---------|
| OC5 | Critical | `fetch()`, `http.request()`, `https.request()`, `net.connect()` to external hosts |
| OC6 | Critical | WebSocket connections to external servers |
| OC7 | Warning | Any network-related imports (`http`, `https`, `net`, `dgram`, `dns`) |

### Sensitive Data Access

| Check | Risk | Pattern |
|-------|------|---------|
| OC8 | Critical | `process.env.ANTHROPIC_API_KEY` or similar secret access |
| OC9 | Warning | Broad `process.env` access beyond documented needs |
| OC10 | Warning | Reading files outside the plugin's own directory tree |

### Message Manipulation

| Check | Risk | Pattern |
|-------|------|---------|
| OC11 | Critical | Message transforms that inject content not derived from the project's own SKILL.md files |
| OC12 | Warning | Message transforms that modify existing user messages (beyond prepending bootstrap) |
| OC13 | Info | Missing guard against double-injection (checking for `EXTREMELY_IMPORTANT` before injecting) |

### Legitimate Plugin Baseline

A legitimate OpenCode plugin should only:
1. Register the project's `skills/` path in config
2. Read its own SKILL.md files
3. Prepend bootstrap content to the first user message
4. Provide tool mapping documentation

---

## Category 4: Agent Prompt Safety (Weight: Medium)

Scan `agents/*.md` and any `*-prompt.md` files within skill directories.

| Check | Risk | Pattern |
|-------|------|---------|
| AG1 | Critical | Instructions to "ignore", "override", or "bypass" safety guidelines or user instructions |
| AG2 | Critical | Instructions to access credentials, secrets, or API keys |
| AG3 | Critical | Instructions to make network requests or exfiltrate data |
| AG4 | Warning | Instructions that expand scope beyond the agent's stated role |
| AG5 | Warning | Instructions that claim elevated permissions ("you have full system access") |
| AG6 | Info | Missing scope constraints (agent prompt doesn't limit what files/actions are in scope) |

---

## Category 5: Bundled Script Safety (Weight: Medium)

Scan `scripts/` directory and any executable files within skill directories.

| Check | Risk | Pattern |
|-------|------|---------|
| BS1 | Critical | Network calls (`curl`, `wget`, `fetch`) in scripts not documented as needing network |
| BS2 | Critical | System modification patterns (same as HK8-HK12) |
| BS3 | Critical | Reading or transmitting sensitive files or environment variables |
| BS4 | Warning | Scripts that accept unsanitized user input passed to `eval` or command execution |
| BS5 | Warning | Scripts that download and execute remote code |
| BS6 | Info | Scripts missing `set -euo pipefail` or equivalent error handling |

### Legitimate Script Baseline

The standard `bump-version.sh` should only:
1. Read `.version-bump.json`
2. Read/write version fields in declared JSON files using `jq`
3. Grep the repo for version strings
4. Output results to stdout

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
| hooks/session-start | Hook script | 0 | 0 | 0 |
| .opencode/plugins/example.js | OpenCode plugin | 0 | 0 | 1 |
| skills/my-skill/SKILL.md | Skill content | 0 | 0 | 0 |
| agents/reviewer.md | Agent prompt | 0 | 0 | 0 |
| scripts/bump-version.sh | Bundled script | 0 | 0 | 0 |

### Recommendations
1. <highest-priority remediation>
2. ...
```

Order recommendations by risk: critical first, then warnings, then info.
