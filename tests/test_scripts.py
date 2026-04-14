#!/usr/bin/env python3
"""
Tests for the auditing and releasing scripts in skills/auditing/scripts/
and skills/releasing/scripts/.

Run: python tests/test_scripts.py
Or:  python -m pytest tests/test_scripts.py -v
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUDITING_SCRIPTS = REPO_ROOT / "skills" / "auditing" / "scripts"


class TestAuditSkillProjectMode(unittest.TestCase):
    """Tests for skills/auditing/scripts/audit_skill.py in project-level mode."""

    def _run_project(self, *extra_args):
        return subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_skill.py"),
             "--all", *extra_args, str(REPO_ROOT)],
            capture_output=True, text=True
        )

    def test_project_mode_runs_without_error(self):
        result = self._run_project()
        self.assertIn("Skill Quality Audit", result.stdout)

    def test_project_mode_autodetect(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_skill.py"), str(REPO_ROOT)],
            capture_output=True, text=True
        )
        self.assertIn("Skill Quality Audit", result.stdout)

    def test_project_mode_json_output(self):
        result = self._run_project("--json")
        data = json.loads(result.stdout)
        self.assertIn("skills", data)
        self.assertIn("summary", data)
        self.assertIsInstance(data["skills"], list)
        self.assertGreater(len(data["skills"]), 0)

    def test_project_mode_finds_expected_skills(self):
        result = self._run_project("--json")
        data = json.loads(result.stdout)
        skill_names = {s["skill"] for s in data["skills"]}
        expected = {"blueprinting", "scaffolding", "authoring", "auditing",
                    "optimizing", "releasing",
                    "using-bundles-forge"}
        self.assertTrue(expected.issubset(skill_names),
                        f"Missing skills: {expected - skill_names}")

    def test_project_mode_no_deleted_skills(self):
        result = self._run_project("--json")
        data = json.loads(result.stdout)
        skill_names = {s["skill"] for s in data["skills"]}
        removed = {"scanning-security", "iterating-feedback", "managing-versions"}
        self.assertTrue(removed.isdisjoint(skill_names),
                        f"Deleted skills still present: {removed & skill_names}")


class TestAuditSecurity(unittest.TestCase):
    """Tests for skills/auditing/scripts/audit_security.py"""

    def test_scan_runs_without_crash(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_security.py"), str(REPO_ROOT)],
            capture_output=True, text=True
        )
        self.assertIn("Security Scan", result.stdout)

    def test_scan_json_output(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_security.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        self.assertIn("files", data)
        self.assertIn("summary", data)
        self.assertIsInstance(data["files"], list)

    def test_scan_classifies_file_types(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_security.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        types_found = {f["type"] for f in data["files"]}
        self.assertIn("hook_script", types_found)
        self.assertIn("skill_content", types_found)

    def test_findings_have_confidence(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_security.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        all_findings = [f for fr in data["files"] for f in fr["findings"]]
        for f in all_findings:
            self.assertIn(f.get("confidence"), ("deterministic", "suspicious"),
                          f"Finding {f.get('check_id')} missing valid confidence")

    def test_suspicious_findings_affect_exit_code(self):
        """Suspicious findings should affect exit code (at least exit 1)."""
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_security.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        s = data["summary"]
        has_suspicious = (s.get("suspicious_critical", 0) > 0
                          or s.get("suspicious_warning", 0) > 0)
        if has_suspicious:
            self.assertGreater(result.returncode, 0,
                               "Suspicious findings should cause non-zero exit")

    def test_summary_has_suspicious_counts(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_security.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        s = data["summary"]
        self.assertIn("suspicious_critical", s)
        self.assertIn("suspicious_warning", s)


class TestAuditPlugin(unittest.TestCase):
    """Tests for skills/auditing/scripts/audit_plugin.py"""

    def test_audit_runs_without_crash(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_plugin.py"), str(REPO_ROOT)],
            capture_output=True, text=True
        )
        self.assertIn("Bundle-Plugin Audit", result.stdout)

    def test_audit_json_output(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_plugin.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        self.assertIn("categories", data)
        self.assertIn("status", data)
        self.assertIn(data["status"], ("PASS", "WARN", "FAIL"))

    def test_audit_has_all_categories(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_plugin.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        expected_cats = {"structure", "manifests", "version_sync",
                         "skill_quality", "cross_references", "hooks",
                         "documentation", "security"}
        actual_cats = set(data["categories"].keys())
        self.assertTrue(expected_cats.issubset(actual_cats),
                        f"Missing categories: {expected_cats - actual_cats}")


class TestGraphRules(unittest.TestCase):
    """Tests for G1-G4 graph analysis rules in audit_skill.py."""

    def _get_lint_data(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_skill.py"),
             "--all", "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        return json.loads(result.stdout)

    def test_lint_json_has_graph_key(self):
        """lint --json output includes 'graph' key when >=2 skills."""
        data = self._get_lint_data()
        self.assertIn("graph", data,
                       "lint JSON output missing 'graph' key")
        self.assertIsInstance(data["graph"], list)

    def test_no_undeclared_circular_dependencies(self):
        """G1: no undeclared circular dependency findings (warning level)."""
        data = self._get_lint_data()
        undeclared_cycles = [
            f for f in data["graph"]
            if f["check"] == "G1" and f["severity"] == "warning"
        ]
        self.assertEqual(undeclared_cycles, [],
                         f"Undeclared circular dependencies:\n"
                         + "\n".join(f["message"] for f in undeclared_cycles))

    def test_all_skills_reachable(self):
        """G2: all skills reachable from using-* entry points or declared direct-call."""
        data = self._get_lint_data()
        unreachable = [
            f for f in data["graph"]
            if f["check"] == "G2"
        ]
        self.assertEqual(unreachable, [],
                         f"Unreachable skills:\n"
                         + "\n".join(f["message"] for f in unreachable))

    def test_terminal_skills_have_outputs(self):
        """G3: terminal skills have ## Outputs section."""
        data = self._get_lint_data()
        missing_outputs = [
            f for f in data["graph"]
            if f["check"] == "G3"
        ]
        self.assertEqual(missing_outputs, [],
                         f"Terminal skills without Outputs:\n"
                         + "\n".join(f["message"] for f in missing_outputs))

    def test_referenced_skills_have_inputs(self):
        """G4: skills with incoming refs have ## Inputs section."""
        data = self._get_lint_data()
        missing_inputs = [
            f for f in data["graph"]
            if f["check"] == "G4"
        ]
        self.assertEqual(missing_inputs, [],
                         f"Referenced skills without Inputs:\n"
                         + "\n".join(f["message"] for f in missing_inputs))


