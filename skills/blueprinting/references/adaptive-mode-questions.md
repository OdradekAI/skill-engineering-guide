# Adaptive Mode Questions (Phase 2)

These questions are only asked in adaptive mode. Quick mode skips them entirely (defaults: no visibility classification, no workflow chain, no bootstrap, no advanced components).

## 4a. Skill Visibility

For projects with workflow chains, classify each skill:

- **Entry-point** — users invoke directly. Gets a matching command in `commands/` for discoverability. Description describes user-facing triggering conditions.
- **Internal** — called by other skills as part of a workflow chain, not invoked directly by users. Description should say "Use when called by `<project>:<parent-skill>`, not directly." No matching command needed.

Record the classification in the skill inventory table.

## 5. Workflow Chain

Do skills depend on each other? Map the chain:

```
skill-a → calls → skill-b → calls → skill-c
skill-d (independent)
```

If skills are independent, note that — it simplifies the bootstrap skill.

## 6. Bootstrap Strategy

Does the user want an always-loaded meta-skill (`using-<project>`) that teaches agents how to find and use other skills?

**Recommend yes when:**
- Project has 3+ skills
- Skills form a workflow chain
- Multiple platforms targeted

**Skip when:**
- Single bundle-plugin project
- Skills are fully independent utilities

## 7. Advanced Components

Do NOT proactively offer this menu. Only ask about advanced components when the user has explicitly mentioned a need that maps to one during earlier answers. If no signals emerged, skip this step entirely.

Signal → Component mapping is documented in `references/advanced-components.md`.
