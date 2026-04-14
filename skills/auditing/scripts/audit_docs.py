#!/usr/bin/env python3
"""
Documentation consistency checker for bundle-plugins.

Validates that project documentation (CLAUDE.md, AGENTS.md, README.md,
README translations, docs/) stays in sync with the actual project state
(skills/, agents/, scripts/, .version-bump.json).

Nine checks:
  D1 — Skill list sync across docs vs skills/ directory
  D2 — Cross-reference validity (bundles-forge:<name> → skills/<name>/)
  D3 — Platform manifest sync (CLAUDE.md table vs .version-bump.json)
  D4 — Command/script accuracy (CLAUDE.md scripts vs actual file paths)
  D5 — Agent list sync (CLAUDE.md agents vs agents/ directory)
  D6 — README data sync (README.md vs README.zh.md hard data)
  D7 — Guide language sync (docs/*.md vs docs/*.zh.md hard data)
  D8 — Canonical source declaration (docs/*.md guides → skill/agent file)
  D9 — Numeric cross-validation (docs/*.md numbers vs canonical source)

Usage:
    python audit_docs.py [project-root]
    python audit_docs.py --json [project-root]

Exit codes: 0 = all pass, 1 = warnings, 2 = critical
"""

import json
import re
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Extraction helpers
# ---------------------------------------------------------------------------

_TABLE_ROW_RE = re.compile(r"^\|(.+)\|\s*$", re.MULTILINE)
_CROSS_REF_BACKTICK_RE = re.compile(r"`([a-z0-9-]+):([a-z0-9-]+)`")
_CROSS_REF_BOLD_RE = re.compile(r"\*\*([a-z0-9-]+):([a-z0-9-]+)\*\*")
_SCRIPT_REF_RE = re.compile(r"(?:python\s+)?(?:skills/[a-z-]+/scripts/([a-z_]+\.py))")
_AGENT_FILE_RE = re.compile(r"`(agents/[a-z0-9_-]+\.md)`")
_AGENT_BACKTICK_NAME_RE = re.compile(r"`([a-z0-9_-]+)`")


def _read_if_exists(path):
    if path.exists():
        return path.read_text(encoding="utf-8", errors="replace")
    return None


def _parse_table_column(content, col_index, *, section_header=None):
    """Extract values from a specific column of a markdown table.

    If section_header is given, only parse tables under that ## heading.
    Skips separator rows (containing only dashes/pipes/spaces).
    """
    lines = content.splitlines()
    in_section = section_header is None
    values = []

    for line in lines:
        stripped = line.strip()
        if section_header and stripped.startswith("#"):
            heading = stripped.lstrip("#").strip()
            in_section = heading == section_header

        if not in_section:
            continue

        m = _TABLE_ROW_RE.match(line.strip())
        if not m:
            continue

        cells = [c.strip() for c in m.group(1).split("|")]
        if col_index >= len(cells):
            continue

        cell = cells[col_index]
        if re.fullmatch(r"[-:\s]+", cell):
            continue

        values.append(cell)

    return values


def _extract_backtick_names(cells):
    """Extract names wrapped in backticks from a list of cell strings."""
    names = set()
    for cell in cells:
        for m in _AGENT_BACKTICK_NAME_RE.finditer(cell):
            names.add(m.group(1))
    return names


# ---------------------------------------------------------------------------
# Check D1 — Skill list sync
# ---------------------------------------------------------------------------

