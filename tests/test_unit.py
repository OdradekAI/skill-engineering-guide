#!/usr/bin/env python3
"""Unit tests for internal modules: _parsing, _scoring, and bump_version helpers.

These test pure functions directly (no subprocess), complementing the
end-to-end tests in test_scripts.py and the graph fixture tests in
test_graph_fixtures.py.

Run: python tests/test_unit.py
Or:  python -m pytest tests/test_unit.py -v
"""

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
AUDITING_SCRIPTS = REPO_ROOT / "skills" / "auditing" / "scripts"
RELEASING_SCRIPTS = REPO_ROOT / "skills" / "releasing" / "scripts"

sys.path.insert(0, str(AUDITING_SCRIPTS))
sys.path.insert(0, str(RELEASING_SCRIPTS))

from _cli import BundlesForgeError, run_main
from _parsing import parse_frontmatter, estimate_tokens, FRONTMATTER_RE
from _scoring import compute_baseline_score, compute_weighted_average
from _graph import generate_mermaid
from bump_version import _resolve_field_path, _set_field_path


# ---------------------------------------------------------------------------
# _parsing.parse_frontmatter
# ---------------------------------------------------------------------------

class TestParseFrontmatter(unittest.TestCase):
    """Edge cases for the zero-dependency YAML frontmatter parser."""

    def test_no_frontmatter_returns_none(self):
        content = "# Just a heading\n\nSome body text.\n"
        fm, body = parse_frontmatter(content)
        self.assertIsNone(fm)
        self.assertEqual(body, content)

    def test_empty_frontmatter_with_blank_line(self):
        content = "---\n\n---\nBody here.\n"
        fm, body = parse_frontmatter(content)
        self.assertIsNotNone(fm)
        self.assertEqual(fm, {})
        self.assertEqual(body.strip(), "Body here.")

    def test_empty_frontmatter_no_blank_line(self):
        """Adjacent --- markers with no content between them are not parsed."""
        content = "---\n---\nBody here.\n"
        fm, body = parse_frontmatter(content)
        self.assertIsNone(fm, "Parser requires at least one line between --- delimiters")

    def test_basic_key_value(self):
        content = "---\nname: my-skill\ndescription: Use when testing.\n---\nBody.\n"
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm["name"], "my-skill")
        self.assertEqual(fm["description"], "Use when testing.")

    def test_quoted_values_stripped(self):
        content = '---\nname: "my-skill"\ndescription: \'Use when testing.\'\n---\nBody.\n'
        fm, _ = parse_frontmatter(content)
        self.assertEqual(fm["name"], "my-skill")
        self.assertEqual(fm["description"], "Use when testing.")

    def test_block_scalar_literal(self):
        content = "---\ndescription: |\n  Line one.\n  Line two.\n---\nBody.\n"
        fm, _ = parse_frontmatter(content)
        self.assertIn("Line one.", fm["description"])
        self.assertIn("Line two.", fm["description"])

    def test_block_scalar_folded(self):
        content = "---\ndescription: >\n  Folded line one.\n  Folded line two.\n---\nBody.\n"
        fm, _ = parse_frontmatter(content)
        self.assertIn("Folded line one.", fm["description"])
        self.assertIn("Folded line two.", fm["description"])

    def test_value_with_colon(self):
        content = "---\ndescription: Use when: testing things.\n---\nBody.\n"
        fm, _ = parse_frontmatter(content)
        self.assertEqual(fm["description"], "Use when: testing things.")

    def test_missing_closing_delimiter(self):
        content = "---\nname: broken\nNo closing delimiter.\n"
        fm, body = parse_frontmatter(content)
        self.assertIsNone(fm)
        self.assertEqual(body, content)

    def test_empty_value(self):
        content = "---\nname:\n---\nBody.\n"
        fm, _ = parse_frontmatter(content)
        self.assertEqual(fm["name"], "")

    def test_body_is_content_after_frontmatter(self):
        content = "---\nname: test\n---\nLine 1\nLine 2\n"
        _, body = parse_frontmatter(content)
        self.assertIn("Line 1", body)
        self.assertIn("Line 2", body)


