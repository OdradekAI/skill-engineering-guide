#!/usr/bin/env python3
"""
Skill quality linter for skill projects.

Validates SKILL.md frontmatter, descriptions, line counts, cross-references,
and relative path links across all skills in a project.

Usage:
    python scripts/lint-skills.py [project-root]
    python scripts/lint-skills.py --json [project-root]

Exit codes: 0 = all pass, 1 = warnings, 2 = errors
"""

import argparse
import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Frontmatter parsing (pure regex, no pyyaml dependency)
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
WORKFLOW_SUMMARY_PHRASES = re.compile(
    r"first\b.*then\b.*finally|step\s+\d|phase\s+\d|"
    r"scans?\s+.*checks?\s+.*generates?|"
    r"reads?\s+.*writes?\s+.*outputs?",
    re.IGNORECASE,
)
KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CROSS_REF_RE = re.compile(r"`([a-z0-9-]+):([a-z0-9-]+)`")
RELATIVE_PATH_RE = re.compile(r"`((?:references|assets|scripts|templates)/[^`]+)`")


def parse_frontmatter(content):
    m = FRONTMATTER_RE.match(content)
    if not m:
        return None, content
    raw = m.group(1)
    fm = {}
    current_key = None
    for line in raw.split("\n"):
        if line.startswith("  ") and current_key:
            fm[current_key] += " " + line.strip()
            continue
        idx = line.find(":")
        if idx > 0:
            key = line[:idx].strip()
            val = line[idx + 1:].strip().strip('"').strip("'")
            fm[key] = val
            current_key = key
    body_start = m.end()
    return fm, content[body_start:]


# ---------------------------------------------------------------------------
# Linting rules
# ---------------------------------------------------------------------------

