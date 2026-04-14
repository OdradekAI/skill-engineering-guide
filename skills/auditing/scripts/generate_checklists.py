"""Generate checklist markdown tables from the canonical audit-checks.json registry.

The registry lives at skills/auditing/references/audit-checks.json.

Usage:
    python generate_checklists.py [project-root]        # regenerate tables
    python generate_checklists.py --check [project-root] # drift detection (exit 1 if stale)
"""

import json
import re
import sys
from collections import OrderedDict
from pathlib import Path

try:
    from _cli import resolve_root
except ImportError:
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    from _cli import resolve_root

BEGIN_RE = re.compile(r"^<!--\s*BEGIN:(.+?)\s*-->")
END_RE = re.compile(r"^<!--\s*END:(.+?)\s*-->")

THREAT_LABELS = OrderedDict([
    ("network_exfiltration", "Network exfiltration"),
    ("sensitive_data_access", "Sensitive data access"),
    ("safety_overrides", "Safety overrides"),
    ("system_modification", "System modification"),
    ("encoding_obfuscation", "Encoding/obfuscation"),
])

SURFACE_LABELS = OrderedDict([
    ("security/skill_content", "SKILL.md"),
    ("security/hook_scripts", "Hooks"),
    ("security/opencode_plugins", "OpenCode"),
    ("security/agent_prompts", "Agents"),
    ("security/bundled_scripts", "Scripts"),
    ("security/mcp_config", "MCP"),
    ("security/plugin_config", "Config"),
])

SECTION_HEADERS = {
    "security/skill_content": ("Check", "Risk", "Pattern", "Automation"),
    "security/hook_scripts": ("Check", "Risk", "Pattern", "Automation"),
    "security/opencode_plugins": ("Check", "Risk", "Pattern", "Automation"),
    "security/agent_prompts": ("Check", "Risk", "Pattern", "Automation"),
    "security/bundled_scripts": ("Check", "Risk", "Pattern", "Automation"),
    "security/mcp_config": ("Check", "Risk", "Pattern", "Automation"),
    "security/plugin_config": ("Check", "Risk", "Pattern", "Automation"),
    "skill/security": ("Check", "Risk", "Criteria", "Automation"),
}
DEFAULT_HEADER = ("Check", "Severity", "Criteria", "Automation")

CHECKLIST_FILES = {
    "skills/auditing/references/plugin-checklist.md": {
        "structure": {"scope": "plugin", "category": "structure"},
        "platform_manifests": {"scope": "plugin", "category": "platform_manifests"},
        "version_sync": {"scope": "plugin", "category": "version_sync"},
        "skill_quality": {"scope": "plugin", "category": "skill_quality"},
        "cross_references": {"scope": "plugin", "category": "cross_references"},
        "hooks": {"scope": "plugin", "category": "hooks"},
        "testing": {"scope": "plugin", "category": "testing"},
        "documentation": {"scope": "plugin", "category": "documentation"},
    },
    "skills/auditing/references/skill-checklist.md": {
        "skill/structure": {"scope": "skill", "category": "structure"},
        "skill/quality": {"scope": "skill", "category": "skill_quality"},
        "skill/cross_references": {"scope": "skill", "category": "cross_references"},
        "skill/security": {"scope": "skill", "category": ["security/skill_content",
                            "security/agent_prompts"]},
    },
    "skills/auditing/references/workflow-checklist.md": {
        "workflow/static": {"scope": "workflow", "category": "workflow/static"},
        "workflow/semantic": {"scope": "workflow", "category": "workflow/semantic"},
        "workflow/behavioral": {"scope": "workflow", "category": "workflow/behavioral"},
    },
    "skills/auditing/references/security-checklist.md": {
        "security/threat_mapping": {"scope": "security", "special": "threat_mapping"},
        "security/skill_content": {"scope": "security", "category": "security/skill_content", "grouped": True},
        "security/hook_scripts": {"scope": "security", "category": "security/hook_scripts", "grouped": True},
        "security/opencode_plugins": {"scope": "security", "category": "security/opencode_plugins", "grouped": True},
        "security/agent_prompts": {"scope": "security", "category": "security/agent_prompts"},
        "security/bundled_scripts": {"scope": "security", "category": "security/bundled_scripts"},
        "security/mcp_config": {"scope": "security", "category": "security/mcp_config"},
        "security/plugin_config": {"scope": "security", "category": "security/plugin_config", "grouped": True},
    },
}


def load_registry(root):
    path = root / "skills" / "auditing" / "references" / "audit-checks.json"
    if not path.exists():
        print(f"error: {path} not found", file=sys.stderr)
        sys.exit(2)
    data = json.loads(path.read_text(encoding="utf-8"))
    ids = [c["id"] for c in data]
    dupes = [x for x in set(ids) if ids.count(x) > 1]
    if dupes:
        print(f"error: duplicate IDs in registry: {', '.join(sorted(dupes))}",
              file=sys.stderr)
        sys.exit(2)
    return data


def filter_checks(registry, scope, categories):
    if isinstance(categories, str):
        categories = [categories]
    return [c for c in registry
            if scope in c.get("scopes", [])
            and c["category"] in categories]


def _make_sep(header):
    return "|" + "|".join("-" * (len(h) + 2) for h in header) + "|"


def _format_severity(sev):
    if "/" in sev:
        return sev.title().replace("/", "/")
    return sev.capitalize()


