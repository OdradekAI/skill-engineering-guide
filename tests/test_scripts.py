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


class TestOutputDir(unittest.TestCase):
    """Tests for --output-dir support across audit scripts."""

    def test_output_dir_writes_json(self):
        """--output-dir + --json writes a JSON file to the specified directory."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [sys.executable, str(AUDITING_SCRIPTS / "audit_plugin.py"),
                 "--json", "--output-dir", tmpdir, str(REPO_ROOT)],
                capture_output=True, text=True
            )
            files = list(Path(tmpdir).glob("audit_plugin-*.json"))
            self.assertEqual(len(files), 1,
                             f"Expected 1 JSON file, found {len(files)} in {tmpdir}")
            data = json.loads(files[0].read_text(encoding="utf-8"))
            self.assertIn("categories", data)

    def test_output_dir_creates_directory(self):
        """--output-dir auto-creates the directory if it doesn't exist."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            nested = Path(tmpdir) / "nonexistent" / "subdir"
            result = subprocess.run(
                [sys.executable, str(AUDITING_SCRIPTS / "audit_plugin.py"),
                 "--json", "--output-dir", str(nested), str(REPO_ROOT)],
                capture_output=True, text=True
            )
            self.assertTrue(nested.is_dir(),
                            f"--output-dir should auto-create {nested}")
            files = list(nested.glob("audit_plugin-*.json"))
            self.assertEqual(len(files), 1)

    def test_output_dir_writes_markdown(self):
        """--output-dir without --json writes a Markdown file."""
        import tempfile
        with tempfile.TemporaryDirectory() as tmpdir:
            result = subprocess.run(
                [sys.executable, str(AUDITING_SCRIPTS / "audit_plugin.py"),
                 "--output-dir", tmpdir, str(REPO_ROOT)],
                capture_output=True, text=True
            )
            files = list(Path(tmpdir).glob("audit_plugin-*.md"))
            self.assertEqual(len(files), 1,
                             f"Expected 1 MD file, found {len(files)} in {tmpdir}")
            content = files[0].read_text(encoding="utf-8")
            self.assertIn("Bundle-Plugin Audit", content)


class TestGraphRules(unittest.TestCase):
    """Tests for W1-W4 graph analysis rules via _graph.run_graph_analysis."""

    def _get_graph_data(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_workflow.py"),
             "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        return [f for f in data.get("focus_findings", [])
                + data.get("context_findings", [])
                if f.get("layer") == "static"]

    def test_no_undeclared_circular_dependencies(self):
        """W1: no undeclared circular dependency findings (warning level)."""
        findings = self._get_graph_data()
        undeclared_cycles = [
            f for f in findings
            if f["check"] == "W1" and f["severity"] == "warning"
        ]
        self.assertEqual(undeclared_cycles, [],
                         f"Undeclared circular dependencies:\n"
                         + "\n".join(f["message"] for f in undeclared_cycles))

    def test_all_skills_reachable(self):
        """W2: all skills reachable from using-* entry points or declared direct-call."""
        findings = self._get_graph_data()
        unreachable = [
            f for f in findings
            if f["check"] == "W2"
        ]
        self.assertEqual(unreachable, [],
                         f"Unreachable skills:\n"
                         + "\n".join(f["message"] for f in unreachable))

    def test_terminal_skills_have_outputs(self):
        """W3: terminal skills have ## Outputs section."""
        findings = self._get_graph_data()
        missing_outputs = [
            f for f in findings
            if f["check"] == "W3"
        ]
        self.assertEqual(missing_outputs, [],
                         f"Terminal skills without Outputs:\n"
                         + "\n".join(f["message"] for f in missing_outputs))

    def test_referenced_skills_have_inputs(self):
        """W4: skills with incoming refs have ## Inputs section."""
        findings = self._get_graph_data()
        missing_inputs = [
            f for f in findings
            if f["check"] == "W4"
        ]
        self.assertEqual(missing_inputs, [],
                         f"Referenced skills without Inputs:\n"
                         + "\n".join(f["message"] for f in missing_inputs))


