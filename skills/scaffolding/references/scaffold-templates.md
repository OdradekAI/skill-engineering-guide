# Scaffold Templates

Index of ready-to-use template files for generating new bundle-plugins. All templates live in `assets/` — read each file directly when generating.

Replace all placeholders before writing to the target project.

## Placeholder Reference

| Placeholder | Source |
|-------------|--------|
| `<project-name>` | Design: project name (kebab-case) |
| `<Project Name>` | Title-cased project name |
| `<author-name>` | User or git config |
| `<author-email>` | User or git config |
| `<repo-url>` | User-provided or constructed |
| `<one-line description>` | From design or user |

---

## Template Inventory

### Infrastructure (always generated)

| Template File | Target Path | Purpose |
|---------------|-------------|---------|
| `assets/hooks/session-start.py` | `hooks/session-start.py` | Bootstrap injection script (Python; shared across Claude Code, Cursor) |
| `assets/scripts/bump_version.py` | `skills/releasing/scripts/bump_version.py` | Version sync tool (bump, check, audit) |
| `assets/root/version-bump.json` | `.version-bump.json` | Version sync config (adapt `files` array to target platforms) |
| `assets/root/gitignore` | `.gitignore` | Standard ignores |
| `assets/root/package.json` | `package.json` | Project identity (omit `main` if OpenCode not targeted) |

### Documentation (always generated)

| Template File | Target Path | Purpose |
|---------------|-------------|---------|
| `assets/root/README.md` | `README.md` | Project README (adapt sections per target platforms) |
| `assets/root/AGENTS.md` | `AGENTS.md` | Codex pointer to CLAUDE.md |
| `assets/root/GEMINI.md` | `GEMINI.md` | Gemini CLI context file (only if Gemini targeted) |

### Bootstrap Skill (if bootstrap requested)

| Template File | Target Path | Purpose |
|---------------|-------------|---------|
| `assets/root/bootstrap-skill.md` | `skills/using-<project-name>/SKILL.md` | Meta-skill: instruction priority, skill routing table |

### Optional Components (if specified in design)

| Template File | Target Path | Purpose |
|---------------|-------------|---------|
| `assets/mcp-json.md` | `.mcp.json` | MCP server definitions (choose transport from template variants) |

### Platform Adapters

Platform-specific manifest templates live in `assets/platforms/`. Use those when generating per-platform files (plugin.json, hooks.json, etc.). The Claude Code `hooks.json` template includes a top-level `description` (use `<Project Name>` placeholder) and per-handler `timeout: 10`.

---

## Generation Notes

- **Hooks:** platform templates should invoke `python` with `hooks/session-start.py` (see `assets/platforms/*/hooks*.json`)
- **`.version-bump.json`:** only include entries for platforms that have version-bearing manifest files
- **`package.json`:** omit the `main` field if OpenCode is not a target platform
- **`GEMINI.md`:** only generate if Gemini CLI is a target platform
- **`AGENTS.md`:** only generate if Codex is a target platform
- **Bootstrap skill:** keep under 200 lines — extract heavy content to `references/`