def render_table(checks, section_name):
    header = SECTION_HEADERS.get(section_name, DEFAULT_HEADER)
    lines = [
        "| " + " | ".join(header) + " |",
        _make_sep(header),
    ]
    for c in checks:
        lines.append(f"| {c['id']} | {_format_severity(c['severity'])} "
                     f"| {c['criteria']} | {c['automation']} |")
    return "\n".join(lines)


def render_grouped_table(checks, section_name):
    header = SECTION_HEADERS.get(section_name, DEFAULT_HEADER)
    sep = _make_sep(header)
    header_line = "| " + " | ".join(header) + " |"
    groups = OrderedDict()
    for c in checks:
        g = c.get("group", "")
        groups.setdefault(g, []).append(c)

    parts = []
    for group_name, group_checks in groups.items():
        if group_name:
            parts.append(f"\n### {group_name}\n")
        table_lines = [header_line, sep]
        for c in group_checks:
            table_lines.append(
                f"| {c['id']} | {_format_severity(c['severity'])} "
                f"| {c['criteria']} | {c['automation']} |")
        parts.append("\n".join(table_lines))
    return "\n".join(parts)


def render_threat_mapping(registry):
    threat_map = {}
    for c in registry:
        tc = c.get("threat_class")
        if not tc:
            continue
        cat = c["category"]
        threat_map.setdefault(tc, {}).setdefault(cat, []).append(c["id"])

    header = "| Threat | " + " | ".join(SURFACE_LABELS.values()) + " |"
    sep = "|--------|" + "|".join(["-------"] * len(SURFACE_LABELS)) + "|"
    rows = [header, sep]
    for tc_key, tc_label in THREAT_LABELS.items():
        surfaces = threat_map.get(tc_key, {})
        cells = []
        for cat_key in SURFACE_LABELS:
            ids = surfaces.get(cat_key, [])
            cells.append(_compact_ids(ids) if ids else "\u2014")
        rows.append(f"| {tc_label} | " + " | ".join(cells) + " |")
    return "\n".join(rows)


def _compact_ids(ids):
    if not ids:
        return ""
    if len(ids) == 1:
        return ids[0]
    prefix = ids[0].rstrip("0123456789")
    nums = []
    for i in ids:
        p = i.rstrip("0123456789")
        n = i[len(p):]
        if p == prefix and n.isdigit():
            nums.append(int(n))
        else:
            return ", ".join(ids)
    nums.sort()
    ranges = []
    start = nums[0]
    end = nums[0]
    for n in nums[1:]:
        if n == end + 1:
            end = n
        else:
            ranges.append(f"{prefix}{start}" if start == end
                          else f"{prefix}{start}-{prefix}{end}")
            start = end = n
    ranges.append(f"{prefix}{start}" if start == end
                  else f"{prefix}{start}-{prefix}{end}")
    return ", ".join(ranges)


def generate_section(registry, section_name, section_cfg):
    scope = section_cfg["scope"]

    if section_cfg.get("special") == "threat_mapping":
        return render_threat_mapping(registry)

    categories = section_cfg["category"]
    checks = filter_checks(registry, scope, categories)
    if not checks:
        return "<!-- no checks for this section -->"

    use_groups = (section_cfg.get("grouped", False)
                  and any(c.get("group") for c in checks))
    if use_groups:
        return render_grouped_table(checks, section_name)
    return render_table(checks, section_name)


def process_file(filepath, sections, registry, check_mode=False):
    text = filepath.read_text(encoding="utf-8")
    lines = text.split("\n")
    result = []
    in_section = None
    changed = False

    for line in lines:
        begin_m = BEGIN_RE.match(line)
        end_m = END_RE.match(line)

        if begin_m and not in_section:
            section_name = begin_m.group(1)
            if section_name in sections:
                in_section = section_name
                result.append(line)
                new_content = generate_section(registry, section_name,
                                               sections[section_name])
                result.append(new_content)
                continue
        if end_m and in_section and end_m.group(1) == in_section:
            in_section = None
            result.append(line)
            continue
        if in_section:
            continue
        result.append(line)

    new_text = "\n".join(result)
    if new_text != text:
        changed = True
        if not check_mode:
            filepath.write_text(new_text, encoding="utf-8")
    return changed


def main():
    import argparse
    parser = argparse.ArgumentParser(
        description="Generate checklist tables from audit-checks.json registry")
    parser.add_argument("project_root", nargs="?", default=".",
                        help="Bundle-plugin root (default: current directory)")
    parser.add_argument("--check", action="store_true",
                        help="Check for drift without writing (exit 1 if stale)")
    args = parser.parse_args()

    root = resolve_root(args.project_root)
    registry = load_registry(root)

    stale_files = []
    for rel_path, sections in CHECKLIST_FILES.items():
        filepath = root / rel_path
        if not filepath.exists():
            print(f"warning: {rel_path} not found, skipping", file=sys.stderr)
            continue
        changed = process_file(filepath, sections, registry,
                               check_mode=args.check)
        if changed:
            stale_files.append(rel_path)

    if args.check:
        if stale_files:
            print("Checklist drift detected — tables are out of sync with "
                  "skills/auditing/references/audit-checks.json:")
            for f in stale_files:
                print(f"  {f}")
            print("\nRun: python generate_checklists.py")
            sys.exit(1)
        else:
            print("All checklists are in sync with audit-checks.json registry.")
            sys.exit(0)
    else:
        if stale_files:
            print(f"Updated {len(stale_files)} file(s):")
            for f in stale_files:
                print(f"  {f}")
        else:
            print("All checklists already in sync.")


if __name__ == "__main__":
    main()
