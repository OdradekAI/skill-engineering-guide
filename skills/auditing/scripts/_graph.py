"""Workflow graph analysis for bundle-plugin skill dependencies (W1-W5).

Provides unified cross-reference extraction (regex constants + helpers),
cycle detection, and the full graph analysis that emits W1-W5 findings.
"""

import re
from collections import deque

# ---------------------------------------------------------------------------
# Unified cross-reference regex constants
#
# All cross-ref extraction across the auditing scripts imports from here.
# ---------------------------------------------------------------------------

CALLS_HEADER_RE = re.compile(r"\*\*Calls?:?\*\*", re.IGNORECASE)
CALLED_BY_HEADER_RE = re.compile(r"\*\*Called\s+by:?\*\*", re.IGNORECASE)
BOLD_REF_RE = re.compile(r"\*\*([a-z0-9-]+):([a-z0-9-]+)\*\*")
CROSS_REF_RE = re.compile(r"`([a-z0-9-]+):([a-z0-9-]+)`")
CYCLE_DECL_RE = re.compile(r"<!--\s*cycle:([\w,-]+)\s*-->")
ARTIFACT_ID_RE = re.compile(r"`([a-z][a-z0-9-]*)`")


# ---------------------------------------------------------------------------
# Reference extraction helpers
# ---------------------------------------------------------------------------

def _extract_refs_from_block(content, header_re, valid_prefixes):
    """Extract skill refs from a **Calls:** or **Called by:** block."""
    refs = set()
    lines = content.splitlines()
    in_block = False
    for line in lines:
        if header_re.search(line):
            in_block = True
            for m in BOLD_REF_RE.finditer(line):
                if m.group(1) in valid_prefixes:
                    refs.add(m.group(2))
            for m in CROSS_REF_RE.finditer(line):
                if m.group(1) in valid_prefixes:
                    refs.add(m.group(2))
            continue
        if in_block:
            if line.startswith("- ") or line.startswith("  "):
                for m in BOLD_REF_RE.finditer(line):
                    if m.group(1) in valid_prefixes:
                        refs.add(m.group(2))
                for m in CROSS_REF_RE.finditer(line):
                    if m.group(1) in valid_prefixes:
                        refs.add(m.group(2))
            elif line.strip() and not line.startswith("-"):
                in_block = False
    return refs


def extract_calls(content, valid_prefixes):
    """Extract outgoing skill refs from the Integration Calls block."""
    return _extract_refs_from_block(content, CALLS_HEADER_RE, valid_prefixes)


def extract_called_by(content, valid_prefixes):
    """Extract incoming skill refs from the Integration Called by block."""
    return _extract_refs_from_block(content, CALLED_BY_HEADER_RE, valid_prefixes)


def extract_all_refs(content, valid_prefixes):
    """Extract all backtick `prefix:skill` refs from the full document."""
    refs = set()
    for m in CROSS_REF_RE.finditer(content):
        if m.group(1) in valid_prefixes:
            refs.add(m.group(2))
    return refs


# ---------------------------------------------------------------------------
# Cycle detection
# ---------------------------------------------------------------------------

def get_declared_cycle_sets(content):
    """Return all declared cycle sets from a skill's content."""
    result = []
    for m in CYCLE_DECL_RE.finditer(content):
        result.append(set(m.group(1).split(",")))
    return result


def find_minimal_cycles(graph):
    """Find shortest elementary cycles (no redundant sub-paths)."""
    seen_cycle_sets = set()
    cycles = []
    for start in sorted(graph):
        for neighbor in graph.get(start, set()):
            queue = deque([(neighbor, [start, neighbor])])
            visited_in_search = {start, neighbor}
            while queue:
                node, path = queue.popleft()
                for nxt in graph.get(node, set()):
                    if nxt == start:
                        canon = tuple(sorted(path))
                        if canon not in seen_cycle_sets:
                            seen_cycle_sets.add(canon)
                            cycles.append(tuple(path))
                        break
                    if nxt not in visited_in_search and nxt in graph:
                        visited_in_search.add(nxt)
                        queue.append((nxt, path + [nxt]))
                else:
                    continue
                break
    return cycles


# ---------------------------------------------------------------------------
# Artifact extraction
# ---------------------------------------------------------------------------

def extract_artifact_ids(content, section_name, exclude_prefixes):
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
            for m in ARTIFACT_ID_RE.finditer(line):
                candidate = m.group(1)
                if candidate not in exclude_prefixes and ":" not in candidate:
                    ids.add(candidate)
    return ids


# ---------------------------------------------------------------------------
# Graph analysis (W1-W5) — workflow DAG checks
#
# Accepts parsed_skills from _parsing.parse_all_skills() and emits findings
# with canonical W1-W5 check IDs directly (no G-to-W remapping).
# ---------------------------------------------------------------------------

