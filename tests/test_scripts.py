#!/usr/bin/env python3
"""
Cross-platform tests for the Python scripts in scripts/.

Run: python tests/test_scripts.py
Or:  python -m pytest tests/test_scripts.py -v
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPTS_DIR = REPO_ROOT / "scripts"


class TestLintSkills(unittest.TestCase):
    """Tests for scripts/lint-skills.py"""

    def test_lint_runs_without_error(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "lint-skills.py"), str(REPO_ROOT)],
            capture_output=True, text=True
        )
        self.assertIn("Skill Quality Lint", result.stdout)

    def test_lint_json_output(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "lint-skills.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        self.assertIn("skills", data)
        self.assertIn("summary", data)
        self.assertIsInstance(data["skills"], list)
        self.assertGreater(len(data["skills"]), 0)

    def test_lint_finds_expected_skills(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "lint-skills.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        skill_names = {s["skill"] for s in data["skills"]}
        expected = {"designing", "scaffolding", "auditing", "optimizing",
                    "releasing", "adapting-platforms", "writing-skill",
                    "using-bundles-forge"}
        self.assertTrue(expected.issubset(skill_names),
                        f"Missing skills: {expected - skill_names}")

    def test_lint_no_deleted_skills(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "lint-skills.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        skill_names = {s["skill"] for s in data["skills"]}
        removed = {"scanning-security", "iterating-feedback", "managing-versions"}
        self.assertTrue(removed.isdisjoint(skill_names),
                        f"Deleted skills still present: {removed & skill_names}")


class TestScanSecurity(unittest.TestCase):
    """Tests for scripts/scan-security.py"""

    def test_scan_runs_without_crash(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "scan-security.py"), str(REPO_ROOT)],
            capture_output=True, text=True
        )
        self.assertIn("Security Scan", result.stdout)

    def test_scan_json_output(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "scan-security.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        self.assertIn("files", data)
        self.assertIn("summary", data)
        self.assertIsInstance(data["files"], list)

    def test_scan_classifies_file_types(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "scan-security.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        types_found = {f["type"] for f in data["files"]}
        self.assertIn("hook_script", types_found)
        self.assertIn("skill_content", types_found)


class TestAuditProject(unittest.TestCase):
    """Tests for scripts/audit-project.py"""

    def test_audit_runs_without_crash(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "audit-project.py"), str(REPO_ROOT)],
            capture_output=True, text=True
        )
        self.assertIn("Bundle-Plugin Audit", result.stdout)

    def test_audit_json_output(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "audit-project.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        self.assertIn("categories", data)
        self.assertIn("overall_score", data)
        self.assertIn("scores", data)

    def test_audit_has_all_categories(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "audit-project.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        expected_cats = {"structure", "manifests", "version_sync",
                         "skill_quality", "hooks", "documentation", "security"}
        actual_cats = set(data["categories"].keys())
        self.assertTrue(expected_cats.issubset(actual_cats),
                        f"Missing categories: {expected_cats - actual_cats}")

    def test_audit_score_range(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "audit-project.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        self.assertGreaterEqual(data["overall_score"], 0)
        self.assertLessEqual(data["overall_score"], 10)


class TestCrossReferences(unittest.TestCase):
    """Verify cross-references resolve to existing skills."""

    def test_no_broken_crossrefs(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "lint-skills.py"), "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        broken = []
        for skill in data["skills"]:
            for finding in skill["findings"]:
                if finding["check"] == "X1":
                    broken.append(f"{skill['skill']}: {finding['message']}")
        self.assertEqual(broken, [], f"Broken cross-references:\n" + "\n".join(broken))


if __name__ == "__main__":
    unittest.main()
