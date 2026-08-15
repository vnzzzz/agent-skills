from __future__ import annotations

from base64 import b64encode
import json
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from urllib.parse import quote
from zipfile import ZIP_DEFLATED, ZipFile
import zlib

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "plugins" / "agent-skills" / "skills" / "excel-diagram-interchange" / "scripts"))

from diagram_exchange.canonical import read_json, read_xml, write_json, write_xml
from diagram_exchange.drawio import read_drawio, write_drawio
from diagram_exchange.excel_ooxml import read_xlsx, write_xlsx
from diagram_exchange.mermaid import read_mermaid, write_mermaid
from diagram_exchange.model import Diagram, Edge, Node, Page, Style
from diagram_exchange.security import preflight_xlsx


def rewrite_zip_entry(path: Path, name: str, transform) -> None:
    replacement = path.with_suffix(".tmp")
    with ZipFile(path) as source, ZipFile(replacement, "w", ZIP_DEFLATED) as target:
        for info in source.infolist():
            data = source.read(info.filename)
            if info.filename == name:
                data = transform(data)
            target.writestr(info, data)
    replacement.replace(path)


def sample() -> Diagram:
    return Diagram(title="System", pages=[Page(
        id="page_1", name="Architecture", width=1000, height=600,
        nodes=[
            Node(id="web", label="Web <App>", shape="roundRect", x=80, y=100, width=180, height=80,
                 style=Style(fill="#dae8fc", stroke="#6c8ebf", stroke_width=2, font_size=14)),
            Node(id="db", label="Database", shape="can", x=420, y=100, width=160, height=100, z=1,
                 style=Style(fill="#d5e8d4", stroke="#82b366", stroke_width=2, font_size=14)),
        ],
        edges=[Edge(id="e1", source="web", target="db", label="SQL", z=2,
                    style=Style(fill="none", stroke_width=2, arrow_end="triangle"))],
    )])


class InterchangeTests(unittest.TestCase):
    def test_json_xml_roundtrip(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.xml"
            write_xml(sample(), path)
            restored = read_xml(path)
            self.assertEqual(restored.pages[0].nodes[0].label, "Web <App>")
            self.assertEqual(restored.pages[0].edges[0].target, "db")

    def test_drawio_roundtrip(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.drawio"
            write_drawio(sample(), path)
            restored = read_drawio(path)
            self.assertEqual(len(restored.pages[0].nodes), 2)
            self.assertEqual(len(restored.pages[0].edges), 1)
            self.assertEqual(restored.pages[0].nodes[0].label, "Web <App>")

    def test_compressed_drawio_import(self):
        model = '<mxGraphModel><root><mxCell id="0"/><mxCell id="1" parent="0"/><mxCell id="2" value="A" vertex="1" parent="1"><mxGeometry x="10" y="20" width="100" height="40" as="geometry"/></mxCell></root></mxGraphModel>'
        compressor = zlib.compressobj(wbits=-15)
        packed = compressor.compress(quote(model).encode()) + compressor.flush()
        xml = f'<mxfile compressed="true"><diagram name="P">{b64encode(packed).decode()}</diagram></mxfile>'
        with TemporaryDirectory() as td:
            path = Path(td) / "compressed.drawio"
            path.write_text(xml, encoding="utf-8")
            restored = read_drawio(path)
            self.assertEqual(restored.pages[0].nodes[0].label, "A")

    def test_mermaid_roundtrip_preserves_profile_geometry(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.mmd"
            write_mermaid(sample(), path)
            restored = read_mermaid(path)
            by_id = {node.id: node for node in restored.pages[0].nodes}
            self.assertEqual(by_id["web"].x, 80)
            self.assertEqual(by_id["web"].width, 180)
            self.assertEqual(restored.pages[0].edges[0].label, "SQL")

    def test_mermaid_rejects_click_directive(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "unsafe.mmd"
            path.write_text('flowchart LR\nA["a"]\nclick A "https://example.com"\n', encoding="utf-8")
            with self.assertRaises(ValueError):
                read_mermaid(path)

    def test_xlsx_roundtrip_ignores_cells(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.xlsx"
            write_xlsx(sample(), path)
            rewrite_zip_entry(
                path, "xl/worksheets/sheet1.xml",
                lambda data: data.decode().replace(
                    "<sheetData/>",
                    '<sheetData><row r="1"><c r="A1" t="inlineStr"><is><t>IGNORE ME</t></is></c></row></sheetData>',
                ).encode(),
            )
            restored = read_xlsx(path)
            labels = [node.label for node in restored.pages[0].nodes]
            self.assertNotIn("IGNORE ME", labels)
            self.assertEqual(labels, ["Web <App>", "Database"])
            self.assertEqual(restored.pages[0].edges[0].source, "page_1_shape_2")
            self.assertEqual(restored.pages[0].edges[0].target, "page_1_shape_3")

    def test_xlsx_rejects_macro_part(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.xlsx"
            write_xlsx(sample(), path)
            with ZipFile(path, "a", ZIP_DEFLATED) as zf:
                zf.writestr("xl/vbaProject.bin", b"x")
            with self.assertRaisesRegex(ValueError, "Blocked workbook part"):
                preflight_xlsx(path)

    def test_xlsx_rejects_external_relationship(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.xlsx"
            write_xlsx(sample(), path)
            rewrite_zip_entry(
                path, "_rels/.rels",
                lambda data: data.decode().replace(
                    "</Relationships>",
                    '<Relationship Id="rId9" Type="x" Target="https://example.com" TargetMode="External"/></Relationships>',
                ).encode(),
            )
            with self.assertRaisesRegex(ValueError, "External relationship"):
                preflight_xlsx(path)

    def test_json_writer_reader(self):
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.json"
            write_json(sample(), path)
            restored = read_json(path)
            self.assertEqual(restored.title, "System")
            self.assertEqual(restored.pages[0].nodes[1].shape, "can")

    def test_canonical_model_rejects_style_injection(self):
        raw = sample().to_dict()
        raw["pages"][0]["nodes"][0]["style"]["stroke"] = "#000000;html=1"
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.json"
            path.write_text(json.dumps(raw), encoding="utf-8")
            restored = read_json(path)
            self.assertEqual(restored.pages[0].nodes[0].style.stroke, "#000000")

    def test_canonical_model_rejects_invalid_id(self):
        raw = sample().to_dict()
        raw["pages"][0]["nodes"][0]["id"] = "bad;id"
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.json"
            path.write_text(json.dumps(raw), encoding="utf-8")
            with self.assertRaises(ValueError):
                read_json(path)


if __name__ == "__main__":
    unittest.main()