class TestArtifactMatching(unittest.TestCase):
    """Tests for W5 artifact identifier matching."""

    def test_w5_no_critical_mismatches(self):
        """W5: workflow edges have matching artifact IDs (info level only)."""
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_workflow.py"),
             "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        all_findings = (data.get("focus_findings", [])
                        + data.get("context_findings", []))
        w5_findings = [
            f for f in all_findings
            if f["check"] == "W5"
        ]
        for f in w5_findings:
            self.assertEqual(f["severity"], "info",
                             f"W5 should be info-level: {f['message']}")


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


class TestSecurityScannerRefinements(unittest.TestCase):
    """Tests for audit_security.py false-positive reduction (v1.7.0 fixes)."""

    @classmethod
    def setUpClass(cls):
        sys.path.insert(0, str(AUDITING_SCRIPTS))
        import audit_security
        cls.mod = audit_security

    def test_classify_file_skill_reference(self):
        """references/*.md classified as skill_reference, not skill_content."""
        from pathlib import PurePosixPath
        rel = PurePosixPath("skills/scaffolding/references/external-integration.md")
        self.assertEqual(self.mod.classify_file(rel), "skill_reference")

    def test_classify_file_skill_content_unchanged(self):
        """SKILL.md still classified as skill_content."""
        from pathlib import PurePosixPath
        rel = PurePosixPath("skills/scaffolding/SKILL.md")
        self.assertEqual(self.mod.classify_file(rel), "skill_content")

    def test_reference_sc1_downgraded_to_warning(self):
        """SC1 in SKILL_REFERENCE_RULES has risk=warning, not critical."""
        sc1_rules = [r for r in self.mod.SKILL_REFERENCE_RULES if r[0] == "SC1"]
        self.assertTrue(len(sc1_rules) > 0)
        for cid, risk, _pat, _desc, _conf in sc1_rules:
            self.assertEqual(risk, "warning",
                             f"SC1 in skill_reference should be warning, got {risk}")

    def test_reference_sc2_downgraded_to_warning(self):
        """SC2 in SKILL_REFERENCE_RULES has risk=warning, not critical."""
        sc2_rules = [r for r in self.mod.SKILL_REFERENCE_RULES if r[0] == "SC2"]
        self.assertTrue(len(sc2_rules) > 0)
        for cid, risk, _pat, _desc, _conf in sc2_rules:
            self.assertEqual(risk, "warning",
                             f"SC2 in skill_reference should be warning, got {risk}")

    def test_hk4_skips_without_network_imports(self):
        """HK4 does not fire when file has no network library imports."""
        import tempfile, os
        content = '#!/usr/bin/env python3\n"""Hook for the host IDE."""\nprint("ok")\n'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False,
                                         encoding="utf-8") as f:
            f.write(content)
            f.flush()
            tmp_path = Path(f.name)
        try:
            findings = self.mod.scan_file(tmp_path, Path("hooks/test.py"), "hook_script")
            hk4 = [f for f in findings if f["check_id"] == "HK4"]
            self.assertEqual(hk4, [], "HK4 should not fire without network imports")
        finally:
            os.unlink(tmp_path)

    def test_hk4_fires_with_network_imports(self):
        """HK4 fires when file has network imports and DNS command."""
        import tempfile, os
        content = '#!/usr/bin/env python3\nimport socket\nhost lookup\n'
        with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False,
                                         encoding="utf-8") as f:
            f.write(content)
            f.flush()
            tmp_path = Path(f.name)
        try:
            findings = self.mod.scan_file(tmp_path, Path("hooks/test.py"), "hook_script")
            hk4 = [f for f in findings if f["check_id"] == "HK4"]
            self.assertGreater(len(hk4), 0, "HK4 should fire with network imports present")
        finally:
            os.unlink(tmp_path)

    def test_sc12_skips_in_code_fence(self):
        """SC12 does not fire inside markdown code fences."""
        import tempfile, os
        content = (
            "---\nname: test\n---\n# Test\n"
            "```python\n"
            'tags = "<EXTREMELY_IMPORTANT>"\n'
            "```\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False,
                                         encoding="utf-8") as f:
            f.write(content)
            f.flush()
            tmp_path = Path(f.name)
        try:
            findings = self.mod.scan_file(tmp_path, Path("skills/test/SKILL.md"),
                                          "skill_content")
            sc12 = [f for f in findings if f["check_id"] == "SC12"]
            self.assertEqual(sc12, [], "SC12 should not fire inside code fences")
        finally:
            os.unlink(tmp_path)

    def test_sc12_skips_inline_backtick(self):
        """SC12 does not fire when wrapped in inline backticks."""
        import tempfile, os
        content = (
            "---\nname: test\n---\n# Test\n"
            "Wraps in `<EXTREMELY_IMPORTANT>` tags\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False,
                                         encoding="utf-8") as f:
            f.write(content)
            f.flush()
            tmp_path = Path(f.name)
        try:
            findings = self.mod.scan_file(tmp_path, Path("skills/test/SKILL.md"),
                                          "skill_content")
            sc12 = [f for f in findings if f["check_id"] == "SC12"]
            self.assertEqual(sc12, [], "SC12 should not fire for backtick-wrapped refs")
        finally:
            os.unlink(tmp_path)

    def test_sc12_fires_outside_code_fence(self):
        """SC12 still fires for bare EXTREMELY_IMPORTANT outside code fences."""
        import tempfile, os
        content = (
            "---\nname: test\n---\n# Test\n"
            "<EXTREMELY_IMPORTANT>\n"
        )
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False,
                                         encoding="utf-8") as f:
            f.write(content)
            f.flush()
            tmp_path = Path(f.name)
        try:
            findings = self.mod.scan_file(tmp_path, Path("skills/test/SKILL.md"),
                                          "skill_content")
            sc12 = [f for f in findings if f["check_id"] == "SC12"]
            self.assertGreater(len(sc12), 0,
                               "SC12 should fire for bare EXTREMELY_IMPORTANT")
        finally:
            os.unlink(tmp_path)


