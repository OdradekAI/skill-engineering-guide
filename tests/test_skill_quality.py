#!/usr/bin/env python3
"""
Skill content quality tests — deterministic checks on SKILL.md content.

Covers: description format/length, cross-reference resolution, and
Integration section symmetry (Calls/Called-by).

Run: python tests/test_skill_quality.py -v
Or:  python -m pytest tests/test_skill_quality.py -v
"""

import re
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "auditing" / "scripts"))
from _parsing import parse_frontmatter, parse_all_skills

SKILLS_DIR = REPO_ROOT / "skills"

EXPECTED_SKILLS = [
    "authoring",
    "auditing",
    "blueprinting",
    "optimizing",
    "releasing",
    "scaffolding",
    "testing",
    "using-bundles-forge",
]

_XREF_RE = re.compile(r"bundles-forge:([\w-]+)")
_CALLS_RE = re.compile(
    r"\*\*bundles-forge:([\w-]+)\*\*", re.MULTILINE
)


def _parse_integration(body):
    """Extract Calls and Called-by skill names from an Integration section.

    Returns (set_of_calls, set_of_called_by).
    """
    calls = set()
    called_by = set()

    section_match = re.search(r"^## Integration\s*$", body, re.MULTILINE)
    if not section_match:
        return calls, called_by

    section_text = body[section_match.end():]
    next_h2 = re.search(r"^## ", section_text, re.MULTILINE)
    if next_h2:
        section_text = section_text[:next_h2.start()]

    current_label = None
    for line in section_text.split("\n"):
        stripped = line.strip()
        if stripped.startswith("**Calls:**"):
            current_label = "calls"
        elif stripped.startswith("**Called by:**"):
            current_label = "called_by"
        elif stripped.startswith("**Pairs with:**"):
            current_label = "pairs"
        elif stripped.startswith("- **bundles-forge:"):
            ref_match = _CALLS_RE.search(stripped)
            if ref_match and current_label == "calls":
                calls.add(ref_match.group(1))
            elif ref_match and current_label == "called_by":
                called_by.add(ref_match.group(1))

    return calls, called_by


class TestDescriptionFormat(unittest.TestCase):
    """Verify skill descriptions follow project conventions."""

    def setUp(self):
        self.parsed = parse_all_skills(REPO_ROOT)

    def test_descriptions_start_with_use_when(self):
        for name, data in self.parsed["skills"].items():
            fm = data["frontmatter"]
            if fm is None:
                continue
            desc = fm.get("description", "")
            self.assertTrue(
                desc.startswith("Use when"),
                f"{name}: description must start with 'Use when', "
                f"got: {desc[:60]!r}..."
            )

    def test_descriptions_under_250_characters(self):
        for name, data in self.parsed["skills"].items():
            fm = data["frontmatter"]
            if fm is None:
                continue
            desc = fm.get("description", "")
            self.assertLessEqual(
                len(desc), 250,
                f"{name}: description is {len(desc)} chars (max 250)"
            )


class TestCrossReferences(unittest.TestCase):
    """Verify bundles-forge:<name> cross-references resolve to existing skills."""

    def setUp(self):
        self.parsed = parse_all_skills(REPO_ROOT)
        self.existing = set(self.parsed["skills"].keys())

    def test_all_cross_references_resolve(self):
        for name, data in self.parsed["skills"].items():
            body = data["body"]
            refs = _XREF_RE.findall(body)
            for ref in refs:
                self.assertIn(
                    ref, self.existing,
                    f"{name}/SKILL.md references bundles-forge:{ref} "
                    f"but skills/{ref}/ does not exist"
                )


class TestIntegrationSymmetry(unittest.TestCase):
    """Verify Calls/Called-by declarations are symmetric across skills.

    If skill A declares Calls: B, then B must declare Called-by: A.
    """

    def setUp(self):
        self.parsed = parse_all_skills(REPO_ROOT)
        self.graph = {}
        for name, data in self.parsed["skills"].items():
            body = data["body"]
            calls, called_by = _parse_integration(body)
            self.graph[name] = {"calls": calls, "called_by": called_by}

    def test_calls_have_matching_called_by(self):
        for caller, edges in self.graph.items():
            for callee in edges["calls"]:
                if callee not in self.graph:
                    continue
                self.assertIn(
                    caller, self.graph[callee]["called_by"],
                    f"{caller} declares Calls: {callee}, but {callee} "
                    f"does not list {caller} in Called by"
                )

    def test_called_by_have_matching_calls(self):
        for callee, edges in self.graph.items():
            for caller in edges["called_by"]:
                if caller not in self.graph:
                    continue
                self.assertIn(
                    callee, self.graph[caller]["calls"],
                    f"{callee} declares Called by: {caller}, but {caller} "
                    f"does not list {callee} in Calls"
                )


if __name__ == "__main__":
    unittest.main()
