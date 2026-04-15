#!/usr/bin/env python3
"""
Comprehensive audit for bundle-plugins.

Orchestrates audit_security.py, audit_skill.py, audit_workflow.py, and
audit_docs.py, then runs additional structural, version-sync, hook, and
testing checks to produce a combined plugin health report.

For agent-authored rich reports, see skills/auditing/references/plugin-report-template.md.

Usage:
    python audit_plugin.py [project-root]
    python audit_plugin.py --json [project-root]

Exit codes: 0 = pass, 1 = warnings, 2 = critical findings
"""

import json
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
_RELEASING_DIR = _SCRIPT_DIR.parent.parent.parent / "skills" / "releasing" / "scripts"
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
if str(_RELEASING_DIR) not in sys.path:
    sys.path.insert(0, str(_RELEASING_DIR))

import audit_workflow
import bump_version
import audit_docs
import audit_security
import audit_skill
import _graph
from _parsing import parse_all_skills

# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

from _scoring import compute_baseline_score, compute_weighted_average

CATEGORY_WEIGHTS = {
    "structure": 3,
    "manifests": 2,
    "version_sync": 3,
    "skill_quality": 2,
    "cross_references": 2,
    "workflow": 3,
    "hooks": 2,
    "testing": 2,
    "documentation": 1,
    "security": 3,
}


# ---------------------------------------------------------------------------
# Category checkers
# ---------------------------------------------------------------------------

def check_structure(root):
    """Directory layout and required files."""
    findings = []
    required_dirs = ["skills", "hooks"]

    for d in required_dirs:
        if not (root / d).is_dir():
            findings.append(dict(check="S1", severity="critical",
                                 message=f"Missing required directory: {d}/"))

    has_any_manifest = any((root / d).is_dir() for d in [
        ".claude-plugin", ".cursor-plugin", ".codex", ".opencode"])
    if not has_any_manifest and not (root / "GEMINI.md").exists():
        findings.append(dict(check="S2", severity="warning",
                             message="No platform manifest found"))

    if not (root / ".gitignore").exists():
        findings.append(dict(check="S3", severity="warning", message="Missing .gitignore"))

    if not (root / "README.md").exists():
        findings.append(dict(check="S5", severity="warning", message="Missing README.md"))

    if not (root / "LICENSE").exists():
        findings.append(dict(check="S6", severity="info", message="Missing LICENSE file"))

    skills_dir = root / "skills"
    if skills_dir.is_dir():
        skill_count = sum(1 for d in skills_dir.iterdir() if d.is_dir())
        bootstrap_found = any(
            (skills_dir / d / "SKILL.md").exists()
            for d in skills_dir.iterdir()
            if d.is_dir() and d.name.startswith("using-"))
        if skill_count > 0 and not bootstrap_found:
            findings.append(dict(check="S7", severity="warning",
                                 message="No bootstrap skill (using-*) found"))

    return findings


def check_manifests(root):
    """Platform manifest validity."""
    findings = []

    manifest_map = {
        ".claude-plugin/plugin.json": "Claude Code",
        ".cursor-plugin/plugin.json": "Cursor",
        ".codex/INSTALL.md": "Codex",
        "GEMINI.md": "Gemini CLI",
    }
    for path_str, platform in manifest_map.items():
        fpath = root / path_str
        if not fpath.exists():
            continue
        if fpath.suffix == ".json":
            try:
                data = json.loads(fpath.read_text(encoding="utf-8"))
                if not isinstance(data, dict):
                    findings.append(dict(check="P2", severity="critical",
                                         message=f"{path_str}: not a JSON object"))
                    continue
                skills_val = data.get("skills", [])
                if isinstance(skills_val, str):
                    if skills_val and not (root / skills_val).exists():
                        findings.append(dict(check="P3", severity="critical",
                                             message=f"{path_str}: skill path not found: {skills_val}"))
                elif isinstance(skills_val, list):
                    for entry in skills_val:
                        sp = entry if isinstance(entry, str) else entry.get("path", "")
                        if sp and not (root / sp).exists():
                            findings.append(dict(check="P3", severity="critical",
                                                 message=f"{path_str}: skill path not found: {sp}"))
            except json.JSONDecodeError as e:
                findings.append(dict(check="P2", severity="critical",
                                     message=f"{path_str}: invalid JSON — {e}"))

    opencode_dir = root / ".opencode" / "plugins"
    if opencode_dir.is_dir():
        for js_file in opencode_dir.glob("*.js"):
            content = js_file.read_text(encoding="utf-8", errors="replace")
            if "module.exports" not in content and "export" not in content:
                findings.append(dict(check="P6", severity="warning",
                                     message=f"{js_file.relative_to(root)}: no module.exports"))

    return findings


