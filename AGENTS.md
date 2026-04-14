# Bundles Forge — Agent Guidelines

For full contributor guidelines, see [CLAUDE.md](CLAUDE.md).

## Quick Reference

This is a bundle-plugin engineering toolkit supporting 5 platforms. It contains 7 skills covering the full lifecycle of bundle-plugin development.

**Key rules:**
- Skill naming: lowercase with hyphens, directory name must match frontmatter `name` field
- Descriptions: must start with "Use when...", describe triggering conditions, stay under 250 characters
- Cross-references: use `bundles-forge:<skill-name>` format
- Run `python skills/releasing/scripts/bump_version.py --check` before committing
- Run `python skills/auditing/scripts/generate_checklists.py --check` before committing
- Run `bundles-forge:auditing` before releases
- Run `python skills/auditing/scripts/audit_docs.py` before releases (documentation consistency)

## Available Skills

| Skill | Layer | Purpose |
|-------|-------|---------|
| `blueprinting` | Orchestrator | Plan new bundle-plugins and orchestrate the creation pipeline (scaffolding → authoring → auditing) |
| `optimizing` | Orchestrator | Diagnose and orchestrate improvements; delegates content changes to authoring |
| `releasing` | Orchestrator | Release pipeline: audit, version bump, publish |
| `scaffolding` | Executor | Generate project structure, add or remove platform support |
| `authoring` | Executor | Write/improve SKILL.md and agents/*.md content |
| `auditing` | Executor | Pure diagnostics: quality assessment, security scanning, reporting |
| `using-bundles-forge` | Meta-skill | Bootstrap: skill discovery and routing |
