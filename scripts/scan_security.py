#!/usr/bin/env python3
"""
Security scanner for bundle-plugins.

Scans SKILL.md files, hook scripts, OpenCode plugins, agent prompts,
and bundled scripts for patterns that could exfiltrate data, destroy
resources, install backdoors, or override safety controls.

Usage:
    python scripts/scan_security.py [project-root]
    python scripts/scan_security.py --json [project-root]

Exit codes: 0 = clean, 1 = warnings only, 2 = critical findings
"""

import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Rule definitions — (check_id, risk, regex_pattern, description)
# Rules with pattern=None use custom logic in scan_file().
# ---------------------------------------------------------------------------

def _compile(pairs):
    return [(cid, risk, re.compile(pat, re.IGNORECASE) if pat else None, desc)
            for cid, risk, pat, desc in pairs]

SKILL_CONTENT_RULES = _compile([
    ("SC1", "critical", r"\.(env|ssh/|credentials|secrets|tokens|api_key)\b",
     "References to sensitive files/directories"),
    ("SC2", "critical", r"send.*(external|remote|server)|exfiltrat|upload.*secret",
     "Instructions to send data externally"),
    ("SC3", "warning", r"~/\.(config|aws|kube|gcloud)/",
     "References to user config directories"),
    ("SC4", "warning", r"process\.env|(\$ENV\b)|\$[A-Z_]*API[_]?KEY",
     "Environment variable access beyond documented needs"),
    ("SC5", "critical", r"rm\s+-rf\s+[/~]|rmdir\s+/s|del\s+/[fq]",
     "Destructive file deletion on broad paths"),
    ("SC6", "critical", r"git\s+push\s+--force|git\s+reset\s+--hard",
     "Force push or hard reset"),
    ("SC7", "critical", r"DROP\s+TABLE|DELETE\s+FROM(?!.*WHERE)",
     "Destructive database operations"),
    ("SC8", "warning", r"overwrite.*outside|modify.*outside.*project",
     "Modifying files outside the project directory"),
    ("SC9", "critical", r"ignore\s+(previous\s+)?instructions|override\s+safety|disable\s+verification",
     "Safety override instructions"),
    ("SC10", "critical", r"--no-verify|bypass\s+lint|disable\s+test|skip\s+hook",
     "Instructions to skip safety checks"),
    ("SC11", "warning", r"highest\s+priority|override\s+(all|user)|supersede",
     "Claims priority over user instructions"),
    ("SC15", "info", None, "Excessively long line (>500 chars)"),
])

HOOK_RULES = _compile([
    ("HK1", "critical", r"\b(curl|wget|nc|ncat|telnet)\b",
     "Network command in hook script"),
    ("HK2", "critical", r"https?://(?!localhost|127\.0\.0\.1)",
     "External URL"),
    ("HK3", "critical", r"\$[A-Z_]+.*\|\s*(curl|wget|nc)|cat.*\|\s*(curl|wget|nc)",
     "Piping data to network commands"),
    ("HK4", "warning", r"\b(dig|nslookup|host)\s",
     "DNS lookup that could encode data"),
    ("HK5", "critical", r"(ANTHROPIC|OPENAI|GITHUB|AZURE|GCP|AWS)_?(API_?)?KEY|GITHUB_TOKEN",
     "Reading API keys or secrets"),
    ("HK6", "warning", None, "Env var access beyond allowed set (custom check)"),
    ("HK7", "info", None, "Missing set -euo pipefail"),
    ("HK8", "critical", r"\.(bashrc|zshrc|profile|bash_profile)\b",
     "Writing to shell config files"),
    ("HK9", "critical", r"\b(crontab|systemctl|launchctl)\b",
     "Creating persistent services"),
    ("HK10", "critical", r"npm\s+(-g|install\s+-g)|pip\s+install\s+--user",
     "Installing global packages"),
    ("HK11", "warning", r"(>|>>)\s*/|mkdir\s+-p\s+/(?!tmp)",
     "Creating files outside project directory"),
    ("HK12", "warning", r"chmod\s+[2467]",
     "chmod with setuid/setgid bits"),
])

