#!/usr/bin/env python3
"""
Pattern-based security smell detector for bundle-plugins.

Scans 7 file categories — SKILL.md files, hook scripts, hook configs
(HTTP hooks), OpenCode plugins, agent prompts, bundled scripts, and
MCP configs — for known dangerous patterns (network calls, eval,
sensitive file references, etc.) that could indicate data exfiltration,
resource destruction, backdoors, or safety control overrides.

This is a static pattern matcher, not a comprehensive security auditor.
It detects explicitly written dangerous patterns but cannot catch
obfuscated code, indirect calls, or logic-level vulnerabilities.

Each rule has a confidence level:
  - deterministic: unambiguous in executable code; affects score and exit code.
  - suspicious: context-sensitive (e.g. docs referencing .env); shown in
    report as "needs review", affects exit code (at least exit 1).
    JSON output includes a "confidence" field for CI to make fine-grained
    decisions on whether to block on suspicious findings.

Usage:
    python audit_security.py [target-dir]
    python audit_security.py --json [target-dir]

Exit codes: 0 = clean, 1 = warnings only, 2 = critical findings
           (both deterministic and suspicious findings affect exit codes)
"""

import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Rule definitions — (check_id, risk, regex_pattern, description, confidence)
#
# confidence: "deterministic" = unambiguous in executable code, counts toward
#             score and exit code.  "suspicious" = context-sensitive, needs
#             model review; counts toward score/exit (at least warning level).
# Rules with pattern=None use custom logic in scan_file().
# ---------------------------------------------------------------------------

_DET = "deterministic"
_SUS = "suspicious"


def _compile(pairs):
    return [(cid, risk, re.compile(pat, re.IGNORECASE) if pat else None, desc, conf)
            for cid, risk, pat, desc, conf in pairs]

SKILL_CONTENT_RULES = _compile([
    ("SC1", "critical", r"\.(env|ssh/|credentials|secrets|tokens|api_key)\b",
     "References to sensitive files/directories", _SUS),
    ("SC2", "critical", r"send.*(external|remote|server)|exfiltrat|upload.*secret",
     "Instructions to send data externally", _SUS),
    ("SC3", "warning", r"~/\.(config|aws|kube|gcloud)/|%(APPDATA|LOCALAPPDATA|USERPROFILE)%",
     "References to user config directories", _SUS),
    ("SC4", "warning", r"process\.env|(\$ENV\b)|\$[A-Z_]*API[_]?KEY",
     "Environment variable access beyond documented needs", _SUS),
    ("SC5", "critical", r"rm\s+-rf\s+[/~]|rmdir\s+/s|del\s+/[fq]",
     "Destructive file deletion on broad paths", _DET),
    ("SC6", "critical", r"git\s+push\s+--force|git\s+reset\s+--hard",
     "Force push or hard reset", _DET),
    ("SC7", "critical", r"DROP\s+TABLE|DELETE\s+FROM(?!.*WHERE)",
     "Destructive database operations", _DET),
    ("SC8", "warning", r"overwrite.*outside|modify.*outside.*project",
     "Modifying files outside the project directory", _DET),
    ("SC9", "critical", r"ignore\s+(previous\s+)?instructions|override\s+safety|disable\s+verification",
     "Safety override instructions", _DET),
    ("SC10", "critical", r"--no-verify|bypass\s+lint|disable\s+test|skip\s+hook",
     "Instructions to skip safety checks", _DET),
    ("SC11", "warning", r"highest\s+priority|override\s+(all|user)|supersede",
     "Claims priority over user instructions", _SUS),
    ("SC12", "warning", r"<EXTREMELY.?IMPORTANT>|EXTREMELY.?IMPORTANT",
     "Emphasis tags (EXTREMELY_IMPORTANT) outside bootstrap skill", _SUS),
    ("SC15", "info", None, "Excessively long line (>500 chars)", _SUS),
])

SKILL_REFERENCE_RULES = [
    (cid, "warning" if cid in ("SC1", "SC2") else risk, pat, desc, conf)
    for cid, risk, pat, desc, conf in SKILL_CONTENT_RULES
]