def lint_skill(skill_dir, project_root, project_name, project_abbreviation=None):
    findings = []
    skill_md = skill_dir / "SKILL.md"
    dir_name = skill_dir.name

    if not skill_md.exists():
        findings.append(dict(check="Q1", severity="error", message="Missing SKILL.md"))
        return findings

    content = skill_md.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(content)
    lines = content.splitlines()

    # Q1: Frontmatter exists
    if fm is None:
        findings.append(dict(check="Q1", severity="error",
                             message="No YAML frontmatter (missing --- delimiters)"))
        return findings

    fm_raw = FRONTMATTER_RE.match(content).group(1) if FRONTMATTER_RE.match(content) else ""

    # Q2: name field
    name = fm.get("name", "")
    if not name:
        findings.append(dict(check="Q2", severity="error", message="Missing 'name' in frontmatter"))
    else:
        # Q4: kebab-case
        if not KEBAB_CASE_RE.match(name):
            findings.append(dict(check="Q4", severity="warning",
                                 message=f"name '{name}' is not kebab-case"))
        # S9: directory name matches
        if name != dir_name:
            findings.append(dict(check="S9", severity="info",
                                 message=f"Directory '{dir_name}' != name '{name}'"))

    # Q3: description field
    desc = fm.get("description", "")
    if not desc:
        findings.append(dict(check="Q3", severity="error", message="Missing 'description' in frontmatter"))
    else:
        # Q5: starts with "Use when"
        if not desc.lower().startswith("use when"):
            findings.append(dict(check="Q5", severity="warning",
                                 message="Description should start with 'Use when...'"))
        # Q6: workflow summary anti-pattern
        if WORKFLOW_SUMMARY_PHRASES.search(desc):
            findings.append(dict(check="Q6", severity="warning",
                                 message="Description appears to summarize workflow instead of triggering conditions"))
        # Q7: length
        if len(desc) > 500:
            findings.append(dict(check="Q7", severity="warning",
                                 message=f"Description is {len(desc)} chars (max 500)"))

    # Q8: frontmatter size
    if len(fm_raw) > 1024:
        findings.append(dict(check="Q8", severity="warning",
                             message=f"Frontmatter is {len(fm_raw)} chars (max 1024)"))

    # Q9: body line count
    body_lines = len(body.splitlines())
    if body_lines > 500:
        findings.append(dict(check="Q9", severity="warning",
                             message=f"SKILL.md body is {body_lines} lines (max 500)"))

    # Q10: Overview section
    if "## Overview" not in content and "## overview" not in content.lower():
        findings.append(dict(check="Q10", severity="info", message="Missing Overview section"))

    # Q11: Common Mistakes section
    if "## Common Mistakes" not in content and "common mistakes" not in content.lower():
        findings.append(dict(check="Q11", severity="info", message="Missing Common Mistakes section"))

    # X1: Cross-reference resolution (supports both full name and abbreviation)
    skills_root = project_root / "skills"
    valid_prefixes = {project_name}
    if project_abbreviation:
        valid_prefixes.add(project_abbreviation)
    for match in CROSS_REF_RE.finditer(content):
        proj, skill_name = match.group(1), match.group(2)
        if proj in valid_prefixes:
            target = skills_root / skill_name
            if not target.is_dir():
                findings.append(dict(check="X1", severity="warning",
                                     message=f"Cross-ref '{proj}:{skill_name}' — "
                                             f"skills/{skill_name}/ not found"))

    # X2: Relative path references (skip template placeholders like <platform>)
    for match in RELATIVE_PATH_RE.finditer(content):
        ref_path = match.group(1)
        if "<" in ref_path or ">" in ref_path:
            continue
        clean_path = ref_path.split()[0] if " " in ref_path else ref_path
        resolved = skill_dir / clean_path
        resolved_from_root = project_root / clean_path
        if not resolved.exists() and not resolved_from_root.exists():
            findings.append(dict(check="X2", severity="warning",
                                 message=f"Relative path '{ref_path}' not found"))

    # Q12: Heavy inline content that should be in references/
    non_fm_lines = body.splitlines()
    if len(non_fm_lines) > 300:
        refs_dir = skill_dir / "references"
        if not refs_dir.is_dir() or not any(refs_dir.iterdir()):
            findings.append(dict(check="Q12", severity="info",
                                 message="SKILL.md has 300+ lines but no references/ files"))

    return findings


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_lint(project_root):
    project_root = Path(project_root).resolve()
    skills_dir = project_root / "skills"
    project_name = project_root.name

    # Detect project name and abbreviation from package.json if available
    project_abbreviation = None
    pkg_path = project_root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            project_name = pkg.get("name", project_name)
            project_abbreviation = pkg.get("abbreviation")
        except (json.JSONDecodeError, OSError):
            pass

    results = {"skills": [], "summary": {"error": 0, "warning": 0, "info": 0}}

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        findings = lint_skill(skill_dir, project_root, project_name,
                              project_abbreviation)
        skill_result = {
            "skill": skill_dir.name,
            "findings": findings,
            "counts": {"error": 0, "warning": 0, "info": 0},
        }
        for f in findings:
            skill_result["counts"][f["severity"]] += 1
            results["summary"][f["severity"]] += 1
        results["skills"].append(skill_result)

    return results

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def format_markdown(results):
    s = results["summary"]
    out = [
        "## Skill Quality Lint\n",
        f"**Skills checked:** {len(results['skills'])}",
        f"**Results:** {s['error']} errors, {s['warning']} warnings, {s['info']} info\n",
    ]

    for sev, heading in [("error", "### Errors"), ("warning", "### Warnings"), ("info", "### Info")]:
        items = []
        for sr in results["skills"]:
            for f in sr["findings"]:
                if f["severity"] == sev:
                    items.append(f"- [{f['check']}] {sr['skill']}: {f['message']}")
        if items:
            out.append(heading)
            out.extend(items)
            out.append("")

    out.append("### Per-Skill Summary\n")
    out.append("| Skill | Errors | Warnings | Info |")
    out.append("|-------|--------|----------|------|")
    for sr in results["skills"]:
        c = sr["counts"]
        out.append(f"| {sr['skill']} | {c['error']} | {c['warning']} | {c['info']} |")
    return "\n".join(out)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Lint skill quality in a skill project.")
    parser.add_argument("project_root", nargs="?", default=".",
                        help="Skill project root (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of markdown")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not (root / "skills").is_dir():
        print(f"error: {root} has no skills/ directory", file=sys.stderr)
        sys.exit(1)

    results = run_lint(root)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_markdown(results))

    sys.exit(2 if results["summary"]["error"] else
             1 if results["summary"]["warning"] else 0)


if __name__ == "__main__":
    main()
