"""Shared parsing utilities for auditing scripts.

Provides frontmatter parsing, token estimation, and project-wide skill
data loading — the shared data source for audit_skill, audit_workflow,
and _graph.
"""

import json
import re
from pathlib import Path

# ---------------------------------------------------------------------------
# Frontmatter parsing (pure-stdlib, zero external dependencies)
#
# Why not PyYAML: bundle-plugins are designed for `git clone` → immediate use.
# Requiring `pip install pyyaml` would break zero-setup workflows (CI runners,
# containers, restricted corporate environments). Python 3.8+ stdlib is the
# only hard dependency.
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_BLOCK_SCALAR_RE = re.compile(r"^[|>][+-]?\d*$")


def parse_frontmatter(content):
    """Parse YAML-like frontmatter between --- delimiters.

    Returns (dict, body_text) or (None, full_content) when no frontmatter.
    """
    m = FRONTMATTER_RE.match(content)
    if not m:
        return None, content
    raw = m.group(1)
    fm = {}
    current_key = None
    block_join = " "
    for line in raw.split("\n"):
        if line.startswith("  ") and current_key:
            sep = block_join if fm[current_key] else ""
            fm[current_key] += sep + line.strip()
            continue
        idx = line.find(":")
        if idx > 0:
            key = line[:idx].strip()
            val = line[idx + 1:].strip()
            if _BLOCK_SCALAR_RE.match(val):
                fm[key] = ""
                current_key = key
                block_join = "\n" if val[0] == "|" else " "
                continue
            if (val.startswith('"') and val.endswith('"')) or \
               (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            fm[key] = val
            current_key = key
            block_join = " "
    body_start = m.end()
    return fm, content[body_start:]


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------

_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```")
_TABLE_ROW_RE = re.compile(r"^\|.+\|$", re.MULTILINE)


def estimate_tokens(content):
    """Estimate token count with separate rates for code, tables, and prose."""
    code_blocks = _CODE_BLOCK_RE.findall(content)
    table_rows = _TABLE_ROW_RE.findall(content)

    code_chars = sum(len(b) for b in code_blocks)
    table_chars = sum(len(r) for r in table_rows)

    code_tokens = int(code_chars / 3.5)
    table_tokens = int(table_chars / 3.0)

    prose_content = _CODE_BLOCK_RE.sub("", content)
    prose_content = _TABLE_ROW_RE.sub("", prose_content)
    prose_tokens = int(len(prose_content.split()) * 1.3)

    return prose_tokens + code_tokens + table_tokens


# ---------------------------------------------------------------------------
# Project-wide skill loading
# ---------------------------------------------------------------------------

def detect_project_meta(target_dir):
    """Detect project name and abbreviation from package.json.

    Returns (project_name, project_abbreviation).
    """
    target_dir = Path(target_dir).resolve()
    project_name = target_dir.name
    project_abbreviation = None
    pkg_path = target_dir / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            project_name = pkg.get("name", project_name)
            project_abbreviation = pkg.get("abbreviation")
        except (json.JSONDecodeError, OSError):
            pass
    return project_name, project_abbreviation


def parse_all_skills(target_dir):
    """Load and parse all skills in a project.

    Returns a dict consumed by run_lint(), run_graph_analysis(), and
    run_workflow_audit() — the single shared data source that eliminates
    redundant file reads and frontmatter parsing.

    Structure::

        {
            "target_dir": Path,
            "project_name": str,
            "project_abbreviation": str | None,
            "valid_prefixes": set,
            "skills_dir": Path,
            "skills": {
                "skill-name": {
                    "frontmatter": dict | None,
                    "content": str,       # full file content
                    "body": str,          # content after frontmatter
                    "path": Path,         # SKILL.md path
                    "token_estimate": int,
                },
                ...
            }
        }
    """
    target_dir = Path(target_dir).resolve()
    skills_dir = target_dir / "skills"
    project_name, project_abbreviation = detect_project_meta(target_dir)

    valid_prefixes = {project_name}
    if project_abbreviation:
        valid_prefixes.add(project_abbreviation)

    skills = {}
    if skills_dir.is_dir():
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                skills[skill_dir.name] = {
                    "frontmatter": None,
                    "content": "",
                    "body": "",
                    "path": skill_md,
                    "token_estimate": 0,
                }
                continue
            content = skill_md.read_text(encoding="utf-8", errors="replace")
            fm, body = parse_frontmatter(content)
            skills[skill_dir.name] = {
                "frontmatter": fm,
                "content": content,
                "body": body,
                "path": skill_md,
                "token_estimate": estimate_tokens(body),
            }

    return {
        "target_dir": target_dir,
        "project_name": project_name,
        "project_abbreviation": project_abbreviation,
        "valid_prefixes": valid_prefixes,
        "skills_dir": skills_dir,
        "skills": skills,
    }
