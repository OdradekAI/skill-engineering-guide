#!/usr/bin/env python3
"""
Workflow audit for bundle-plugins.

Evaluates workflow quality across three layers: static structure (W1-W5 via
_graph.run_graph_analysis), semantic interface (W6-W9), and behavioral
verification (W10-W11 — agent-only).

Supports --focus-skills to partition findings into Focus Area and Context.

For agent-authored rich reports, see skills/auditing/references/workflow-report-template.md.

Usage:
    python audit_workflow.py [target-dir]
    python audit_workflow.py --focus-skills skill-a,skill-b [target-dir]
    python audit_workflow.py --json [target-dir]

Exit codes: 0 = pass, 1 = warnings, 2 = critical findings
"""

import json
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import audit_skill
import _graph
from _parsing import parse_all_skills
from _scoring import compute_baseline_score, compute_weighted_average

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

LAYER_WEIGHTS = {
    "static": 3,
    "semantic": 2,
    "behavioral": 1,
}

_PLACEHOLDER_RE = re.compile(
    r"^\s*[-*]?\s*(?:TBD|TODO|WIP|placeholder|fill in|coming soon)\s*$",
    re.IGNORECASE,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

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
# Layer 1: Static Structure (W1-W5) — from _graph.run_graph_analysis
# ---------------------------------------------------------------------------

def check_static(parsed_skills, focus_skills=None):
    """Run W1-W5 via _graph.run_graph_analysis and tag with layer/focus."""
    findings = []
    graph_findings, graph = _graph.run_graph_analysis(parsed_skills)

    for gf in graph_findings:
        wf = dict(gf)
        wf["layer"] = "static"
        wf["focus"] = _involves_focus(wf, focus_skills)
        findings.append(wf)

    return findings, graph


# ---------------------------------------------------------------------------
# Layer 2: Semantic Interface (W6-W9)
# ---------------------------------------------------------------------------

def check_semantic(parsed_skills, lint_results, focus_skills=None):
    """Run W6-W9 semantic checks on skill Integration/Inputs/Outputs."""
    findings = []
    valid_prefixes = parsed_skills["valid_prefixes"]
    skill_names = set(parsed_skills["skills"].keys())

    if len(skill_names) < 2:
        return findings

    skill_contents = {
        sname: sdata["content"]
        for sname, sdata in parsed_skills["skills"].items()
        if sdata["content"]
    }

    calls_map = {}
    called_by_map = {s: set() for s in skill_names}
    for sname, content in skill_contents.items():
        outgoing = _graph.extract_calls(content, valid_prefixes)
        outgoing = {r for r in outgoing if r in skill_names and r != sname}
        calls_map[sname] = outgoing
        for target in outgoing:
            called_by_map[target].add(sname)

    declared_called_by = {}
    for sname, content in skill_contents.items():
        declared_called_by[sname] = _graph.extract_called_by(
            content, valid_prefixes)

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

    # W8: Inputs/Outputs semantic quality
    for sname, content in skill_contents.items():
        if sname.startswith("using-"):
            continue
        for section_name in ("Inputs", "Outputs"):
            section_lines = _extract_section_content(content, section_name)
            if f"## {section_name}" in content and \
                    _section_is_empty_or_placeholder(section_lines):
                findings.append(dict(
                    check="W8", severity="warning", layer="semantic",
                    skills_involved=[sname],
                    focus=_involves_focus(
                        {"skills_involved": [sname]}, focus_skills),
                    message=f"Skill '{sname}': ## {section_name} section "
                            "is empty or contains only placeholder text"))

    # W9: Integration symmetry — Calls/Called by declarations match
    for src, targets in calls_map.items():
        for tgt in targets:
            dcb = declared_called_by.get(tgt, set())
            if src not in dcb:
                findings.append(dict(
                    check="W9", severity="warning", layer="semantic",
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
                        check="W9", severity="warning", layer="semantic",
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

def run_workflow_audit(target_dir, focus_skills=None,
                       parsed_skills=None, lint_results=None):
    """Run the full workflow audit. Returns structured results dict.

    Args:
        target_dir: Path to the bundle-plugin root.
        focus_skills: Optional set of skill names to focus on. If provided,
            findings are tagged with focus=True/False.
        parsed_skills: Optional pre-computed result from parse_all_skills().
        lint_results: Optional pre-computed result from audit_skill.run_lint().
    """
    root = Path(target_dir).resolve()
    if focus_skills and isinstance(focus_skills, (list, tuple)):
        focus_skills = set(focus_skills)

    if parsed_skills is None:
        parsed_skills = parse_all_skills(root)

    if lint_results is None:
        lint_results = audit_skill.run_lint(root, parsed_skills=parsed_skills)

    static_findings, graph = check_static(parsed_skills, focus_skills)
    semantic_findings = check_semantic(parsed_skills, lint_results, focus_skills)
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
            scores[layer_name] = None
            layer_data["baseline_score"] = None
        else:
            scores[layer_name] = compute_baseline_score(layer_data["findings"])
            layer_data["baseline_score"] = scores[layer_name]

    overall_score = compute_weighted_average(scores, LAYER_WEIGHTS)

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

    skill_layers = {}
    for sname, sdata in parsed_skills["skills"].items():
        fm = sdata.get("frontmatter") or {}
        layer = fm.get("layer", "")
        if layer:
            skill_layers[sname] = layer
        elif sname.startswith("using-"):
            skill_layers[sname] = "meta"
    mermaid = _graph.generate_mermaid(graph, skill_layers or None)

    return {
        "status": status,
        "overall_score": overall_score,
        "layers": layers,
        "summary": {"critical": total_critical, "warning": total_warning},
        "focus_skills": sorted(focus_skills) if focus_skills else None,
        "focus_findings": focus_findings,
        "context_findings": context_findings,
        "mermaid": mermaid,
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
        skipped = data.get("skipped", False)
        s = data.get("baseline_score")
        score_str = "N/A (excluded from average)" if skipped else f"{s}/10"
        label = f"{layer_name} (skipped)" if skipped else layer_name
        out.append(f"| {label} | {w} | {score_str} "
                   f"| {c.get('critical', 0)} | {c.get('warning', 0)} "
                   f"| {c.get('info', 0)} |")

    mermaid = results.get("mermaid")
    if mermaid:
        out.append("\n### Dependency Graph\n")
        out.append("```mermaid")
        out.append(mermaid)
        out.append("```")
        out.append("")

    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Workflow audit for bundle-plugins.")
    parser.add_argument("target_dir", nargs="?", default=".",
                        help="Bundle-plugin root (default: current directory)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of markdown")
    parser.add_argument("--focus-skills",
                        help="Comma-separated list of skill names to focus on")
    args = parser.parse_args()

    from _cli import resolve_target, exit_by_severity
    root = resolve_target(args.target_dir)

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
