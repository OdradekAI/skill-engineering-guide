# Gemini CLI Tool Mapping

When bundles-forge skills reference Claude Code tools, substitute these Gemini CLI equivalents:

| Claude Code Tool | Gemini CLI Equivalent |
|-----------------|----------------------|
| `Skill` | `activate_skill` |
| `TodoWrite` | Use structured output / task tracking |
| `Task` (subagents) | Not available — execute inline |
| `Read` | `read_file` |
| `Write` | `write_file` |
| `Edit` | `edit_file` |
| `Bash` | `run_shell_command` |

Skills are loaded via `GEMINI.md` context includes and activated on demand.
