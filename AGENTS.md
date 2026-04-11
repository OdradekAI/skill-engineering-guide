# Bundles Forge — Agent Guidelines

For full contributor guidelines, see [CLAUDE.md](CLAUDE.md).

## Quick Reference

This is a bundle-plugin engineering toolkit supporting 5 platforms. It contains 8 skills covering the full lifecycle of bundle-plugin development.

**Key rules:**
- Skill naming: lowercase with hyphens, directory name must match frontmatter `name` field
- Descriptions: must start with "Use when...", describe triggering conditions, stay under 250 characters
- Cross-references: use `bundles-forge:<skill-name>` format
- Run `python scripts/bump_version.py --check` before committing
- Run `bundles-forge:auditing` before releases

## Available Skills

| Skill | Purpose |
|-------|---------|
| `blueprinting` | Plan a new bundle-plugin through structured interview |
| `scaffolding` | Generate project structure from design |
| `authoring` | Guide SKILL.md authoring |
| `auditing` | Quality assessment and security scanning |
| `optimizing` | Engineering optimization and feedback iteration |
| `porting` | Add platform support |
| `releasing` | Version management and release pipeline |
| `using-bundles-forge` | Bootstrap meta-skill: skill discovery and routing |
