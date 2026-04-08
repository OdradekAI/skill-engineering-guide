# Bundles Forge

[中文](README.zh.md)

A bundles engineering toolkit: scaffolding, platform adaptation, version management, auditing, and skill lifecycle management across all major AI coding platforms.

## Installation

### Claude Code

```bash
claude plugin install bundles-forge
```

Or for development:

```bash
git clone https://github.com/odradekai/bundles-forge.git
cd bundles-forge
claude plugin link .
```

### Cursor

Search for `bundles-forge` in the Cursor plugin marketplace, or use `/add-plugin bundles-forge`.

### Codex

See [`.codex/INSTALL.md`](.codex/INSTALL.md)

### OpenCode

See [`.opencode/INSTALL.md`](.opencode/INSTALL.md)

### Copilot CLI

```bash
copilot plugin install bundles-forge
```

### Gemini CLI

```bash
gemini extensions install https://github.com/odradekai/bundles-forge.git
```

## Skills

| Skill | Description |
|-------|-------------|
| `using-bundles-forge` | Bootstrap meta-skill — establishes how to find and use all other skills |
| `designing` | Plan a new bundles or decompose a complex skill through structured interview |
| `scaffolding` | Generate project structure, manifests, hooks, and bootstrap skill |
| `writing-skill` | Guide authoring of SKILL.md files — structure, descriptions, progressive disclosure |
| `auditing` | Systematic quality assessment with 9-category scoring |
| `optimizing` | Engineering optimization — descriptions, token efficiency, workflow chains |
| `adapting-platforms` | Add platform support (Claude Code, Cursor, Codex, OpenCode, Copilot CLI, Gemini CLI) |
| `managing-versions` | Version sync infrastructure, drift detection, and auditing |
| `iterating-feedback` | Iterate on skill improvements based on user feedback — validate, fork external skills, auto-audit |
| `scanning-security` | Scan bundles for security risks in hooks, plugins, agent prompts, and instructions |
| `releasing` | Full release pipeline — audit, security scan, version bump, CHANGELOG, publish |

## Workflow

The skills cover the full lifecycle of a bundles:

```
designing → scaffolding → writing-skill
                                                              ↓
                           auditing ← ── ── ── ┘
                                ↓               ↓
               optimizing   iterating-feedback
               (project engineering)       (single-skill effectiveness)
                                ↓               ↓
                           releasing
                                    ↑
              scanning-security (called by audit + release)
              adapting-platforms (add platforms at any phase)
              managing-versions (supports all phases)
```

1. **Design** — interview to determine project scope, or decompose a complex skill into a project
2. **Scaffold** — generate the complete project structure from the design
3. **Write** — author SKILL.md files with effective descriptions, instructions, and progressive disclosure
4. **Audit** — verify quality across 9 categories (structure, manifests, versions, skills, security, etc.)
5. **Optimize** — targeted engineering improvements to descriptions, token efficiency, workflow chains
6. **Iterate** — improve individual skill effectiveness based on user feedback, with validation and auto-audit
7. **Security** — scan for risks in hooks, plugins, agent prompts, and skill instructions
8. **Adapt** — add support for additional platforms
9. **Version** — keep all manifests in sync
10. **Release** — orchestrate the full pre-release verification and publishing pipeline

## Agents

| Agent | Role |
|-------|------|
| `scaffold-reviewer` | Validates scaffolded project structure |
| `project-auditor` | Executes systematic quality audit |
| `security-scanner` | Performs security risk assessment across 5 attack surface categories |

## Commands

| Command | Redirects To |
|---------|-------------|
| `/use-bundles-forge` | `bundles-forge:using-bundles-forge` |
| `/design-project` | `bundles-forge:designing` |
| `/scaffold-project` | `bundles-forge:scaffolding` |
| `/audit-project` | `bundles-forge:auditing` |
| `/scan-security` | `bundles-forge:scanning-security` |

Other skills are triggered automatically via their descriptions — no slash command needed.

## Contributing

Contributions welcome. Please follow the existing code style and ensure all platform manifests stay in sync using `scripts/bump-version.sh --check`.

## License

MIT
