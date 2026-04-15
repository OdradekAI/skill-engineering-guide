# Scaffolding Guide

[中文](scaffolding-guide.zh.md)

User-oriented guide to generating bundle-plugin projects and managing platform support with Bundles Forge. Covers mode selection, new project generation, platform adaptation, platform comparison, and common pitfalls.

## Overview

Scaffolding handles two related jobs: generating new bundle-plugin projects from a design blueprint, and managing platform support (add, fix, migrate, remove) on existing projects. It is an **executor** in the execution layer — a single-responsibility worker for structure generation, platform adaptation, and inspector self-check. Orchestrators (`blueprinting`, `optimizing`) dispatch it as part of a pipeline, or you can invoke it directly for platform operations and new-project generation.

**Why it matters:** A well-scaffolded project has the right files in the right places from day one — manifests, hooks, version sync, and bootstrap. Fixing structural problems after the fact is significantly harder than getting them right at scaffold time.

> **Canonical source:** The full execution protocol (generation steps, platform adaptation flow, validation checklist) lives in `skills/scaffolding/SKILL.md`. This guide helps you decide *which mode to use* and *what to expect* — the skill itself handles execution.

---

## Choosing a Mode

Scaffolding supports three modes. The right choice depends on your situation:

| Mode | When to Use | What You Get | Platforms |
|------|-------------|--------------|-----------|
| **Minimal** | Quick packaging of standalone skills | Plugin manifest + skills + README + LICENSE | Claude Code only |
| **Intelligent** | Most new projects — agent recommends architecture | Full project based on your description | Selected platforms |
| **Custom** | You want explicit control over every component | Full menu of options presented one by one | Selected platforms |

### Decision Flowchart

```
Are you coming from blueprinting with a design document?
  ├─ Yes → Mode is already set (minimal or intelligent)
  └─ No  → Is this a new project or platform adaptation?
            ├─ New project → Do you want AI to recommend the architecture?
            │                 ├─ Yes → Intelligent mode
            │                 └─ No  → Custom mode
            └─ Platform adaptation → See "Platform Adaptation" below
```

### End-to-End Flow

All six scaffolding operations follow the same three-phase structure: detect context, generate/modify files, validate output.

| Operation | Entry Condition | Phase 1 | Phase 2 | Phase 3 |
|-----------|----------------|---------|---------|---------|
| New project (minimal) | Design or user + no project | Load Claude Code template | Generate manifest + skills + docs | git init, validate JSON |
| New project (intelligent) | Design or user + no project | Load template index, templates, anatomy | Replace placeholders, generate per-platform, skills, commands, bootstrap, optional | git init, version check |
| New project (custom) | User + no project | Same as intelligent | Same, but each component confirmed interactively | git init, version check |
| Add platform | Existing project + target platform | Detect current platforms, read adapter reference | Generate adapter files, update version sync + hooks + docs | Validate manifests, version check |
| Remove platform | Existing project + target platform | Identify files to remove | Delete manifests, clean hooks, update docs | Version check, inspector validation |
| Manage optional components | Existing project + component type | Read external-integration decision tree | Generate/remove component files, update manifests + skills + docs | Inspector validation |

After every operation, scaffolding runs deterministic checks (`bundles-forge audit-skill`) and dispatches the inspector agent for semantic validation.

### Minimal Mode

Best for: packaging 1-3 standalone skills for marketplace distribution with zero infrastructure overhead.

**What gets generated:**

| File | Purpose |
|------|---------|
| `.claude-plugin/plugin.json` | Plugin identity for Claude Code |
| `skills/<name>/SKILL.md` | One directory per skill |
| `README.md` | Install instructions and skill catalog |
| `LICENSE` | MIT by default |

No hooks, no bootstrap, no version infrastructure. You can add these later by invoking scaffolding again for platform adaptation.

### Intelligent Mode

Best for: most new projects. Tell the agent what you're building and it recommends the right components — without over-engineering.

**What to expect:** The agent asks what you're building, which platforms you use, and how many skills you have. Based on your answers, it generates only what's needed — no unnecessary optional components.

**Generated layers:**
1. **Core** — `package.json`, `.gitignore`, `.version-bump.json`, skills, commands
2. **Platform adapters** — only for selected platforms (manifests, hooks, install docs)
3. **Bootstrap** — if you have 3+ skills or a workflow chain
4. **Optional components** — only if the agent detects a need (MCP servers, LSP servers, executables, output styles, default settings, user configuration, marketplace entry)

### Custom Mode

Best for: experienced users who want explicit control, or unusual project configurations.

**What to expect:** The agent presents the complete architecture option set and asks about each component one by one. This takes longer but gives you full control over what gets included.

---

## New Project: What to Expect

### Coming from Blueprinting

If you ran `/bundles-blueprint` first, the design document already contains your mode, platforms, skill inventory, and component choices. Scaffolding reads this and generates everything automatically — no additional questions.

```
/bundles-blueprint
  → Interview complete, design approved
  → Scaffolding auto-invoked with design document
  → Project generated
  → Inspector validates structure (if subagents available)
  → Orchestrating skill (blueprinting or optimizing) handles next steps
```

