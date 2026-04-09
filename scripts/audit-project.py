#!/usr/bin/env python3
"""
Comprehensive audit for bundle-plugins.

Orchestrates scan-security.py and lint-skills.py, then runs additional
structural, version-sync, hook, and documentation checks to produce a
combined project health report.

Usage:
    python scripts/audit-project.py [project-root]
    python scripts/audit-project.py --json [project-root]

Exit codes: 0 = healthy, 1 = warnings, 2 = critical findings
"""

import argparse
import json
import re
import sys
from pathlib import Path

# Import sibling modules by path
_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
import importlib
scan_security = importlib.import_module("scan-security")
lint_skills = importlib.import_module("lint-skills")

# ---------------------------------------------------------------------------
# Category checkers (structure, manifests, version-sync, hooks, docs)
# ---------------------------------------------------------------------------

def check_structure(root):
    """Category 1: Directory layout and required files."""
    findings = []
    required_dirs = ["skills", "hooks", "scripts"]
    optional_dirs = ["agents", "commands", ".claude-plugin", ".cursor-plugin", ".codex", ".opencode"]

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

    if not (root / "package.json").exists():
        findings.append(dict(check="S4", severity="info", message="Missing package.json"))

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
    """Category 2: Platform manifest validity."""
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
                    findings.append(dict(check="M1", severity="critical",
                                         message=f"{path_str}: not a JSON object"))
                    continue
                skills_val = data.get("skills", [])
                if isinstance(skills_val, str):
                    if skills_val and not (root / skills_val).exists():
                        findings.append(dict(check="M2", severity="critical",
                                             message=f"{path_str}: skill path not found: {skills_val}"))
                elif isinstance(skills_val, list):
                    for entry in skills_val:
                        sp = entry if isinstance(entry, str) else entry.get("path", "")
                        if sp and not (root / sp).exists():
                            findings.append(dict(check="M2", severity="critical",
                                                 message=f"{path_str}: skill path not found: {sp}"))
            except json.JSONDecodeError as e:
                findings.append(dict(check="M1", severity="critical",
                                     message=f"{path_str}: invalid JSON — {e}"))

    opencode_dir = root / ".opencode" / "plugins"
    if opencode_dir.is_dir():
        for js_file in opencode_dir.glob("*.js"):
            content = js_file.read_text(encoding="utf-8", errors="replace")
            if "module.exports" not in content and "export" not in content:
                findings.append(dict(check="M3", severity="warning",
                                     message=f"{js_file.relative_to(root)}: no module.exports"))

    return findings


