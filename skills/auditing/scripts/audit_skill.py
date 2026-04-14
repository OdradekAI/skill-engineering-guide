#!/usr/bin/env python3
"""
Skill audit for bundle-plugins.

Unified entry point for skill quality checks — supports both single-skill
audits and project-level linting.  Auto-detects mode from the path argument:

  - Path to a skill directory or SKILL.md → single-skill audit (4 categories)
  - Path to a project root (contains skills/) → project-level lint (all skills)
  - --all flag forces project-level mode

Usage:
    python audit_skill.py <skill-dir-or-SKILL.md>   # single skill
    python audit_skill.py [project-root]             # project lint
    python audit_skill.py --all [project-root]       # force project
    python audit_skill.py --json <path>              # JSON output

Exit codes: 0 = pass, 1 = warnings, 2 = critical findings
"""

import json
import re
import sys
from pathlib import Path

_SCRIPT_DIR = Path(__file__).resolve().parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))

import audit_security

# ---------------------------------------------------------------------------
# Frontmatter parsing (pure-stdlib, zero external dependencies)
#
# Why not PyYAML: bundle-plugins are designed for `git clone` → immediate use.
# Requiring `pip install pyyaml` would break zero-setup workflows (CI runners,
# containers, restricted corporate environments). Python 3.8+ stdlib is the
# only hard dependency.
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
_BLOCK_SCALAR_RE = re.compile(r"^[|>][+-]?\d*$")
WORKFLOW_SUMMARY_PHRASES = re.compile(
    r"first\b.*then\b.*finally|step\s+\d|phase\s+\d|"
    r"scans?\s+.*checks?\s+.*generates?|"
    r"reads?\s+.*writes?\s+.*outputs?|"
    r"\d\)\s+\w+.*\d\)\s+\w+|"
    r"\b\w+(?:e?s)\b[,;]\s+\w+(?:e?s)\b[,;]\s+(?:and\s+)?\w+(?:e?s)\b",
    re.IGNORECASE,
)
KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
CROSS_REF_RE = re.compile(r"`([a-z0-9-]+):([a-z0-9-]+)`")
RELATIVE_PATH_RE = re.compile(r"`((?:references|assets|scripts|templates)/[^`]+)`")
ALLOWED_TOOLS_PATH_RE = re.compile(r"\b((?:skills/[a-z-]+/)?scripts/[^\s*)+]+(?:\.py|\.sh|\.js)?)")
REFERENCED_DIR_RE = re.compile(
    r"(?:in|under|from|see)\s+`(references|templates|assets|examples)/`",
    re.IGNORECASE,
)
_INSTRUCTIONAL_CONTEXT_RE = re.compile(
    r"move|extract|create|put|place|→|——|should\s+be|"
    r"one\s+file\s+per|a\s+file\s+under|files?\s+under",
    re.IGNORECASE,
)
CONDITIONAL_BLOCK_RE = re.compile(
    r"^\*\*(?:If|When)\b.*[:：]?\*\*$|"
    r"^(?:If|When)\s+.*(?:unavailable|not available|fails?|missing|skip)",
    re.IGNORECASE,
)