def check_skill_list_sync(root, findings):
    """Verify skill names in docs match skills/ directory."""
    skills_dir = root / "skills"
    actual_skills = {d.name for d in skills_dir.iterdir() if d.is_dir()}

    sources = {}

    # AGENTS.md Available Skills table — skill names in column 0
    agents_md = _read_if_exists(root / "AGENTS.md")
    if agents_md:
        cells = _parse_table_column(agents_md, 0, section_header="Available Skills")
        sources["AGENTS.md"] = _extract_backtick_names(cells)

    # CLAUDE.md — skill names from Skill Lifecycle Flow + Directory Layout
    claude_md = _read_if_exists(root / "CLAUDE.md")
    if claude_md:
        claude_skills = set()
        # Lifecycle flow: `name` → `name`
        lifecycle_re = re.compile(r"`([a-z-]+)`\s*[→↔]\s*`([a-z-]+)`")
        for m in lifecycle_re.finditer(claude_md):
            claude_skills.add(m.group(1))
            claude_skills.add(m.group(2))
        # Also pick up any skill mentioned after "can be invoked"
        invoked_re = re.compile(r"`([a-z-]+)`\s+can be invoked")
        for m in invoked_re.finditer(claude_md):
            claude_skills.add(m.group(1))
        # Pick up skills mentioned in Directory Layout "N skill directories"
        dir_layout_re = re.compile(r"(\d+)\s+skill\s+director", re.IGNORECASE)
        dir_layout_match = dir_layout_re.search(claude_md)
        expected_count = int(dir_layout_match.group(1)) if dir_layout_match else None
        # Pick up backtick-wrapped names that are actual skill directories
        for m in _AGENT_BACKTICK_NAME_RE.finditer(claude_md):
            name = m.group(1)
            if name in actual_skills:
                claude_skills.add(name)
        if claude_skills:
            sources["CLAUDE.md"] = claude_skills
        if expected_count and expected_count != len(actual_skills):
            findings.append(dict(
                check="D1", severity="warning",
                message=f"CLAUDE.md says '{expected_count} skill directories' "
                        f"but skills/ has {len(actual_skills)}"))

    # README.md Skills table — skill names in column 1 (Phase | Skill | ...)
    readme_md = _read_if_exists(root / "README.md")
    if readme_md:
        cells = _parse_table_column(readme_md, 1, section_header="Skills")
        names = _extract_backtick_names(cells)
        # Also capture bootstrap skill mentioned in prose
        if "using-bundles-forge" in readme_md:
            names.add("using-bundles-forge")
        if names:
            sources["README.md"] = names

    # README.zh.md Skills table
    readme_zh = _read_if_exists(root / "README.zh.md")
    if readme_zh:
        # Chinese README uses 阶段 | 技能 | 作用 — skill names in column 1
        cells = _parse_table_column(readme_zh, 1, section_header="技能")
        if not cells:
            cells = _parse_table_column(readme_zh, 1, section_header="Skills")
        names = _extract_backtick_names(cells)
        if "using-bundles-forge" in readme_zh:
            names.add("using-bundles-forge")
        if names:
            sources["README.zh.md"] = names

    for source_name, doc_skills in sources.items():
        missing_in_docs = actual_skills - doc_skills
        extra_in_docs = doc_skills - actual_skills

        for s in sorted(missing_in_docs):
            findings.append(dict(
                check="D1", severity="warning",
                message=f"Skill '{s}' exists in skills/ but missing from {source_name}"))
        for s in sorted(extra_in_docs):
            findings.append(dict(
                check="D1", severity="warning",
                message=f"Skill '{s}' listed in {source_name} but not found in skills/"))


# ---------------------------------------------------------------------------
# Check D2 — Cross-reference validity
# ---------------------------------------------------------------------------

def check_cross_references(root, findings):
    """Verify all bundles-forge:<name> references point to existing skills."""
    skills_dir = root / "skills"
    actual_skills = {d.name for d in skills_dir.iterdir() if d.is_dir()}

    # Detect project name / abbreviation
    project_name = root.name
    project_abbreviation = None
    pkg_path = root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            project_name = pkg.get("name", project_name)
            project_abbreviation = pkg.get("abbreviation")
        except (json.JSONDecodeError, OSError):
            pass

    valid_prefixes = {project_name}
    if project_abbreviation:
        valid_prefixes.add(project_abbreviation)

    # Scan all .md files in project (excluding .git, node_modules, .repos)
    # CHANGELOG.md is excluded — it records historical skill names that may
    # have been renamed; treating these as broken refs is a false positive.
    exclude_dirs = {".git", "node_modules", ".repos", "__pycache__"}
    exclude_files = {"CHANGELOG.md"}
    broken_refs = {}

    for md_file in root.rglob("*.md"):
        if any(part in exclude_dirs for part in md_file.parts):
            continue
        if md_file.name in exclude_files:
            continue

        content = md_file.read_text(encoding="utf-8", errors="replace")
        rel_path = md_file.relative_to(root)

        for pattern in [_CROSS_REF_BACKTICK_RE, _CROSS_REF_BOLD_RE]:
            for m in pattern.finditer(content):
                prefix, skill_name = m.group(1), m.group(2)
                if prefix in valid_prefixes and skill_name not in actual_skills:
                    key = f"{prefix}:{skill_name}"
                    if key not in broken_refs:
                        broken_refs[key] = []
                    broken_refs[key].append(str(rel_path))

    for ref, files in sorted(broken_refs.items()):
        file_list = ", ".join(files[:3])
        suffix = f" (+{len(files) - 3} more)" if len(files) > 3 else ""
        findings.append(dict(
            check="D2", severity="critical",
            message=f"Broken cross-reference '{ref}' in: {file_list}{suffix}"))


