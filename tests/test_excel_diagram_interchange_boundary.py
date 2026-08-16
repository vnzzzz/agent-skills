from __future__ import annotations

from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "agent-skills" / "skills" / "excel-diagram-interchange"


class RepositoryBoundaryTests(unittest.TestCase):
    def test_skill_contains_only_runtime_categories(self) -> None:
        required = {
            "SKILL.md",
            "agents/openai.yaml",
            "references/capabilities.md",
            "references/model-schema.md",
            "scripts/convert.py",
        }
        actual = {
            path.relative_to(SKILL).as_posix()
            for path in SKILL.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts and path.suffix != ".pyc"
        }
        self.assertTrue(required <= actual)

        forbidden_names = {
            "README.md",
            "SECURITY_REVIEW.md",
            "requirements.lock",
            "requirements.txt",
        }
        forbidden_parts = {"tests", "fixtures", "demo", "examples", ".github"}
        for relative in actual:
            path = Path(relative)
            self.assertNotIn(path.name, forbidden_names)
            self.assertTrue(forbidden_parts.isdisjoint(path.parts))
            if path.suffix == ".py":
                self.assertEqual("scripts", path.parts[0])

    def test_repository_owns_development_files_without_runtime_dependencies(self) -> None:
        self.assertFalse((ROOT / "requirements.lock").exists())
        for relative in (
            "tests/test_excel_diagram_interchange.py",
            "tests/test_excel_diagram_interchange_security.py",
            "scripts/audit-excel-diagram-interchange.py",
        ):
            self.assertTrue((ROOT / relative).is_file(), relative)


if __name__ == "__main__":
    unittest.main()
