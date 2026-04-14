# Distribution Strategy

Choose how users will install the plugin based on the target audience:

| Strategy | Best For | How |
|----------|----------|-----|
| Marketplace (Claude Code) | Public distribution, widest reach | `claude plugin publish` — users install via `claude plugin install` |
| Project scope | Team tooling shared via git | Install with `--scope project` — config committed to `.claude/settings.json` |
| Local scope | Personal project-specific plugins | Install with `--scope local` — gitignored, per-developer |
| Git-based (Codex, OpenCode, Gemini) | Platforms without marketplaces | Users clone the repo and follow per-platform install docs |
| Development mode | Iterating before publishing | `claude --plugin-dir .` — loads current directory, no caching |

For marketplace distribution, ensure `.claude-plugin/marketplace.json` exists with plugin metadata. For development iteration, use `--plugin-dir .` to bypass caching — changes take effect immediately without version bumps.
