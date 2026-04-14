# Composition Analysis

When the user wants to combine multiple existing skills into a unified bundle-plugin, analyze compatibility and design the orchestration before scaffolding.

## C1. Inventory Existing Skills

Collect all candidate skills. For each one, record:
- Source (local file, git repo, marketplace plugin, another bundle-plugin project)
- Current structure (standalone SKILL.md, has references/, has scripts/)
- Frontmatter quality (has name/description? follows conventions?)
- Rigid or flexible type

**For third-party skills** (marketplace, GitHub, other bundle-plugins), additionally record:
- License (MIT, Apache-2.0, proprietary, unknown)
- Version or commit hash at time of evaluation
- Maintenance status (actively maintained, archived, unknown)
- Original project name and namespace (for cross-reference rewriting)

## C2. Analyze Compatibility

Check for issues that need resolution before combining:

| Check | What to Look For |
|-------|-----------------|
| Naming conflicts | Two skills with the same or confusingly similar names |
| Description style | Inconsistent patterns (some start with "Use when...", some don't) |
| Overlapping responsibilities | Skills that do similar things — merge, deduplicate, or clearly scope each |
| Shared dependencies | Multiple skills referencing the same tools, scripts, or external resources |
| Cross-reference conventions | Mismatched project prefixes or reference styles |

**For third-party skills**, also check:

| Check | What to Look For |
|-------|-----------------|
| License compatibility | Can this license coexist with the project's license? |
| Security posture | Does the skill invoke external tools, network calls, or eval()? Run `bundles-forge:auditing` |
| Staleness risk | Is the skill actively maintained? Will you need to own updates? |

Classify each skill as:
- **Ready** — can be included as-is
- **Needs adaptation** — rename, rewrite description, adjust references
- **Needs merge** — overlaps with another skill, combine into one
- **Needs import** — third-party skill requiring copy + source attribution

## C3. Integration Intent & Security Audit (for third-party skills)

For each skill classified as **Needs import**, follow the third-party integration process in `skills/optimizing/references/third-party-integration.md` (shared with `bundles-forge:optimizing`). This covers:

- Integration intent classification (repackage as-is vs integrate into workflow)
- Source attribution template
- Mandatory security audit via `bundles-forge:auditing`
- Intent B adaptation steps (rewrite description, cross-references, workflow declarations)

## C4. Design the Orchestration

With the inventory and compatibility analysis in hand, design how the skills work together:

- **Workflow chains** — which skills call or depend on each other? Map the full dependency graph
- **Independent skills** — which skills stand alone with no dependencies?
- **Glue skills** — do you need new skills to bridge gaps between existing ones (e.g., a skill that coordinates the handoff between two unrelated skills)?
- **Shared resources** — extract common scripts, reference docs, or templates into project-level `scripts/` or shared `references/` files
- **Bootstrap routing** — design the `using-<project>` skill's routing table to cover all composed skills

Present the composition plan to the user. Get approval before proceeding to the Interview (Scenario A) to finalize project details like name, platforms, and bootstrap strategy.
