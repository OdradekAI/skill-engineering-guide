#!/usr/bin/env python3
"""
Skill quality linter for bundle-plugins.

Validates SKILL.md frontmatter, descriptions, line counts, cross-references,
and relative path links across all skills in a project.

Usage:
    python scripts/lint_skills.py [project-root]
    python scripts/lint_skills.py --json [project-root]

Exit codes: 0 = all pass, 1 = warnings, 2 = critical
"""

import json
import re
import sys
from pathlib import Path

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
ALLOWED_TOOLS_PATH_RE = re.compile(r"\b(scripts/[^\s*)+]+(?:\.py|\.sh|\.js)?)")
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
# Linting rules
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
    lines = content.splitlines()

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

    # Q16: Inputs section (skip for bootstrap skills)
    if not is_bootstrap and "## Inputs" not in content:
        findings.append(dict(check="Q16", severity="info", message="Missing Inputs section"))

    # Q17: Outputs section (skip for bootstrap skills)
    if not is_bootstrap and "## Outputs" not in content:
        findings.append(dict(check="Q17", severity="info", message="Missing Outputs section"))

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
        findings.append(dict(check="Q13", severity="warning",
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
# Runner
# ---------------------------------------------------------------------------

def run_lint(project_root):
    project_root = Path(project_root).resolve()
    skills_dir = project_root / "skills"
    project_name = project_root.name

    # Detect project name and abbreviation from package.json if available
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
    # Cross-skill consistency checks (C1-C3) — project-level only
    # -----------------------------------------------------------------------
    if len(results["skills"]) >= 2:
        consistency = []

        # Gather per-skill traits (skip bootstrap skills for structural checks)
        has_overview = []
        has_subagent_fallback = []
        desc_verb_forms = []  # "gerund" or "bare" after "Use when"
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

        # C1: Overview section consistency
        if has_overview and not all(has_overview) and any(has_overview):
            with_count = sum(has_overview)
            without_count = len(has_overview) - with_count
            consistency.append(dict(
                check="C1", severity="info",
                message=f"Inconsistent Overview sections: {with_count} skills "
                        f"have it, {without_count} do not"))

        # C2: Subagent fallback consistency
        users = [sr["skill"] for sr, has in
                 zip(results["skills"], has_subagent_fallback)
                 if has] if has_subagent_fallback else []
        if has_subagent_fallback and any(has_subagent_fallback) \
                and not all(has_subagent_fallback):
            consistency.append(dict(
                check="C2", severity="info",
                message="Inconsistent subagent fallback patterns: "
                        "some skills handle 'subagent unavailable', others don't"))

        # C3: Description verb form consistency
        if desc_verb_forms and len(set(desc_verb_forms)) > 1:
            gerund_n = desc_verb_forms.count("gerund")
            bare_n = desc_verb_forms.count("bare")
            consistency.append(dict(
                check="C3", severity="info",
                message=f"Mixed verb forms after 'Use when': "
                        f"{gerund_n} gerund (-ing) vs {bare_n} bare infinitive"))

        results["consistency"] = consistency
        for f in consistency:
            results["summary"][f["severity"]] += 1

    # -------------------------------------------------------------------
    # Graph analysis (G1-G4) — workflow DAG checks
    # -------------------------------------------------------------------
    if len(results["skills"]) >= 2:
        graph_findings = []

        graph_valid_prefixes = {project_name}
        if project_abbreviation:
            graph_valid_prefixes.add(project_abbreviation)

        # Build directed graph from the ## Integration section's
        # **Calls:** block. This is the authoritative source for workflow
        # edges — body references and "Pairs with" are informational.
        _CALLS_HEADER_RE = re.compile(r"\*\*Calls?:?\*\*", re.IGNORECASE)
        # Integration sections use **project:skill** (bold), not backticks
        _BOLD_REF_RE = re.compile(r"\*\*([a-z0-9-]+):([a-z0-9-]+)\*\*")

        def _extract_calls(content):
            """Extract outgoing skill refs from the Integration Calls block."""
            calls = set()
            lines = content.splitlines()
            in_calls = False
            for line in lines:
                if _CALLS_HEADER_RE.search(line):
                    in_calls = True
                    for m in _BOLD_REF_RE.finditer(line):
                        if m.group(1) in graph_valid_prefixes:
                            calls.add(m.group(2))
                    for m in CROSS_REF_RE.finditer(line):
                        if m.group(1) in graph_valid_prefixes:
                            calls.add(m.group(2))
                    continue
                if in_calls:
                    if line.startswith("- ") or line.startswith("  "):
                        for m in _BOLD_REF_RE.finditer(line):
                            if m.group(1) in graph_valid_prefixes:
                                calls.add(m.group(2))
                        for m in CROSS_REF_RE.finditer(line):
                            if m.group(1) in graph_valid_prefixes:
                                calls.add(m.group(2))
                    elif line.strip() and not line.startswith("-"):
                        in_calls = False
            return calls

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
            refs = _extract_calls(scontent)
            refs.discard(sname)
            existing_refs = {r for r in refs
                            if (skills_dir / r).is_dir()}
            graph[sname] = existing_refs

        all_skill_names = set(graph.keys())

        # G1: Cycle detection — find minimal cycles using Johnson's
        # approach simplified: for each edge A->B where B->...->A exists,
        # find the shortest back-path. Only report unique minimal cycles.
        CYCLE_DECL_RE = re.compile(r"<!--\s*cycle:([\w,-]+)\s*-->")

        def _get_declared_cycle_sets(content):
            """Return all declared cycle sets from a skill's content."""
            result = []
            for m in CYCLE_DECL_RE.finditer(content):
                result.append(set(m.group(1).split(",")))
            return result

        def _find_minimal_cycles(g):
            """Find shortest elementary cycles (no redundant sub-paths)."""
            seen_cycle_sets = set()
            cycles = []
            for start in sorted(g):
                from collections import deque
                for neighbor in g.get(start, set()):
                    queue = deque([(neighbor, [start, neighbor])])
                    visited_in_search = {start, neighbor}
                    while queue:
                        node, path = queue.popleft()
                        for nxt in g.get(node, set()):
                            if nxt == start:
                                canon = tuple(sorted(path))
                                if canon not in seen_cycle_sets:
                                    seen_cycle_sets.add(canon)
                                    cycles.append(tuple(path))
                                break
                            if nxt not in visited_in_search \
                                    and nxt in g:
                                visited_in_search.add(nxt)
                                queue.append((nxt, path + [nxt]))
                        else:
                            continue
                        break
            return cycles

        for cycle in _find_minimal_cycles(graph):
            cycle_set = set(cycle)
            declared = True
            for node in cycle_set:
                content = skill_contents.get(node, "")
                decl_sets = _get_declared_cycle_sets(content)
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
        # Entry points = skills referenced by using-* bootstrap skills
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

        # G5: Artifact identifier matching (experimental) — check that
        # for each edge A->B, A's Outputs contain at least one artifact
        # identifier that also appears in B's Inputs.
        _SECTION_RE = re.compile(r"^## (Inputs|Outputs)\s*$", re.MULTILINE)
        _ARTIFACT_ID_RE = re.compile(r"`([a-z][a-z0-9-]*)`")

        def _extract_artifact_ids(content, section_name):
            """Extract backtick-wrapped artifact IDs from a named section."""
            ids = set()
            lines = content.splitlines()
            in_section = False
            for line in lines:
                if line.strip() == f"## {section_name}":
                    in_section = True
                    continue
                if in_section:
                    if line.startswith("## "):
                        break
                    for m in _ARTIFACT_ID_RE.finditer(line):
                        candidate = m.group(1)
                        if candidate not in graph_valid_prefixes \
                                and ":" not in candidate:
                            ids.add(candidate)
            return ids

        skill_outputs = {}
        skill_inputs = {}
        for sname, scontent in skill_contents.items():
            skill_outputs[sname] = _extract_artifact_ids(scontent, "Outputs")
            skill_inputs[sname] = _extract_artifact_ids(scontent, "Inputs")

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
    # Agent architecture checks (S10, S12) — skill-agent relationship
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

            # S10: Agent self-containment — body should have substantial
            # instructions, not just a file-read pointer.
            if len(body_lines) < 5:
                agent_findings.append(dict(
                    check="S10", severity="info",
                    message=f"Agent '{agent_name}' has only {len(body_lines)} "
                            "non-empty body lines — may not be self-contained"))

        # S12: Inline fallback references agent file — skills that dispatch
        # agents should reference the agent file in their fallback blocks.
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
# Output
# ---------------------------------------------------------------------------

def format_markdown(results):
    s = results["summary"]
    out = [
        "## Skill Quality Lint\n",
        f"**Skills checked:** {len(results['skills'])}",
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
    out.append("| Skill | Critical | Warnings | Info |")
    out.append("|-------|----------|----------|------|")
    for sr in results["skills"]:
        c = sr["counts"]
        out.append(f"| {sr['skill']} | {c['critical']} | {c['warning']} | {c['info']} |")
    return "\n".join(out)

# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    from _cli import make_parser, resolve_root, exit_by_severity
    args = make_parser("Lint skill quality in a bundle-plugin project.").parse_args()
    root = resolve_root(args.project_root)

    results = run_lint(root)
    if args.json:
        print(json.dumps(results, indent=2))
    else:
        print(format_markdown(results))

    exit_by_severity(results["summary"])


if __name__ == "__main__":
    main()
