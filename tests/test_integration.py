#!/usr/bin/env python3
"""
Integration tests for bundles-forge — cross-platform replacements for shell tests.

Replaces:
  - test-bootstrap-injection.sh
  - test-version-sync.sh
  - test-skill-discovery.sh

Run: python tests/test_integration.py -v
Or:  python -m pytest tests/test_integration.py -v
"""

import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
HOOK_PATH = REPO_ROOT / "hooks" / "session-start"
SKILLS_DIR = REPO_ROOT / "skills"
SCRIPTS_DIR = REPO_ROOT / "scripts"
VERSION_CONFIG = REPO_ROOT / ".version-bump.json"

EXPECTED_SKILLS = [
    "authoring",
    "auditing",
    "blueprinting",
    "optimizing",
    "releasing",
    "scaffolding",
    "using-bundles-forge",
    "porting",
]


def _run_hook(env_overrides=None):
    """Run the session-start hook and return (stdout, stderr, returncode)."""
    env = os.environ.copy()
    env.pop("CURSOR_PLUGIN_ROOT", None)
    env.pop("CLAUDE_PLUGIN_ROOT", None)
    if env_overrides:
        env.update(env_overrides)

    result = subprocess.run(
        ["bash", str(HOOK_PATH)],
        capture_output=True, text=True, env=env, timeout=15,
    )
    return result.stdout, result.stderr, result.returncode