def check_version_sync(root):
    """Version drift across manifests (delegates to bump_version)."""
    findings = []
    vb_path = root / ".version-bump.json"
    if not vb_path.exists():
        findings.append(dict(check="V1", severity="critical",
                             message="Missing .version-bump.json"))
        return findings

    try:
        result = bump_version.run_check(root)
    except (json.JSONDecodeError, SystemExit):
        findings.append(dict(check="V1", severity="critical",
                             message=".version-bump.json invalid or unreadable"))
        return findings

    for m in result.get("missing", []):
        findings.append(dict(check="V2", severity="warning",
                             message=f".version-bump.json lists missing file: {m}"))

    if len(result.get("unique_versions", [])) > 1:
        drift = ", ".join(f"{k}={v}" for k, v in result["versions"].items())
        findings.append(dict(check="V3", severity="critical",
                             message=f"Version drift detected: {drift}"))

    bump_script = root / "scripts" / "bump-version.sh"
    if not bump_script.exists():
        findings.append(dict(check="V4", severity="info",
                             message="Missing scripts/bump-version.sh"))

    canonical = root / "skills" / "releasing" / "scripts" / "bump_version.py"
    template = root / "skills" / "scaffolding" / "assets" / "scripts" / "bump_version.py"
    if canonical.exists() and template.exists():
        c_lines = canonical.read_text(encoding="utf-8", errors="replace").splitlines()
        t_lines = template.read_text(encoding="utf-8", errors="replace").splitlines()
        def _skip_docstring(lines):
            """Return lines after the module docstring."""
            in_doc = False
            result = []
            for line in lines:
                if not in_doc and line.strip().startswith('"""'):
                    in_doc = True
                    if line.strip().count('"""') >= 2:
                        in_doc = False
                    continue
                if in_doc:
                    if '"""' in line:
                        in_doc = False
                    continue
                result.append(line)
            return result
        c_body = _skip_docstring(c_lines)
        t_body = _skip_docstring(t_lines)
        if c_body != t_body:
            findings.append(dict(check="V8", severity="warning",
                                 message="bump_version.py template drift: "
                                         "scaffolding/assets copy differs from releasing source"))

    return findings


def check_hooks(root):
    """Bootstrap injection and hook scripts."""
    findings = []
    hooks_dir = root / "hooks"
    if not hooks_dir.is_dir():
        findings.append(dict(check="H1", severity="warning", message="Missing hooks/ directory"))
        return findings

    session_start = hooks_dir / "session-start.py"
    if not session_start.exists():
        findings.append(dict(check="H2", severity="warning",
                             message="Missing hooks/session-start.py"))
    else:
        content = session_start.read_text(encoding="utf-8", errors="replace")
        if "SKILL.md" not in content:
            findings.append(dict(check="H3", severity="warning",
                                 message="session-start.py doesn't reference any SKILL.md"))

    hooks_json = hooks_dir / "hooks.json"
    if hooks_json.exists():
        try:
            data = json.loads(hooks_json.read_text(encoding="utf-8", errors="replace"))
            if "description" not in data:
                findings.append(dict(check="H9", severity="info",
                                     message="hooks.json missing top-level 'description' field"))
            hooks_block = data.get("hooks", {})
            for event_name, groups in hooks_block.items():
                if isinstance(groups, list):
                    for group in groups:
                        for handler in group.get("hooks", []):
                            if isinstance(handler, dict) and "timeout" not in handler:
                                findings.append(dict(check="H9", severity="info",
                                                     message=f"hooks.json handler in {event_name} missing 'timeout' field"))
        except (json.JSONDecodeError, OSError):
            pass

    return findings


def check_documentation(root):
    """Documentation consistency via audit_docs.py (D1-D9)."""
    result = audit_docs.run_check(root)
    return result.get("findings", [])