# ---------------------------------------------------------------------------
# _parsing.estimate_tokens
# ---------------------------------------------------------------------------

class TestEstimateTokens(unittest.TestCase):
    """Token estimation with separate rates for code, tables, and prose."""

    def test_empty_input(self):
        self.assertEqual(estimate_tokens(""), 0)

    def test_pure_prose(self):
        prose = "This is a simple sentence with several words."
        tokens = estimate_tokens(prose)
        self.assertGreater(tokens, 0)
        word_count = len(prose.split())
        self.assertAlmostEqual(tokens, int(word_count * 1.3), delta=2)

    def test_pure_code_block(self):
        code = "```python\nfor i in range(10):\n    print(i)\n```"
        tokens = estimate_tokens(code)
        self.assertGreater(tokens, 0)

    def test_table_rows(self):
        table = "| Col1 | Col2 |\n|------|------|\n| a    | b    |\n"
        tokens = estimate_tokens(table)
        self.assertGreater(tokens, 0)

    def test_mixed_content(self):
        content = (
            "Some prose here.\n\n"
            "```python\nprint('hello')\n```\n\n"
            "| A | B |\n|---|---|\n| 1 | 2 |\n"
        )
        tokens = estimate_tokens(content)
        self.assertGreater(tokens, 0)


# ---------------------------------------------------------------------------
# _scoring.compute_baseline_score
# ---------------------------------------------------------------------------

class TestComputeBaselineScore(unittest.TestCase):
    """Scoring edge cases for the deterministic baseline formula."""

    def test_empty_findings(self):
        self.assertEqual(compute_baseline_score([]), 10)

    def test_all_info_no_penalty(self):
        findings = [
            {"check": "Q10", "severity": "info"},
            {"check": "Q11", "severity": "info"},
            {"check": "Q12", "severity": "info"},
        ]
        self.assertEqual(compute_baseline_score(findings), 10)

    def test_single_critical(self):
        findings = [{"check": "Q1", "severity": "critical"}]
        self.assertEqual(compute_baseline_score(findings), 7)

    def test_multiple_criticals_floor_at_zero(self):
        findings = [
            {"check": "Q1", "severity": "critical"},
            {"check": "Q2", "severity": "critical"},
            {"check": "Q3", "severity": "critical"},
            {"check": "Q4", "severity": "critical"},
        ]
        self.assertEqual(compute_baseline_score(findings), 0)

    def test_single_warning(self):
        findings = [{"check": "Q5", "severity": "warning"}]
        self.assertEqual(compute_baseline_score(findings), 9)

    def test_cap_per_id_true_limits_same_check(self):
        findings = [
            {"check": "Q7", "severity": "warning"},
            {"check": "Q7", "severity": "warning"},
            {"check": "Q7", "severity": "warning"},
            {"check": "Q7", "severity": "warning"},
            {"check": "Q7", "severity": "warning"},
        ]
        score = compute_baseline_score(findings, cap_per_id=True)
        self.assertEqual(score, 7)

    def test_cap_per_id_false_counts_each(self):
        findings = [
            {"check": "Q7", "severity": "warning"},
            {"check": "Q7", "severity": "warning"},
            {"check": "Q7", "severity": "warning"},
            {"check": "Q7", "severity": "warning"},
            {"check": "Q7", "severity": "warning"},
        ]
        score = compute_baseline_score(findings, cap_per_id=False)
        self.assertEqual(score, 5)

    def test_mixed_severities(self):
        findings = [
            {"check": "Q1", "severity": "critical"},
            {"check": "Q5", "severity": "warning"},
            {"check": "Q10", "severity": "info"},
        ]
        score = compute_baseline_score(findings)
        self.assertEqual(score, 6)

    def test_risk_field_fallback(self):
        """Security findings use 'risk' instead of 'severity'."""
        findings = [{"check": "SC1", "risk": "critical"}]
        self.assertEqual(compute_baseline_score(findings), 7)