def _parse_frontmatter(content):
    """Minimal frontmatter parser — extract key: value pairs between --- fences."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return None
    fm = {}
    current_key = None
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if line.startswith("  ") and current_key:
            fm[current_key] += " " + line.strip()
            continue
        idx = line.find(":")
        if idx > 0:
            key = line[:idx].strip()
            val = line[idx + 1:].strip()
            if (val.startswith('"') and val.endswith('"')) or \
               (val.startswith("'") and val.endswith("'")):
                val = val[1:-1]
            fm[key] = val
            current_key = key
    return fm


class TestBootstrapInjection(unittest.TestCase):
    """Replaces test-bootstrap-injection.sh — runtime behavior tests."""

    def test_hook_script_exists(self):
        self.assertTrue(HOOK_PATH.exists(), "hooks/session-start missing")

    def test_hook_references_bootstrap_skill(self):
        content = HOOK_PATH.read_text(encoding="utf-8")
        self.assertIn("using-bundles-forge/SKILL.md", content)

    @unittest.skipUnless(
        subprocess.run(["bash", "--version"], capture_output=True).returncode == 0,
        "bash not available"
    )
    def test_claude_code_output_is_valid_json(self):
        stdout, _, rc = _run_hook()
        self.assertEqual(rc, 0, f"Hook exited {rc}")
        data = json.loads(stdout)
        self.assertIn("hookSpecificOutput", data,
                       "Claude Code mode should produce hookSpecificOutput")

    @unittest.skipUnless(
        subprocess.run(["bash", "--version"], capture_output=True).returncode == 0,
        "bash not available"
    )
    def test_cursor_output_is_valid_json(self):
        stdout, _, rc = _run_hook({"CURSOR_PLUGIN_ROOT": str(REPO_ROOT)})
        self.assertEqual(rc, 0, f"Hook exited {rc}")
        data = json.loads(stdout)
        self.assertIn("additional_context", data,
                       "Cursor mode should produce additional_context")

    @unittest.skipUnless(
        subprocess.run(["bash", "--version"], capture_output=True).returncode == 0,
        "bash not available"
    )
    def test_output_contains_bootstrap_markers(self):
        stdout, _, _ = _run_hook()
        self.assertIn("EXTREMELY_IMPORTANT", stdout)
        self.assertIn("bundles-forge", stdout)

    def test_hook_detects_cursor_platform(self):
        content = HOOK_PATH.read_text(encoding="utf-8")
        self.assertIn("CURSOR_PLUGIN_ROOT", content,
                       "Hook should check CURSOR_PLUGIN_ROOT for platform detection")

    def test_claude_code_is_default_branch(self):
        """Claude Code output is the else branch — no explicit env var needed."""
        content = HOOK_PATH.read_text(encoding="utf-8")
        self.assertIn("hookSpecificOutput", content,
                       "Hook should emit hookSpecificOutput in default (Claude) branch")


class TestVersionSync(unittest.TestCase):
    """Replaces test-version-sync.sh — pure Python, no jq dependency."""

    def test_version_bump_config_exists(self):
        self.assertTrue(VERSION_CONFIG.exists(), ".version-bump.json missing")

    def test_all_declared_files_exist(self):
        config = json.loads(VERSION_CONFIG.read_text(encoding="utf-8"))
        for entry in config.get("files", []):
            fpath = REPO_ROOT / entry["path"]
            self.assertTrue(fpath.exists(), f"Declared file missing: {entry['path']}")

    def test_bump_version_script_exists(self):
        self.assertTrue(
            (SCRIPTS_DIR / "bump_version.py").exists(),
            "scripts/bump_version.py missing"
        )

    def test_no_version_drift(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPTS_DIR / "bump_version.py"), "--check"],
            capture_output=True, text=True
        )
        self.assertEqual(result.returncode, 0,
                         f"Version drift detected:\n{result.stdout}")

    def test_all_versions_match(self):
        """Read each declared file and verify all version strings are identical."""
        config = json.loads(VERSION_CONFIG.read_text(encoding="utf-8"))
        versions = {}
        for entry in config.get("files", []):
            fpath = REPO_ROOT / entry["path"]
            if not fpath.exists():
                continue
            data = json.loads(fpath.read_text(encoding="utf-8"))
            parts = entry["field"].split(".")
            val = data
            for p in parts:
                if p.isdigit():
                    val = val[int(p)]
                else:
                    val = val[p]
            versions[entry["path"]] = val

        unique = set(versions.values())
        self.assertEqual(len(unique), 1,
                         f"Version mismatch: {versions}")


class TestSkillDiscovery(unittest.TestCase):
    """Replaces test-skill-discovery.sh — frontmatter validation in Python."""

    def test_skills_directory_exists(self):
        self.assertTrue(SKILLS_DIR.is_dir(), "skills/ directory missing")

    def test_all_expected_skills_present(self):
        for skill in EXPECTED_SKILLS:
            self.assertTrue(
                (SKILLS_DIR / skill).is_dir(),
                f"skills/{skill}/ directory missing"
            )

    def test_each_skill_has_skill_md(self):
        for skill in EXPECTED_SKILLS:
            self.assertTrue(
                (SKILLS_DIR / skill / "SKILL.md").exists(),
                f"skills/{skill}/SKILL.md missing"
            )

    def test_each_skill_has_valid_frontmatter(self):
        for skill in EXPECTED_SKILLS:
            skill_md = SKILLS_DIR / skill / "SKILL.md"
            if not skill_md.exists():
                continue
            content = skill_md.read_text(encoding="utf-8")
            fm = _parse_frontmatter(content)
            self.assertIsNotNone(fm, f"{skill}/SKILL.md: missing frontmatter")
            self.assertIn("name", fm, f"{skill}/SKILL.md: missing name field")
            self.assertIn("description", fm, f"{skill}/SKILL.md: missing description field")

    def test_skill_names_match_directories(self):
        for skill in EXPECTED_SKILLS:
            skill_md = SKILLS_DIR / skill / "SKILL.md"
            if not skill_md.exists():
                continue
            content = skill_md.read_text(encoding="utf-8")
            fm = _parse_frontmatter(content)
            if fm and "name" in fm:
                self.assertEqual(
                    fm["name"], skill,
                    f"Directory '{skill}' != frontmatter name '{fm['name']}'"
                )


if __name__ == "__main__":
    unittest.main()