def parse_frontmatter(content):
    m = FRONTMATTER_RE.match(content)
    if not m:
        return None, content
    raw = m.group(1)
    fm = {}
    current_key = None
    block_join = " "
    for line in raw.split("\n"):
        if line.startswith("  ") and current_key:
            sep = block_join if fm[current_key] else ""
            fm[current_key] += sep + line.strip()
            continue
        idx = line.find(":")
        if idx > 0:
            key = line[:idx].strip()
            val = line[idx + 1:].strip()
            if _BLOCK_SCALAR_RE.match(val):
                fm[key] = ""
                current_key = key
                block_join = "\n" if val[0] == "|" else " "
                continue
            if (val.startswith('"') and val.endswith('"')) or \
               (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            fm[key] = val
            current_key = key
            block_join = " "
    body_start = m.end()
    return fm, content[body_start:]


_CODE_BLOCK_RE = re.compile(r"```[\s\S]*?```")
_TABLE_ROW_RE = re.compile(r"^\|.+\|$", re.MULTILINE)


def estimate_tokens(content):
    """Estimate token count with separate rates for code, tables, and prose."""
    code_blocks = _CODE_BLOCK_RE.findall(content)
    table_rows = _TABLE_ROW_RE.findall(content)

    code_chars = sum(len(b) for b in code_blocks)
    table_chars = sum(len(r) for r in table_rows)

    code_tokens = int(code_chars / 3.5)
    table_tokens = int(table_chars / 3.0)

    prose_content = _CODE_BLOCK_RE.sub("", content)
    prose_content = _TABLE_ROW_RE.sub("", prose_content)
    prose_tokens = int(len(prose_content.split()) * 1.3)

    return prose_tokens + code_tokens + table_tokens


# ---------------------------------------------------------------------------
# Per-skill linting rules (Q1-Q15, S9, X1-X3)
# ---------------------------------------------------------------------------

def lint_skill(skill_dir, project_root, project_name, project_abbreviation=None):
    findings = []
    skill_md = skill_dir / "SKILL.md"
    dir_name = skill_dir.name

    if not skill_md.exists():
        findings.append(dict(check="Q1", severity="critical", message="Missing SKILL.md"))
        return findings

    content = skill_md.read_text(encoding="utf-8", errors="replace")
    fm, body = parse_frontmatter(content)

    # Q1: Frontmatter exists
    if fm is None:
        findings.append(dict(check="Q1", severity="critical",
                             message="No YAML frontmatter (missing --- delimiters)"))
        return findings

    fm_raw = FRONTMATTER_RE.match(content).group(1) if FRONTMATTER_RE.match(content) else ""

    # Q2: name field
    name = fm.get("name", "")
    if not name:
        findings.append(dict(check="Q2", severity="critical", message="Missing 'name' in frontmatter"))
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
        findings.append(dict(check="Q3", severity="critical", message="Missing 'description' in frontmatter"))
    else:
        # Q5: starts with "Use when"
        if not desc.lower().startswith("use when"):
            findings.append(dict(check="Q5", severity="warning",
                                 message="Description should start with 'Use when...'"))
        # Q6: workflow summary anti-pattern
        if WORKFLOW_SUMMARY_PHRASES.search(desc):
            findings.append(dict(check="Q6", severity="warning",
                                 message="Description appears to summarize workflow instead of triggering conditions"))
        # Q7: length (Claude Code truncates descriptions beyond 250 chars in skill listing)
        if len(desc) > 250:
            findings.append(dict(check="Q7", severity="warning",
                                 message=f"Description is {len(desc)} chars (max 250)"))

    # Q8: frontmatter size
    if len(fm_raw) > 1024:
        findings.append(dict(check="Q8", severity="warning",
                             message=f"Frontmatter is {len(fm_raw)} chars (max 1024)"))

    # Q9: body line count
    body_lines = len(body.splitlines())
    if body_lines > 500:
        findings.append(dict(check="Q9", severity="warning",
                             message=f"SKILL.md body is {body_lines} lines (max 500)"))

    # Q10: Overview section (skip for bootstrap skills like using-*)
    is_bootstrap = skill_dir.name.startswith("using-")
    if not is_bootstrap and "## Overview" not in content and "## overview" not in content.lower():
        findings.append(dict(check="Q10", severity="info", message="Missing Overview section"))

    # Q11: Common Mistakes section (skip for bootstrap skills)
    if not is_bootstrap and "## Common Mistakes" not in content and "common mistakes" not in content.lower():
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

    # Q13: Static token budget (bootstrap skills have a tighter 200-line budget)
    body_lines = len(body.splitlines())
    estimated_tokens = estimate_tokens(body)
    if is_bootstrap and body_lines > 200:
        findings.append(dict(check="Q13", severity="info",
                             message=f"Bootstrap skill body is {body_lines} lines "
                                     f"(~{estimated_tokens} tokens, estimated); "
                                     f"budget is 200 lines"))
    elif not is_bootstrap and estimated_tokens > 4000:
        findings.append(dict(check="Q13", severity="info",
                             message=f"SKILL.md body ~{estimated_tokens} estimated tokens "
                                     f"({body_lines} lines); actual may vary by model"))

    # Q14: allowed-tools dependency existence
    allowed_tools = fm.get("allowed-tools", "")
    if allowed_tools:
        for m in ALLOWED_TOOLS_PATH_RE.finditer(allowed_tools):
            tool_path = m.group(1)
            resolved = project_root / tool_path
            if not resolved.exists() and not any(project_root.glob(tool_path)):
                findings.append(dict(check="Q14", severity="warning",
                                     message=f"allowed-tools references '{tool_path}' "
                                             "which does not exist"))

    # X3: Documentation vs implementation consistency — skill text uses
    # locative phrases like "in `references/`" implying the directory exists.
    # Skip instructional context (teaching users to create/extract to these dirs).
    seen_x3_dirs = set()
    for m in REFERENCED_DIR_RE.finditer(body):
        ref_dir_name = m.group(1)
        if ref_dir_name in seen_x3_dirs:
            continue
        line_start = body.rfind("\n", 0, m.start()) + 1
        line_end = body.find("\n", m.end())
        if line_end == -1:
            line_end = len(body)
        line_text = body[line_start:line_end]
        if _INSTRUCTIONAL_CONTEXT_RE.search(line_text):
            continue
        if not (skill_dir / ref_dir_name).is_dir():
            seen_x3_dirs.add(ref_dir_name)
            findings.append(dict(check="X3", severity="warning",
                                 message=f"Text references '{ref_dir_name}/' directory "
                                         "but it does not exist in skill directory"))

    # Q15: Conditional branch reachability — large blocks guarded by
    # "If ... unavailable" style conditions should be in references/
    body_line_list = body.splitlines()
    i = 0
    while i < len(body_line_list):
        line = body_line_list[i]
        if CONDITIONAL_BLOCK_RE.match(line.strip()):
            block_start = i
            i += 1
            while i < len(body_line_list):
                next_line = body_line_list[i].strip()
                if next_line.startswith("## ") or next_line.startswith("### ") \
                        or CONDITIONAL_BLOCK_RE.match(next_line):
                    break
                i += 1
            block_size = i - block_start
            if block_size > 30:
                findings.append(dict(check="Q15", severity="info",
                                     message=f"Conditional block at line {block_start + 1} "
                                             f"spans {block_size} lines; consider moving "
                                             "to references/"))
        else:
            i += 1

    return findings


# ---------------------------------------------------------------------------
# Project-level runner (C1, G1-G5, S10, S12)
# ---------------------------------------------------------------------------

def run_lint(project_root):
    """Run project-level lint across all skills.

    Returns a dict consumed by audit_plugin.py and audit_workflow.py:
    {"skills": [...], "summary": {...}, "graph": [...], ...}
    """
    project_root = Path(project_root).resolve()
    skills_dir = project_root / "skills"
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

    results = {"skills": [], "summary": {"critical": 0, "warning": 0, "info": 0}}

    skill_dirs = [d for d in sorted(skills_dir.iterdir()) if d.is_dir()]
    if not skill_dirs:
        print("warning: skills/ directory is empty — no skills to check",
              file=sys.stderr)

    for skill_dir in sorted(skills_dir.iterdir()):
        if not skill_dir.is_dir():
            continue
        findings = lint_skill(skill_dir, project_root, project_name,
                              project_abbreviation)
        skill_result = {
            "skill": skill_dir.name,
            "findings": findings,
            "counts": {"critical": 0, "warning": 0, "info": 0},
        }
        for f in findings:
            skill_result["counts"][f["severity"]] += 1
            results["summary"][f["severity"]] += 1
        results["skills"].append(skill_result)

    # -----------------------------------------------------------------------
    # Cross-skill consistency check (C1) — project-level only
    # -----------------------------------------------------------------------
    if len(results["skills"]) >= 2:
        consistency = []
        sub_issues = []

        has_overview = []
        has_subagent_fallback = []
        desc_verb_forms = []
        for sr in results["skills"]:
            sname = sr["skill"]
            sdir = skills_dir / sname
            smd = sdir / "SKILL.md"
            if not smd.exists():
                continue
            scontent = smd.read_text(encoding="utf-8", errors="replace")

            is_bootstrap = sname.startswith("using-")
            if not is_bootstrap:
                has_overview.append(
                    "## Overview" in scontent or "## overview" in scontent.lower())
                has_subagent_fallback.append(
                    "subagent" in scontent.lower()
                    and ("unavailable" in scontent.lower()
                         or "not available" in scontent.lower()))

            sfm, _ = parse_frontmatter(scontent)
            if sfm:
                desc = sfm.get("description", "")
                after_when = re.sub(r"(?i)^use\s+when\s+", "", desc).strip()
                if after_when:
                    first_word = after_when.split()[0].lower()
                    if first_word.endswith("ing"):
                        desc_verb_forms.append("gerund")
                    else:
                        desc_verb_forms.append("bare")

        if has_overview and not all(has_overview) and any(has_overview):
            with_count = sum(has_overview)
            without_count = len(has_overview) - with_count
            sub_issues.append(
                f"Overview sections: {with_count} skills have it, "
                f"{without_count} do not")

        if has_subagent_fallback and any(has_subagent_fallback) \
                and not all(has_subagent_fallback):
            sub_issues.append(
                "subagent fallback: some skills handle "
                "'subagent unavailable', others don't")

        if desc_verb_forms and len(set(desc_verb_forms)) > 1:
            gerund_n = desc_verb_forms.count("gerund")
            bare_n = desc_verb_forms.count("bare")
            sub_issues.append(
                f"verb forms after 'Use when': "
                f"{gerund_n} gerund (-ing) vs {bare_n} bare infinitive")

        if sub_issues:
            consistency.append(dict(
                check="C1", severity="info",
                message="Cross-skill inconsistencies: " + "; ".join(sub_issues)))

        results["consistency"] = consistency
        for f in consistency:
            results["summary"][f["severity"]] += 1

    # -------------------------------------------------------------------
    # Graph analysis (G1-G5) — workflow DAG checks
    # -------------------------------------------------------------------
    if len(results["skills"]) >= 2:
        import _graph

        graph_findings = []

        graph_valid_prefixes = {project_name}
        if project_abbreviation:
            graph_valid_prefixes.add(project_abbreviation)

        graph = {}
        skill_contents = {}
        for sr in results["skills"]:
            sname = sr["skill"]
            sdir = skills_dir / sname
            smd = sdir / "SKILL.md"
            if not smd.exists():
                continue
            scontent = smd.read_text(encoding="utf-8", errors="replace")
            skill_contents[sname] = scontent
            refs = _graph.extract_calls(scontent, graph_valid_prefixes)
            refs.discard(sname)
            existing_refs = {r for r in refs
                            if (skills_dir / r).is_dir()}
            graph[sname] = existing_refs

        all_skill_names = set(graph.keys())

        # G1: Cycle detection
        for cycle in _graph.find_minimal_cycles(graph):
            cycle_set = set(cycle)
            declared = True
            for node in cycle_set:
                content = skill_contents.get(node, "")
                decl_sets = _graph.get_declared_cycle_sets(content)
                if any(cycle_set.issubset(ds) for ds in decl_sets):
                    continue
                declared = False
                break
            sev = "info" if declared else "warning"
            chain = " -> ".join(cycle) + " -> " + cycle[0]
            msg = f"Circular dependency: {chain}"
            if declared:
                msg += " (declared feedback loop)"
            graph_findings.append(dict(check="G1", severity=sev, message=msg))

        # G2: Reachability from entry points
        entry_points = set()
        for sname, scontent in skill_contents.items():
            if sname.startswith("using-"):
                for match in CROSS_REF_RE.finditer(scontent):
                    proj, skill_ref = match.group(1), match.group(2)
                    if proj in graph_valid_prefixes and skill_ref in all_skill_names:
                        entry_points.add(skill_ref)
                entry_points.add(sname)

        if entry_points:
            reachable = set(entry_points)
            queue = list(entry_points)
            while queue:
                current = queue.pop(0)
                for neighbor in graph.get(current, set()):
                    if neighbor not in reachable:
                        reachable.add(neighbor)
                        queue.append(neighbor)

            for sname in sorted(all_skill_names - reachable):
                content = skill_contents.get(sname, "")
                if "Called by: user directly" in content:
                    continue
                graph_findings.append(dict(
                    check="G2", severity="info",
                    message=f"Skill '{sname}' is not reachable from any "
                            "entry point (add to bootstrap routing or declare "
                            "'Called by: user directly' in Integration)"))

        # G3: Terminal skills (no outgoing edges) without Outputs section
        for sname in sorted(all_skill_names):
            if not graph.get(sname):
                content = skill_contents.get(sname, "")
                if "## Outputs" not in content and not sname.startswith("using-"):
                    graph_findings.append(dict(
                        check="G3", severity="info",
                        message=f"Terminal skill '{sname}' has no outgoing "
                                "references and no ## Outputs section"))

        # G4: Skills with incoming edges but no Inputs section
        has_incoming = set()
        for sname, refs in graph.items():
            has_incoming.update(refs)
        for sname in sorted(has_incoming):
            content = skill_contents.get(sname, "")
            if "## Inputs" not in content:
                graph_findings.append(dict(
                    check="G4", severity="info",
                    message=f"Skill '{sname}' is referenced by other skills "
                            "but has no ## Inputs section"))

        # G5: Artifact identifier matching (experimental)
        skill_outputs = {}
        skill_inputs = {}
        for sname, scontent in skill_contents.items():
            skill_outputs[sname] = _graph.extract_artifact_ids(
                scontent, "Outputs", graph_valid_prefixes)
            skill_inputs[sname] = _graph.extract_artifact_ids(
                scontent, "Inputs", graph_valid_prefixes)

        for src, targets in graph.items():
            src_out = skill_outputs.get(src, set())
            if not src_out:
                continue
            for tgt in targets:
                tgt_in = skill_inputs.get(tgt, set())
                if not tgt_in:
                    continue
                if not src_out & tgt_in:
                    graph_findings.append(dict(
                        check="G5", severity="info",
                        message=f"No matching artifact IDs between "
                                f"'{src}' outputs {sorted(src_out)} and "
                                f"'{tgt}' inputs {sorted(tgt_in)}"))

        results["graph"] = graph_findings
        for f in graph_findings:
            results["summary"][f["severity"]] += 1

    # -------------------------------------------------------------------
    # Agent architecture checks (S10, S12)
    # -------------------------------------------------------------------
    agents_dir = project_root / "agents"
    if agents_dir.is_dir():
        agent_findings = []

        agent_files = sorted(agents_dir.glob("*.md"))
        for agent_file in agent_files:
            agent_content = agent_file.read_text(encoding="utf-8", errors="replace")
            agent_fm, agent_body = parse_frontmatter(agent_content)
            agent_name = agent_fm.get("name", agent_file.stem) if agent_fm else agent_file.stem
            body_lines = [l for l in agent_body.strip().splitlines() if l.strip()]

            # S10: Agent self-containment
            if len(body_lines) < 5:
                agent_findings.append(dict(
                    check="S10", severity="info",
                    message=f"Agent '{agent_name}' has only {len(body_lines)} "
                            "non-empty body lines — may not be self-contained"))

        # S12: Inline fallback references agent file
        _DISPATCH_RE = re.compile(
            r"[Dd]ispatch.*`agents/([a-z0-9_-]+\.md)`")
        _FALLBACK_AGENT_REF_RE = re.compile(
            r"(?:read|follow|see)\s+`agents/", re.IGNORECASE)

        for sr in results["skills"]:
            sname = sr["skill"]
            sdir = skills_dir / sname
            smd = sdir / "SKILL.md"
            if not smd.exists():
                continue
            scontent = smd.read_text(encoding="utf-8", errors="replace")

            dispatched_agents = _DISPATCH_RE.findall(scontent)
            if not dispatched_agents:
                continue

            has_fallback = ("unavailable" in scontent.lower()
                           or "not available" in scontent.lower())
            if not has_fallback:
                continue

            if not _FALLBACK_AGENT_REF_RE.search(scontent):
                agent_list = ", ".join(dispatched_agents)
                agent_findings.append(dict(
                    check="S12", severity="info",
                    message=f"Skill '{sname}' dispatches {agent_list} but "
                            "its inline fallback does not reference the "
                            "agent file — consider using 'read `agents/...`' "
                            "for single source of truth"))

        if agent_findings:
            results["agent_architecture"] = agent_findings
            for f in agent_findings:
                results["summary"][f["severity"]] += 1

    return results


# ---------------------------------------------------------------------------
# Scoring (shared by both modes)
# ---------------------------------------------------------------------------

from _scoring import compute_baseline_score, compute_weighted_average

SKILL_CATEGORY_WEIGHTS = {
    "structure": 3,
    "skill_quality": 2,
    "cross_references": 2,
    "security": 3,
}


# ---------------------------------------------------------------------------
# Skill path resolution
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
# Single-skill audit
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
    if check.startswith(("SEC", "SC", "HK", "AG", "BS", "MC", "OC", "PC")):
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

    lint_findings = lint_skill(
        skill_dir, project_root, project_name, project_abbreviation)

    # Security checks via audit_security
    sec_findings_raw = []
    scannable = audit_security.collect_scannable_files(skill_dir)
    self_path = Path(__file__).resolve()
    for f in scannable:
        if f.resolve() == self_path:
            continue
        rel = f.relative_to(skill_dir) if f.is_relative_to(skill_dir) else f
        file_type = audit_security.classify_file(
            f.relative_to(project_root) if f.is_relative_to(project_root) else rel)
        if file_type is None:
            skill_md = skill_dir / "SKILL.md"
            if f.resolve() == skill_md.resolve():
                file_type = "skill_content"
            else:
                continue
        findings = audit_security.scan_file(f, rel, file_type)
        for finding in findings:
            sec_findings_raw.append({
                "check": finding.get("check_id", ""),
                "severity": finding.get("risk", "info"),
                "message": f"{f.name}:{finding.get('line', '?')} — "
                           f"{finding.get('description', '')}",
            })

    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        already_scanned = any(
            f.resolve() == skill_md.resolve() for f in scannable)
        if not already_scanned:
            findings = audit_security.scan_file(
                skill_md, Path("SKILL.md"), "skill_content")
            for finding in findings:
                sec_findings_raw.append({
                    "check": finding.get("check_id", ""),
                    "severity": finding.get("risk", "info"),
                    "message": f"SKILL.md:{finding.get('line', '?')} — "
                               f"{finding.get('description', '')}",
                })

    categories = {
        "structure": {"findings": [], "counts": {"critical": 0, "warning": 0, "info": 0}},
        "skill_quality": {"findings": [], "counts": {"critical": 0, "warning": 0, "info": 0}},
        "cross_references": {"findings": [], "counts": {"critical": 0, "warning": 0, "info": 0}},
        "security": {"findings": sec_findings_raw, "counts": {"critical": 0, "warning": 0, "info": 0}},
    }

    for f in lint_findings:
        cat = _classify_finding(f)
        categories[cat]["findings"].append(f)

    for cat_data in categories.values():
        for f in cat_data["findings"]:
            sev = f.get("severity", "info")
            cat_data["counts"][sev] = cat_data["counts"].get(sev, 0) + 1

    scores = {}
    for cat_name, cat_data in categories.items():
        scores[cat_name] = compute_baseline_score(cat_data["findings"],
                                                    cap_per_id=False)
        cat_data["baseline_score"] = scores[cat_name]

    overall_score = compute_weighted_average(scores, SKILL_CATEGORY_WEIGHTS)

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
# Output formatters
# ---------------------------------------------------------------------------

def format_skill_markdown(results):
    """Format single-skill audit results as markdown."""
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
        w = SKILL_CATEGORY_WEIGHTS.get(cat, 1)
        s = data.get("baseline_score", "—")
        out.append(f"| {cat} | {w} | {s}/10 | {c.get('critical', 0)} "
                   f"| {c.get('warning', 0)} | {c.get('info', 0)} |")

    return "\n".join(out)


def format_project_markdown(results):
    """Format project-level lint results as markdown (audit style)."""
    s = results["summary"]
    skill_count = len(results["skills"])

    total_critical = s["critical"]
    total_warning = s["warning"]
    if total_critical > 0:
        status = "FAIL"
    elif total_warning > 0:
        status = "WARN"
    else:
        status = "PASS"

    out = [
        f"## Skill Quality Audit ({skill_count} skills)\n",
        f"### Status: {status}\n",
        f"**Results:** {s['critical']} critical, {s['warning']} warnings, {s['info']} info\n",
    ]

    for sev, heading in [("critical", "### Critical"), ("warning", "### Warnings"), ("info", "### Info")]:
        items = []
        for sr in results["skills"]:
            for f in sr["findings"]:
                if f["severity"] == sev:
                    items.append(f"- [{f['check']}] {sr['skill']}: {f['message']}")
        for f in results.get("agent_architecture", []):
            if f["severity"] == sev:
                items.append(f"- [{f['check']}] {f['message']}")
        if items:
            out.append(heading)
            out.extend(items)
            out.append("")

    out.append("### Per-Skill Summary\n")
    out.append("| Skill | Score | Critical | Warnings | Info |")
    out.append("|-------|-------|----------|----------|------|")
    for sr in results["skills"]:
        c = sr["counts"]
        score = compute_baseline_score(sr["findings"], cap_per_id=False)
        out.append(f"| {sr['skill']} | {score}/10 | {c['critical']} | {c['warning']} | {c['info']} |")
    return "\n".join(out)


# ---------------------------------------------------------------------------
# Mode detection
# ---------------------------------------------------------------------------

def detect_mode(raw_path, force_all=False):
    """Auto-detect whether to run single-skill or project-level audit.

    Returns ("skill", resolved_path) or ("project", resolved_path).
    """
    p = Path(raw_path).resolve()
    if force_all:
        return "project", p
    if p.is_file() and p.name == "SKILL.md":
        return "skill", p
    if p.is_dir() and (p / "skills").is_dir():
        return "project", p
    if p.is_dir() and (p / "SKILL.md").exists():
        return "skill", p
    return "project", p


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Skill audit for bundle-plugins (single skill or project-level).")
    parser.add_argument("path", nargs="?", default=".",
                        help="Skill directory, SKILL.md file, or project root "
                             "(default: current directory)")
    parser.add_argument("--all", action="store_true",
                        help="Force project-level mode (audit all skills)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of markdown")
    args = parser.parse_args()

    mode, resolved = detect_mode(args.path, force_all=args.all)

    if mode == "project":
        if not (resolved / "skills").is_dir():
            print(f"error: {resolved} has no skills/ directory", file=sys.stderr)
            sys.exit(1)
        results = run_lint(resolved)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(format_project_markdown(results))
        from _cli import exit_by_severity
        exit_by_severity(results["summary"])
    else:
        results = run_skill_audit(resolved)
        if args.json:
            print(json.dumps(results, indent=2))
        else:
            print(format_skill_markdown(results))
        from _cli import exit_by_severity
        exit_by_severity(results["summary"])


if __name__ == "__main__":
    main()
