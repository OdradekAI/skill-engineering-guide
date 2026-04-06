# Skill Engineering Guide (SEG)

[中文](README.zh.md)

A skill-project engineering toolkit: scaffolding, platform adaptation, version management, auditing, and skill lifecycle management across all major AI coding platforms.

**Abbreviation:** `seg` — use `seg:<skill-name>` as shorthand for `skill-engineering-guide:<skill-name>` in cross-references.

## Installation

### Claude Code

```bash
claude plugin install skill-engineering-guide
```

Or for development:

```bash
git clone https://github.com/odradekai/skill-engineering-guide.git
cd skill-engineering-guide
claude plugin link .
```

### Cursor

Search for `skill-engineering-guide` in the Cursor plugin marketplace, or use `/add-plugin skill-engineering-guide`.

### Codex

See [`.codex/INSTALL.md`](.codex/INSTALL.md)

### OpenCode

See [`.opencode/INSTALL.md`](.opencode/INSTALL.md)

### Copilot CLI

```bash
copilot plugin install skill-engineering-guide
```

### Gemini CLI

```bash
gemini extensions install https://github.com/odradekai/skill-engineering-guide.git
```

## Skills

| Skill | Description |
|-------|-------------|
| `using-skill-engineering-guide` | Bootstrap meta-skill — establishes how to find and use all other skills |
| `designing-skill-projects` | Plan a new skill-project or decompose a complex skill through structured interview |
| `scaffolding-skill-projects` | Generate project structure, manifests, hooks, and bootstrap skill |
| `writing-skill-content` | Guide authoring of SKILL.md files — structure, descriptions, progressive disclosure |
| `auditing-skill-projects` | Systematic quality assessment with 9-category scoring |
| `optimizing-skill-projects` | Engineering optimization — descriptions, token efficiency, workflow chains |
| `adapting-skill-platforms` | Add platform support (Claude Code, Cursor, Codex, OpenCode, Copilot CLI, Gemini CLI) |
| `managing-skill-versions` | Version sync infrastructure, drift detection, and auditing |
| `scanning-skill-security` | Scan skill-projects for security risks in hooks, plugins, agent prompts, and instructions |
| `releasing-skill-projects` | Full release pipeline — audit, security scan, version bump, CHANGELOG, publish |

## Workflow

The skills cover the full lifecycle of a skill-project:

```
designing-skill-projects → scaffolding-skill-projects → writing-skill-content
                                                              ↓
                           auditing-skill-projects ← ── ── ── ┘
                                    ↓
                           optimizing-skill-projects
                                    ↓
                           releasing-skill-projects
                                    ↑
              scanning-skill-security (called by audit + release)
              adapting-skill-platforms (add platforms at any phase)
              managing-skill-versions (supports all phases)
```

1. **Design** — interview to determine project scope, or decompose a complex skill into a project
2. **Scaffold** — generate the complete project structure from the design
3. **Write** — author SKILL.md files with effective descriptions, instructions, and progressive disclosure
4. **Audit** — verify quality across 9 categories (structure, manifests, versions, skills, security, etc.)
5. **Optimize** — targeted engineering improvements to descriptions, token efficiency, workflow chains
6. **Security** — scan for risks in hooks, plugins, agent prompts, and skill instructions
7. **Adapt** — add support for additional platforms
8. **Version** — keep all manifests in sync
9. **Release** — orchestrate the full pre-release verification and publishing pipeline

## Agents

| Agent | Role |
|-------|------|
| `scaffold-reviewer` | Validates scaffolded project structure |
| `project-auditor` | Executes systematic quality audit |
| `security-scanner` | Performs security risk assessment across 5 attack surface categories |

## Commands

| Command | Redirects To |
|---------|-------------|
| `/use-seg` | `seg:using-skill-engineering-guide` |
| `/design-project` | `seg:designing-skill-projects` |
| `/scaffold-project` | `seg:scaffolding-skill-projects` |
| `/audit-project` | `seg:auditing-skill-projects` |
| `/scan-security` | `seg:scanning-skill-security` |

Other skills are triggered automatically via their descriptions — no slash command needed.

## Contributing

Contributions welcome. Please follow the existing code style and ensure all platform manifests stay in sync using `scripts/bump-version.sh --check`.

## License

MIT
