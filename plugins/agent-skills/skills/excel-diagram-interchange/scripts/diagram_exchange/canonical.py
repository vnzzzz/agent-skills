from __future__ import annotations

from pathlib import Path
import json
import xml.etree.ElementTree as WET

from .model import Diagram, Edge, Node, Page, Style, diagram_from_dict
from .safe_xml import parse_xml_file


def read_json(path: Path) -> Diagram:
    raw = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ValueError("Canonical JSON must be an object")
    return diagram_from_dict(raw)


def write_json(diagram: Diagram, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(diagram.to_dict(), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_xml(diagram: Diagram, path: Path) -> None:
    root = WET.Element("diagram", {"schema-version": diagram.schema_version, "title": diagram.title})
    metadata = WET.SubElement(root, "metadata")
    for key, value in sorted(diagram.metadata.items()):
        item = WET.SubElement(metadata, "item", {"key": str(key)})
        item.text = json.dumps(value, ensure_ascii=False)
    pages = WET.SubElement(root, "pages")
    for page in diagram.pages:
        p = WET.SubElement(pages, "page", {
            "id": page.id, "name": page.name, "width": str(page.width), "height": str(page.height),
        })
        warnings = WET.SubElement(p, "warnings")
        for warning in page.warnings:
            WET.SubElement(warnings, "warning").text = warning
        nodes = WET.SubElement(p, "nodes")
        for node in page.nodes:
            n = WET.SubElement(nodes, "node", {
                "id": node.id, "shape": node.shape, "x": str(node.x), "y": str(node.y),
                "width": str(node.width), "height": str(node.height), "rotation": str(node.rotation), "z": str(node.z),
            })
            WET.SubElement(n, "label").text = node.label
            _write_style(n, node.style)
            _write_metadata(n, node.metadata)
        edges = WET.SubElement(p, "edges")
        for edge in page.edges:
            attrs = {"id": edge.id, "z": str(edge.z)}
            if edge.source is not None:
                attrs["source"] = edge.source
            if edge.target is not None:
                attrs["target"] = edge.target
            e = WET.SubElement(edges, "edge", attrs)
            WET.SubElement(e, "label").text = edge.label
            points = WET.SubElement(e, "points")
            for point in edge.points:
                if len(point) >= 2:
                    WET.SubElement(points, "point", {"x": str(point[0]), "y": str(point[1])})
            _write_style(e, edge.style)
            _write_metadata(e, edge.metadata)
    WET.indent(root, space="  ")
    path.parent.mkdir(parents=True, exist_ok=True)
    WET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def _write_style(parent, style: Style) -> None:
    WET.SubElement(parent, "style", {key.replace("_", "-"): str(value).lower() if isinstance(value, bool) else str(value)
                                            for key, value in vars(style).items()})


def _write_metadata(parent, values: dict) -> None:
    metadata = WET.SubElement(parent, "metadata")
    for key, value in sorted(values.items()):
        item = WET.SubElement(metadata, "item", {"key": str(key)})
        item.text = json.dumps(value, ensure_ascii=False)


def _read_style(parent) -> Style:
    elem = parent.find("style")
    if elem is None:
        return Style()
    raw: dict[str, object] = {}
    for key, value in elem.attrib.items():
        normalized = key.replace("-", "_")
        if normalized in {"stroke_width", "font_size"}:
            raw[normalized] = float(value)
        elif normalized == "dashed":
            raw[normalized] = value.lower() == "true"
        else:
            raw[normalized] = value
    return Style(**raw)


def _read_metadata(parent) -> dict:
    out: dict = {}
    metadata = parent.find("metadata")
    if metadata is None:
        return out
    for item in metadata.findall("item"):
        key = item.get("key")
        if not key:
            continue
        text = item.text or "null"
        try:
            out[key] = json.loads(text)
        except json.JSONDecodeError:
            out[key] = text
    return out


def read_xml(path: Path) -> Diagram:
    root = parse_xml_file(path)
    if root.tag != "diagram":
        raise ValueError("Canonical XML root must be <diagram>")
    pages: list[Page] = []
    for p in root.findall("./pages/page"):
        nodes: list[Node] = []
        for n in p.findall("./nodes/node"):
            nodes.append(Node(
                id=n.attrib["id"], label=n.findtext("label", ""), shape=n.get("shape", "rect"),
                x=float(n.get("x", "0")), y=float(n.get("y", "0")),
                width=float(n.get("width", "120")), height=float(n.get("height", "60")),
                rotation=float(n.get("rotation", "0")), z=int(n.get("z", "0")),
                style=_read_style(n), metadata=_read_metadata(n),
            ))
        edges: list[Edge] = []
        for e in p.findall("./edges/edge"):
            points = [[float(pt.get("x", "0")), float(pt.get("y", "0"))] for pt in e.findall("./points/point")]
            edges.append(Edge(
                id=e.attrib["id"], source=e.get("source"), target=e.get("target"),
                label=e.findtext("label", ""), points=points, z=int(e.get("z", "0")),
                style=_read_style(e), metadata=_read_metadata(e),
            ))
        pages.append(Page(
            id=p.attrib["id"], name=p.get("name", p.attrib["id"]),
            width=float(p.get("width", "1600")), height=float(p.get("height", "900")),
            nodes=nodes, edges=edges,
            warnings=[w.text or "" for w in p.findall("./warnings/warning")],
        ))
    return Diagram(
        title=root.get("title", "Diagram"), pages=pages,
        schema_version=root.get("schema-version", "1.0"), metadata=_read_metadata(root),
    )
