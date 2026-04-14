# Bundles Forge Documentation

[中文](index.zh.md)

> **Canonical source:** This index provides navigation across all guides. Each guide's canonical source is its corresponding skill definition; the project structure is defined in `CLAUDE.md`.

This directory contains guides for every aspect of bundle-plugin development with Bundles Forge. Each guide has a companion Chinese translation (`*.zh.md`).

## Where to Start

| If you want to... | Start here |
|-------------------|------------|
| Understand core concepts | [Concepts Guide](concepts-guide.md) |
| Build a new bundle-plugin | [Blueprinting Guide](blueprinting-guide.md) |
| Audit an existing project | [Auditing Guide](auditing-guide.md) |
| Improve a project | [Optimizing Guide](optimizing-guide.md) |
| Prepare a release | [Releasing Guide](releasing-guide.md) |

## Full Guide Index

| Guide | Phase | Covers |
|-------|-------|--------|
| [Concepts Guide](concepts-guide.md) | Foundation | Core terminology, architecture, design decisions |
| [Blueprinting Guide](blueprinting-guide.md) | Design | Interview techniques, design documents, decomposition patterns |
| [Scaffolding Guide](scaffolding-guide.md) | Generate | Project anatomy, platform adapters, template system |
| [Authoring Guide](authoring-guide.md) | Write | SKILL.md writing, progressive disclosure, agent authoring |
| [Auditing Guide](auditing-guide.md) | Validate | 10-category checklists, report templates, CI integration |
| [Optimizing Guide](optimizing-guide.md) | Improve | Description tuning, token reduction, workflow restructuring |
| [Releasing Guide](releasing-guide.md) | Publish | Version management, CHANGELOG format, publishing workflow |

## Lifecycle Flow

```
Concepts → Blueprinting → Scaffolding → Authoring → Auditing → Optimizing → Releasing
```

Each guide is self-contained — you can jump directly to the phase you need. The [Concepts Guide](concepts-guide.md) provides shared vocabulary used across all other guides.

## Canonical Sources

These guides are derived from their corresponding skill definitions (`skills/*/SKILL.md`) and agent files (`agents/*.md`). When conflicts arise, the skill file is the single source of truth — see `skills/auditing/references/source-of-truth-policy.md`.