class TestBumpVersion(unittest.TestCase):
    """Tests for skills/releasing/scripts/bump_version.py modes."""

    BUMP_SCRIPT = REPO_ROOT / "skills" / "releasing" / "scripts" / "bump_version.py"

    def _run_bump(self, *args):
        return subprocess.run(
            [sys.executable, str(self.BUMP_SCRIPT), *args, str(REPO_ROOT)],
            capture_output=True, text=True
        )

    def test_check_mode_exits_zero_when_synced(self):
        result = self._run_bump("--check")
        self.assertEqual(result.returncode, 0,
                         f"--check should exit 0 when versions are in sync:\n"
                         f"{result.stdout}\n{result.stderr}")

    def test_audit_mode_runs(self):
        result = self._run_bump("--audit")
        self.assertIn(result.returncode, (0, 1),
                      f"--audit should exit 0 or 1:\n{result.stderr}")
        self.assertIn("version", result.stdout.lower(),
                      "--audit output should mention version")

    def test_dry_run_does_not_modify_files(self):
        import json
        pkg = REPO_ROOT / "package.json"
        before = json.loads(pkg.read_text(encoding="utf-8"))["version"]
        result = subprocess.run(
            [sys.executable, str(self.BUMP_SCRIPT), str(REPO_ROOT),
             "99.99.99", "--dry-run"],
            capture_output=True, text=True
        )
        after = json.loads(pkg.read_text(encoding="utf-8"))["version"]
        self.assertEqual(before, after,
                         "--dry-run should not modify package.json")
        self.assertIn("dry run", result.stdout.lower(),
                      "--dry-run output should mention dry run")

    def test_invalid_version_rejected(self):
        result = subprocess.run(
            [sys.executable, str(self.BUMP_SCRIPT), str(REPO_ROOT), "not-a-version"],
            capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0,
                            "Invalid version format should cause non-zero exit")


