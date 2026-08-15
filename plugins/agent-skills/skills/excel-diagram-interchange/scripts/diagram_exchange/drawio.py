from __future__ import annotations

from base64 import b64decode
from html import unescape
from pathlib import Path
import re
from urllib.parse import unquote
import xml.etree.ElementTree as WET
import zlib

from defusedxml import ElementTree as DET

from .model import Diagram, Edge, Node, Page, Style
from .util import normalize_color, safe_id


def _decode_diagram_text(text: str, *, max_uncompressed_mib: int = 100) -> bytes:
    packed = b64decode(text.strip(), validate=True)
    limit = max_uncompressed_mib * 1024 * 1024
    decompressor = zlib.decompressobj(-15)
    raw = decompressor.decompress(packed, limit + 1)
    if len(raw) > limit or decompressor.unconsumed_tail:
        raise ValueError("Compressed draw.io page exceeds expansion limit")
    raw += decompressor.flush(limit + 1 - len(raw))
    if len(raw) > limit:
        raise ValueError("Compressed draw.io page exceeds expansion limit")
    return unquote(raw.decode("utf-8")).encode("utf-8")


def _plain_label(value: str | None, *, html_enabled: bool = False) -> str:
    if not value:
        return ""
    value = unescape(value)
    if not html_enabled:
        return value
    value = re.sub(r"<br\s*/?>", "\n", value, flags=re.I)
    return re.sub(r"<[^>]+>", "", value)


def _style_map(style: str | None) -> dict[str, str]:
    out: dict[str, str] = {}
    for item in (style or "").split(";"):
        if not item:
            continue
        if "=" in item:
            key, value = item.split("=", 1)
            out[key] = value
        else:
            out[item] = "1"
    return out


def _canonical_shape(style: dict[str, str]) -> str:
    shape = style.get("shape", "")
    if style.get("ellipse") == "1" or shape == "ellipse":
        return "ellipse"
    if style.get("rhombus") == "1" or shape == "rhombus":
        return "diamond"
    if shape in {"cylinder3", "cylinder"}:
        return "can"
    if shape in {"cloud", "hexagon", "triangle", "parallelogram"}:
        return shape
    if style.get("rounded") == "1":
        return "roundRect"
    return "rect"


def _node_style(style: dict[str, str], edge: bool = False) -> Style:
    return Style(
        fill="none" if edge else normalize_color(style.get("fillColor"), "#ffffff"),
        stroke=normalize_color(style.get("strokeColor"), "#000000"),
        stroke_width=float(style.get("strokeWidth", "1") or 1),
        dashed=style.get("dashed") == "1",
        font_color=normalize_color(style.get("fontColor"), "#000000"),
        font_size=float(style.get("fontSize", "12") or 12),
        arrow_start=style.get("startArrow", "none"),
        arrow_end=style.get("endArrow", "none"),
    )


def _model_root(root):
    if root.tag == "mxGraphModel":
        return [("Page 1", root)]
    if root.tag != "mxfile":
        raise ValueError("draw.io input must contain <mxfile> or <mxGraphModel>")
    models = []
    compressed = root.get("compressed", "true").lower() != "false"
    for index, diagram in enumerate(root.findall("diagram"), 1):
        children = list(diagram)
        if children and children[0].tag == "mxGraphModel":
            model = children[0]
        elif diagram.text and diagram.text.strip():
            data = _decode_diagram_text(diagram.text) if compressed else diagram.text.encode("utf-8")
            model = DET.fromstring(data)
        else:
            continue
        models.append((diagram.get("name", f"Page {index}"), model))
    return models


def read_drawio(path: Path) -> Diagram:
    root = DET.parse(path).getroot()
    pages: list[Page] = []
    for page_index, (name, model) in enumerate(_model_root(root), 1):
        page = Page(id=f"page_{page_index}", name=name,
                    width=float(model.get("pageWidth", "1600")), height=float(model.get("pageHeight", "900")))
        cells = model.findall("./root/mxCell")
        id_map: dict[str, str] = {}
        for z, cell in enumerate(cells):
            if cell.get("vertex") != "1":
                continue
            cell_id = cell.get("id", f"v{z}")
            node_id = safe_id(f"{page.id}_{cell_id}")
            id_map[cell_id] = node_id
            geometry = cell.find("mxGeometry")
            if geometry is None:
                continue
            sm = _style_map(cell.get("style"))
            page.nodes.append(Node(
                id=node_id, label=_plain_label(cell.get("value"), html_enabled=sm.get("html") == "1"), shape=_canonical_shape(sm),
                x=float(geometry.get("x", "0")), y=float(geometry.get("y", "0")),
                width=float(geometry.get("width", "120")), height=float(geometry.get("height", "60")),
                rotation=float(sm.get("rotation", "0") or 0), z=z, style=_node_style(sm),
                metadata={"source": "drawio", "drawio_id": cell_id},
            ))
        for z, cell in enumerate(cells):
            if cell.get("edge") != "1":
                continue
            geometry = cell.find("mxGeometry")
            points: list[list[float]] = []
            if geometry is not None:
                source_point = geometry.find("mxPoint[@as='sourcePoint']")
                target_point = geometry.find("mxPoint[@as='targetPoint']")
                if source_point is not None:
                    points.append([float(source_point.get("x", "0")), float(source_point.get("y", "0"))])
                array = geometry.find("Array[@as='points']")
                if array is not None:
                    points.extend([[float(p.get("x", "0")), float(p.get("y", "0"))] for p in array.findall("mxPoint")])
                if target_point is not None:
                    points.append([float(target_point.get("x", "0")), float(target_point.get("y", "0"))])
            sm = _style_map(cell.get("style"))
            page.edges.append(Edge(
                id=safe_id(f"{page.id}_{cell.get('id', f'e{z}')}", "e"),
                source=id_map.get(cell.get("source", "")), target=id_map.get(cell.get("target", "")),
                label=_plain_label(cell.get("value"), html_enabled=sm.get("html") == "1"), points=points, z=z, style=_node_style(sm, edge=True),
                metadata={"source": "drawio", "drawio_id": cell.get("id")},
            ))
        page = Page(id=page.id, name=page.name, width=page.width, height=page.height,
                    nodes=list(page.nodes), edges=list(page.edges), warnings=list(page.warnings))
        pages.append(page)
    return Diagram(title=path.stem, pages=pages, metadata={"source_format": "drawio"})