OPENCODE_RULES = _compile([
    ("OC1", "critical", r"\beval\s*\(|new\s+Function\s*\(|vm\.runIn",
     "Dynamic code execution"),
    ("OC2", "critical", r"child_process\.(exec|spawn)|execSync",
     "Child process execution"),
    ("OC3", "critical", r"require\s*\(\s*['\"]child_process|import\s*\(\s*['\"]child_process",
     "Importing child_process module"),
    ("OC4", "warning", r"require\s*\([^'\"]+\)|import\s*\([^'\"]+\)",
     "Dynamic require/import with variable paths"),
    ("OC5", "critical", r"\bfetch\s*\(|http\.request|https\.request|net\.connect",
     "Network requests"),
    ("OC6", "critical", r"\bWebSocket\b",
     "WebSocket connections"),
    ("OC7", "warning", r"require\s*\(\s*['\"](?:http|https|net|dgram|dns)['\"]",
     "Network-related module imports"),
    ("OC8", "critical", r"process\.env\.(ANTHROPIC|OPENAI|GITHUB|AZURE|AWS)",
     "Accessing API key environment variables"),
    ("OC9", "warning", r"process\.env\b",
     "Broad process.env access"),
])

AGENT_RULES = _compile([
    ("AG1", "critical", r"ignore.*(safety|guideline|instruction)|override.*(safety|rule)|bypass.*(safety|security)",
     "Safety override instructions in agent prompt"),
    ("AG2", "critical", r"(access|read|use).*(credential|secret|api.?key|token)",
     "Instructions to access credentials"),
    ("AG3", "critical", r"(make|send|perform).*(network|http|request)|exfiltrat|upload",
     "Instructions to make network requests"),
    ("AG4", "warning", r"full\s+(system\s+)?access|unrestricted|any\s+file",
     "Overly broad permission claims"),
    ("AG5", "warning", r"elevated\s+perm|admin\s+access|root\s+access|sudo",
     "Elevated permission claims"),
])

SCRIPT_RULES = _compile([
    ("BS1", "critical", r"\b(curl|wget)\b",
     "Network calls in bundled script"),
    ("BS2", "critical", r"\.(bashrc|zshrc|profile)|crontab|systemctl|npm\s+-g",
     "System modification patterns"),
    ("BS3", "critical", r"(ANTHROPIC|OPENAI|GITHUB)_?(API_?)?KEY|\.(env|ssh/|credentials)",
     "Accessing sensitive files or secrets"),
    ("BS4", "warning", r"\beval\b.*\$|exec\b.*\$",
     "Unsanitized input passed to eval/exec"),
    ("BS5", "warning", r"curl.*\|\s*(ba)?sh|wget.*\|\s*(ba)?sh",
     "Download and execute remote code"),
    ("BS6", "info", None, "Missing set -euo pipefail"),
])

# ---------------------------------------------------------------------------
# File classification
# ---------------------------------------------------------------------------

ALLOWED_HOOK_ENV_VARS = frozenset({
    "CLAUDE_PLUGIN_ROOT", "CURSOR_PLUGIN_ROOT",
    "SCRIPT_DIR", "PLUGIN_ROOT", "HOOK_NAME", "HOOK_PATH",
    "GIT_EXE", "GIT_DIR", "BASH_EXE",
})


def classify_file(rel_path):
    parts = rel_path.parts
    name = rel_path.name.lower()
    if name.endswith(".js") and ".opencode" in parts:
        return "opencode_plugin"
    if "hooks" in parts and name not in ("hooks.json", "hooks-cursor.json"):
        return "hook_script"
    if "agents" in parts and name.endswith(".md"):
        return "agent_prompt"
    if "scripts" in parts and any(name.endswith(e) for e in (".sh", ".py", ".js")):
        return "bundled_script"
    if name == "skill.md":
        return "skill_content"
    if "references" in parts and name.endswith(".md"):
        return None
    return None

# ---------------------------------------------------------------------------
# Scanning engine
# ---------------------------------------------------------------------------