# ---------------------------------------------------------------------------
# _scoring.compute_weighted_average
# ---------------------------------------------------------------------------

class TestComputeWeightedAverage(unittest.TestCase):
    """Weighted average with None handling and edge cases."""

    def test_empty_scores(self):
        self.assertEqual(compute_weighted_average({}, {}), 0.0)

    def test_all_none_scores(self):
        scores = {"a": None, "b": None}
        weights = {"a": 3, "b": 2}
        self.assertEqual(compute_weighted_average(scores, weights), 0.0)

    def test_single_category(self):
        scores = {"quality": 8}
        weights = {"quality": 2}
        self.assertEqual(compute_weighted_average(scores, weights), 8.0)

    def test_mixed_weights(self):
        scores = {"structure": 10, "quality": 6}
        weights = {"structure": 3, "quality": 2}
        expected = round((10 * 3 + 6 * 2) / (3 + 2), 1)
        self.assertEqual(
            compute_weighted_average(scores, weights), expected)

    def test_none_scores_excluded(self):
        scores = {"structure": 10, "quality": None, "security": 8}
        weights = {"structure": 3, "quality": 2, "security": 3}
        expected = round((10 * 3 + 8 * 3) / (3 + 3), 1)
        self.assertEqual(
            compute_weighted_average(scores, weights), expected)

    def test_default_weight_one(self):
        scores = {"unknown_cat": 7}
        weights = {}
        self.assertEqual(compute_weighted_average(scores, weights), 7.0)


# ---------------------------------------------------------------------------
# bump_version._resolve_field_path / _set_field_path
# ---------------------------------------------------------------------------

class TestFieldPathResolution(unittest.TestCase):
    """JSON field path traversal for version bump."""

    def test_simple_key(self):
        data = {"version": "1.0.0"}
        self.assertEqual(_resolve_field_path(data, "version"), "1.0.0")

    def test_nested_dict(self):
        data = {"package": {"version": "2.0.0"}}
        self.assertEqual(_resolve_field_path(data, "package.version"), "2.0.0")

    def test_array_index(self):
        data = {"plugins": [{"version": "3.0.0"}]}
        self.assertEqual(
            _resolve_field_path(data, "plugins.0.version"), "3.0.0")

    def test_missing_key_returns_none(self):
        data = {"version": "1.0.0"}
        self.assertIsNone(_resolve_field_path(data, "nonexistent"))

    def test_array_index_out_of_bounds(self):
        data = {"plugins": []}
        self.assertIsNone(_resolve_field_path(data, "plugins.0.version"))

    def test_type_mismatch_dict_expected(self):
        data = {"version": "1.0.0"}
        self.assertIsNone(_resolve_field_path(data, "version.sub"))

    def test_type_mismatch_list_expected(self):
        data = {"plugins": {"version": "1.0.0"}}
        self.assertIsNone(_resolve_field_path(data, "plugins.0"))

    def test_set_simple_key(self):
        data = {"version": "1.0.0"}
        _set_field_path(data, "version", "2.0.0")
        self.assertEqual(data["version"], "2.0.0")

    def test_set_nested_path(self):
        data = {"package": {"version": "1.0.0"}}
        _set_field_path(data, "package.version", "2.0.0")
        self.assertEqual(data["package"]["version"], "2.0.0")

    def test_set_array_element(self):
        data = {"plugins": [{"version": "1.0.0"}]}
        _set_field_path(data, "plugins.0.version", "2.0.0")
        self.assertEqual(data["plugins"][0]["version"], "2.0.0")


# ---------------------------------------------------------------------------
# _cli.BundlesForgeError
# ---------------------------------------------------------------------------