def check_testing(root):
    """Test directory, prompt files, and eval results."""
    findings = []
    tests_dir = root / "tests"
    if not tests_dir.is_dir():
        findings.append(dict(check="T1", severity="warning",
                             message="Missing tests/ directory"))
        return findings

    skills_dir = root / "skills"
    if skills_dir.is_dir():
        for skill_dir in sorted(skills_dir.iterdir()):
            if not skill_dir.is_dir():
                continue
            name = skill_dir.name
            prompts_a = tests_dir / "prompts" / f"{name}.yml"
            prompts_b = skill_dir / "tests" / "prompts.yml"
            if not prompts_a.exists() and not prompts_b.exists():
                findings.append(dict(check="T5", severity="warning",
                                     message=f"No test prompts for skill '{name}'"))

    bundles_dir = root / ".bundles-forge"
    if not bundles_dir.is_dir() or not any(
            f.name.endswith("-eval-original.md") or "-eval-" in f.name
            for f in bundles_dir.iterdir() if f.is_file()):
        findings.append(dict(check="T8", severity="info",
                             message="No A/B eval results found in .bundles-forge/"))

    if bundles_dir.is_dir():
        has_chain_eval = any(
            "-chain-eval-" in f.name
            for f in bundles_dir.iterdir() if f.is_file())
        if not has_chain_eval:
            findings.append(dict(check="T9", severity="info",
                                 message="No chain eval results found in "
                                         ".bundles-forge/"))

    return findings


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run_audit(project_root):
    root = Path(project_root).resolve()

    parsed_skills = parse_all_skills(root)

    sec_results = audit_security.run_scan(root)
    lint_results = audit_skill.run_lint(root, parsed_skills=parsed_skills)
    workflow_results = audit_workflow.run_workflow_audit(
        root, parsed_skills=parsed_skills, lint_results=lint_results)
    graph_findings, _graph_adj = _graph.run_graph_analysis(parsed_skills)
    structure = check_structure(root)
    manifests = check_manifests(root)
    version_sync = check_version_sync(root)
    hooks = check_hooks(root)
    docs = check_documentation(root)
    testing = check_testing(root)

    def _count(findings, key="severity"):
        c = {"critical": 0, "warning": 0, "info": 0}
        for f in findings:
            s = f.get(key, "info")
            c[s] = c.get(s, 0) + 1
        return c

    def _flat_findings(detail, finding_key="findings", risk_key="severity"):
        """Extract a flat list of findings from a detail result."""
        flat = []
        if "files" in detail:
            for fr in detail["files"]:
                for f in fr.get("findings", []):
                    entry = {"severity": f.get("risk", "info"),
                             "check": f.get("check_id", "")}
                    if "confidence" in f:
                        entry["confidence"] = f["confidence"]
                    flat.append(entry)
        if "skills" in detail:
            for sr in detail["skills"]:
                for f in sr.get("findings", []):
                    flat.append(f)
        return flat

    categories = {
        "structure": {"findings": structure, "counts": _count(structure)},
        "manifests": {"findings": manifests, "counts": _count(manifests)},
        "version_sync": {"findings": version_sync, "counts": _count(version_sync)},
        "skill_quality": {
            "findings": [],
            "counts": lint_results["summary"],
            "detail": lint_results,
        },
        "cross_references": {
            "findings": graph_findings,
            "counts": _count(graph_findings),
        },
        "workflow": {
            "findings": (workflow_results.get("focus_findings", [])
                         + workflow_results.get("context_findings", [])),
            "counts": workflow_results["summary"],
            "detail": workflow_results,
        },
        "hooks": {"findings": hooks, "counts": _count(hooks)},
        "testing": {"findings": testing, "counts": _count(testing)},
        "documentation": {"findings": docs, "counts": _count(docs)},
        "security": {
            "findings": [],
            "counts": sec_results["summary"],
            "detail": sec_results,
        },
    }

    # Compute baseline scores per category
    scores = {}
    for cat_name, cat_data in categories.items():
        if cat_data["findings"]:
            scores[cat_name] = compute_baseline_score(cat_data["findings"])
        elif "detail" in cat_data:
            flat = _flat_findings(cat_data["detail"])
            scores[cat_name] = compute_baseline_score(flat)
        else:
            scores[cat_name] = 10
        cat_data["baseline_score"] = scores[cat_name]

    overall_score = compute_weighted_average(scores, CATEGORY_WEIGHTS)

    total_critical = sum(
        d["counts"].get("critical", 0) for d in categories.values())
    total_warning = sum(
        d["counts"].get("warning", 0) for d in categories.values())

    if total_critical > 0:
        status = "FAIL"
    elif total_warning > 0:
        status = "WARN"
    else:
        status = "PASS"

    return {
        "status": status,
        "overall_score": overall_score,
        "categories": categories,
        "summary": {"critical": total_critical, "warning": total_warning},
    }

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def _classify_check(check_code):
    """Map a check code to one of the 4 skill-level categories."""
    if check_code.startswith("S"):
        return "Structure"
    if check_code.startswith("Q"):
        return "Skill Quality"
    if check_code.startswith("X"):
        return "Cross-References"
    if check_code.startswith(("SEC", "SC", "HK", "AG", "BS", "MC", "OC", "PC")):
        return "Security"
    return "Skill Quality"


