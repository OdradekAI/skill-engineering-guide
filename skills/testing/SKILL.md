---
name: testing
description: "Use when testing a bundle-plugin locally before release — generating dev-marketplace environments, verifying component discovery, running hook smoke tests, and validating cross-platform readiness"
---

# Testing Bundle-Plugins

## Overview

Dynamic verification of a bundle-plugin project: install it locally, confirm components are discoverable, validate hooks fire correctly, and run cross-platform smoke tests. Complements `bundles-forge:auditing` (static analysis) with runtime validation.

**Core principle:** Audit tells you if the structure is correct; testing tells you if it actually works.

**Skill type:** Flexible — adapt the test scope based on target platforms and project maturity.

**Announce at start:** "I'm using the testing skill to verify this plugin works correctly."

## Step 1: Resolve Input & Detect Scope

### Input Normalization

The target must be a local bundle-plugin project (has `package.json` + `skills/`). Remote URLs and archives are not supported — testing requires a local working directory.

### Scope Detection

| Target | Mode |
|--------|------|
| Project root with multiple platforms | **Full testing** — all 5 test phases |
| Project root with single platform | **Platform testing** — phases 1-4 for the target platform |
| Single skill directory | **Skill-only testing** — phase 3 (component discovery) only |

---

## Phase 1: Local Test Environment

Generate a temporary dev-marketplace for local installation testing.

### For Claude Code

1. Create `../dev-marketplace/` adjacent to the project directory
2. Generate `.claude-plugin/marketplace.json` pointing to the project:

```json
{
  "name": "<project-name>-dev",
  "owner": { "name": "dev" },
  "plugins": [
    {
      "name": "<project-name>",
      "source": "../<project-directory-name>"
    }
  ]
}
```

3. Instruct the user:

```
Dev marketplace created at ../dev-marketplace/

To install locally:
  /plugin marketplace add ./dev-marketplace
  /plugin install <project-name>@<project-name>-dev

To reload after changes:
  /plugin marketplace update <project-name>-dev

To clean up when done:
  /plugin marketplace remove <project-name>-dev
```

### For Cursor

Cursor plugins are installed from local paths directly:

```
To test locally in Cursor:
  1. Open Cursor Settings → Extensions → Install from Path
  2. Select the project root directory
  3. Reload Cursor to pick up changes
```

### For Other Platforms

- **Codex:** Symlink `skills/` into `~/.agents/skills/` per INSTALL.md
- **OpenCode:** Register the plugin path in `.opencode/plugins/`
- **Gemini CLI:** Point the extension config to the local directory

See `references/platform-test-guides.md` for platform-specific setup instructions.

---

## Phase 2: Hook Smoke Tests

Verify hooks execute without errors by running them directly.

### SessionStart Hook

```bash
python hooks/session-start.py
```

**Expected:** Exits 0, prints a one-line prompt containing the project name and available skills. No stderr output.

**Verify output format:**
- If `CLAUDE_PLUGIN_ROOT` is set: valid JSON with `hookSpecificOutput.additionalContext`
- If `CURSOR_PLUGIN_ROOT` is set: valid JSON with `additional_context`
- Neither: plain text

### Custom Hooks (if configured)

If the project defines `PreToolUse` or `PostToolUse` hooks in `hooks.json`, run each referenced script directly and verify:
- PreToolUse scripts: exit 0 on a valid project, exit 2 to block writes on critical issues
- PostToolUse scripts: always exit 0, warnings go to stderr

### OpenClaw Hook-Pack (if present)

Verify `hooks/openclaw-bootstrap/HOOK.md` has valid YAML frontmatter with `events` declaration, and `handler.js` uses ESM `export default`.

---

## Phase 3: Component Discovery

Verify that all declared components can be found by the host platform.

### Skills

For each directory under `skills/`:
- [ ] Contains `SKILL.md`
- [ ] Frontmatter has `name` and `description`
- [ ] `name` matches directory name
- [ ] `description` starts with "Use when..."

### Commands

For each `.md` file under `commands/`:
- [ ] Has YAML frontmatter with `description`
- [ ] Cross-reference (`<project>:<skill>`) resolves to an existing skill

### Agents

For each `.md` file under `agents/`:
- [ ] Has YAML frontmatter
- [ ] Body has 5+ non-empty lines (self-contained protocol)

### Platform Manifests

For each target platform:
- [ ] Manifest file exists and is valid JSON
- [ ] Paths in manifest resolve to existing files/directories
- [ ] Version matches `package.json` version

---

## Phase 4: Cross-Platform Readiness

Generate a platform-specific test checklist based on `references/platform-test-guides.md` and known limitations from `bundles-forge:scaffolding` — `references/platform-adapters.md`.

### Known Limitations to Verify

| Platform | Limitation | Test |
|----------|-----------|------|
| Claude Code | Plugin caching breaks `../` paths | Verify no `../` in hook commands or manifest paths |
| Cursor | Bootstrap lost after `/clear` | Verify session-start runs independently of prior context |
| Codex | No hook bootstrap | Verify AGENTS.md or INSTALL.md has manual setup instructions |
| OpenCode | Plugin JS must use ESM | Verify `export default` in `.opencode/plugins/*.js` |
| Gemini CLI | Extension needs `contextFileName` | Verify `gemini-extension.json` has `contextFileName` field |
| OpenClaw | Hook-pack wiring uncertain | Document as known risk in test report |

---

## Phase 5: Test Report

Generate a test report summarizing all findings.

### Report Structure

```markdown
# Test Report: <project-name>

**Date:** YYYY-MM-DD
**Scope:** [Full / Platform / Skill-only]
**Platforms tested:** [list]

## Results

| Phase | Status | Details |
|-------|--------|---------|
| 1. Local Environment | PASS/FAIL/SKIP | ... |
| 2. Hook Smoke Tests | PASS/FAIL/SKIP | ... |
| 3. Component Discovery | PASS/FAIL/SKIP | N skills, M commands, K agents |
| 4. Cross-Platform | PASS/FAIL/SKIP | ... |

## Issues Found

### Critical
- (blocks release)

### Warnings
- (should fix before release)

## Recommendations

- ...
```

**Report location:** `.bundles-forge/audits/<timestamp>-test-report.md`

---

## Integration with Releasing

In the releasing pipeline, testing runs after auditing and before version bump:

```
audit → test → version bump → publish
```

If testing reveals critical issues, the release pipeline is blocked until they are resolved.

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Skipping local install test | Always test with a real dev-marketplace — file discovery differs from file existence |
| Testing only on one platform | Run cross-platform checklist for every target platform |
| Ignoring hook exit codes | Hooks must exit 0 to avoid blocking the host; test all code paths |
| Not cleaning up dev-marketplace | Always remove dev-marketplace after testing |
| Testing after version bump | Test before bumping — avoid releasing a broken version |

## Inputs

- `project-directory` (required) — bundle-plugin project root

## Outputs

- `test-report` — comprehensive test results written to `.bundles-forge/audits/`
- `dev-marketplace` (temporary) — local marketplace directory for installation testing

## Integration

**Called by:**
- **bundles-forge:releasing** — pre-release dynamic verification (after audit, before version bump)
- User directly — standalone local testing during development

**Calls:**
- (none — testing is a pure executor, does not dispatch other skills)