# ---------------------------------------------------------------------------
# Check D3 — Platform manifest sync
# ---------------------------------------------------------------------------

def check_platform_manifests(root, findings):
    """Verify CLAUDE.md Platform Manifests table matches .version-bump.json."""
    claude_md = _read_if_exists(root / "CLAUDE.md")
    vbump_path = root / ".version-bump.json"

    if not claude_md or not vbump_path.exists():
        return

    try:
        vbump = json.loads(vbump_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        findings.append(dict(
            check="D3", severity="warning",
            message="Cannot parse .version-bump.json"))
        return

    vbump_paths = {f["path"] for f in vbump.get("files", [])}

    # Parse Platform Manifests table — column 1 is Manifest, column 2 (if
    # present) is "Version-synced".  Only flag entries that are expected to
    # carry a version string.
    manifest_cells = _parse_table_column(claude_md, 1, section_header="Platform Manifests")
    sync_cells = _parse_table_column(claude_md, 2, section_header="Platform Manifests")

    doc_paths = set()
    for idx, cell in enumerate(manifest_cells):
        if idx < len(sync_cells) and re.search(r"\bNo\b", sync_cells[idx], re.IGNORECASE):
            continue
        for m in re.finditer(r"`([^`]+)`", cell):
            doc_paths.add(m.group(1))

    # .version-bump.json may include paths not in the CLAUDE.md table
    # (e.g., marketplace.json). We only warn about paths in docs that
    # don't exist in .version-bump.json, and vice versa for manifest files.
    manifest_vbump = {p for p in vbump_paths if "plugin.json" in p or "extension" in p}
    manifest_docs = {p for p in doc_paths if p}

    for p in sorted(manifest_docs - vbump_paths):
        findings.append(dict(
            check="D3", severity="warning",
            message=f"CLAUDE.md lists manifest '{p}' but it's not in .version-bump.json"))

    for p in sorted(manifest_vbump - manifest_docs):
        findings.append(dict(
            check="D3", severity="info",
            message=f".version-bump.json tracks '{p}' but it's not in CLAUDE.md Platform Manifests table"))


# ---------------------------------------------------------------------------
# Check D4 — Command/script accuracy
# ---------------------------------------------------------------------------

def check_script_references(root, findings):
    """Verify skill scripts referenced in CLAUDE.md exist at their declared paths."""
    claude_md = _read_if_exists(root / "CLAUDE.md")
    if not claude_md:
        return

    for m in _SCRIPT_REF_RE.finditer(claude_md):
        full_match = m.group(0)
        if not (root / full_match.split()[-1]).exists():
            findings.append(dict(
                check="D4", severity="critical",
                message=f"CLAUDE.md references '{full_match}' but file does not exist"))


# ---------------------------------------------------------------------------
# Check D5 — Agent list sync
# ---------------------------------------------------------------------------

def check_agent_sync(root, findings):
    """Verify agent references in CLAUDE.md match agents/ directory."""
    claude_md = _read_if_exists(root / "CLAUDE.md")
    agents_dir = root / "agents"

    if not claude_md or not agents_dir.is_dir():
        return

    actual_agents = {f.stem for f in agents_dir.iterdir()
                     if f.is_file() and f.suffix == ".md"}

    # Extract agent names from Agent Dispatch section
    doc_agents = set()
    in_dispatch = False
    for line in claude_md.splitlines():
        if "Agent Dispatch" in line and line.strip().startswith("#"):
            in_dispatch = True
            continue
        if in_dispatch and line.strip().startswith("## "):
            break
        if in_dispatch:
            # Look for backtick-wrapped agent names in list items
            if line.strip().startswith("- `"):
                m = re.match(r"^-\s+`([a-z0-9_-]+)`", line.strip())
                if m:
                    doc_agents.add(m.group(1))

    if not doc_agents:
        return

    for a in sorted(actual_agents - doc_agents):
        findings.append(dict(
            check="D5", severity="warning",
            message=f"Agent '{a}' exists in agents/ but missing from CLAUDE.md Agent Dispatch"))
    for a in sorted(doc_agents - actual_agents):
        findings.append(dict(
            check="D5", severity="critical",
            message=f"CLAUDE.md references agent '{a}' but agents/{a}.md does not exist"))


# ---------------------------------------------------------------------------
# Check D6 — README data sync
# ---------------------------------------------------------------------------

def check_readme_sync(root, findings):
    """Compare hard data between README.md and README.zh.md."""
    readme_en = _read_if_exists(root / "README.md")
    readme_zh = _read_if_exists(root / "README.zh.md")

    if not readme_en or not readme_zh:
        if readme_en and not readme_zh:
            findings.append(dict(
                check="D6", severity="warning",
                message="README.md exists but README.zh.md is missing"))
        return

    # --- Skill names ---
    en_skill_cells = _parse_table_column(readme_en, 1, section_header="Skills")
    en_skills = _extract_backtick_names(en_skill_cells)

    # Chinese heading is "技能"
    zh_skill_cells = _parse_table_column(readme_zh, 1, section_header="技能")
    if not zh_skill_cells:
        zh_skill_cells = _parse_table_column(readme_zh, 1, section_header="Skills")
    zh_skills = _extract_backtick_names(zh_skill_cells)

    if en_skills and zh_skills and en_skills != zh_skills:
        missing = en_skills - zh_skills
        extra = zh_skills - en_skills
        parts = []
        if missing:
            parts.append(f"missing in zh: {sorted(missing)}")
        if extra:
            parts.append(f"extra in zh: {sorted(extra)}")
        findings.append(dict(
            check="D6", severity="warning",
            message=f"Skill table mismatch between READMEs — {'; '.join(parts)}"))

    # --- Agent names ---
    en_agent_cells = _parse_table_column(readme_en, 0, section_header="Agents")
    en_agents = _extract_backtick_names(en_agent_cells)

    zh_agent_cells = _parse_table_column(readme_zh, 0, section_header="Agents")
    zh_agents = _extract_backtick_names(zh_agent_cells)

    if en_agents and zh_agents and en_agents != zh_agents:
        findings.append(dict(
            check="D6", severity="warning",
            message=f"Agent table mismatch between READMEs — "
                    f"EN: {sorted(en_agents)}, ZH: {sorted(zh_agents)}"))

    # --- Command tables ---
    en_cmd_cells = _parse_table_column(readme_en, 0, section_header="Commands")
    if not en_cmd_cells:
        en_cmd_cells = _parse_table_column(readme_en, 0, section_header="命令")
    zh_cmd_cells = _parse_table_column(readme_zh, 0, section_header="命令")
    if not zh_cmd_cells:
        zh_cmd_cells = _parse_table_column(readme_zh, 0, section_header="Commands")

    en_cmds = _extract_backtick_names(set(en_cmd_cells)) if en_cmd_cells else set()
    zh_cmds = _extract_backtick_names(set(zh_cmd_cells)) if zh_cmd_cells else set()

    # Commands use /slash format — extract with a different regex
    slash_re = re.compile(r"`(/[a-z-]+)`")
    en_slash = set()
    zh_slash = set()
    for cell in en_cmd_cells:
        for m in slash_re.finditer(cell):
            en_slash.add(m.group(1))
    for cell in zh_cmd_cells:
        for m in slash_re.finditer(cell):
            zh_slash.add(m.group(1))

    if en_slash and zh_slash and en_slash != zh_slash:
        findings.append(dict(
            check="D6", severity="warning",
            message=f"Command table mismatch between READMEs — "
                    f"EN: {sorted(en_slash)}, ZH: {sorted(zh_slash)}"))

    # --- Code blocks (bash commands) ---
    code_block_re = re.compile(r"```bash\n(.*?)```", re.DOTALL)

    def _extract_commands(text):
        """Extract executable commands from bash code blocks, stripping comments."""
        cmds = set()
        for m in code_block_re.finditer(text):
            for line in m.group(1).strip().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                # Strip trailing inline comments for comparison
                cmd = re.sub(r"\s+#\s+.*$", "", line).strip()
                if cmd:
                    cmds.add(cmd)
        return cmds

    en_code = _extract_commands(readme_en)
    zh_code = _extract_commands(readme_zh)

    if en_code and zh_code:
        missing_in_zh = en_code - zh_code
        significant = {c for c in missing_in_zh
                       if c.startswith("python ") or c.startswith("bash ")
                       or c.startswith("claude ") or c.startswith("git ")
                       or c.startswith("gemini ") or c.startswith("cd ")}
        if significant:
            sample = sorted(significant)[:3]
            findings.append(dict(
                check="D6", severity="info",
                message=f"Bash commands in README.md not found in README.zh.md: "
                        f"{sample}"))

    # --- URLs/links ---
    link_re = re.compile(r"\]\(([^)]+)\)")
    en_links = {m.group(1) for m in link_re.finditer(readme_en)
                if not m.group(1).startswith("#")}
    zh_links = {m.group(1) for m in link_re.finditer(readme_zh)
                if not m.group(1).startswith("#")}

    # Only check file-path links (not anchors, not external URLs that may differ)
    en_file_links = {l for l in en_links
                     if not l.startswith("http") and not l.startswith("#")}
    zh_file_links = {l for l in zh_links
                     if not l.startswith("http") and not l.startswith("#")}

    def _normalize_link(link):
        """Treat foo.zh.md as equivalent to foo.md for bilingual comparison."""
        if link.endswith(".zh.md"):
            return link[:-6] + ".md"
        return link

    en_normalized = {_normalize_link(l) for l in en_file_links}
    zh_normalized = {_normalize_link(l) for l in zh_file_links}
    missing_links = en_normalized - zh_normalized
    # Exclude README cross-links (README.md ↔ README.zh.md)
    missing_links = {l for l in missing_links
                     if "README" not in l}
    if missing_links:
        findings.append(dict(
            check="D6", severity="info",
            message=f"File links in README.md missing from README.zh.md: "
                    f"{sorted(missing_links)[:5]}"))


# ---------------------------------------------------------------------------
# Check docs/ content consistency
# ---------------------------------------------------------------------------

def check_guide_language_sync(root, findings):
    """Check that docs/ guide pairs (*.md ↔ *.zh.md) have consistent hard data."""
    docs_dir = root / "docs"
    if not docs_dir.is_dir():
        return

    en_guides = {}
    for f in docs_dir.iterdir():
        if f.is_file() and f.suffix == ".md" and not f.stem.endswith(".zh"):
            zh_counterpart = docs_dir / f"{f.stem}.zh.md"
            if zh_counterpart.exists():
                en_guides[f.stem] = (f, zh_counterpart)
            else:
                findings.append(dict(
                    check="D7", severity="warning",
                    message=f"docs/{f.name} has no Chinese counterpart "
                            f"(expected docs/{f.stem}.zh.md)"))

    code_block_re = re.compile(r"```(?:bash|json|yaml|markdown)?\n(.*?)```", re.DOTALL)
    link_re = re.compile(r"\]\(([^)]+)\)")
    slash_re = re.compile(r"`(/[a-z-]+)`")

    def _extract_commands(text):
        cmds = set()
        for m in code_block_re.finditer(text):
            for line in m.group(1).strip().splitlines():
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                cmd = re.sub(r"\s+#\s+.*$", "", line).strip()
                if cmd:
                    cmds.add(cmd)
        return cmds

    for guide_name, (en_path, zh_path) in sorted(en_guides.items()):
        en_content = en_path.read_text(encoding="utf-8", errors="replace")
        zh_content = zh_path.read_text(encoding="utf-8", errors="replace")
        rel_en = f"docs/{en_path.name}"
        rel_zh = f"docs/{zh_path.name}"

        en_tables = set()
        zh_tables = set()
        for m in _TABLE_ROW_RE.finditer(en_content):
            cells = [c.strip() for c in m.group(1).split("|")]
            for cell in cells:
                for bt in _AGENT_BACKTICK_NAME_RE.finditer(cell):
                    en_tables.add(bt.group(1))
        for m in _TABLE_ROW_RE.finditer(zh_content):
            cells = [c.strip() for c in m.group(1).split("|")]
            for cell in cells:
                for bt in _AGENT_BACKTICK_NAME_RE.finditer(cell):
                    zh_tables.add(bt.group(1))

        en_code = _extract_commands(en_content)
        zh_code = _extract_commands(zh_content)
        if en_code and zh_code:
            missing_cmds = {c for c in (en_code - zh_code)
                           if c.startswith("python ") or c.startswith("bash ")
                           or c.startswith("claude ") or c.startswith("git ")
                           or c.startswith("gemini ") or c.startswith("cd ")}
            if missing_cmds:
                sample = sorted(missing_cmds)[:3]
                findings.append(dict(
                    check="D7", severity="info",
                    message=f"Bash commands in {rel_en} not found in "
                            f"{rel_zh}: {sample}"))

        en_slash = set()
        zh_slash = set()
        for m in slash_re.finditer(en_content):
            en_slash.add(m.group(1))
        for m in slash_re.finditer(zh_content):
            zh_slash.add(m.group(1))
        if en_slash and zh_slash and en_slash != zh_slash:
            findings.append(dict(
                check="D7", severity="warning",
                message=f"Slash command mismatch between {rel_en} and "
                        f"{rel_zh} — EN: {sorted(en_slash)}, "
                        f"ZH: {sorted(zh_slash)}"))

        en_file_links = {m.group(1) for m in link_re.finditer(en_content)
                         if not m.group(1).startswith("http")
                         and not m.group(1).startswith("#")}
        zh_file_links = {m.group(1) for m in link_re.finditer(zh_content)
                         if not m.group(1).startswith("http")
                         and not m.group(1).startswith("#")}
        en_file_links = {l for l in en_file_links
                         if not l.endswith(".zh.md")}
        zh_file_links = {l for l in zh_file_links
                         if not l.endswith(".md") or l.endswith(".zh.md")}

        def _en_to_zh(link):
            if link.endswith(".md") and not link.endswith(".zh.md"):
                return link[:-3] + ".zh.md"
            return link

        en_normalized = {_en_to_zh(l) for l in en_file_links}
        missing_links = en_normalized - zh_file_links
        if missing_links:
            findings.append(dict(
                check="D7", severity="info",
                message=f"File links in {rel_en} missing from "
                        f"{rel_zh}: {sorted(missing_links)[:5]}"))


# ---------------------------------------------------------------------------
# Check D8 — Canonical source declaration
# ---------------------------------------------------------------------------

_CANONICAL_RE = re.compile(
    r">\s*\*\*Canonical source:\*\*.*?`([^`]+)`", re.IGNORECASE)


def check_canonical_source(root, findings):
    """Verify each docs/*.md guide declares a canonical source that exists."""
    docs_dir = root / "docs"
    if not docs_dir.is_dir():
        return

    for doc_file in sorted(docs_dir.iterdir()):
        if not doc_file.is_file() or doc_file.suffix != ".md":
            continue
        if doc_file.stem.endswith(".zh"):
            continue

        content = doc_file.read_text(encoding="utf-8", errors="replace")
        rel_path = f"docs/{doc_file.name}"

        m = _CANONICAL_RE.search(content)
        if not m:
            findings.append(dict(
                check="D8", severity="warning",
                message=f"{rel_path} has no '> **Canonical source:**' declaration"))
            continue

        ref_path = m.group(1)
        resolved = root / ref_path
        if not resolved.exists():
            findings.append(dict(
                check="D8", severity="warning",
                message=f"{rel_path} declares canonical source '{ref_path}' "
                        "but the file does not exist"))


# ---------------------------------------------------------------------------
# Check D9 — Numeric cross-validation
# ---------------------------------------------------------------------------

_NUMERIC_PATTERNS = [
    (re.compile(r"(\d+)\s+attack\s+surfaces?", re.IGNORECASE), "attack surfaces"),
    (re.compile(r"(\d+)\s+categor(?:y|ies)", re.IGNORECASE), "categories"),
    (re.compile(r"(\d+)\s+targets?", re.IGNORECASE), "targets"),
    (re.compile(r"(\d+)\s+checks?(?:\s|,|\.|\))", re.IGNORECASE), "checks"),
    (re.compile(r"(\d+)\s+layers?", re.IGNORECASE), "layers"),
    (re.compile(r"(\d+)\s+paths?(?:\s|,|\.|\))", re.IGNORECASE), "paths"),
    (re.compile(r"(\d+)\s+skills?(?:\s|,|\.|\))", re.IGNORECASE), "skills"),
]


def _extract_key_numbers(text):
    """Extract (label, set-of-numbers) pairs from text."""
    results = {}
    for pattern, label in _NUMERIC_PATTERNS:
        nums = set()
        for m in pattern.finditer(text):
            nums.add(int(m.group(1)))
        if nums:
            results[label] = nums
    return results


def check_numeric_cross_validation(root, findings):
    """Verify key numbers in docs/*.md guides match their canonical source."""
    docs_dir = root / "docs"
    if not docs_dir.is_dir():
        return

    for doc_file in sorted(docs_dir.iterdir()):
        if not doc_file.is_file() or doc_file.suffix != ".md":
            continue
        if doc_file.stem.endswith(".zh"):
            continue

        content = doc_file.read_text(encoding="utf-8", errors="replace")
        rel_path = f"docs/{doc_file.name}"

        m = _CANONICAL_RE.search(content)
        if not m:
            continue

        ref_path = m.group(1)
        resolved = root / ref_path
        if not resolved.exists():
            continue

        source_content = resolved.read_text(encoding="utf-8", errors="replace")
        source_nums = _extract_key_numbers(source_content)
        guide_nums = _extract_key_numbers(content)

        for label, guide_values in guide_nums.items():
            if label not in source_nums:
                continue
            source_values = source_nums[label]
            mismatches = guide_values - source_values
            if mismatches and source_values:
                findings.append(dict(
                    check="D9", severity="warning",
                    message=f"{rel_path} mentions {sorted(mismatches)} {label} "
                            f"but canonical source '{ref_path}' has "
                            f"{sorted(source_values)}"))


# ---------------------------------------------------------------------------
# Check docs/ content consistency
# ---------------------------------------------------------------------------

def check_docs_content(root, findings):
    """Verify docs/ files reference accurate skill/script/agent names."""
    docs_dir = root / "docs"
    if not docs_dir.is_dir():
        return

    skills_dir = root / "skills"
    actual_skills = {d.name for d in skills_dir.iterdir() if d.is_dir()}

    project_name = root.name
    pkg_path = root / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            project_name = pkg.get("name", project_name)
        except (json.JSONDecodeError, OSError):
            pass

    for doc_file in docs_dir.rglob("*.md"):
        content = doc_file.read_text(encoding="utf-8", errors="replace")
        rel_path = doc_file.relative_to(root)

        for m in _CROSS_REF_BACKTICK_RE.finditer(content):
            prefix, skill_name = m.group(1), m.group(2)
            if prefix == project_name and skill_name not in actual_skills:
                findings.append(dict(
                    check="D2", severity="critical",
                    message=f"Broken cross-reference '{prefix}:{skill_name}' in {rel_path}"))

        for m in _SCRIPT_REF_RE.finditer(content):
            full_path = m.group(0).split()[-1]
            if not (root / full_path).exists():
                findings.append(dict(
                    check="D4", severity="warning",
                    message=f"docs/{rel_path} references '{full_path}' "
                            "which does not exist"))


# ---------------------------------------------------------------------------
# Runner
# ---------------------------------------------------------------------------

def run_check(project_root):
    root = Path(project_root).resolve()
    findings = []

    check_skill_list_sync(root, findings)
    check_cross_references(root, findings)
    check_platform_manifests(root, findings)
    check_script_references(root, findings)
    check_agent_sync(root, findings)
    check_readme_sync(root, findings)
    check_guide_language_sync(root, findings)
    check_canonical_source(root, findings)
    check_numeric_cross_validation(root, findings)
    check_docs_content(root, findings)

    summary = {"critical": 0, "warning": 0, "info": 0}
    for f in findings:
        summary[f["severity"]] += 1

    return {"findings": findings, "summary": summary}


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def format_markdown(results):
    s = results["summary"]
    out = [
        "## Documentation Consistency Check\n",
        f"**Results:** {s['critical']} critical, {s['warning']} warnings, {s['info']} info\n",
    ]

    for sev, heading in [("critical", "### Critical"),
                         ("warning", "### Warnings"),
                         ("info", "### Info")]:
        items = [f"- [{f['check']}] {f['message']}"
                 for f in results["findings"] if f["severity"] == sev]
        if items:
            out.append(heading)
            out.extend(items)
            out.append("")

    if not any(results["summary"].values()):
        out.append("All documentation is consistent with project state.")

    return "\n".join(out)


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    from _cli import make_parser, resolve_root, exit_by_severity
    args = make_parser(
        "Check documentation consistency in a bundle-plugin project."
    ).parse_args()
    root = resolve_root(args.project_root)

    results = run_check(root)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_markdown(results))

    exit_by_severity(results["summary"])


if __name__ == "__main__":
    main()