def _skill_category_counts(findings):
    """Tally findings per skill-level category."""
    cats = {
        "Structure": {"critical": 0, "warning": 0, "info": 0},
        "Skill Quality": {"critical": 0, "warning": 0, "info": 0},
        "Cross-References": {"critical": 0, "warning": 0, "info": 0},
        "Security": {"critical": 0, "warning": 0, "info": 0},
    }
    for f in findings:
        cat = _classify_check(f.get("check", ""))
        sev = f.get("severity", "info")
        cats[cat][sev] = cats[cat].get(sev, 0) + 1
    return cats


def format_markdown(results, project_name):
    overall = results.get("overall_score", "N/A")
    out = [
        f"## Bundle-Plugin Audit: {project_name}\n",
        f"### Status: {results['status']} — Overall Score: {overall}/10\n",
    ]

    all_findings = []
    for cat_name, cat_data in results["categories"].items():
        for f in cat_data.get("findings", []):
            all_findings.append((cat_name, f))

    sec_detail = results["categories"].get("security", {}).get("detail", {})
    for fr in sec_detail.get("files", []):
        for f in fr.get("findings", []):
            entry = {
                "check": f.get("check_id", ""),
                "severity": f.get("risk", "info"),
                "message": f"{fr['file']}:{f.get('line', '?')} — {f.get('description', '')}",
            }
            if "confidence" in f:
                entry["confidence"] = f["confidence"]
            all_findings.append(("security", entry))

    lint_detail = results["categories"].get("skill_quality", {}).get("detail", {})
    for sr in lint_detail.get("skills", []):
        for f in sr.get("findings", []):
            all_findings.append(("skill_quality", {
                "check": f.get("check", ""),
                "severity": f.get("severity", "info"),
                "message": f"{sr['skill']}: {f.get('message', '')}",
            }))


    for sev, heading in [
        ("critical", "### Critical (must fix)"),
        ("warning", "### Warnings (should fix)"),
        ("info", "### Info (consider)"),
    ]:
        items = [f"- [{item[1].get('check', '')}] ({item[0]}) {item[1].get('message', '')}"
                 for item in all_findings
                 if item[1].get("severity") == sev
                 and item[1].get("confidence") != "suspicious"]
        if items:
            out.append(heading)
            out.extend(items)
            out.append("")

    sus_items = [f"- [{item[1].get('check', '')}] ({item[0]}) "
                 f"{item[1].get('message', '')} ({item[1].get('severity', '')})"
                 for item in all_findings
                 if item[1].get("confidence") == "suspicious"
                 and item[1].get("severity") in ("critical", "warning")]
    if sus_items:
        out.append("### Suspicious (needs review)")
        out.extend(sus_items)
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

    # Per-skill breakdown
    skill_results = lint_detail.get("skills", [])
    if skill_results:
        out.append("")
        out.append("### Per-Skill Breakdown\n")
        for sr in skill_results:
            skill_name = sr["skill"]
            out.append(f"#### {skill_name}\n")

            findings = sr.get("findings", [])
            if not findings:
                out.append("No findings.\n")
                continue

            for f in findings:
                sev_char = f["severity"][0].upper()
                out.append(f"- [{sev_char}] {f['check']}: {f['message']}")

            cat_counts = _skill_category_counts(findings)
            out.append("")
            out.append("| Category | Critical | Warning | Info |")
            out.append("|----------|----------|---------|------|")
            for cat_name, counts in cat_counts.items():
                out.append(f"| {cat_name} | {counts['critical']} "
                           f"| {counts['warning']} | {counts['info']} |")
            out.append("")

    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    from _cli import make_parser, resolve_root, exit_by_severity
    args = make_parser("Comprehensive audit for bundle-plugins.").parse_args()
    root = resolve_root(args.project_root)

    results = run_audit(root)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_markdown(results, root.name))

    exit_by_severity(results["summary"])


if __name__ == "__main__":
    main()