class TestWorkflowMermaidOutput(unittest.TestCase):
    """audit_workflow.py JSON output includes a mermaid field."""

    def test_json_has_mermaid_field(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_workflow.py"),
             "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        self.assertIn(result.returncode, (0, 1),
                      f"audit_workflow should exit 0 or 1:\n{result.stderr}")
        data = json.loads(result.stdout)
        self.assertIn("mermaid", data,
                      "JSON output should contain 'mermaid' field")
        self.assertIn("graph LR", data["mermaid"],
                      "Mermaid output should start with 'graph LR'")

    def test_mermaid_contains_edges(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_workflow.py"),
             "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        self.assertIn("-->", data["mermaid"],
                      "Mermaid graph should contain at least one edge")


class TestSkillAuditC1Redundancy(unittest.TestCase):
    """audit_skill.py project mode detects paragraph redundancy in C1."""

    def test_consistency_field_exists(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_skill.py"),
             "--all", "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        data = json.loads(result.stdout)
        self.assertIn("consistency", data,
                      "Project-level audit should include 'consistency' field")

    def test_x4_check_registered(self):
        checks_file = (REPO_ROOT / "skills" / "auditing" / "references"
                       / "audit-checks.json")
        data = json.loads(checks_file.read_text(encoding="utf-8"))
        ids = [c["id"] for c in data]
        self.assertIn("X4", ids, "X4 should be registered in audit-checks.json")


class TestBundlesForgeErrorIntegration(unittest.TestCase):
    """Scripts using BundlesForgeError print clean error messages."""

    def test_audit_skill_bad_path(self):
        result = subprocess.run(
            [sys.executable, str(AUDITING_SCRIPTS / "audit_skill.py"),
             "/nonexistent/path"],
            capture_output=True, text=True
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("error:", result.stderr,
                      "Error message should go to stderr with 'error:' prefix")
        self.assertNotIn("Traceback", result.stderr,
                         "BundlesForgeError should not produce tracebacks")


CLI_DISPATCHER = REPO_ROOT / "bin" / "bundles-forge"


class TestCLIDispatcher(unittest.TestCase):
    """Tests for the bin/bundles-forge CLI dispatcher."""

    def test_help_exits_zero(self):
        result = subprocess.run(
            [sys.executable, str(CLI_DISPATCHER), "--help"],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Usage:", result.stdout)
        self.assertIn("audit-plugin", result.stdout)

    def test_no_args_shows_help(self):
        result = subprocess.run(
            [sys.executable, str(CLI_DISPATCHER)],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0)
        self.assertIn("Commands:", result.stdout)

    def test_unknown_command_exits_one(self):
        result = subprocess.run(
            [sys.executable, str(CLI_DISPATCHER), "nonexistent-cmd"],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 1)
        self.assertIn("unknown command", result.stderr)

    def test_audit_plugin_via_dispatcher(self):
        result = subprocess.run(
            [sys.executable, str(CLI_DISPATCHER),
             "audit-plugin", "--json", str(REPO_ROOT)],
            capture_output=True, text=True
        )
        self.assertIn(result.returncode, (0, 1, 2),
                       f"Expected exit 0/1/2, got {result.returncode}")
        data = json.loads(result.stdout)
        self.assertIn("categories", data)

    def test_polyglot_format(self):
        content = CLI_DISPATCHER.read_text(encoding="utf-8")
        lines = content.splitlines()
        self.assertEqual(lines[0], "#!/bin/sh",
                         "First line should be #!/bin/sh shebang")
        self.assertEqual(lines[1], "''':'",
                         "Second line should open the shell preamble with ''':'")
        self.assertIn("find_python", content,
                       "Polyglot should contain find_python probe")
        self.assertIn("exec \"$PYTHON\" \"$0\" \"$@\"", content,
                       "Polyglot should exec Python with $0")
        self.assertIn("'''", content.split("exec \"$PYTHON\" \"$0\" \"$@\"")[1],
                       "Triple-quote should close after exec line")
        self.assertIn("def main():", content,
                       "Python section must define main()")


if __name__ == "__main__":
    unittest.main()
