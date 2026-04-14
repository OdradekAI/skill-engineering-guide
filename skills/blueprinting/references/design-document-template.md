# Design Document Template

After the interview, compile a design summary using this template. Present to user for approval before proceeding to the Orchestration Pipeline.

```markdown
## Bundle-Plugin Design: <project-name>

**Mode:** quick / adaptive
**Platforms:** <list>
**Bootstrap:** yes/no

### Skills
| Name | Purpose | Type | Visibility | Dependencies |
|------|---------|------|------------|--------------|
| ... | ... | rigid/flexible | entry-point/internal | ... |

### Workflow Chain
<description or "independent">

### Advanced Components (adaptive mode only)
<list any: bin/, .mcp.json, userConfig, .lsp.json, output-styles/, settings.json — or "none">

### Third-Party Sources (if applicable)
| Skill | Source | License | Integration Intent |
|-------|--------|---------|-------------------|
| ... | ... | ... | repackage / integrate |

### Notes
<any special requirements or constraints>
```
