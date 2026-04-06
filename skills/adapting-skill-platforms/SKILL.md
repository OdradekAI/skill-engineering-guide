---
name: adapting-skill-platforms
description: "Use when adding Claude Code, Cursor, Codex, OpenCode, Copilot CLI, or Gemini CLI support to an existing skill project, when platform manifests need updating or fixing, when migrating a skill project to a new platform, or when platform-specific hooks or configuration need changes"
---

# Adapting Skill Platforms

## Overview

Add support for a new AI coding platform to an existing skill project. Each platform has its own manifest format, discovery mechanism, and hook wiring. This skill generates the correct adapter files and wires them into the project.

**Core principle:** One project, many platforms. Platform adapters translate the same skills into each platform's native format.

**Announce at start:** "I'm using the adapting-skill-platforms skill to add <platform> support."

## The Process

```
Detect current platforms
  → Identify target platform
  → Generate adapter files
  → Update version sync
  → Update hooks (if needed)
  → Update README
  → Verify
```

### Step 1: Detect Current Platforms

Scan for existing manifests:

| File | Platform |
|------|----------|
| `.claude-plugin/plugin.json` | Claude Code |
| `.cursor-plugin/plugin.json` | Cursor |
| `.codex/INSTALL.md` | Codex |
| `.opencode/plugins/*.js` | OpenCode |
| `gemini-extension.json` | Gemini CLI |

### Step 2: Identify Target

What platform to add? Read `references/platform-adapters.md` for platform documentation and wiring details, then read the specific template files from `assets/<platform>/`.

### Step 3: Generate Adapter

Create all files for the target platform using the template files from `assets/<platform>/`. Replace all `<project-name>` placeholders with the actual project name.

**Key differences between platforms:**

| Aspect | Claude Code | Cursor | Codex | OpenCode | Gemini |
|--------|------------|--------|-------|----------|--------|
| Discovery | Convention | Explicit paths | Symlink | Plugin config | Context file |
| Hook format | `hooks.json` (PascalCase) | `hooks-cursor.json` (camelCase) | N/A | JS plugin | N/A |
| Skills path | Auto `skills/` | Declared in manifest | Symlink | Registered in JS | `@` includes |

### Step 4: Update Version Sync

Add new manifest files to `.version-bump.json` if they contain version strings. Use `seg:managing-skill-versions` for version infrastructure.

### Step 5: Update Hooks

If the platform uses session hooks (Claude Code, Cursor, Copilot CLI), ensure `session-start` handles the new platform's JSON format. Platform detection uses environment variables:

| Variable | Platform |
|----------|----------|
| `CURSOR_PLUGIN_ROOT` | Cursor |
| `CLAUDE_PLUGIN_ROOT` (without `COPILOT_CLI`) | Claude Code |
| `COPILOT_CLI` | Copilot CLI |

### Step 6: Update Documentation

- Add installation section to README for the new platform
- Create platform-specific install doc if needed (e.g., `.codex/INSTALL.md`)

### Step 7: Verify

- New manifest is valid JSON (where applicable)
- Version sync includes new files: `bump-version.sh --check`
- Hooks handle new platform: test with appropriate env var
- README has installation instructions

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Copying template without customizing | Replace every `<project-name>` placeholder |
| Forgetting `.version-bump.json` entry | Every version-bearing manifest needs tracking |
| Wrong hook format (PascalCase vs camelCase) | Claude Code: `SessionStart`, Cursor: `sessionStart` |
| Missing `run-hook.cmd` for Windows | Include if any hook platform is targeted |

## Integration

**Called by:**
- **seg:designing-skill-projects** — when adding platforms to a new project

**Calls:**
- **seg:auditing-skill-projects** — verify after adaptation

**Pairs with:**
- **seg:managing-skill-versions** — version sync for new manifests