def check_version_sync(root):
    """Category 3: Version drift across manifests."""
    findings = []
    vb_path = root / ".version-bump.json"
    if not vb_path.exists():
        findings.append(dict(check="V1", severity="warning",
                             message="Missing .version-bump.json"))
        return findings

    try:
        vb = json.loads(vb_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        findings.append(dict(check="V1", severity="critical",
                             message=f".version-bump.json invalid JSON: {e}"))
        return findings

    version_re = re.compile(r"\d+\.\d+\.\d+")
    versions_found = {}
    for entry in vb.get("files", []):
        fpath_str = entry["path"] if isinstance(entry, dict) else entry
        fpath = root / fpath_str
        if not fpath.exists():
            findings.append(dict(check="V2", severity="warning",
                                 message=f".version-bump.json lists missing file: {fpath_str}"))
            continue
        content = fpath.read_text(encoding="utf-8", errors="replace")
        matches = version_re.findall(content)
        if matches:
            versions_found[fpath_str] = matches[0]

    unique = set(versions_found.values())
    if len(unique) > 1:
        drift = ", ".join(f"{k}={v}" for k, v in versions_found.items())
        findings.append(dict(check="V3", severity="critical",
                             message=f"Version drift detected: {drift}"))

    bump_script = root / "scripts" / "bump-version.sh"
    if not bump_script.exists():
        findings.append(dict(check="V4", severity="info",
                             message="Missing scripts/bump-version.sh"))

    return findings


def check_hooks(root):
    """Category 5: Bootstrap injection and hook scripts."""
    findings = []
    hooks_dir = root / "hooks"
    if not hooks_dir.is_dir():
        findings.append(dict(check="H1", severity="warning", message="Missing hooks/ directory"))
        return findings

    session_start = hooks_dir / "session-start"
    if not session_start.exists():
        findings.append(dict(check="H2", severity="warning",
                             message="Missing hooks/session-start"))
    else:
        content = session_start.read_text(encoding="utf-8", errors="replace")
        if "SKILL.md" not in content:
            findings.append(dict(check="H3", severity="warning",
                                 message="session-start doesn't reference any SKILL.md"))
        if "#!/" not in content.splitlines()[0] if content.splitlines() else "":
            findings.append(dict(check="H4", severity="info",
                                 message="session-start missing shebang line"))

    run_hook = hooks_dir / "run-hook.cmd"
    if not run_hook.exists():
        findings.append(dict(check="H5", severity="info",
                             message="Missing hooks/run-hook.cmd (Windows support)"))

    return findings


def check_documentation(root):
    """Category 8: README, CHANGELOG, install docs."""
    findings = []

    readme = root / "README.md"
    if readme.exists():
        content = readme.read_text(encoding="utf-8", errors="replace")
        if "## Install" not in content and "## Installation" not in content:
            findings.append(dict(check="D1", severity="info",
                                 message="README.md missing Installation section"))
        if "## Skills" not in content and "## Available Skills" not in content:
            findings.append(dict(check="D2", severity="info",
                                 message="README.md missing Skills listing"))

    changelog = root / "CHANGELOG.md"
    if not changelog.exists():
        findings.append(dict(check="D3", severity="info", message="Missing CHANGELOG.md"))

    return findings


# ---------------------------------------------------------------------------
# Category weights and scoring
# ---------------------------------------------------------------------------

CATEGORY_WEIGHTS = {
    "structure": 0.15,
    "manifests": 0.15,
    "version_sync": 0.15,
    "skill_quality": 0.15,
    "hooks": 0.10,
    "documentation": 0.05,
    "security": 0.25,
}


def severity_score(counts):
    crit = counts.get("critical", counts.get("error", 0))
    warn = counts.get("warning", 0)
    if crit > 0:
        return max(0, 4 - crit)
    if warn > 0:
        return max(4, 8 - warn)
    return 10


# ---------------------------------------------------------------------------
# Orchestrator
# ---------------------------------------------------------------------------

def run_audit(project_root):
    root = Path(project_root).resolve()

    sec_results = scan_security.run_scan(root)
    lint_results = lint_skills.run_lint(root)
    structure = check_structure(root)
    manifests = check_manifests(root)
    version_sync = check_version_sync(root)
    hooks = check_hooks(root)
    docs = check_documentation(root)

    def _count(findings, key="severity"):
        c = {"critical": 0, "warning": 0, "info": 0, "error": 0}
        for f in findings:
            s = f.get(key, "info")
            c[s] = c.get(s, 0) + 1
        return c

    categories = {
        "structure": {"findings": structure, "counts": _count(structure)},
        "manifests": {"findings": manifests, "counts": _count(manifests)},
        "version_sync": {"findings": version_sync, "counts": _count(version_sync)},
        "skill_quality": {
            "findings": [],
            "counts": lint_results["summary"],
            "detail": lint_results,
        },
        "hooks": {"findings": hooks, "counts": _count(hooks)},
        "documentation": {"findings": docs, "counts": _count(docs)},
        "security": {
            "findings": [],
            "counts": sec_results["summary"],
            "detail": sec_results,
        },
    }

    scores = {}
    for cat, data in categories.items():
        scores[cat] = severity_score(data["counts"])
    overall = sum(scores[c] * CATEGORY_WEIGHTS[c] for c in CATEGORY_WEIGHTS)

    total_critical = sum(
        d["counts"].get("critical", 0) + d["counts"].get("error", 0)
        for d in categories.values())
    total_warning = sum(d["counts"].get("warning", 0) for d in categories.values())

    return {
        "categories": {k: {"score": scores[k], **v} for k, v in categories.items()},
        "scores": scores,
        "overall_score": round(overall, 1),
        "summary": {"critical": total_critical, "warning": total_warning},
    }

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def format_markdown(results, project_name):
    out = [
        f"## Bundle-Plugin Audit: {project_name}\n",
        f"### Overall Score: {results['overall_score']}/10\n",
    ]

    all_findings = []
    for cat_name, cat_data in results["categories"].items():
        for f in cat_data.get("findings", []):
            all_findings.append((cat_name, f))

    sec_detail = results["categories"].get("security", {}).get("detail", {})
    for fr in sec_detail.get("files", []):
        for f in fr.get("findings", []):
            all_findings.append(("security", {
                "check": f.get("check_id", ""),
                "severity": f.get("risk", "info"),
                "message": f"{fr['file']}:{f.get('line', '?')} — {f.get('description', '')}",
            }))

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
        ("error", "### Errors"),
        ("warning", "### Warnings (should fix)"),
        ("info", "### Info (consider)"),
    ]:
        items = [f"- [{item[1].get('check', '')}] ({item[0]}) {item[1].get('message', '')}"
                 for item in all_findings if item[1].get("severity") == sev]
        if items:
            out.append(heading)
            out.extend(items)
            out.append("")

    out.append("### Category Breakdown\n")
    out.append("| Category | Score | Critical | Warning | Info |")
    out.append("|----------|-------|----------|---------|------|")
    for cat, data in results["categories"].items():
        c = data["counts"]
        crit = c.get("critical", 0) + c.get("error", 0)
        out.append(f"| {cat} | {data['score']}/10 | {crit} | {c.get('warning', 0)} | {c.get('info', 0)} |")

    return "\n".join(out)


def _json_safe(obj):
    if isinstance(obj, dict):
        cleaned = {}
        for k, v in obj.items():
            if k == "detail":
                continue
            cleaned[k] = _json_safe(v)
        return cleaned
    if isinstance(obj, list):
        return [_json_safe(i) for i in obj]
    return obj

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Comprehensive audit for bundle-plugins.")
    parser.add_argument("project_root", nargs="?", default=".",
                        help="Bundle-plugin root (default: current directory)")
    parser.add_argument("--json", action="store_true", help="Output JSON instead of markdown")
    args = parser.parse_args()

    root = Path(args.project_root).resolve()
    if not (root / "skills").is_dir():
        print(f"error: {root} has no skills/ directory", file=sys.stderr)
        sys.exit(1)

    results = run_audit(root)
    if args.json:
        print(json.dumps(_json_safe(results), indent=2))
    else:
        print(format_markdown(results, root.name))

    sys.exit(2 if results["summary"]["critical"] else
             1 if results["summary"]["warning"] else 0)


if __name__ == "__main__":
    main()
