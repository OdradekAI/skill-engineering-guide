#!/usr/bin/env python3
"""
Static workflow chain tests — verify the live project's workflow integrity.

Unlike test_graph_fixtures.py (which tests detection logic using synthetic
fixtures), these tests validate the actual bundles-forge skill graph:
dependency symmetry, node connectivity, and artifact matching.

Run: python tests/test_workflow_chains.py -v
Or:  python -m pytest tests/test_workflow_chains.py -v
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT / "skills" / "auditing" / "scripts"))

from _parsing import parse_all_skills
from _graph import (
    extract_calls,
    extract_called_by,
    run_graph_analysis,
)


class TestLiveGraphIntegrity(unittest.TestCase):
    """Run W1-W5 checks on the live project and assert zero warnings."""

    def setUp(self):
        self.parsed = parse_all_skills(REPO_ROOT)
        self.findings, self.graph = run_graph_analysis(self.parsed)

    def test_no_undeclared_cycles(self):
        w1_warnings = [f for f in self.findings
                       if f["check"] == "W1" and f["severity"] == "warning"]
        self.assertEqual(
            len(w1_warnings), 0,
            f"Undeclared circular dependencies: "
            f"{[f['message'] for f in w1_warnings]}"
        )

    def test_all_skills_reachable(self):
        w2 = [f for f in self.findings if f["check"] == "W2"]
        self.assertEqual(
            len(w2), 0,
            f"Unreachable skills: {[f['message'] for f in w2]}"
        )

    def test_terminal_skills_have_outputs(self):
        w3 = [f for f in self.findings if f["check"] == "W3"]
        self.assertEqual(
            len(w3), 0,
            f"Terminal skills without Outputs: {[f['message'] for f in w3]}"
        )

    def test_referenced_skills_have_inputs(self):
        w4 = [f for f in self.findings if f["check"] == "W4"]
        self.assertEqual(
            len(w4), 0,
            f"Referenced skills without Inputs: {[f['message'] for f in w4]}"
        )


class TestCallsCalledBySymmetry(unittest.TestCase):
    """Verify Calls/Called-by declarations are symmetric across all skills."""

    def setUp(self):
        self.parsed = parse_all_skills(REPO_ROOT)
        self.prefixes = self.parsed["valid_prefixes"]
        self.skills = self.parsed["skills"]

    def _build_maps(self):
        calls_map = {}
        called_by_map = {}
        for name, data in self.skills.items():
            content = data["content"]
            if not content:
                continue
            calls_map[name] = extract_calls(content, self.prefixes)
            called_by_map[name] = extract_called_by(content, self.prefixes)
        return calls_map, called_by_map

    def test_every_call_has_called_by(self):
        calls_map, called_by_map = self._build_maps()
        missing = []
        for caller, callees in calls_map.items():
            for callee in callees:
                if callee not in called_by_map:
                    continue
                if caller not in called_by_map[callee]:
                    missing.append(f"{caller} -> {callee}")
        self.assertEqual(
            missing, [],
            f"Calls without matching Called-by: {missing}"
        )

    def test_every_called_by_has_call(self):
        calls_map, called_by_map = self._build_maps()
        missing = []
        for callee, callers in called_by_map.items():
            for caller in callers:
                if caller not in calls_map:
                    continue
                if callee not in calls_map[caller]:
                    missing.append(f"{callee} <- {caller}")
        self.assertEqual(
            missing, [],
            f"Called-by without matching Calls: {missing}"
        )


class TestGraphConnectivity(unittest.TestCase):
    """Verify the dependency graph has expected connectivity properties."""

    def setUp(self):
        self.parsed = parse_all_skills(REPO_ROOT)
        _, self.graph = run_graph_analysis(self.parsed)
        self.all_nodes = set(self.graph.keys())

    def _incoming(self):
        inc = {n: set() for n in self.all_nodes}
        for src, tgts in self.graph.items():
            for tgt in tgts:
                if tgt in inc:
                    inc[tgt].add(src)
        return inc

    def test_no_isolated_non_meta_skills(self):
        """Every non-meta skill has at least one connection (in or out)."""
        incoming = self._incoming()
        for name in self.all_nodes:
            if name.startswith("using-"):
                continue
            has_outgoing = len(self.graph.get(name, set())) > 0
            has_incoming = len(incoming.get(name, set())) > 0
            self.assertTrue(
                has_outgoing or has_incoming,
                f"Skill '{name}' is isolated (no calls in/out)"
            )

    def test_orchestrators_have_outgoing(self):
        """Orchestrator skills (hub) should have outgoing calls."""
        orchestrators = ["blueprinting", "optimizing", "releasing"]
        for name in orchestrators:
            if name not in self.graph:
                continue
            self.assertGreater(
                len(self.graph[name]), 0,
                f"Orchestrator '{name}' has no outgoing calls"
            )

    def test_executors_have_incoming(self):
        """Executor skills (spoke) should have incoming calls."""
        executors = ["scaffolding", "authoring", "auditing", "testing"]
        incoming = self._incoming()
        for name in executors:
            if name not in incoming:
                continue
            self.assertGreater(
                len(incoming[name]), 0,
                f"Executor '{name}' has no incoming calls"
            )


if __name__ == "__main__":
    unittest.main()