### Direct Invocation

If you invoke scaffolding directly (via `/bundles-scaffold` or by asking the agent), it detects whether a project already exists:

- **No existing project** → enters new project flow, asks for mode preference
- **Existing project** → enters platform adaptation flow

### Post-Scaffold Validation

After generation, scaffolding dispatches the **inspector agent** to validate the output. The inspector checks:

- Directory structure matches target platforms
- All JSON manifests parse correctly
- Version sync config covers all version-bearing files
- Hook scripts reference correct bootstrap paths
- Skill frontmatter follows conventions

If subagents aren't available, the agent offers to run validation inline.

---

## Optional Components

Most projects only need core files and platform adapters. Optional components are generated only when the design document specifies them or the agent detects a clear need during intelligent/custom mode.

### Component Overview

| Component | Files | When to Include |
|-----------|-------|-----------------|
| Executables | `bin/<tool-name>` | Skills reference CLI tools that should be added to `$PATH` |
| MCP servers | `.mcp.json` | Skills need stateful connections, rich discovery, or authenticated external services |
| LSP servers | `.lsp.json` | Skills involve language-specific code intelligence |
| Output styles | `output-styles/<style>.md` | Custom output formatting for agent responses |
| Default settings | `settings.json` | Default agent activation at plugin root |
| User configuration | `userConfig` in `plugin.json` | Skills need user-provided API keys, endpoints, or tokens (Claude Code only) |
| Marketplace entry | `.claude-plugin/marketplace.json` | Plugin targets marketplace distribution |

### Choosing the Right Integration Level

When a skill needs external tool access, choose the lightest integration that meets the requirement:

```
Does the skill need external tool access?
├─ No → No integration needed
└─ Yes → Is it stateless, single-execution, with clear input/output?
   ├─ Yes → Level 1: CLI (bin/ executable + allowed-tools)
   └─ No → Does it need persistent connection, rich querying, or authenticated service?
      ├─ Yes → Level 2: MCP server (.mcp.json)
      └─ Both → Level 3: CLI wrapper launching MCP stdio server
```

For the full decision tree with examples and platform-specific wiring details, see `references/external-integration.md` in the scaffolding skill.

---

## Platform Adaptation

Use scaffolding to add or remove platform support on an existing project. This is the primary direct-invocation use case.

### Adding a Platform

```
User: "Add Cursor support to my project"
  → Scaffolding detects existing project
  → Scans current platform manifests
  → Generates Cursor adapter files from templates
  → Updates .version-bump.json
  → Updates hooks (if needed)
  → Adds install section to README
  → Runs validation
```

### Removing a Platform

```
User: "Remove Codex support"
  → Scaffolding detects existing project
  → Deletes Codex manifest files (.codex/INSTALL.md)
  → Removes entries from .version-bump.json
  → Cleans up any platform-specific hook config
  → Removes install section from README
  → Runs validation
```

### Managing Optional Components

Beyond platforms, scaffolding can add or remove optional components on an existing project.

**Adding a component:**

```
User: "Add MCP server support to my project"
  → Scaffolding detects existing project
  → Consults external-integration.md decision tree
  → Generates .mcp.json from template
  → Updates plugin manifests (Cursor needs explicit paths)
  → Updates skill frontmatter (allowed-tools)
  → Updates README with setup instructions
  → Runs validation
```

**Removing a component:**

Scaffolding can remove MCP servers, CLI executables, or LSP servers — including downgrading MCP to a lighter CLI alternative when the full server is no longer needed. The removal flow cleans up manifest entries, skill references, and documentation. See `references/external-integration.md` for step-by-step removal instructions.

### What Gets Created Per Platform

| Platform | Manifest | Hooks | Install Doc | Version Tracked |
|----------|----------|-------|-------------|:---------------:|
| Claude Code | `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json` (optional) | `hooks/hooks.json` + shared hooks | — | Yes |
| Cursor | `.cursor-plugin/plugin.json` | `hooks/hooks-cursor.json` + shared hooks | — | Yes |
| Codex | — | — | `.codex/INSTALL.md` | No |
| OpenCode | `.opencode/plugins/<name>.js` | — (JS plugin handles bootstrap) | `.opencode/INSTALL.md` | No |
| Gemini CLI | `gemini-extension.json` | — | `GEMINI.md` | Yes |

**Shared hooks:** `hooks/session-start.py` is shared between Claude Code and Cursor. It's created when either platform is targeted. Written in Python for cross-platform compatibility.

**`marketplace.json`:** Only generated when the plugin targets marketplace distribution. It declares plugin metadata for the marketplace index and is version-tracked via `.version-bump.json`.

**`AGENTS.md`:** If the project doesn't already have a root-level `AGENTS.md`, scaffolding generates a lightweight version that points to `CLAUDE.md`. This file is shared project documentation (used by Codex and other platforms), not a platform-specific install artifact — it should not be deleted when removing a single platform.