HOOK_RULES = _compile([
    ("HK1", "critical", r"\b(curl|wget|nc|ncat|telnet)\b",
     "Network command in hook script", _DET),
    ("HK2", "critical", r"https?://(?!localhost|127\.0\.0\.1)",
     "External URL", _DET),
    ("HK3", "critical", r"\$[A-Z_]+.*\|\s*(curl|wget|nc)|cat.*\|\s*(curl|wget|nc)",
     "Piping data to network commands", _DET),
    ("HK4", "warning", r"\b(dig|nslookup|host)\s",
     "DNS lookup that could encode data", _DET),
    ("HK5", "critical", r"(ANTHROPIC|OPENAI|GITHUB|AZURE|GCP|AWS)_?(API_?)?KEY|GITHUB_TOKEN",
     "Reading API keys or secrets", _DET),
    ("HK6", "warning", None,
     "Env var access beyond allowed set (custom check)", _DET),
    ("HK7", "info", None, "Missing set -euo pipefail", _DET),
    ("HK8", "critical", r"\.(bashrc|zshrc|profile|bash_profile)\b|PowerShell_profile\.ps1|\$PROFILE\b",
     "Writing to shell config files", _DET),
    ("HK9", "critical", r"\b(crontab|systemctl|launchctl|schtasks)\b|\breg\s+add\b|Set-ExecutionPolicy",
     "Creating persistent services or modifying system config", _DET),
    ("HK10", "critical", r"npm\s+(-g|install\s+-g)|pip\s+install\s+--user",
     "Installing global packages", _DET),
    ("HK11", "warning", r"(?<![a-zA-Z_-])(>|>>)\s*/(?!dev/null)|mkdir\s+-p\s+/(?!tmp)",
     "Creating files outside project directory", _DET),
    ("HK12", "warning", r"chmod\s+[2467]",
     "chmod with setuid/setgid bits", _DET),
])

OPENCODE_RULES = _compile([
    ("OC1", "critical", r"\beval\s*\(|new\s+Function\s*\(|vm\.runIn",
     "Dynamic code execution", _DET),
    ("OC2", "critical", r"child_process\.(exec|spawn)|execSync",
     "Child process execution", _DET),
    ("OC3", "critical", r"require\s*\(\s*['\"]child_process|import\s*\(\s*['\"]child_process",
     "Importing child_process module", _DET),
    ("OC4", "warning", r"require\s*\([^'\"]+\)|import\s*\([^'\"]+\)",
     "Dynamic require/import with variable paths", _DET),
    ("OC5", "critical", r"\bfetch\s*\(|http\.request|https\.request|net\.connect",
     "Network requests", _DET),
    ("OC6", "critical", r"\bWebSocket\b",
     "WebSocket connections", _DET),
    ("OC7", "warning", r"require\s*\(\s*['\"](?:http|https|net|dgram|dns)['\"]",
     "Network-related module imports", _DET),
    ("OC8", "critical", r"process\.env\.(ANTHROPIC|OPENAI|GITHUB|AZURE|AWS)",
     "Accessing API key environment variables", _DET),
    ("OC9", "warning", r"process\.env\b",
     "Broad process.env access", _DET),
])

MCP_RULES = [
    ("MC1", "critical", re.compile(
        r"""(?:['"](?:Authorization|api[_-]?key|token|secret|password)['"]"""
        r"""\s*:\s*['"][^${']+['"])""",
        re.IGNORECASE),
     "Hardcoded credential in MCP server config", _DET),
    ("MC2", "critical", re.compile(r'"headersHelper"', re.IGNORECASE),
     "headersHelper field executes arbitrary shell commands", _DET),
    ("MC3", "warning", None,
     "Env var value embedded directly instead of using ${VAR} expansion", _DET),
    ("MC4", "warning", re.compile(r'"url"\s*:\s*"http://(?!localhost|127\.0\.0\.1)', re.IGNORECASE),
     "MCP server URL uses plain HTTP instead of HTTPS", _DET),
    ("MC5", "info", re.compile(r'"command"\s*:\s*"/(?!dev/null)', re.IGNORECASE),
     "Absolute path in command field (may not be portable)", _DET),
    ("PC1", "warning", re.compile(r'\.\./'),
     "Path traversal (../) in config — breaks after marketplace install", _DET),
    ("PC2", "warning", re.compile(r'["\'][A-Z]:\\|["\']/(?:usr|home|etc|opt|var)/'),
     "Absolute path in plugin config — use relative paths or ${CLAUDE_PLUGIN_ROOT}", _DET),
]

