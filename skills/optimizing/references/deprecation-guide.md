# Deprecation and Migration Guide

Step-by-step processes for deprecating, renaming, splitting, and merging skills within a bundle-plugin project.

## Deprecation Process

When a skill is superseded by another but should remain available during a transition period.

### Step 1: Mark the skill

Update the skill's SKILL.md frontmatter:

```yaml
---
name: old-skill
description: "Use when... (deprecated — use new-skill instead)"
deprecated: true
superseded-by: <project>:new-skill
---
```

### Step 2: Update documentation

1. Update the bootstrap routing table (`using-<project>/SKILL.md`):
   - Add a deprecation note next to the skill entry
   - Point users to the replacement

2. Update AGENTS.md and CLAUDE.md:
   - Mark the skill as deprecated in skill tables
   - Add migration guidance if behavior changed

3. Update README.md / README.zh.md:
   - Mark deprecated in the skills table

### Step 3: Update cross-references

Search all SKILL.md files, Integration sections, and documentation for references to the deprecated skill. For each reference:
- If the reference is a dispatch (`Calls: <project>:old-skill`), update to the replacement
- If the reference is informational, add "(deprecated)" note

### Step 4: Version bump

Deprecation is a **minor** version change (adding the deprecated marker is non-breaking).

### Step 5: Removal timeline

After at least one minor version with the deprecation marker:
1. Remove the skill directory
2. Remove command stubs
3. Update all remaining references
4. Bump version (removal is a **major** change if the skill was publicly used)

---

## Renaming Process

When a skill needs a new name (better trigger semantics, consistency fix, etc.).

### Step 1: Rename directory

```
mv skills/old-name/ skills/new-name/
```

### Step 2: Update frontmatter

In `skills/new-name/SKILL.md`, change:
```yaml
name: new-name
```

### Step 3: Global cross-reference update

Search and replace across the entire project:

| Search | Replace | Files |
|--------|---------|-------|
| `<project>:old-name` | `<project>:new-name` | All SKILL.md, agents/*.md |
| `old-name` in Integration sections | `new-name` | Skills with Calls/Called-by references |
| Command stubs referencing old skill | Updated references | commands/*.md |
| Bootstrap routing table | Updated entry | using-<project>/SKILL.md |
| Documentation tables | Updated entries | README.md, CLAUDE.md, AGENTS.md |

### Step 4: Verify

```bash
bundles-forge audit-docs <target-dir>    # catches stale references
bundles-forge audit-skill <target-dir>   # catches name mismatches
```

### Step 5: Version bump

Renaming is a **major** version change (breaks existing cross-references from external projects).

---

## Splitting Process

When a skill has grown too large or covers multiple responsibilities.

### Step 1: Design

Invoke `bundles-forge:blueprinting` (scenario B — split skill) to design the new skill boundaries:
- What responsibilities belong to each new skill?
- What are the workflow connections?
- Which new skill inherits the original's position in the chain?

### Step 2: Scaffold

Invoke `bundles-forge:scaffolding` to create new skill directories.

### Step 3: Author

Invoke `bundles-forge:authoring` for each new skill:
- Extract relevant content from the original
- Write new frontmatter with proper triggering descriptions
- Set up Integration sections with correct Calls/Called-by

### Step 4: Deprecate original

Follow the Deprecation Process above for the original skill, pointing to the new skills.

### Step 5: Update chain

Update all skills that referenced the original:
- Determine which new skill(s) they should reference
- Update Integration sections

### Step 6: Verify

```bash
bundles-forge audit-workflow <target-dir>   # workflow chain integrity
bundles-forge audit-docs <target-dir>       # documentation consistency
```

---

## Merging Process

When multiple skills should be consolidated into one.

### Step 1: Design

Invoke `bundles-forge:blueprinting` (scenario C — compose skills) to design the merged skill:
- What is the combined responsibility?
- How do the merged workflows connect?
- What description captures all triggering conditions?

### Step 2: Author

Invoke `bundles-forge:authoring` to write the merged skill:
- Combine relevant content from all source skills
- Resolve any conflicting guidance
- Write comprehensive Integration section

### Step 3: Deprecate sources

Follow the Deprecation Process for each source skill, pointing to the merged skill.

### Step 4: Update chain

Update all skills that referenced any of the source skills to point to the merged skill.

### Step 5: Verify

Same as splitting verification.

---

## Platform Cleanup Checklist

After any structural change (deprecation, rename, split, merge):

- [ ] Cursor `plugin.json` paths still resolve
- [ ] `.version-bump.json` entries still valid
- [ ] Hook configurations reference existing scripts
- [ ] OpenCode plugin.js skill paths correct
- [ ] Gemini GEMINI.md references updated
- [ ] Command stubs in `commands/` updated or removed
- [ ] `.clawhubignore` updated if skill directories changed
- [ ] Run `bundles-forge:testing` to verify component discovery
