# Advanced Components Reference

This table maps user signals to advanced components. Only consult when the user has explicitly mentioned a need during the interview — do not proactively offer these options.

## Signal → Component Mapping

| Component | User Signal (explicit mention required) | What It Provides |
|-----------|----------------------------------------|-----------------|
| External integrations (`bin/` or `.mcp.json`) | "I need to call an external tool/API/service" | CLI executables or MCP servers — consult `bundles-forge:scaffolding` — `references/external-integration.md` to decide CLI vs MCP |
| `userConfig` | "Users need to provide API keys/endpoints/tokens" | User prompts at enable time with optional sensitive storage (Claude Code only) |
| `.lsp.json` servers | "I need language-specific code intelligence" | Real-time diagnostics, go-to-definition |
| `output-styles/` | "I want custom output formatting" | Output style definitions |
| `settings.json` | "The plugin should activate a default agent" | Sets default agent when plugin is enabled |

## Integration Type Guidance

When external integrations are needed:
- **CLI (`bin/`)** — stateless single-shot tools, no persistent connection needed
- **MCP (`.mcp.json`)** — stateful connections, authenticated services, or tools requiring session context
