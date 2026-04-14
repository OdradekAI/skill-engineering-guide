#!/usr/bin/env python3
"""Tests for W1-W4 graph analysis detection logic using isolated fixtures.

Unlike TestGraphRules in test_scripts.py (which validates the live repo has
no problems), these tests verify the detection logic itself using synthetic
skill structures with intentional violations.
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
FIXTURES_DIR = Path(__file__).resolve().parent / "fixtures"
AUDITING_SCRIPTS = REPO_ROOT / "skills" / "auditing" / "scripts"

sys.path.insert(0, str(AUDITING_SCRIPTS))

import _graph
from _parsing import parse_all_skills


class TestW1CircularDependencies(unittest.TestCase):
    """W1: Undeclared circular dependencies should be detected."""

    def setUp(self):
        self.parsed = parse_all_skills(FIXTURES_DIR / "circular-deps")

    def test_cycle_detected(self):
        findings = _graph.run_graph_analysis(self.parsed)
        w1 = [f for f in findings if f["check"] == "W1"]
        self.assertGreater(len(w1), 0,
                           "Expected at least one W1 cycle finding")

    def test_undeclared_cycle_is_warning(self):
        findings = _graph.run_graph_analysis(self.parsed)
        w1_warnings = [f for f in findings
                       if f["check"] == "W1" and f["severity"] == "warning"]
        self.assertGreater(len(w1_warnings), 0,
                           "Undeclared cycle should produce a warning")

    def test_cycle_message_contains_skill_names(self):
        findings = _graph.run_graph_analysis(self.parsed)
        w1 = [f for f in findings if f["check"] == "W1"]
        msg = w1[0]["message"]
        self.assertIn("skill-a", msg)
        self.assertIn("skill-b", msg)
        self.assertIn("skill-c", msg)


class TestW2Unreachable(unittest.TestCase):
    """W2: Skills not reachable from entry points should be detected."""

    def setUp(self):
        self.parsed = parse_all_skills(FIXTURES_DIR / "unreachable")

    def test_orphan_skill_detected(self):
        findings = _graph.run_graph_analysis(self.parsed)
        w2 = [f for f in findings if f["check"] == "W2"]
        orphan_findings = [f for f in w2 if "skill-orphan" in f["message"]]
        self.assertGreater(len(orphan_findings), 0,
                           "Expected W2 finding for unreachable 'skill-orphan'")

    def test_reachable_skill_not_flagged(self):
        findings = _graph.run_graph_analysis(self.parsed)
        w2 = [f for f in findings if f["check"] == "W2"]
        w2_messages = " ".join(f["message"] for f in w2)
        self.assertNotIn("skill-a", w2_messages,
                         "skill-a is reachable and should not be flagged")
        self.assertNotIn("skill-b", w2_messages,
                         "skill-b is reachable via skill-a and should not be flagged")


class TestW3TerminalWithoutOutputs(unittest.TestCase):
    """W3: Terminal skills (no outgoing refs) without Outputs section."""

    def setUp(self):
        self.parsed = parse_all_skills(FIXTURES_DIR / "missing-sections")

    def test_terminal_skill_without_outputs_detected(self):
        findings = _graph.run_graph_analysis(self.parsed)
        w3 = [f for f in findings if f["check"] == "W3"]
        w3_for_b = [f for f in w3 if "skill-b" in f["message"]]
        self.assertGreater(len(w3_for_b), 0,
                           "Terminal skill-b has no Outputs section — "
                           "expected W3 finding")

    def test_skill_with_outputs_not_flagged(self):
        findings = _graph.run_graph_analysis(self.parsed)
        w3 = [f for f in findings if f["check"] == "W3"]
        w3_messages = " ".join(f["message"] for f in w3)
        self.assertNotIn("skill-a", w3_messages,
                         "skill-a has outgoing refs, should not be flagged")


class TestW4IncomingWithoutInputs(unittest.TestCase):
    """W4: Skills with incoming refs but no Inputs section."""

    def setUp(self):
        self.parsed = parse_all_skills(FIXTURES_DIR / "missing-sections")

    def test_referenced_skill_without_inputs_detected(self):
        findings = _graph.run_graph_analysis(self.parsed)
        w4 = [f for f in findings if f["check"] == "W4"]
        w4_for_b = [f for f in w4 if "skill-b" in f["message"]]
        self.assertGreater(len(w4_for_b), 0,
                           "skill-b is referenced by skill-a but has no "
                           "Inputs section — expected W4 finding")


if __name__ == "__main__":
    unittest.main()
