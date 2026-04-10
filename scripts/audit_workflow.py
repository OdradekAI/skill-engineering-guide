#!/usr/bin/env python3
"""
Workflow audit for bundle-plugins.

Evaluates workflow quality across three layers: static structure (from
lint_skills.py graph analysis), semantic interface (Integration/Inputs/Outputs
completeness), and behavioral verification (chain eval — agent-only).

Supports --focus-skills to partition findings into Focus Area and Context.

For agent-authored rich reports, see skills/auditing/references/workflow-report-template.md.

Usage:
    python scripts/audit_workflow.py [project-root]
    python scripts/audit_workflow.py --focus-skills skill-a,skill-b [project-root]
    python scripts/audit_workflow.py --json [project-root]

Exit codes: 0 = pass, 1 = warnings, 2 = critical findings
"""

import json
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import lint_skills

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LAYER_WEIGHTS = {
    "static": 3,
    "semantic": 2,
    "behavioral": 1,
}

_G_TO_W = {"G1": "W1", "G2": "W2", "G3": "W3", "G4": "W4", "G5": "W5"}

_PLACEHOLDER_RE = re.compile(
    r"^\s*[-*]?\s*(?:TBD|TODO|WIP|placeholder|fill in|coming soon)\s*$",
    re.IGNORECASE,
)
_CALLS_HEADER_RE = re.compile(r"\*\*Calls?:?\*\*", re.IGNORECASE)
_CALLED_BY_HEADER_RE = re.compile(r"\*\*Called\s+by:?\*\*", re.IGNORECASE)
_BOLD_REF_RE = re.compile(r"\*\*([a-z0-9-]+):([a-z0-9-]+)\*\*")
_BACKTICK_REF_RE = re.compile(r"`([a-z0-9-]+):([a-z0-9-]+)`")


# ---------------------------------------------------------------------------
# Scoring (shared formula with audit_project)
# ---------------------------------------------------------------------------

def compute_baseline_score(findings):
    critical = sum(1 for f in findings if f.get("severity") == "critical")
    warning = sum(1 for f in findings if f.get("severity") == "warning")
    return max(0, 10 - (critical * 3 + warning * 1))


def compute_weighted_average(scores):
    total_weight = 0
    weighted_sum = 0.0
    for layer, score in scores.items():
        w = LAYER_WEIGHTS.get(layer, 1)
        weighted_sum += score * w
        total_weight += w
    return round(weighted_sum / total_weight, 1) if total_weight else 0.0


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _read_skill_content(skills_dir, skill_name):
    path = skills_dir / skill_name / "SKILL.md"
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    return ""


def _detect_project_prefixes(project_root):
    """Return the set of valid cross-reference prefixes for the project."""
    prefixes = {project_root.name}
    pkg_path = project_root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            prefixes.add(pkg.get("name", project_root.name))
            abbrev = pkg.get("abbreviation")
            if abbrev:
                prefixes.add(abbrev)
        except (json.JSONDecodeError, OSError):
            pass
    return prefixes


def _extract_refs_from_block(content, header_re, valid_prefixes):
    """Extract skill refs from a **Calls:** or **Called by:** block."""
    refs = set()
    lines = content.splitlines()
    in_block = False
    for line in lines:
        if header_re.search(line):
            in_block = True
            for m in _BOLD_REF_RE.finditer(line):
                if m.group(1) in valid_prefixes:
                    refs.add(m.group(2))
            for m in _BACKTICK_REF_RE.finditer(line):
                if m.group(1) in valid_prefixes:
                    refs.add(m.group(2))
            continue
        if in_block:
            if line.startswith("- ") or line.startswith("  "):
                for m in _BOLD_REF_RE.finditer(line):
                    if m.group(1) in valid_prefixes:
                        refs.add(m.group(2))
                for m in _BACKTICK_REF_RE.finditer(line):
                    if m.group(1) in valid_prefixes:
                        refs.add(m.group(2))
            elif line.strip() and not line.startswith("-"):
                in_block = False
    return refs


def _extract_section_content(content, section_name):
    """Return lines between ## <section_name> and the next ## heading."""
    lines = content.splitlines()
    in_section = False
    section_lines = []
    for line in lines:
        if line.strip() == f"## {section_name}":
            in_section = True
            continue
        if in_section:
            if line.startswith("## "):
                break
            section_lines.append(line)
    return section_lines


def _section_is_empty_or_placeholder(section_lines):
    """Check if section lines are empty or only contain placeholder text."""
    meaningful = [ln for ln in section_lines if ln.strip()
                  and not ln.strip().startswith("#")]
    if not meaningful:
        return True
    return all(_PLACEHOLDER_RE.match(ln) for ln in meaningful)


def _involves_focus(finding, focus_skills):
    """Check whether a finding involves any of the focus skills."""
    if not focus_skills:
        return True
    msg = finding.get("message", "")
    skills_involved = finding.get("skills_involved", [])
    if skills_involved:
        return bool(set(skills_involved) & focus_skills)
    for s in focus_skills:
        if f"'{s}'" in msg or f"`{s}`" in msg or s in msg:
            return True
    return False