AGENT_RULES = _compile([
    ("AG1", "critical", r"ignore.*(safety|guideline|instruction)|override.*(safety|rule)|bypass.*(safety|security)",
     "Safety override instructions in agent prompt", _SUS),
    ("AG2", "critical", r"(access|read|use).*(credential|secret|api.?key|token)",
     "Instructions to access credentials", _SUS),
    ("AG3", "critical", r"(make|send|perform).*(network|http|request)|exfiltrat|upload",
     "Instructions to make network requests", _SUS),
    ("AG4", "warning", r"full\s+(system\s+)?access|unrestricted|any\s+file",
     "Overly broad permission claims", _SUS),
    ("AG5", "warning", r"elevated\s+perm|admin\s+access|root\s+access|sudo",
     "Elevated permission claims", _SUS),
])

_NEGATIVE_CONTEXT_RE = re.compile(
    r"\b(never|do\s+not|don't|must\s+not|cannot|prohibited|disallow|forbid)",
    re.IGNORECASE,
)

_USER_PRIORITY_CONTEXT_RE = re.compile(
    r"\buser['s]*\s+(explicit\s+)?instructions\b",
    re.IGNORECASE,
)

_NETWORK_IMPORT_RE = re.compile(
    r"\b(?:import\s+(?:socket|urllib|requests|httpx|dns|http\.client)"
    r"|from\s+(?:socket|urllib|requests|httpx|dns|http\.client)\s+import)",
    re.IGNORECASE,
)

_INLINE_BACKTICK_EXTREMELY_RE = re.compile(
    r"`[^`]*EXTREMELY.?IMPORTANT[^`]*`"
)

SCRIPT_RULES = _compile([
    ("BS1", "critical", r"\b(curl|wget)\b",
     "Network calls in bundled script", _DET),
    ("BS2", "critical", r"\.(bashrc|zshrc|profile)|PowerShell_profile\.ps1|crontab|systemctl|schtasks|\breg\s+add|npm\s+-g",
     "System modification patterns", _DET),
    ("BS3", "critical", r"(ANTHROPIC|OPENAI|GITHUB)_?(API_?)?KEY|\.(env|ssh/|credentials)",
     "Accessing sensitive files or secrets", _DET),
    ("BS4", "warning", r"\beval\b.*\$|exec\b.*\$",
     "Unsanitized input passed to eval/exec", _DET),
    ("BS5", "warning", r"curl.*\|\s*(ba)?sh|wget.*\|\s*(ba)?sh",
     "Download and execute remote code", _DET),
    ("BS6", "info", None, "Missing set -euo pipefail", _DET),
])

# ---------------------------------------------------------------------------
# File classification
# ---------------------------------------------------------------------------

ALLOWED_HOOK_ENV_VARS = frozenset({
    "CLAUDE_PLUGIN_ROOT", "CURSOR_PLUGIN_ROOT",
    "CLAUDE_PLUGIN_DATA", "CLAUDE_ENV_FILE",
    "SCRIPT_DIR", "PLUGIN_ROOT", "HOOK_NAME", "HOOK_PATH",
    "GIT_EXE", "GIT_DIR", "BASH_EXE",
})


def classify_file(rel_path):
    parts = rel_path.parts
    name = rel_path.name.lower()
    if name == ".mcp.json" and len(parts) == 1:
        return "mcp_config"
    if name == "plugin.json" and len(parts) == 2:
        return "mcp_config"
    if name.endswith(".js") and ".opencode" in parts:
        return "opencode_plugin"
    if "hooks" in parts and name in ("hooks.json", "hooks-cursor.json"):
        return "hook_config"
    if "hooks" in parts and name not in ("hooks.json", "hooks-cursor.json"):
        return "hook_script"
    if "agents" in parts and name.endswith(".md"):
        return "agent_prompt"
    if "scripts" in parts and any(name.endswith(e) for e in (".sh", ".py", ".js")):
        return "bundled_script"
    if name == "skill.md":
        return "skill_content"
    if "skills" in parts and "references" in parts and name.endswith(".md"):
        if "auditing" in parts:
            return None
        return "skill_reference"
    return None

# ---------------------------------------------------------------------------
# Scanning engine
# ---------------------------------------------------------------------------

