from __future__ import annotations

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "agent-skills" / "skills" / "excel-diagram-interchange" / "scripts"))

from diagram_exchange.canonical import read_json
from diagram_exchange.drawio import read_drawio
from diagram_exchange.excel_ooxml import read_xlsx, write_xlsx
from diagram_exchange.mermaid import read_mermaid

FIXTURES = ROOT / "tests" / "fixtures" / "excel-diagram-interchange"
DEMO = FIXTURES / "complex-system-architecture.xlsx"
EXPECTED = FIXTURES / "expected"


class DemoRepositoryTests(unittest.TestCase):
    def test_demo_excel_matches_canonical_snapshot(self) -> None:
        actual = read_xlsx(DEMO)
        expected = read_json(EXPECTED / "diagram.json")
        self.assertEqual(actual.to_dict(), expected.to_dict())
        self.assertEqual(actual.metadata["cells_ignored"], True)
        self.assertEqual([len(page.nodes) for page in actual.pages], [17, 10])
        self.assertEqual([len(page.edges) for page in actual.pages], [20, 10])
        self.assertTrue(all(edge.source and edge.target for page in actual.pages for edge in page.edges))

    def test_expected_drawio_retains_both_pages(self) -> None:
        diagram = read_drawio(EXPECTED / "diagram.drawio")
        self.assertEqual([page.name for page in diagram.pages], ["System Architecture", "DR and Operations"])
        self.assertEqual(sum(len(page.nodes) for page in diagram.pages), 27)

    def test_expected_mermaid_is_first_page_logical_view(self) -> None:
        diagram = read_mermaid(EXPECTED / "diagram.mmd")
        self.assertEqual(len(diagram.pages), 1)
        self.assertEqual(len(diagram.pages[0].nodes), 17)
        self.assertEqual(len(diagram.pages[0].edges), 20)

    def test_json_to_excel_to_json_smoke(self) -> None:
        source = read_json(EXPECTED / "diagram.json")
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "roundtrip.xlsx"
            write_xlsx(source, path)
            restored = read_xlsx(path)
        self.assertEqual([node.label for node in source.pages[0].nodes],
                         [node.label for node in restored.pages[0].nodes])
        self.assertEqual(len(restored.pages[1].edges), 10)

    def test_report_declares_cell_ignoring(self) -> None:
        report = json.loads((EXPECTED / "conversion-report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["shape_only"])
        self.assertTrue(report["cells_ignored"])


if __name__ == "__main__":
    unittest.main()