# ---------------------------------------------------------------------------
# Layer 1: Static Structure (W1-W5) — remap from lint_skills graph G1-G5
# ---------------------------------------------------------------------------

def check_static(lint_results, focus_skills=None):
    """Remap G1-G5 from lint_skills graph findings to W1-W5."""
    findings = []
    graph_findings = lint_results.get("graph", [])

    for gf in graph_findings:
        wf = dict(gf)
        old_check = wf.get("check", "")
        wf["check"] = _G_TO_W.get(old_check, old_check)
        wf["layer"] = "static"
        wf["focus"] = _involves_focus(wf, focus_skills)
        findings.append(wf)

    return findings


# ---------------------------------------------------------------------------
# Layer 2: Semantic Interface (W6-W10)
# ---------------------------------------------------------------------------

def check_semantic(project_root, lint_results, focus_skills=None):
    """Run W6-W10 semantic checks on skill Integration/Inputs/Outputs."""
    findings = []
    skills_dir = project_root / "skills"
    valid_prefixes = _detect_project_prefixes(project_root)
    skill_names = set()

    for sr in lint_results.get("skills", []):
        skill_names.add(sr["skill"])

    if len(skill_names) < 2:
        return findings

    skill_contents = {}
    for sname in skill_names:
        skill_contents[sname] = _read_skill_content(skills_dir, sname)

    # Build calls/called-by maps
    calls_map = {}
    called_by_map = {s: set() for s in skill_names}
    for sname, content in skill_contents.items():
        outgoing = _extract_refs_from_block(content, _CALLS_HEADER_RE,
                                            valid_prefixes)
        outgoing = {r for r in outgoing if r in skill_names and r != sname}
        calls_map[sname] = outgoing
        for target in outgoing:
            called_by_map[target].add(sname)

    declared_called_by = {}
    for sname, content in skill_contents.items():
        declared_called_by[sname] = _extract_refs_from_block(
            content, _CALLED_BY_HEADER_RE, valid_prefixes)

    # W6: Integration section with Calls/Called by for skills that have deps
    for sname, content in skill_contents.items():
        if sname.startswith("using-"):
            continue
        has_callers = bool(called_by_map.get(sname))
        has_callees = bool(calls_map.get(sname))
        if has_callers or has_callees:
            if "## Integration" not in content:
                findings.append(dict(
                    check="W6", severity="info", layer="semantic",
                    skills_involved=[sname],
                    focus=_involves_focus(
                        {"skills_involved": [sname]}, focus_skills),
                    message=f"Skill '{sname}' has workflow dependencies but "
                            "no ## Integration section"))

    # W9: Inputs/Outputs semantic quality
    for sname, content in skill_contents.items():
        if sname.startswith("using-"):
            continue
        for section_name in ("Inputs", "Outputs"):
            section_lines = _extract_section_content(content, section_name)
            if f"## {section_name}" in content and \
                    _section_is_empty_or_placeholder(section_lines):
                findings.append(dict(
                    check="W9", severity="warning", layer="semantic",
                    skills_involved=[sname],
                    focus=_involves_focus(
                        {"skills_involved": [sname]}, focus_skills),
                    message=f"Skill '{sname}': ## {section_name} section "
                            "is empty or contains only placeholder text"))

    # W10: Integration symmetry — Calls/Called by declarations match
    for src, targets in calls_map.items():
        for tgt in targets:
            dcb = declared_called_by.get(tgt, set())
            if src not in dcb:
                findings.append(dict(
                    check="W10", severity="warning", layer="semantic",
                    skills_involved=[src, tgt],
                    focus=_involves_focus(
                        {"skills_involved": [src, tgt]}, focus_skills),
                    message=f"Asymmetric integration: '{src}' calls '{tgt}' "
                            f"but '{tgt}' does not list '{src}' in "
                            "**Called by:**"))

    for tgt, declared_callers in declared_called_by.items():
        for caller in declared_callers:
            if caller in skill_names:
                actual_calls = calls_map.get(caller, set())
                if tgt not in actual_calls:
                    findings.append(dict(
                        check="W10", severity="warning", layer="semantic",
                        skills_involved=[caller, tgt],
                        focus=_involves_focus(
                            {"skills_involved": [caller, tgt]}, focus_skills),
                        message=f"Asymmetric integration: '{tgt}' lists "
                                f"'{caller}' in **Called by:** but '{caller}' "
                                f"does not list '{tgt}' in **Calls:**"))

    return findings


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run_workflow_audit(project_root, focus_skills=None):
    """Run the full workflow audit. Returns structured results dict.

    Args:
        project_root: Path to the bundle-plugin root.
        focus_skills: Optional set of skill names to focus on. If provided,
            findings are tagged with focus=True/False.
    """
    root = Path(project_root).resolve()
    if focus_skills and isinstance(focus_skills, (list, tuple)):
        focus_skills = set(focus_skills)

    lint_results = lint_skills.run_lint(root)

    static_findings = check_static(lint_results, focus_skills)
    semantic_findings = check_semantic(root, lint_results, focus_skills)
    behavioral_findings = []

    def _count(findings):
        c = {"critical": 0, "warning": 0, "info": 0}
        for f in findings:
            sev = f.get("severity", "info")
            c[sev] = c.get(sev, 0) + 1
        return c

    layers = {
        "static": {
            "findings": static_findings,
            "counts": _count(static_findings),
        },
        "semantic": {
            "findings": semantic_findings,
            "counts": _count(semantic_findings),
        },
        "behavioral": {
            "findings": behavioral_findings,
            "counts": _count(behavioral_findings),
            "skipped": True,
            "skip_reason": "Behavioral verification requires evaluator agent "
                           "dispatch (not available in script mode)",
        },
    }

    scores = {}
    for layer_name, layer_data in layers.items():
        if layer_data.get("skipped"):
            scores[layer_name] = 10
        else:
            scores[layer_name] = compute_baseline_score(layer_data["findings"])
        layer_data["baseline_score"] = scores[layer_name]

    overall_score = compute_weighted_average(scores)

    all_findings = static_findings + semantic_findings + behavioral_findings
    total_critical = sum(1 for f in all_findings
                         if f.get("severity") == "critical")
    total_warning = sum(1 for f in all_findings
                        if f.get("severity") == "warning")

    if total_critical > 0:
        status = "FAIL"
    elif total_warning > 0:
        status = "WARN"
    else:
        status = "PASS"

    focus_findings = [f for f in all_findings if f.get("focus", True)]
    context_findings = [f for f in all_findings if not f.get("focus", True)]

    return {
        "status": status,
        "overall_score": overall_score,
        "layers": layers,
        "summary": {"critical": total_critical, "warning": total_warning},
        "focus_skills": sorted(focus_skills) if focus_skills else None,
        "focus_findings": focus_findings,
        "context_findings": context_findings,
    }


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def format_markdown(results, project_name):
    overall = results.get("overall_score", "N/A")
    focus = results.get("focus_skills")
    out = [
        f"## Workflow Audit: {project_name}\n",
        f"### Status: {results['status']} — Overall Score: {overall}/10\n",
    ]
    if focus:
        out.append(f"**Focus skills:** {', '.join(focus)}\n")

    for sev, heading in [
        ("critical", "### Critical (must fix)"),
        ("warning", "### Warnings (should fix)"),
        ("info", "### Info (consider)"),
    ]:
        if focus:
            focus_items = [
                f"- [{f.get('check', '')}] ({f.get('layer', '')}) "
                f"{f.get('message', '')}"
                for f in results.get("focus_findings", [])
                if f.get("severity") == sev
            ]
            context_items = [
                f"- [{f.get('check', '')}] ({f.get('layer', '')}) "
                f"{f.get('message', '')}"
                for f in results.get("context_findings", [])
                if f.get("severity") == sev
            ]
            if focus_items or context_items:
                out.append(heading)
            if focus_items:
                out.append("**Focus Area:**")
                out.extend(focus_items)
            if context_items:
                out.append("**Context:**")
                out.extend(context_items)
            if focus_items or context_items:
                out.append("")
        else:
            all_findings = (results.get("focus_findings", [])
                            + results.get("context_findings", []))
            items = [
                f"- [{f.get('check', '')}] ({f.get('layer', '')}) "
                f"{f.get('message', '')}"
                for f in all_findings if f.get("severity") == sev
            ]
            if items:
                out.append(heading)
                out.extend(items)
                out.append("")

    out.append("### Layer Breakdown\n")
    out.append("| Layer | Weight | Score | Critical | Warning | Info |")
    out.append("|-------|--------|-------|----------|---------|------|")
    for layer_name, data in results["layers"].items():
        c = data["counts"]
        w = LAYER_WEIGHTS.get(layer_name, 1)
        s = data.get("baseline_score", "—")
        skipped = " (skipped)" if data.get("skipped") else ""
        out.append(f"| {layer_name}{skipped} | {w} | {s}/10 "
                   f"| {c.get('critical', 0)} | {c.get('warning', 0)} "
                   f"| {c.get('info', 0)} |")

    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Workflow audit for bundle-plugins.")
    parser.add_argument("project_root", nargs="?", default=".",
                        help="Bundle-plugin root (default: current directory)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of markdown")
    parser.add_argument("--focus-skills",
                        help="Comma-separated list of skill names to focus on")
    args = parser.parse_args()

    from _cli import resolve_root, exit_by_severity
    root = resolve_root(args.project_root)

    focus = None
    if args.focus_skills:
        focus = {s.strip() for s in args.focus_skills.split(",") if s.strip()}

    results = run_workflow_audit(root, focus_skills=focus)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_markdown(results, root.name))

    exit_by_severity(results["summary"])


if __name__ == "__main__":
    main()
