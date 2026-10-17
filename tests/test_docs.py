"""Lightweight repository consistency checks using only the Python standard library."""

import json
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MARKDOWN_FILES = [ROOT / "README.md", ROOT / "SKILL.md", *sorted((ROOT / "references").glob("*.md"))]


class RepositoryDocumentationTests(unittest.TestCase):
    def test_expected_reference_files_exist(self):
        expected = {
            "reconnaissance.md",
            "vulnerability-analysis.md",
            "ai-generated-code.md",
            "threat-analysis.md",
            "social-engineering.md",
            "remediation.md",
        }
        actual = {path.name for path in (ROOT / "references").glob("*.md")}
        self.assertTrue(expected.issubset(actual), f"Missing references: {expected - actual}")

    def test_local_markdown_links_resolve(self):
        link_pattern = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
        for markdown_file in MARKDOWN_FILES:
            text = markdown_file.read_text(encoding="utf-8")
            for target in link_pattern.findall(text):
                target = target.strip().split()[0].strip("<>")
                if not target or target.startswith(("https://", "http://", "mailto:", "#")):
                    continue
                path_part = target.split("#", 1)[0]
                if not path_part:
                    continue
                resolved = (markdown_file.parent / path_part).resolve()
                self.assertTrue(resolved.exists(), f"Broken link in {markdown_file.relative_to(ROOT)}: {target}")

    def test_skill_front_matter_has_required_metadata(self):
        text = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        self.assertTrue(text.startswith("---\n"), "SKILL.md must start with YAML front matter")
        front_matter = text.split("---\n", 2)[1]
        self.assertRegex(front_matter, r"(?m)^name:\s*security-analyst\s*$")
        self.assertRegex(front_matter, r"(?m)^description:\s*.+$")
        self.assertRegex(front_matter, r"(?m)^license:\s*MIT\s*$")

    def test_markdown_code_fences_are_balanced(self):
        for markdown_file in MARKDOWN_FILES:
            text = markdown_file.read_text(encoding="utf-8")
            self.assertEqual(text.count("```" ) % 2, 0, f"Unbalanced code fence in {markdown_file.relative_to(ROOT)}")

    def test_json_code_blocks_are_valid(self):
        for markdown_file in MARKDOWN_FILES:
            text = markdown_file.read_text(encoding="utf-8")
            for match in re.finditer(r"```json\s*\n(.*?)\n```", text, re.DOTALL | re.IGNORECASE):
                with self.subTest(file=markdown_file.relative_to(ROOT)):
                    json.loads(match.group(1))

    def test_stix_indicator_example_has_required_fields(self):
        text = (ROOT / "references" / "threat-analysis.md").read_text(encoding="utf-8")
        blocks = re.findall(r"```json\s*\n(.*?)\n```", text, re.DOTALL | re.IGNORECASE)
        indicators = [json.loads(block) for block in blocks if '"type": "indicator"' in block]
        self.assertEqual(len(indicators), 1, "Expected one STIX indicator example")
        indicator = indicators[0]
        for field in ("type", "spec_version", "id", "created", "modified", "pattern", "pattern_type", "valid_from"):
            self.assertIn(field, indicator)
        self.assertEqual(indicator["type"], "indicator")
        self.assertEqual(indicator["spec_version"], "2.1")
        self.assertEqual(indicator["pattern_type"], "stix")
        self.assertRegex(indicator["id"], r"^indicator--[0-9a-f-]{36}$")
        self.assertRegex(indicator["pattern"], r"^\[file:hashes\.'SHA-256' = '[0-9a-f]{64}'\]$")

    def test_domain_tables_match_six_references(self):
        expected_references = 6
        for filename in ("SKILL.md", "README.md"):
            text = (ROOT / filename).read_text(encoding="utf-8")
            self.assertIn("six", text.lower(), f"{filename} should describe the six analysis domains")
        skill = (ROOT / "SKILL.md").read_text(encoding="utf-8")
        domain_table = skill.split("## Analysis Domains", 1)[1].split("## Routing", 1)[0]
        rows = [line for line in domain_table.splitlines() if line.startswith("| ") and not line.startswith("| ---")]
        self.assertEqual(len(rows) - 1, expected_references, "SKILL.md domain table should contain six entries plus its header")

        readme = (ROOT / "README.md").read_text(encoding="utf-8")
        readme_table = readme.split("## What it covers", 1)[1].split("## How it works", 1)[0]
        readme_rows = [line for line in readme_table.splitlines() if line.startswith("| ") and not line.startswith("| ---")]
        self.assertEqual(len(readme_rows) - 1, expected_references, "README domain table should contain six entries plus its header")

    def test_yara_example_uses_a_sample_specific_string_not_a_generic_header(self):
        text = (ROOT / "references" / "threat-analysis.md").read_text(encoding="utf-8")
        self.assertIn("rule example_observed_string_only", text)
        self.assertIn("condition:\n        $observed", text)
        self.assertNotIn("4D 5A 90 00", text)


if __name__ == "__main__":
    unittest.main()