class TestBundlesForgeError(unittest.TestCase):
    """BundlesForgeError carries message and exit code."""

    def test_message_stored(self):
        e = BundlesForgeError("bad input")
        self.assertEqual(e.message, "bad input")

    def test_default_code_is_one(self):
        e = BundlesForgeError("err")
        self.assertEqual(e.code, 1)

    def test_custom_code(self):
        e = BundlesForgeError("err", code=2)
        self.assertEqual(e.code, 2)

    def test_is_exception(self):
        self.assertTrue(issubclass(BundlesForgeError, Exception))

    def test_str_is_message(self):
        e = BundlesForgeError("some error")
        self.assertEqual(str(e), "some error")


class TestRunMain(unittest.TestCase):
    """run_main catches BundlesForgeError and converts to sys.exit."""

    def test_clean_exit(self):
        def ok():
            pass
        run_main(ok)

    def test_catches_error_and_exits(self):
        def fail():
            raise BundlesForgeError("test fail", code=2)
        with self.assertRaises(SystemExit) as ctx:
            run_main(fail)
        self.assertEqual(ctx.exception.code, 2)


# ---------------------------------------------------------------------------
# _graph.generate_mermaid
# ---------------------------------------------------------------------------

class TestGenerateMermaid(unittest.TestCase):
    """generate_mermaid produces valid Mermaid graph syntax."""

    def test_empty_graph(self):
        result = generate_mermaid({})
        self.assertEqual(result, "graph LR")

    def test_single_edge(self):
        result = generate_mermaid({"a": {"b"}})
        self.assertIn("a --> b", result)
        self.assertTrue(result.startswith("graph LR"))

    def test_multiple_edges_sorted(self):
        result = generate_mermaid({"b": {"c", "a"}, "a": {"c"}})
        lines = result.splitlines()
        edge_lines = [l.strip() for l in lines if "-->" in l]
        self.assertEqual(edge_lines, ["a --> c", "b --> a", "b --> c"])

    def test_no_edges_node_only(self):
        result = generate_mermaid({"a": set()})
        self.assertEqual(result, "graph LR")

    def test_with_layers_subgraph(self):
        graph = {"orchestrator": {"worker"}, "worker": set()}
        layers = {"orchestrator": "hub", "worker": "spoke"}
        result = generate_mermaid(graph, skill_layers=layers)
        self.assertIn("subgraph hub [hub]", result)
        self.assertIn("subgraph spoke [spoke]", result)
        self.assertIn("orchestrator --> worker", result)

    def test_layer_ids_sanitized(self):
        graph = {"a": set()}
        layers = {"a": "my layer"}
        result = generate_mermaid(graph, skill_layers=layers)
        self.assertIn("subgraph my_layer [my layer]", result)


# ---------------------------------------------------------------------------
# Paragraph hash redundancy (used by C1 in audit_skill.py)
# ---------------------------------------------------------------------------

class TestParagraphHashHelpers(unittest.TestCase):
    """Test the paragraph extraction and hashing logic used in C1."""

    def _split_paragraphs(self, text):
        """Replicate the paragraph splitting logic from audit_skill.py."""
        import hashlib as _hl
        import re as _re
        body_text = FRONTMATTER_RE.sub("", text, count=1).strip()
        results = {}
        for para in _re.split(r"\n\s*\n", body_text):
            lines = [ln for ln in para.strip().splitlines()
                     if ln.strip() and not ln.strip().startswith("#")]
            if len(lines) < 3:
                continue
            normalized = "\n".join(ln.strip() for ln in lines)
            h = _hl.sha256(normalized.encode()).hexdigest()[:16]
            results[h] = normalized
        return results

    def test_skip_short_paragraphs(self):
        text = "Line one.\n\nLine two."
        self.assertEqual(len(self._split_paragraphs(text)), 0)

    def test_skip_heading_only_lines(self):
        text = "# Title\n## Sub\n### Sub2"
        self.assertEqual(len(self._split_paragraphs(text)), 0)

    def test_extract_long_paragraph(self):
        text = "Line 1\nLine 2\nLine 3\n\nShort."
        paras = self._split_paragraphs(text)
        self.assertEqual(len(paras), 1)

    def test_frontmatter_stripped(self):
        text = "---\nname: test\n---\nLine 1\nLine 2\nLine 3"
        paras = self._split_paragraphs(text)
        self.assertEqual(len(paras), 1)

    def test_same_content_same_hash(self):
        text = "A\nB\nC"
        paras = self._split_paragraphs(text)
        h1 = list(paras.keys())[0]
        paras2 = self._split_paragraphs("  A  \n  B  \n  C  ")
        h2 = list(paras2.keys())[0]
        self.assertEqual(h1, h2)

    def test_different_content_different_hash(self):
        p1 = self._split_paragraphs("A\nB\nC")
        p2 = self._split_paragraphs("X\nY\nZ")
        self.assertNotEqual(list(p1.keys())[0], list(p2.keys())[0])


