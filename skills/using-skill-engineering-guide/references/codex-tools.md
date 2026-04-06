# Codex Tool Mapping

When skill-engineering-guide skills reference Claude Code tools, substitute these Codex equivalents:

| Claude Code Tool | Codex Equivalent |
|-----------------|------------------|
| `Skill` | Native skill discovery from `~/.agents/skills/` |
| `TodoWrite` | `todowrite` |
| `Task` (subagents) | Codex's subagent system |
| `Read` | `read` |
| `Write` | `write` |
| `Edit` | `edit` |
| `Bash` | `bash` |

Skills are discovered automatically when symlinked into `~/.agents/skills/skill-engineering-guide/`.
