# Skill & Workflow Restructuring Operations

Detailed procedures for Target 5 structural changes. Each operation modifies the project's skill inventory, workflow graph, or agent architecture.

## 5a. Adding Skills

When the project has a workflow gap or the user needs new capability:

1. **Read existing project** — list all skills, map the workflow graph (`## Integration` sections), identify the bootstrap skill's routing table
2. **Inventory new skills** — for each skill being added, record source, structure, frontmatter quality
3. **Compatibility analysis** — check naming conflicts, description style, overlapping responsibilities, cross-reference conventions against the existing project
4. **For third-party skills** — follow `references/third-party-integration.md` (inventory checklist, compatibility checks, integration intent, security audit)
5. **Design insertion** — identify where new skills connect to the existing workflow graph, map new `**Calls:**` / `**Called by:**` declarations, update bootstrap routing if needed
6. **Apply** — copy skills into `skills/`, adapt per integration intent, update existing skills' `## Integration` sections
7. **Verify** — run `bundles-forge:auditing` in Workflow mode with `--focus-skills <new-skills>` to verify workflow integrity

For Intent B (integrate into workflow) third-party skills, invoke `bundles-forge:authoring` after adaptation for content quality validation.

## 5b. Replacing Skills

When a better alternative exists for an existing skill:

1. Analyze the replacement skill's compatibility (same checks as 5a)
2. Map all references to the old skill across the project (cross-references, Integration sections, routing table)
3. Replace and update all references
4. Verify with workflow audit

## 5c. Reorganizing Workflows

When the execution chain needs restructuring:

1. Map the current workflow graph
2. Identify inefficiencies: unnecessary handoffs, missing shortcuts, bottleneck skills
3. Propose new chain — present to user for approval
4. Update `## Integration` sections across affected skills
5. Update bootstrap routing table
6. Verify with Chain A/B Eval (see `references/ab-eval-protocol.md`)

## 5d. Skill-to-Agent Conversion

When a skill would work better as a read-only subagent:

Candidates for conversion:
- Execution produces verbose temporary context (search results, file contents, logs) that subsequent steps don't need
- Skills that only inspect/validate without modifying files
- Skills that produce structured reports (self-contained output)
- Skills that could run in parallel with other work (optional bonus)

Conversion steps:
1. Extract the skill's execution protocol into `agents/<role>.md`
2. Update the dispatching skill to use subagent dispatch instead of skill invocation
3. Add fallback logic (read agent file inline when subagents unavailable)
4. Remove the original skill directory if fully replaced

Post-conversion verification:
1. Dispatch `evaluator` (label "original") with test prompts to confirm the new agent correctly executes the former skill's responsibilities
2. Run `bundles-forge:auditing` to verify dispatch/fallback logic in the orchestrating skill
