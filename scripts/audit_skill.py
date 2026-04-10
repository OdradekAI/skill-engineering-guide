#!/usr/bin/env python3
"""
Single skill audit for bundle-plugins.

Orchestrates lint_skills.py (quality + cross-ref checks) and
scan_security.py (security checks) scoped to one skill directory,
producing a 4-category skill audit report.

For agent-authored rich reports, see skills/auditing/references/skill-report-template.md.

Usage:
    python scripts/audit_skill.py <skill-dir-or-SKILL.md>
    python scripts/audit_skill.py --json <skill-dir-or-SKILL.md>

Exit codes: 0 = pass, 1 = warnings, 2 = critical findings
"""

import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import lint_skills
import scan_security

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

CATEGORY_WEIGHTS = {
    "structure": 3,
    "skill_quality": 2,
    "cross_references": 2,
    "security": 3,
}


def compute_baseline_score(findings):
    critical = sum(1 for f in findings if f.get("severity", f.get("risk", "info")) == "critical")
    warning = sum(1 for f in findings if f.get("severity", f.get("risk", "info")) == "warning")
    return max(0, 10 - (critical * 3 + warning * 1))


def compute_weighted_average(scores):
    total_weight = 0
    weighted_sum = 0.0
    for cat, score in scores.items():
        w = CATEGORY_WEIGHTS.get(cat, 1)
        weighted_sum += score * w
        total_weight += w
    return round(weighted_sum / total_weight, 1) if total_weight else 0.0


# ---------------------------------------------------------------------------
# Skill resolution
# ---------------------------------------------------------------------------

def resolve_skill_path(raw_path):
    """Resolve to a skill directory from a dir or SKILL.md path.

    Returns (skill_dir, project_root) or raises SystemExit on error.
    """
    p = Path(raw_path).resolve()
    if p.is_file() and p.name == "SKILL.md":
        skill_dir = p.parent
    elif p.is_dir():
        skill_dir = p
    else:
        print(f"error: {raw_path} is not a directory or SKILL.md file",
              file=sys.stderr)
        sys.exit(1)

    if not (skill_dir / "SKILL.md").exists():
        print(f"error: {skill_dir} does not contain SKILL.md",
              file=sys.stderr)
        sys.exit(1)

    if (skill_dir / "skills").is_dir():
        print(f"warning: {skill_dir} contains a skills/ subdirectory — "
              "this looks like a project root. Use audit_project.py for "
              "full project audits.", file=sys.stderr)

    project_root = _find_project_root(skill_dir)
    return skill_dir, project_root


def _find_project_root(skill_dir):
    """Walk up to find the project root (directory with skills/)."""
    candidate = skill_dir.parent
    while candidate != candidate.parent:
        if (candidate / "skills").is_dir():
            return candidate
        candidate = candidate.parent
    return skill_dir.parent


# ---------------------------------------------------------------------------
# Category checkers
# ---------------------------------------------------------------------------

def _classify_finding(finding):
    """Map a finding to one of the 4 skill-level categories."""
    check = finding.get("check", "")
    if check.startswith("S"):
        return "structure"
    if check.startswith("Q") or check.startswith("C"):
        return "skill_quality"
    if check.startswith("X"):
        return "cross_references"
    if check.startswith("SEC") or check.startswith("SC"):
        return "security"
    return "skill_quality"