class TestArtifactMatching(unittest.TestCase):
    """Tests for G5 artifact identifier matching."""

    def test_g5_no_critical_mismatches(self):
        """G5: workflow edges have matching artifact IDs (info level only)."""
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_skill.py"),
             "--all", "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        g5_findings = [
            f for f in data.get("graph", [])
            if f["check"] == "G5"
        ]
        for f in g5_findings:
            self.assertEqual(f["severity"], "info",
                             f"G5 should be info-level: {f['message']}")


class TestCrossReferences(unittest.TestCase):
    """Verify cross-references resolve to existing skills."""

    def test_no_broken_crossrefs(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_skill.py"),
             "--all", "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        broken = []
        for skill in data["skills"]:
            for finding in skill["findings"]:
                if finding["check"] == "X1":
                    broken.append(f"{skill['skill']}: {finding['message']}")
        self.assertEqual(broken, [], f"Broken cross-references:\n" + "\n".join(broken))


class TestAuditDocs(unittest.TestCase):
    """Tests for skills/auditing/scripts/audit_docs.py (D1-D9)."""

    def test_audit_docs_runs_without_crash(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_docs.py"), str(REPO_ROOT)],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0,
                         f"audit_docs.py failed:\n{result.stdout}\n{result.stderr}")

    def test_audit_docs_json_output(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_docs.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        self.assertIn("findings", data)
        self.assertIn("summary", data)
        self.assertIsInstance(data["findings"], list)

    def test_audit_docs_summary_has_severity_counts(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_docs.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        s = data["summary"]
        for key in ("critical", "warning", "info"):
            self.assertIn(key, s, f"summary missing '{key}' count")


class TestAuditWorkflow(unittest.TestCase):
    """Tests for skills/auditing/scripts/audit_workflow.py (W1-W11)."""

    def test_workflow_audit_runs_without_crash(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_workflow.py"), str(REPO_ROOT)],
            capture_output=True, text=True
        )
        self.assertIn("Workflow", result.stdout)

    def test_workflow_audit_json_output(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_workflow.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        self.assertIn("status", data)
        self.assertIn("layers", data)
        self.assertIn(data["status"], ("PASS", "WARN", "FAIL"))

    def test_workflow_audit_has_three_layers(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_workflow.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        for layer in ("static", "semantic", "behavioral"):
            self.assertIn(layer, data["layers"],
                          f"Missing layer '{layer}' in workflow audit")


class TestGenerateChecklists(unittest.TestCase):
    """Tests for skills/auditing/scripts/generate_checklists.py."""

    def test_checklists_in_sync(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "generate_checklists.py"),
             "--check", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0,
                         f"Checklist drift detected:\n{result.stdout}\n{result.stderr}")


if __name__ == "__main__":
    unittest.main()