def scan_file(path, rel_path, file_type):
    rule_map = {
        "skill_content": SKILL_CONTENT_RULES,
        "hook_script": HOOK_RULES,
        "opencode_plugin": OPENCODE_RULES,
        "agent_prompt": AGENT_RULES,
        "bundled_script": SCRIPT_RULES,
    }
    rules = rule_map[file_type]

    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return []

    lines = content.splitlines()
    findings = []
    has_pipefail = "set -euo pipefail" in content

    for line_num, line in enumerate(lines, 1):
        # SC13: Unicode control characters
        if file_type == "skill_content":
            for ch in line:
                cp = ord(ch)
                if cp in (0x200B, 0x200C, 0x200D, 0xFEFF,
                          0x202A, 0x202B, 0x202C, 0x202D, 0x202E):
                    findings.append(dict(
                        check_id="SC13", risk="critical", line=line_num,
                        description=f"Unicode control character U+{cp:04X}"))

        # SC15: long lines
        if file_type == "skill_content" and len(line) > 500:
            findings.append(dict(
                check_id="SC15", risk="info", line=line_num,
                description=f"Line length {len(line)} chars"))
            continue

        # HK6: env var allowlist (custom)
        if file_type == "hook_script":
            for m in re.finditer(r"\$\{?([A-Z_]{5,})\}?", line):
                var = m.group(1)
                if var not in ALLOWED_HOOK_ENV_VARS:
                    findings.append(dict(
                        check_id="HK6", risk="warning", line=line_num,
                        description=f"Env var access: ${var}"))

        for check_id, risk, pattern, desc in rules:
            if pattern is None or check_id == "HK6":
                continue
            if pattern.search(line):
                findings.append(dict(
                    check_id=check_id, risk=risk, line=line_num,
                    description=desc))

    # HK7 / BS6: missing error handling
    if file_type in ("hook_script", "bundled_script") and not has_pipefail:
        is_bash = any(l.startswith("#!") and "bash" in l for l in lines[:3])
        if is_bash:
            cid = "HK7" if file_type == "hook_script" else "BS6"
            findings.append(dict(
                check_id=cid, risk="info", line=1,
                description="Missing set -euo pipefail"))

    return findings


def collect_scannable_files(project_root):
    """Collect all scannable files from known directories.

    Note: this includes scripts/, so sibling scripts are audited. The scanner
    itself is excluded by absolute-path comparison in run_scan() — but only
    when scanning the project it lives in. Other projects with a file at the
    same relative path are scanned normally.
    """
    scan_dirs = ["skills", "hooks", "agents", "scripts", ".opencode"]
    files = []
    for d in scan_dirs:
        target = project_root / d
        if target.is_dir():
            for f in target.rglob("*"):
                if f.is_file() and not f.name.startswith("."):
                    files.append(f)
    return sorted(files)


def run_scan(project_root):
    project_root = Path(project_root).resolve()
    self_path = Path(__file__).resolve()
    all_files = collect_scannable_files(project_root)
    results = {"files": [], "summary": {"critical": 0, "warning": 0, "info": 0}}

    for f in all_files:
        if f.resolve() == self_path:
            continue
        rel = f.relative_to(project_root)
        file_type = classify_file(rel)
        if file_type is None:
            continue

        findings = scan_file(f, rel, file_type)
        file_result = {
            "file": str(rel).replace("\\", "/"),
            "type": file_type,
            "findings": findings,
            "counts": {"critical": 0, "warning": 0, "info": 0},
        }
        for finding in findings:
            file_result["counts"][finding["risk"]] += 1
            results["summary"][finding["risk"]] += 1
        results["files"].append(file_result)

    return results

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def format_markdown(results, project_name):
    s = results["summary"]
    out = [
        f"## Security Scan: {project_name}\n",
        f"**Files scanned:** {len(results['files'])}",
        f"**Risk summary:** {s['critical']} critical, {s['warning']} warnings, {s['info']} info\n",
    ]
    for level, heading in [
        ("critical", "### Critical Risks"),
        ("warning", "### Warnings"),
        ("info", "### Info"),
    ]:
        items = []
        for fr in results["files"]:
            for f in fr["findings"]:
                if f["risk"] == level:
                    items.append(
                        f"- [{f['check_id']}] {fr['file']}:{f['line']} — {f['description']}")
        if items:
            out.append(heading)
            out.extend(items)
            out.append("")

    out.append("### Files Scanned\n")
    out.append("| File | Type | Critical | Warning | Info |")
    out.append("|------|------|----------|---------|------|")
    for fr in results["files"]:
        c = fr["counts"]
        out.append(f"| {fr['file']} | {fr['type']} | {c['critical']} | {c['warning']} | {c['info']} |")
    return "\n".join(out)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    from _cli import make_parser, resolve_root, exit_by_severity
    args = make_parser("Scan bundle-plugins for security risks.").parse_args()
    root = resolve_root(args.project_root)

    results = run_scan(root)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_markdown(results, root.name))

    exit_by_severity(results["summary"])


if __name__ == "__main__":
    main()