# ---------------------------------------------------------------------------
# X4 orphan detection logic
# ---------------------------------------------------------------------------

class TestX4OrphanDetection(unittest.TestCase):
    """Test the orphan reference file detection used by X4 in audit_skill.py."""

    def setUp(self):
        import tempfile
        self.tmpdir = Path(tempfile.mkdtemp())
        self.skill_dir = self.tmpdir / "skills" / "test-skill"
        self.skill_dir.mkdir(parents=True)
        self.refs_dir = self.skill_dir / "references"
        self.refs_dir.mkdir()

    def tearDown(self):
        import shutil
        shutil.rmtree(self.tmpdir, ignore_errors=True)

    def _detect_orphans(self):
        """Replicate the X4 detection logic from audit_skill.py."""
        refs_dir = self.refs_dir
        skill_dir = self.skill_dir
        skill_md = skill_dir / "SKILL.md"
        content = skill_md.read_text(encoding="utf-8") if skill_md.exists() else ""

        ref_files = sorted(
            f for f in refs_dir.iterdir()
            if f.is_file() and f.suffix in (".md", ".json")
        )
        all_texts = {skill_md: content}
        for rf in ref_files:
            try:
                all_texts[rf] = rf.read_text(encoding="utf-8", errors="replace")
            except OSError:
                pass

        orphans = []
        for rf in ref_files:
            fname = rf.name
            ref_rel = f"references/{fname}"
            referenced = any(
                fname in txt or ref_rel in txt
                for path, txt in all_texts.items() if path != rf
            )
            if not referenced:
                orphans.append(fname)
        return orphans

    def test_no_orphans_when_referenced(self):
        (self.skill_dir / "SKILL.md").write_text(
            "See `references/guide.md` for details.", encoding="utf-8")
        (self.refs_dir / "guide.md").write_text("# Guide", encoding="utf-8")
        self.assertEqual(self._detect_orphans(), [])

    def test_orphan_detected(self):
        (self.skill_dir / "SKILL.md").write_text(
            "No references here.", encoding="utf-8")
        (self.refs_dir / "orphan.md").write_text("# Orphan", encoding="utf-8")
        self.assertEqual(self._detect_orphans(), ["orphan.md"])

    def test_sibling_reference_counts(self):
        (self.skill_dir / "SKILL.md").write_text(
            "See `references/main.md`.", encoding="utf-8")
        (self.refs_dir / "main.md").write_text(
            "Also see helper.md for more.", encoding="utf-8")
        (self.refs_dir / "helper.md").write_text("# Helper", encoding="utf-8")
        self.assertEqual(self._detect_orphans(), [])

    def test_filename_only_match(self):
        (self.skill_dir / "SKILL.md").write_text(
            "Refer to guide.md in the references directory.", encoding="utf-8")
        (self.refs_dir / "guide.md").write_text("# Guide", encoding="utf-8")
        self.assertEqual(self._detect_orphans(), [])

    def test_empty_references_dir(self):
        (self.skill_dir / "SKILL.md").write_text("Content.", encoding="utf-8")
        self.assertEqual(self._detect_orphans(), [])


if __name__ == "__main__":
    unittest.main()