def _drawio_style(style: Style, shape: str, *, edge: bool = False) -> str:
    parts = ["html=0", "whiteSpace=wrap"]
    if edge:
        parts.extend(["edgeStyle=orthogonalEdgeStyle", "rounded=0", "orthogonalLoop=1", "jettySize=auto"])
        parts.append(f"startArrow={style.arrow_start}")
        parts.append(f"endArrow={style.arrow_end}")
    else:
        if shape == "ellipse":
            parts.append("ellipse=1")
        elif shape == "diamond":
            parts.append("rhombus=1")
        elif shape == "roundRect":
            parts.append("rounded=1")
        elif shape == "can":
            parts.append("shape=cylinder3")
        elif shape not in {"rect", ""}:
            parts.append(f"shape={shape}")
        parts.append(f"fillColor={style.fill if style.fill != 'none' else 'none'}")
    parts.extend([
        f"strokeColor={style.stroke}", f"strokeWidth={style.stroke_width:g}",
        f"fontColor={style.font_color}", f"fontSize={style.font_size:g}",
    ])
    if style.dashed:
        parts.append("dashed=1")
    return ";".join(parts) + ";"


def write_drawio(diagram: Diagram, path: Path) -> None:
    mxfile = WET.Element("mxfile", {"host": "app.diagrams.net", "compressed": "false"})
    for page_index, page in enumerate(diagram.pages, 1):
        d = WET.SubElement(mxfile, "diagram", {"id": page.id, "name": page.name})
        model = WET.SubElement(d, "mxGraphModel", {
            "dx": "1200", "dy": "800", "grid": "1", "gridSize": "10", "guides": "1",
            "tooltips": "1", "connect": "1", "arrows": "1", "fold": "1", "page": "1",
            "pageScale": "1", "pageWidth": str(int(page.width)), "pageHeight": str(int(page.height)),
            "math": "0", "shadow": "0",
        })
        root = WET.SubElement(model, "root")
        WET.SubElement(root, "mxCell", {"id": "0"})
        WET.SubElement(root, "mxCell", {"id": "1", "parent": "0"})
        node_ids: dict[str, str] = {}
        next_id = 2
        for node in sorted(page.nodes, key=lambda n: n.z):
            cell_id = str(next_id); next_id += 1
            node_ids[node.id] = cell_id
            cell = WET.SubElement(root, "mxCell", {
                "id": cell_id, "value": node.label, "style": _drawio_style(node.style, node.shape),
                "vertex": "1", "parent": "1",
            })
            WET.SubElement(cell, "mxGeometry", {
                "x": f"{node.x:g}", "y": f"{node.y:g}", "width": f"{node.width:g}",
                "height": f"{node.height:g}", "as": "geometry",
            })
        for edge in sorted(page.edges, key=lambda e: e.z):
            attrs = {
                "id": str(next_id), "value": edge.label, "style": _drawio_style(edge.style, "line", edge=True),
                "edge": "1", "parent": "1",
            }
            next_id += 1
            if edge.source in node_ids:
                attrs["source"] = node_ids[edge.source]
            if edge.target in node_ids:
                attrs["target"] = node_ids[edge.target]
            cell = WET.SubElement(root, "mxCell", attrs)
            geometry = WET.SubElement(cell, "mxGeometry", {"relative": "1", "as": "geometry"})
            if edge.points:
                if edge.source not in node_ids:
                    WET.SubElement(geometry, "mxPoint", {"x": f"{edge.points[0][0]:g}", "y": f"{edge.points[0][1]:g}", "as": "sourcePoint"})
                middle = edge.points[1:-1]
                if middle:
                    array = WET.SubElement(geometry, "Array", {"as": "points"})
                    for x, y in middle:
                        WET.SubElement(array, "mxPoint", {"x": f"{x:g}", "y": f"{y:g}"})
                if edge.target not in node_ids:
                    WET.SubElement(geometry, "mxPoint", {"x": f"{edge.points[-1][0]:g}", "y": f"{edge.points[-1][1]:g}", "as": "targetPoint"})
    WET.indent(mxfile, space="  ")
    path.parent.mkdir(parents=True, exist_ok=True)
    WET.ElementTree(mxfile).write(path, encoding="utf-8", xml_declaration=True)
