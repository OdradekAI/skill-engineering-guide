"""Workflow graph analysis for bundle-plugin skill dependencies (G1-G5)."""

import re
from collections import deque

CALLS_HEADER_RE = re.compile(r"\*\*Calls?:?\*\*", re.IGNORECASE)
BOLD_REF_RE = re.compile(r"\*\*([a-z0-9-]+):([a-z0-9-]+)\*\*")
CROSS_REF_RE = re.compile(r"`([a-z0-9-]+):([a-z0-9-]+)`")
CYCLE_DECL_RE = re.compile(r"<!--\s*cycle:([\w,-]+)\s*-->")
ARTIFACT_ID_RE = re.compile(r"`([a-z][a-z0-9-]*)`")


def extract_calls(content, valid_prefixes):
    """Extract outgoing skill refs from the Integration Calls block."""
    calls = set()
    lines = content.splitlines()
    in_calls = False
    for line in lines:
        if CALLS_HEADER_RE.search(line):
            in_calls = True
            for m in BOLD_REF_RE.finditer(line):
                if m.group(1) in valid_prefixes:
                    calls.add(m.group(2))
            for m in CROSS_REF_RE.finditer(line):
                if m.group(1) in valid_prefixes:
                    calls.add(m.group(2))
            continue
        if in_calls:
            if line.startswith("- ") or line.startswith("  "):
                for m in BOLD_REF_RE.finditer(line):
                    if m.group(1) in valid_prefixes:
                        calls.add(m.group(2))
                for m in CROSS_REF_RE.finditer(line):
                    if m.group(1) in valid_prefixes:
                        calls.add(m.group(2))
            elif line.strip() and not line.startswith("-"):
                in_calls = False
    return calls


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