def generate_mermaid(graph, skill_layers=None):
    """Generate a Mermaid flowchart from the skill dependency graph.

    Args:
        graph: Dict mapping skill names to sets of outgoing skill refs.
        skill_layers: Optional dict mapping skill names to layer labels
            (e.g. "hub" / "spoke") for subgraph grouping.

    Returns:
        Mermaid diagram source as a string.
    """
    lines = ["graph LR"]

    if skill_layers:
        by_layer = {}
        for sname, layer in skill_layers.items():
            by_layer.setdefault(layer, []).append(sname)
        for layer, members in sorted(by_layer.items()):
            safe_id = layer.replace(" ", "_").replace("-", "_")
            lines.append(f"    subgraph {safe_id} [{layer}]")
            for sname in sorted(members):
                lines.append(f"        {sname}")
            lines.append("    end")

    for src in sorted(graph):
        for tgt in sorted(graph[src]):
            lines.append(f"    {src} --> {tgt}")

    return "\n".join(lines)


def run_graph_analysis(parsed_skills):
    """Run W1-W5 graph checks on the workflow DAG.

    Args:
        parsed_skills: Dict returned by _parsing.parse_all_skills().

    Returns:
        Tuple of (findings, graph) where findings is a list of finding dicts
        with check IDs W1-W5, and graph is the adjacency dict mapping skill
        names to sets of outgoing refs.
    """
    skills = parsed_skills["skills"]
    valid_prefixes = parsed_skills["valid_prefixes"]
    skills_dir = parsed_skills["skills_dir"]

    if len(skills) < 2:
        return []

    findings = []

    graph = {}
    skill_contents = {}
    for sname, sdata in skills.items():
        content = sdata["content"]
        if not content:
            continue
        skill_contents[sname] = content
        refs = extract_calls(content, valid_prefixes)
        refs.discard(sname)
        existing_refs = {r for r in refs if r in skills}
        graph[sname] = existing_refs

    all_skill_names = set(graph.keys())

    # W1: Cycle detection
    for cycle in find_minimal_cycles(graph):
        cycle_set = set(cycle)
        declared = True
        for node in cycle_set:
            content = skill_contents.get(node, "")
            decl_sets = get_declared_cycle_sets(content)
            if any(cycle_set.issubset(ds) for ds in decl_sets):
                continue
            declared = False
            break
        sev = "info" if declared else "warning"
        chain = " -> ".join(cycle) + " -> " + cycle[0]
        msg = f"Circular dependency: {chain}"
        if declared:
            msg += " (declared feedback loop)"
        findings.append(dict(check="W1", severity=sev, message=msg))

    # W2: Reachability from entry points
    entry_points = set()
    for sname, content in skill_contents.items():
        if sname.startswith("using-"):
            for ref in extract_all_refs(content, valid_prefixes):
                if ref in all_skill_names:
                    entry_points.add(ref)
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
            findings.append(dict(
                check="W2", severity="info",
                message=f"Skill '{sname}' is not reachable from any "
                        "entry point (add to bootstrap routing or declare "
                        "'Called by: user directly' in Integration)"))

    # W3: Terminal skills (no outgoing edges) without Outputs section
    for sname in sorted(all_skill_names):
        if not graph.get(sname):
            content = skill_contents.get(sname, "")
            if "## Outputs" not in content and not sname.startswith("using-"):
                findings.append(dict(
                    check="W3", severity="info",
                    message=f"Terminal skill '{sname}' has no outgoing "
                            "references and no ## Outputs section"))

    # W4: Skills with incoming edges but no Inputs section
    has_incoming = set()
    for sname, refs in graph.items():
        has_incoming.update(refs)
    for sname in sorted(has_incoming):
        content = skill_contents.get(sname, "")
        if "## Inputs" not in content:
            findings.append(dict(
                check="W4", severity="info",
                message=f"Skill '{sname}' is referenced by other skills "
                        "but has no ## Inputs section"))

    # W5: Artifact identifier matching (experimental)
    skill_outputs = {}
    skill_inputs = {}
    for sname, content in skill_contents.items():
        skill_outputs[sname] = extract_artifact_ids(
            content, "Outputs", valid_prefixes)
        skill_inputs[sname] = extract_artifact_ids(
            content, "Inputs", valid_prefixes)

    for src, targets in graph.items():
        src_out = skill_outputs.get(src, set())
        if not src_out:
            continue
        for tgt in targets:
            tgt_in = skill_inputs.get(tgt, set())
            if not tgt_in:
                continue
            if not src_out & tgt_in:
                findings.append(dict(
                    check="W5", severity="info",
                    message=f"No matching artifact IDs between "
                            f"'{src}' outputs {sorted(src_out)} and "
                            f"'{tgt}' inputs {sorted(tgt_in)}"))

    return findings, graph
