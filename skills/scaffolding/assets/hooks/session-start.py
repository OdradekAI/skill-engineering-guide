#!/usr/bin/env python3
"""SessionStart hook for <project-name> plugin.

Reads the bootstrap meta-skill (using-<project-name>/SKILL.md) and emits
platform-appropriate JSON context for the host IDE.

Platform detection:
  CURSOR_PLUGIN_ROOT  → Cursor format (additional_context)
  CLAUDE_PLUGIN_ROOT  → Claude Code format (hookSpecificOutput)
  neither             → plain text fallback
"""

import json
import os
import sys
from pathlib import Path


def main():
    script_dir = Path(__file__).resolve().parent
    plugin_root = script_dir.parent
    skill_path = plugin_root / "skills" / "using-<project-name>" / "SKILL.md"

    try:
        content = skill_path.read_text(encoding="utf-8")
    except (OSError, IOError) as exc:
        print(f"Warning: cannot read bootstrap skill at {skill_path}: {exc}",
              file=sys.stderr)
        sys.exit(0)

    if not content:
        print(f"Warning: bootstrap skill is empty at {skill_path}",
              file=sys.stderr)
        sys.exit(0)

    escaped = (content
               .replace("\\", "\\\\")
               .replace('"', '\\"')
               .replace("\n", "\\n")
               .replace("\r", "\\r")
               .replace("\t", "\\t"))

    session_ctx = (
        "<EXTREMELY_IMPORTANT>\\n"
        "You have <project-name> skills loaded.\\n\\n"
        "**Below is the full content of your "
        "'<project-name>:using-<project-name>' skill. For all other skills, "
        "use the 'Skill' tool:**\\n\\n"
        f"{escaped}\\n"
        "</EXTREMELY_IMPORTANT>"
    )

    if os.environ.get("CURSOR_PLUGIN_ROOT"):
        output = json.dumps({"additional_context": session_ctx})
    elif os.environ.get("CLAUDE_PLUGIN_ROOT"):
        output = json.dumps({
            "hookSpecificOutput": {
                "hookEventName": "SessionStart",
                "additionalContext": session_ctx,
            }
        })
    else:
        output = session_ctx

    print(output)
    sys.exit(0)


if __name__ == "__main__":
    main()
