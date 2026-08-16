from __future__ import annotations

import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "agent-skills" / "skills" / "excel-diagram-interchange" / "scripts"))

from diagram_exchange.canonical import read_json, read_xml, write_xml
from diagram_exchange.drawio import read_drawio, write_drawio
from diagram_exchange.excel_ooxml import read_xlsx, write_xlsx
from diagram_exchange.mermaid import read_mermaid

FIXTURES = ROOT / "tests" / "fixtures" / "excel-diagram-interchange"
DEMO = FIXTURES / "complex-system-architecture.xlsx"
EXPECTED = FIXTURES / "expected"


def _rounded(value: float) -> float:
    return round(float(value), 3)


def _style_signature(style) -> tuple:
    return (
        style.fill,
        style.stroke,
        _rounded(style.stroke_width),
        style.dashed,
        style.font_color,
        _rounded(style.font_size),
        style.arrow_start,
        style.arrow_end,
    )


def _node_signature(node) -> tuple:
    return (
        node.label,
        node.shape,
        _rounded(node.x),
        _rounded(node.y),
        _rounded(node.width),
        _rounded(node.height),
        _rounded(node.rotation),
        _style_signature(node.style),
    )


def _supported_contract(diagram) -> list[dict[str, object]]:
    pages: list[dict[str, object]] = []
    for page in diagram.pages:
        nodes_by_id = {node.id: node for node in page.nodes}

        def endpoint_signature(node_id: str | None):
            node = nodes_by_id.get(node_id) if node_id else None
            return _node_signature(node) if node is not None else None

        pages.append({
            "name": page.name,
            "nodes": [_node_signature(node) for node in sorted(page.nodes, key=lambda item: item.z)],
            "edges": [
                (
                    endpoint_signature(edge.source),
                    endpoint_signature(edge.target),
                    edge.label,
                    _style_signature(edge.style),
                )
                for edge in sorted(page.edges, key=lambda item: item.z)
            ],
        })
    return pages


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

    def test_complex_json_xlsx_roundtrip_preserves_supported_contract(self) -> None:
        source = read_json(EXPECTED / "diagram.json")
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "roundtrip.xlsx"
            write_xlsx(source, path)
            restored = read_xlsx(path)
        self.assertEqual(_supported_contract(restored), _supported_contract(source))

    def test_complex_json_drawio_roundtrip_preserves_supported_contract(self) -> None:
        source = read_json(EXPECTED / "diagram.json")
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "roundtrip.drawio"
            write_drawio(source, path)
            restored = read_drawio(path)
        self.assertEqual(_supported_contract(restored), _supported_contract(source))

    def test_complex_json_xml_roundtrip_is_canonical_equivalent(self) -> None:
        source = read_json(EXPECTED / "diagram.json")
        with TemporaryDirectory() as temp_dir:
            path = Path(temp_dir) / "roundtrip.xml"
            write_xml(source, path)
            restored = read_xml(path)
        self.assertEqual(restored.to_dict(), source.to_dict())

    def test_report_declares_cell_ignoring(self) -> None:
        report = json.loads((EXPECTED / "conversion-report.json").read_text(encoding="utf-8"))
        self.assertTrue(report["shape_only"])
        self.assertTrue(report["cells_ignored"])


if __name__ == "__main__":
    unittest.main()
