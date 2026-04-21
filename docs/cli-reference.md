# CLI Reference

[中文](cli-reference.zh.md)

> **Canonical source:** Command definitions live in `bin/bundles-forge`. Argument schemas are defined in each script's `main()` function or via `_cli.make_parser()`.

Complete reference for the `bundles-forge` CLI dispatcher and all subcommands.

## Usage

```bash
bundles-forge <command> [args...]
bundles-forge -h | --help
```

The dispatcher routes subcommands to the correct Python script inside the plugin. Exit codes propagate from the target script unchanged.

## Common Options

Most audit commands share these options (provided by `_cli.make_parser()`):

| Option | Description |
|--------|-------------|
| `project_root` | Positional, optional. Bundle-plugin root directory (default: `.`) |
| `--json` | Output JSON instead of Markdown |
| `--output-dir` | Write output to this directory (auto-created) |

## Commands

### audit-skill

Quality audit for individual skills or entire projects.

```bash
bundles-forge audit-skill [target-dir]
bundles-forge audit-skill [skill-directory]
bundles-forge audit-skill --all [target-dir]
bundles-forge audit-skill --json [target-dir]
```

| Option | Description |
|--------|-------------|
| `project_root` | Project root, skill directory, or path to a SKILL.md file |
| `--all` | Force project-level mode (audit all skills) |
| `--json` | Output JSON |
| `--output-dir` | Write output to this directory (auto-created) |

**Scope detection:** Accepts a project root (has `skills/` directory), a single skill directory (contains `SKILL.md`), or a direct path to a `SKILL.md` file. Project mode runs quality lint (Q1-Q15, S9, X1-X4) across all skills; skill mode runs 4 applicable categories on one skill.

**Cross-reference checks:** Includes X1 (skill references), X2 (relative paths), X3 (directory references), and X4 (orphan detection — finds `references/` files not linked from `SKILL.md` or sibling references). In project mode, C1 includes paragraph-hash redundancy detection across skills.

**Exit codes:** `0` clean, `1` warnings, `2` critical.

---

### audit-security

Pattern-based security scan across 7 attack surfaces.

```bash
bundles-forge audit-security [target-dir]
bundles-forge audit-security --json [target-dir]
```

Scans SKILL.md files, hook scripts, hook configs, OpenCode plugins, agent prompts, bundled scripts, and MCP configs for dangerous patterns (network calls, eval, sensitive file references, safety overrides).

Findings are classified by confidence: `deterministic` (unambiguous in executable code) or `suspicious` (context-sensitive, needs manual review).

**Exit codes:** `0` clean, `1` warnings, `2` critical.

---

### audit-docs

Documentation consistency checks (D1-D9).

```bash
bundles-forge audit-docs [target-dir]
bundles-forge audit-docs --json [target-dir]
```

Verifies alignment between documentation files (CLAUDE.md, AGENTS.md, README, guides) and the actual project structure (skills, manifests, platform configs).

**Exit codes:** `0` clean, `1` warnings, `2` critical.

---

### audit-plugin

Combined audit — orchestrates skill, security, workflow, and documentation audits plus plugin health checks.

```bash
bundles-forge audit-plugin [target-dir]
bundles-forge audit-plugin --json [target-dir]
```

Runs all audit scripts in sequence and produces a combined 10-category health report covering structure, versioning, hooks, testing, and all audit dimensions.

**Exit codes:** `0` clean, `1` warnings, `2` critical.

---

### audit-workflow

Workflow integrity audit (W1-W11).

```bash
bundles-forge audit-workflow [target-dir]
bundles-forge audit-workflow --focus-skills skill1,skill2 [target-dir]
bundles-forge audit-workflow --json [target-dir]
```

| Option | Description |
|--------|-------------|
| `--focus-skills` | Comma-separated skill names to focus analysis on |
| `--json` | Output JSON |

Three-layer audit: static graph analysis (W1-W5), semantic interface checks (W6-W9), and behavioral verification (W10-W11). Output includes a Mermaid dependency graph of the skill workflow (in both JSON and Markdown modes).

**Exit codes:** `0` clean, `1` warnings, `2` critical.

---

### checklists

Generate or validate checklist tables from the audit-checks registry.

```bash
bundles-forge checklists [target-dir]
bundles-forge checklists --check [target-dir]
```

| Option | Description |
|--------|-------------|
| `--check` | Detect drift without writing files (exit 1 if stale) |

Without `--check`, regenerates markdown checklist tables from `skills/auditing/references/audit-checks.json`. With `--check`, compares current tables against the registry and exits non-zero if they differ.

**Exit codes:** `0` consistent/updated, `1` drift detected (with `--check`), `2` registry error (duplicate IDs or missing file).

---

### bump-version

Version synchronization across all platform manifests.

```bash
bundles-forge bump-version --check [target-dir]
bundles-forge bump-version --audit [target-dir]
bundles-forge bump-version <version> [target-dir]
bundles-forge bump-version --dry-run <version> [target-dir]
```

| Option | Description |
|--------|-------------|
| `--check` | Report current versions and detect drift |
| `--audit` | Check + scan repo for undeclared version strings |
| `--dry-run` | Preview version bump without writing files |
| `version` | New version in `X.Y.Z` or `X.Y.Z-pre.N` format |

Updates all files declared in `.version-bump.json` to the specified version. The `--audit` mode additionally scans the repository for files containing the current version string that are not tracked by the config.

**Exit codes:** `0` success/consistent, `1` drift detected or invalid input.

## See Also

- [Troubleshooting Guide](troubleshooting-guide.md) — common issues and solutions
- [Auditing Guide](auditing-guide.md) — audit scopes and workflows
- [Releasing Guide](releasing-guide.md) — release pipeline using these commands