**Hook config features:** Claude Code's `hooks.json` supports a top-level `description` field (shown in the `/hooks` menu) and per-handler `timeout` (default 600s — set to 10 for fast bootstrap hooks). See `platform-adapters.md` for the full field reference and Claude vs Cursor comparison table.

---

## Platform Comparison

Understanding platform differences helps you choose which to support.

### Discovery Mechanisms

| Platform | How Skills Are Found | How Bootstrap Works |
|----------|---------------------|-------------------|
| Claude Code | Convention — auto-discovers `skills/`, `agents/`, `commands/` | Shell hook emits JSON on `SessionStart` |
| Cursor | Explicit paths in `plugin.json` | Same shell hook, different JSON format |
| Codex | Symlink into `~/.agents/skills/` | `AGENTS.md` → `CLAUDE.md` (no hook injection) |
| OpenCode | JS plugin registers paths in config | JS plugin prepends to first user message |
| Gemini CLI | `GEMINI.md` context file with `@` includes | `@` syntax pulls in skill content on session start |

### Key Differences

| Aspect | Claude Code | Cursor |
|--------|------------|--------|
| Hook event casing | `SessionStart` (PascalCase) | `sessionStart` (camelCase) |
| Hook re-injection | Fires on `startup\|clear\|compact` | Only on `sessionStart` — no re-injection after context clear |
| Manifest paths | Convention-based (no declaration needed) | Must declare `skills`, `agents`, `commands`, `hooks` explicitly |

### Platform Limitations

- **Codex** has no hook-based bootstrap injection. Users rely on description-based skill matching only.
- **Cursor** doesn't re-inject bootstrap after context clear mid-session.
- **OpenCode** bootstrap is injected via JS transform, not shell hooks.

### Plugin Caching

When a plugin is installed via the marketplace, it gets copied to a platform-managed cache directory. This has important implications for scaffolding:

- **`${CLAUDE_PLUGIN_ROOT}`** points to the cached copy and changes on each plugin update. Do not use it for persistent storage.
- **`${CLAUDE_PLUGIN_DATA}`** is a stable, persistent directory for caches, installed dependencies, and generated state. Use this for any data that must survive plugin updates.
- **No `../` paths** — after marketplace install, the plugin is isolated in its cache directory. Paths referencing files outside the plugin root (`../shared-lib/`) will break. Keep all files within the plugin root.

These constraints apply to marketplace-distributed plugins. Development installs (`claude --plugin-dir .`) use the project directory directly.

---

## Common Mistakes

| Mistake | Why It Happens | Fix |
|---------|---------------|-----|
| Generating all platforms regardless of need | Wanting to be thorough | Only generate for platforms you actually use today |
| Forgetting `.version-bump.json` entries | New manifest added manually | Every version-bearing manifest needs a bump config entry |
| Wrong hook casing | Copying from one platform to another | Claude Code: `SessionStart`, Cursor: `sessionStart` |
| Bootstrap skill > 200 lines | Packing too much into the routing table | Keep lean — extract heavy content to `references/` |
| Using intelligent mode for simple packaging | Wanting full infrastructure for 1-2 skills | Minimal mode exists to avoid over-engineering |
| Missing `python` on PATH | Hook won't run without Python | Ensure `session-start.py` can be invoked by `python` — document prerequisite |
| Using MCP when CLI suffices | Wanting rich integration for simple tools | Consult `references/external-integration.md` decision tree — prefer CLI for stateless, single-shot tools |
| Using `../` paths to reference files outside the plugin | Wanting to share files across projects | After marketplace install, plugins are cached — `../` paths break. Keep all files within the plugin root |
| Writing persistent data to `${CLAUDE_PLUGIN_ROOT}` | Treating plugin root as stable storage | `PLUGIN_ROOT` changes on each update. Use `${CLAUDE_PLUGIN_DATA}` for caches and generated state |

---

## FAQ

**Q: I scaffolded a minimal project but now need hooks and version infrastructure. Do I have to start over?**

No. Invoke scaffolding again — it detects the existing project and offers platform adaptation. You can add any platform and its associated infrastructure incrementally.

**Q: Can I add multiple platforms at once?**

Yes. When adding platforms, you can specify several targets and scaffolding will generate all adapter files in one pass.

**Q: What's the difference between scaffolding and blueprinting?**

Blueprinting is the *planning* phase — it interviews you and produces a design document. Scaffolding is the *execution* phase — it reads the design and generates the actual files. For platform adaptation on existing projects, you skip blueprinting entirely and invoke scaffolding directly.

**Q: I added a platform manually. How do I verify it's set up correctly?**

Run `/bundles-audit` — the auditing skill checks manifest validity, version sync, hook configuration, and cross-references. Or invoke scaffolding and let the inspector agent validate.

---

## Related Skills

| Skill | Relationship |
|-------|-------------|
| `bundles-forge:blueprinting` | Upstream — plans new projects, then dispatches scaffolding to generate structure |
| `bundles-forge:optimizing` | Upstream — dispatches scaffolding for platform coverage improvements |
| `bundles-forge:authoring` | Downstream — writes skill and agent content (`SKILL.md`, `agents/*.md`) after scaffolding completes |