def _scan_mcp_config(path, rel_path):
    """Scan .mcp.json or plugin.json for MCP security issues."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return []

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return []

    servers = data.get("mcpServers", {})
    if not isinstance(servers, dict) or not servers:
        return []

    findings = []
    lines = content.splitlines()

    for check_id, risk, pattern, desc, confidence in MCP_RULES:
        if pattern is None:
            continue
        for line_num, line in enumerate(lines, 1):
            if pattern.search(line):
                findings.append(dict(
                    check_id=check_id, risk=risk, line=line_num,
                    description=desc, confidence=confidence))

    for srv_name, srv_cfg in servers.items():
        if not isinstance(srv_cfg, dict):
            continue
        env = srv_cfg.get("env", {})
        if isinstance(env, dict):
            for key, val in env.items():
                if isinstance(val, str) and val and not val.startswith("${"):
                    if any(kw in key.upper() for kw in
                           ("KEY", "SECRET", "TOKEN", "PASSWORD", "CREDENTIAL")):
                        findings.append(dict(
                            check_id="MC3", risk="warning", line=0,
                            description=f"Env var '{key}' in server '{srv_name}' "
                                        f"may contain a secret — use ${{VAR}} expansion",
                            confidence=_DET))

    return findings


def _scan_hook_config(path, rel_path):
    """Scan hooks.json / hooks-cursor.json for HTTP hooks (data exfiltration risk)."""
    try:
        content = path.read_text(encoding="utf-8", errors="replace")
    except (OSError, PermissionError):
        return []

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        return []

    findings = []
    lines = content.splitlines()

    http_re = re.compile(r'"type"\s*:\s*"http"', re.IGNORECASE)
    for line_num, line in enumerate(lines, 1):
        if http_re.search(line):
            findings.append(dict(
                check_id="HK13", risk="critical", line=line_num,
                description="HTTP hook detected — may exfiltrate tool input/output to external URL",
                confidence=_DET))

    url_re = re.compile(r'"url"\s*:\s*"https?://(?!localhost|127\.0\.0\.1)', re.IGNORECASE)
    for line_num, line in enumerate(lines, 1):
        if url_re.search(line):
            findings.append(dict(
                check_id="HK14", risk="critical", line=line_num,
                description="External URL in hook config — verify destination is trusted",
                confidence=_DET))

    return findings


def scan_file(path, rel_path, file_type):
    if file_type == "mcp_config":
        return _scan_mcp_config(path, rel_path)
    if file_type == "hook_config":
        return _scan_hook_config(path, rel_path)

    rule_map = {
        "skill_content": SKILL_CONTENT_RULES,
        "skill_reference": SKILL_REFERENCE_RULES,
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
    has_network_imports = bool(_NETWORK_IMPORT_RE.search(content))
    in_code_fence = False

    for line_num, line in enumerate(lines, 1):
        stripped_line = line.strip()
        if stripped_line.startswith("```"):
            in_code_fence = not in_code_fence

        # SC13: Unicode control characters
        if file_type in ("skill_content", "skill_reference"):
            for ch in line:
                cp = ord(ch)
                if cp in (0x200B, 0x200C, 0x200D, 0xFEFF,
                          0x202A, 0x202B, 0x202C, 0x202D, 0x202E):
                    findings.append(dict(
                        check_id="SC13", risk="critical", line=line_num,
                        description=f"Unicode control character U+{cp:04X}",
                        confidence=_DET))

        # SC15: long lines
        if file_type in ("skill_content", "skill_reference") and len(line) > 500:
            findings.append(dict(
                check_id="SC15", risk="info", line=line_num,
                description=f"Line length {len(line)} chars",
                confidence=_SUS))
            continue

        # HK6: env var allowlist (custom)
        if file_type == "hook_script":
            for m in re.finditer(r"\$\{?([A-Z_]{5,})\}?", line):
                var = m.group(1)
                if var not in ALLOWED_HOOK_ENV_VARS:
                    findings.append(dict(
                        check_id="HK6", risk="warning", line=line_num,
                        description=f"Env var access: ${var}",
                        confidence=_DET))

        # HK15: CLAUDE_ENV_FILE write detection
        if file_type == "hook_script":
            if re.search(r">>?\s*[\"']?\$\{?CLAUDE_ENV_FILE\}?", line):
                findings.append(dict(
                    check_id="HK15", risk="warning", line=line_num,
                    description="Writing to CLAUDE_ENV_FILE — injects env vars into all subsequent Bash commands",
                    confidence=_DET))

        for check_id, risk, pattern, desc, confidence in rules:
            if pattern is None or check_id == "HK6":
                continue
            if pattern.search(line):
                if check_id == "AG4" and _NEGATIVE_CONTEXT_RE.search(line):
                    continue
                if check_id == "SC11" and _USER_PRIORITY_CONTEXT_RE.search(line):
                    continue
                if check_id == "SC11" and re.search(r"superseded[_-]by\s*:", line):
                    continue
                if check_id == "HK4" and not has_network_imports:
                    continue
                if check_id == "SC12" and "using-" in str(rel_path):
                    continue
                if check_id == "SC12" and in_code_fence:
                    continue
                if check_id == "SC12" and "`" in line and _INLINE_BACKTICK_EXTREMELY_RE.search(line):
                    continue
                findings.append(dict(
                    check_id=check_id, risk=risk, line=line_num,
                    description=desc, confidence=confidence))

    # HK7 / BS6: missing error handling
    if file_type in ("hook_script", "bundled_script") and not has_pipefail:
        is_bash = any(l.startswith("#!") and "bash" in l for l in lines[:3])
        if is_bash:
            cid = "HK7" if file_type == "hook_script" else "BS6"
            findings.append(dict(
                check_id=cid, risk="info", line=1,
                description="Missing set -euo pipefail",
                confidence=_DET))

    return findings


def collect_scannable_files(target_dir):
    """Collect all scannable files from known directories.

    Note: this includes scripts/, so sibling scripts are audited. The scanner
    itself is excluded by absolute-path comparison in run_scan() — but only
    when scanning the project it lives in. Other projects with a file at the
    same relative path are scanned normally.
    """
    scan_dirs = ["skills", "hooks", "agents", "scripts", ".opencode"]
    files = []
    for d in scan_dirs:
        target = target_dir / d
        if target.is_dir():
            for f in target.rglob("*"):
                if f.is_file() and not f.name.startswith("."):
                    if "node_modules" in f.parts:
                        continue
                    files.append(f)

    mcp_json = target_dir / ".mcp.json"
    if mcp_json.is_file():
        files.append(mcp_json)

    for manifest_dir in (".claude-plugin", ".cursor-plugin"):
        pj = target_dir / manifest_dir / "plugin.json"
        if pj.is_file():
            files.append(pj)

    return sorted(files)


def run_scan(target_dir):
    target_dir = Path(target_dir).resolve()
    self_path = Path(__file__).resolve()
    all_files = collect_scannable_files(target_dir)
    results = {"files": [], "summary": {
        "critical": 0, "warning": 0, "info": 0,
        "suspicious_critical": 0, "suspicious_warning": 0,
    }}

    for f in all_files:
        if f.resolve() == self_path:
            continue
        rel = f.relative_to(target_dir)
        file_type = classify_file(rel)
        if file_type is None:
            continue

        findings = scan_file(f, rel, file_type)
        file_result = {
            "file": rel.as_posix(),
            "type": file_type,
            "findings": findings,
            "counts": {"critical": 0, "warning": 0, "info": 0},
        }
        for finding in findings:
            is_suspicious = finding.get("confidence") == "suspicious"
            risk = finding["risk"]
            file_result["counts"][risk] += 1
            results["summary"][risk] += 1
            if is_suspicious and risk in ("critical", "warning"):
                results["summary"][f"suspicious_{risk}"] += 1
        results["files"].append(file_result)

    return results

# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def format_markdown(results, project_name):
    s = results["summary"]
    sus_c = s.get("suspicious_critical", 0)
    sus_w = s.get("suspicious_warning", 0)
    out = [
        f"## Security Scan: {project_name}\n",
        f"**Files scanned:** {len(results['files'])}",
        f"**Risk summary:** {s['critical']} critical, {s['warning']} warnings, {s['info']} info",
    ]
    if sus_c or sus_w:
        out.append(f"**Suspicious (needs review):** {sus_c} critical, {sus_w} warnings")
    out.append("")

    for level, heading in [
        ("critical", "### Critical Risks"),
        ("warning", "### Warnings"),
        ("info", "### Info"),
    ]:
        items = []
        for fr in results["files"]:
            for f in fr["findings"]:
                if f["risk"] == level and f.get("confidence") != "suspicious":
                    items.append(
                        f"- [{f['check_id']}] {fr['file']}:{f['line']} — {f['description']}")
        if items:
            out.append(heading)
            out.extend(items)
            out.append("")

    sus_items = []
    for fr in results["files"]:
        for f in fr["findings"]:
            if f.get("confidence") == "suspicious" and f["risk"] in ("critical", "warning"):
                sus_items.append(
                    f"- [{f['check_id']}] {fr['file']}:{f['line']} — "
                    f"{f['description']} ({f['risk']})")
    if sus_items:
        out.append("### Suspicious (needs review)\n")
        out.extend(sus_items)
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
    from _cli import make_parser, resolve_target, exit_by_severity
    args = make_parser("Scan bundle-plugins for security risks.").parse_args()
    root = resolve_target(args.target_dir)

    results = run_scan(root)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_markdown(results, root.name))

    exit_by_severity(results["summary"])


if __name__ == "__main__":
    main()