def run_skill_audit(skill_path):
    """Run a 4-category audit on a single skill.

    Args:
        skill_path: Path to skill directory or SKILL.md file.

    Returns structured results dict.
    """
    skill_dir, project_root = resolve_skill_path(skill_path)

    project_name = project_root.name
    project_abbreviation = None
    pkg_path = project_root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            project_name = pkg.get("name", project_name)
            project_abbreviation = pkg.get("abbreviation")
        except (json.JSONDecodeError, OSError):
            pass

    # Skill quality + structure + cross-ref checks via lint_skills
    lint_findings = lint_skills.lint_skill(
        skill_dir, project_root, project_name, project_abbreviation)

    # Security checks via scan_security
    sec_findings_raw = []
    scannable = scan_security.collect_scannable_files(skill_dir)
    self_path = Path(__file__).resolve()
    for f in scannable:
        if f.resolve() == self_path:
            continue
        rel = f.relative_to(skill_dir) if f.is_relative_to(skill_dir) else f
        file_type = scan_security.classify_file(
            f.relative_to(project_root) if f.is_relative_to(project_root) else rel)
        if file_type is None:
            skill_md = skill_dir / "SKILL.md"
            if f.resolve() == skill_md.resolve():
                file_type = "skill_content"
            else:
                continue
        findings = scan_security.scan_file(f, rel, file_type)
        for finding in findings:
            sec_findings_raw.append({
                "check": finding.get("check_id", ""),
                "severity": finding.get("risk", "info"),
                "message": f"{f.name}:{finding.get('line', '?')} — "
                           f"{finding.get('description', '')}",
            })

    # Also scan SKILL.md directly if not already covered
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        already_scanned = any(
            f.resolve() == skill_md.resolve() for f in scannable)
        if not already_scanned:
            findings = scan_security.scan_file(
                skill_md, Path("SKILL.md"), "skill_content")
            for finding in findings:
                sec_findings_raw.append({
                    "check": finding.get("check_id", ""),
                    "severity": finding.get("risk", "info"),
                    "message": f"SKILL.md:{finding.get('line', '?')} — "
                               f"{finding.get('description', '')}",
                })

    # Partition lint findings into 3 categories
    categories = {
        "structure": {"findings": [], "counts": {"critical": 0, "warning": 0, "info": 0}},
        "skill_quality": {"findings": [], "counts": {"critical": 0, "warning": 0, "info": 0}},
        "cross_references": {"findings": [], "counts": {"critical": 0, "warning": 0, "info": 0}},
        "security": {"findings": sec_findings_raw, "counts": {"critical": 0, "warning": 0, "info": 0}},
    }

    for f in lint_findings:
        cat = _classify_finding(f)
        categories[cat]["findings"].append(f)

    # Compute counts
    for cat_data in categories.values():
        for f in cat_data["findings"]:
            sev = f.get("severity", "info")
            cat_data["counts"][sev] = cat_data["counts"].get(sev, 0) + 1

    # Compute scores
    scores = {}
    for cat_name, cat_data in categories.items():
        scores[cat_name] = compute_baseline_score(cat_data["findings"])
        cat_data["baseline_score"] = scores[cat_name]

    overall_score = compute_weighted_average(scores)

    total_critical = sum(d["counts"]["critical"] for d in categories.values())
    total_warning = sum(d["counts"]["warning"] for d in categories.values())

    if total_critical > 0:
        status = "FAIL"
    elif total_warning > 0:
        status = "WARN"
    else:
        status = "PASS"

    return {
        "skill": skill_dir.name,
        "status": status,
        "overall_score": overall_score,
        "categories": categories,
        "summary": {"critical": total_critical, "warning": total_warning},
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def format_markdown(results):
    skill = results["skill"]
    overall = results.get("overall_score", "N/A")
    out = [
        f"## Skill Audit: {skill}\n",
        f"### Status: {results['status']} — Overall Score: {overall}/10\n",
    ]

    all_findings = []
    for cat_name, cat_data in results["categories"].items():
        for f in cat_data.get("findings", []):
            all_findings.append((cat_name, f))

    for sev, heading in [
        ("critical", "### Critical (must fix)"),
        ("warning", "### Warnings (should fix)"),
        ("info", "### Info (consider)"),
    ]:
        items = [
            f"- [{item[1].get('check', '')}] ({item[0]}) "
            f"{item[1].get('message', '')}"
            for item in all_findings if item[1].get("severity") == sev
        ]
        if items:
            out.append(heading)
            out.extend(items)
            out.append("")

    out.append("### Category Breakdown\n")
    out.append("| Category | Weight | Score | Critical | Warning | Info |")
    out.append("|----------|--------|-------|----------|---------|------|")
    for cat, data in results["categories"].items():
        c = data["counts"]
        w = CATEGORY_WEIGHTS.get(cat, 1)
        s = data.get("baseline_score", "—")
        out.append(f"| {cat} | {w} | {s}/10 | {c.get('critical', 0)} "
                   f"| {c.get('warning', 0)} | {c.get('info', 0)} |")

    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Single skill audit for bundle-plugins.")
    parser.add_argument("skill_path",
                        help="Skill directory or SKILL.md file path")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of markdown")
    args = parser.parse_args()

    results = run_skill_audit(args.skill_path)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_markdown(results))

    from _cli import exit_by_severity
    exit_by_severity(results["summary"])


if __name__ == "__main__":
    main()
