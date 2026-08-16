from __future__ import annotations

from base64 import b64encode
from contextlib import redirect_stderr
from io import StringIO
from pathlib import Path
import sys
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch
from urllib.parse import quote
from zipfile import ZIP_DEFLATED, ZipFile
import zlib

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "plugins" / "agent-skills" / "skills" / "excel-diagram-interchange" / "scripts"
sys.path.insert(0, str(SCRIPTS))

from diagram_exchange import safe_xml
from diagram_exchange.canonical import read_xml
from diagram_exchange.cli import main
from diagram_exchange.drawio import read_drawio
from diagram_exchange.excel_ooxml import write_xlsx
from diagram_exchange.model import Diagram, Page
from diagram_exchange.security import preflight_xlsx


def rewrite_zip_entry(path: Path, name: str, data: bytes) -> None:
    replacement = path.with_suffix(".tmp")
    with ZipFile(path) as source, ZipFile(replacement, "w", ZIP_DEFLATED) as target:
        for info in source.infolist():
            target.writestr(info, data if info.filename == name else source.read(info.filename))
    replacement.replace(path)


def minimal_diagram() -> Diagram:
    return Diagram(title="Security", pages=[Page(id="page_1", name="Sheet1")])


class XmlSecurityTests(unittest.TestCase):
    def test_cli_rejects_symlink_input_before_resolve(self) -> None:
        with TemporaryDirectory() as td:
            root = Path(td)
            target = root / "input.json"
            target.write_text("{}", encoding="utf-8")
            link = root / "linked.json"
            link.symlink_to(target)
            stderr = StringIO()
            with redirect_stderr(stderr):
                result = main([str(link), "--formats", "json"])
            self.assertEqual(2, result)
            self.assertIn("Symbolic-link input is not allowed", stderr.getvalue())

    def test_canonical_xml_rejects_doctype(self) -> None:
        xml = b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE diagram [<!ENTITY x "boom">]>
<diagram schema-version="1.0" title="x"><metadata/><pages/></diagram>'''
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.xml"
            path.write_bytes(xml)
            with self.assertRaisesRegex(ValueError, "DOCTYPE"):
                read_xml(path)

    def test_utf16_xml_rejects_doctype_without_byte_scanning(self) -> None:
        text = '''<?xml version="1.0" encoding="UTF-16"?>
<!DOCTYPE diagram [<!ENTITY x "boom">]>
<diagram schema-version="1.0" title="x"><metadata/><pages/></diagram>'''
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.xml"
            path.write_bytes(text.encode("utf-16"))
            with self.assertRaisesRegex(ValueError, "DOCTYPE"):
                read_xml(path)

    def test_valid_utf16_xml_is_accepted(self) -> None:
        text = '''<?xml version="1.0" encoding="UTF-16"?>
<diagram schema-version="1.0" title="x"><metadata/><pages/></diagram>'''
        root = safe_xml.parse_xml_bytes(text.encode("utf-16"))
        self.assertEqual("diagram", root.tag)

    def test_drawio_rejects_doctype(self) -> None:
        xml = b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE mxfile [<!ENTITY x "boom">]>
<mxfile compressed="false"><diagram name="P"><mxGraphModel><root/></mxGraphModel></diagram></mxfile>'''
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.drawio"
            path.write_bytes(xml)
            with self.assertRaisesRegex(ValueError, "DOCTYPE"):
                read_drawio(path)

    def test_compressed_drawio_rejects_doctype_in_inner_xml(self) -> None:
        model = '''<!DOCTYPE mxGraphModel [<!ENTITY x "boom">]>
<mxGraphModel><root><mxCell id="0"/></root></mxGraphModel>'''
        compressor = zlib.compressobj(wbits=-15)
        packed = compressor.compress(quote(model).encode("utf-8")) + compressor.flush()
        outer = (
            '<mxfile compressed="true"><diagram name="P">'
            f'{b64encode(packed).decode("ascii")}'
            '</diagram></mxfile>'
        )
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.drawio"
            path.write_text(outer, encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "DOCTYPE"):
                read_drawio(path)

    def test_ooxml_rejects_doctype_in_any_xml_part(self) -> None:
        unsafe = b'''<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE Properties [<!ENTITY x "boom">]>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"/>'''
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.xlsx"
            write_xlsx(minimal_diagram(), path)
            rewrite_zip_entry(path, "docProps/app.xml", unsafe)
            with self.assertRaisesRegex(ValueError, "DOCTYPE"):
                preflight_xlsx(path)

    def test_expat_below_minimum_fails_closed(self) -> None:
        with patch.object(safe_xml.expat, "EXPAT_VERSION", "expat_2.7.1"):
            with self.assertRaisesRegex(RuntimeError, "2.7.2"):
                safe_xml.parse_xml_bytes(b"<root/>")

    def test_xlsx_uncompressed_size_limit_is_preserved(self) -> None:
        with TemporaryDirectory() as td:
            path = Path(td) / "diagram.xlsx"
            write_xlsx(minimal_diagram(), path)
            with self.assertRaisesRegex(ValueError, "uncompressed size limit"):
                preflight_xlsx(path, max_uncompressed_mib=0)


if __name__ == "__main__":
    unittest.main()
