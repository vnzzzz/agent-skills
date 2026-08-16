from __future__ import annotations

from pathlib import Path
import re
import xml.etree.ElementTree as ET
from xml.parsers import expat

MIN_EXPAT_VERSION = (2, 7, 2)
_VERSION_PATTERN = re.compile(r"(\d+)\.(\d+)\.(\d+)")


def _version_tuple(version: str) -> tuple[int, int, int]:
    match = _VERSION_PATTERN.search(version)
    if match is None:
        raise RuntimeError(f"Unable to parse Expat version: {version}")
    return tuple(int(part) for part in match.groups())


def require_safe_expat() -> None:
    if _version_tuple(expat.EXPAT_VERSION) < MIN_EXPAT_VERSION:
        raise RuntimeError(
            f"Expat {expat.EXPAT_VERSION} is unsupported; "
            "Expat 2.7.2 or newer is required for untrusted XML"
        )


def _reject_doctype(*_args: object) -> None:
    raise ValueError("DOCTYPE declarations are not allowed")


def validate_xml_bytes(data: bytes) -> None:
    require_safe_expat()
    parser = expat.ParserCreate()
    parser.StartDoctypeDeclHandler = _reject_doctype
    try:
        parser.Parse(data, True)
    except ValueError:
        raise
    except expat.ExpatError as exc:
        raise ValueError(f"Invalid XML: {exc}") from exc


def parse_xml_bytes(data: bytes) -> ET.Element:
    validate_xml_bytes(data)
    try:
        return ET.fromstring(data)
    except ET.ParseError as exc:
        raise ValueError(f"Invalid XML: {exc}") from exc


def parse_xml_file(path: Path) -> ET.Element:
    return parse_xml_bytes(path.read_bytes())
