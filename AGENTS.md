# Bundles Forge — Agent Guidelines

For full contributor guidelines, see [CLAUDE.md](CLAUDE.md).

## Quick Reference

This is a bundles engineering toolkit supporting 5 platforms. It contains 8 skills covering the full lifecycle of bundles development.

**Key rules:**
- Skill naming: lowercase with hyphens, directory name must match frontmatter `name` field
- Descriptions: must start with "Use when..." and describe triggering conditions
- Cross-references: use `bundles-forge:<skill-name>` format
- Run `scripts/bump-version.sh --check` before committing
- Run `bundles-forge:auditing` before releases

## Available Skills

| Skill | Purpose |
|-------|---------|
| `designing` | Plan new bundles through structured interview |
| `scaffolding` | Generate project structure from design |
| `writing-skill` | Guide SKILL.md authoring |
| `auditing` | Quality assessment and security scanning |
| `optimizing` | Engineering optimization and feedback iteration |
| `adapting-platforms` | Add platform support |
| `releasing` | Version management and release pipeline |
