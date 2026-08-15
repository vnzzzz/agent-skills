from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import re
from html import escape
from math import hypot
from zipfile import ZIP_DEFLATED, ZipFile
import xml.etree.ElementTree as WET

from defusedxml import ElementTree as DET

from .model import Diagram, Edge, Node, Page, Style
from .security import preflight_xlsx
from .util import normalize_color, resolve_part, safe_id

NS = {
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "xdr": "http://schemas.openxmlformats.org/drawingml/2006/spreadsheetDrawing",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "s": "http://schemas.openxmlformats.org/spreadsheetml/2006/main",
    "pr": "http://schemas.openxmlformats.org/package/2006/relationships",
}
EMU_PER_PIXEL = 9525.0
DEFAULT_COL_PX = 64.0
DEFAULT_ROW_PX = 20.0
CONNECTOR_PRESETS = {
    "line", "lineInv", "straightConnector1",
    "bentConnector2", "bentConnector3", "bentConnector4", "bentConnector5",
    "curvedConnector2", "curvedConnector3", "curvedConnector4", "curvedConnector5",
}
DRAWINGML_ARROW_TYPES = {"none", "triangle", "stealth", "diamond", "oval", "arrow"}
DRAWINGML_ARROW_ALIASES = {
    "classic": "triangle",
    "block": "triangle",
    "open": "arrow",
}

for prefix, uri in NS.items():
    if prefix not in {"s", "pr"}:
        WET.register_namespace(prefix, uri)


def _parse(data: bytes):
    return DET.fromstring(data)


def _rels(zf: ZipFile, rels_path: str) -> dict[str, tuple[str, str, str]]:
    if rels_path not in zf.namelist():
        return {}
    root = _parse(zf.read(rels_path))
    out: dict[str, tuple[str, str, str]] = {}
    for rel in root.findall("pr:Relationship", NS):
        rid = rel.get("Id")
        target = rel.get("Target")
        if rid and target:
            out[rid] = (target, rel.get("Type", ""), rel.get("TargetMode", ""))
    return out


def _rels_path(part: str) -> str:
    p = Path(part)
    return str(p.parent / "_rels" / f"{p.name}.rels").replace("\\", "/")


def _column_width_to_px(width: float) -> float:
    # Approximation used only for two-cell anchors; raw anchor metadata is preserved.
    return max(1.0, int(((256.0 * width + int(128 / 7)) / 256.0) * 7.0))


def _grid_metrics(sheet_root) -> tuple[dict[int, float], dict[int, float], float, float]:
    sheet_format = sheet_root.find("s:sheetFormatPr", NS)
    default_col = DEFAULT_COL_PX
    default_row = DEFAULT_ROW_PX
    if sheet_format is not None:
        if sheet_format.get("defaultColWidth"):
            default_col = _column_width_to_px(float(sheet_format.get("defaultColWidth", "8.43")))
        if sheet_format.get("defaultRowHeight"):
            default_row = float(sheet_format.get("defaultRowHeight", "15")) * 96.0 / 72.0
    cols: dict[int, float] = {}
    cols_root = sheet_root.find("s:cols", NS)
    if cols_root is not None:
        for col in cols_root.findall("s:col", NS):
            start = int(col.get("min", "1")) - 1
            end = int(col.get("max", "1")) - 1
            width = _column_width_to_px(float(col.get("width", "8.43")))
            for index in range(start, min(end, 16383) + 1):
                cols[index] = width
    rows: dict[int, float] = {}
    sheet_data = sheet_root.find("s:sheetData", NS)
    if sheet_data is not None:
        for row in sheet_data.findall("s:row", NS):
            if row.get("ht"):
                rows[int(row.get("r", "1")) - 1] = float(row.get("ht", "15")) * 96.0 / 72.0
    return cols, rows, default_col, default_row


def _axis_position(index: int, offset_emu: int, sizes: dict[int, float], default: float) -> float:
    return sum(sizes.get(i, default) for i in range(max(0, index))) + offset_emu / EMU_PER_PIXEL


def _marker(anchor, name: str, cols, rows, default_col, default_row) -> tuple[float, float, dict[str, int]]:
    marker = anchor.find(f"xdr:{name}", NS)
    if marker is None:
        return 0.0, 0.0, {}
    col = int(marker.findtext("xdr:col", "0", NS))
    col_off = int(marker.findtext("xdr:colOff", "0", NS))
    row = int(marker.findtext("xdr:row", "0", NS))
    row_off = int(marker.findtext("xdr:rowOff", "0", NS))
    return (
        _axis_position(col, col_off, cols, default_col),
        _axis_position(row, row_off, rows, default_row),
        {"col": col, "colOff": col_off, "row": row, "rowOff": row_off},
    )


def _anchor_geometry(anchor, cols, rows, default_col, default_row):
    local = anchor.tag.rsplit("}", 1)[-1]
    raw: dict[str, object] = {"kind": local}
    if local == "absoluteAnchor":
        pos = anchor.find("xdr:pos", NS)
        ext = anchor.find("xdr:ext", NS)
        x = int(pos.get("x", "0")) / EMU_PER_PIXEL if pos is not None else 0.0
        y = int(pos.get("y", "0")) / EMU_PER_PIXEL if pos is not None else 0.0
        w = int(ext.get("cx", "0")) / EMU_PER_PIXEL if ext is not None else 1.0
        h = int(ext.get("cy", "0")) / EMU_PER_PIXEL if ext is not None else 1.0
        raw.update({"x": int(pos.get("x", "0")) if pos is not None else 0, "y": int(pos.get("y", "0")) if pos is not None else 0,
                    "cx": int(ext.get("cx", "0")) if ext is not None else 0, "cy": int(ext.get("cy", "0")) if ext is not None else 0})
        return x, y, max(w, 1.0), max(h, 1.0), raw
    x1, y1, from_raw = _marker(anchor, "from", cols, rows, default_col, default_row)
    raw["from"] = from_raw
    if local == "oneCellAnchor":
        ext = anchor.find("xdr:ext", NS)
        w = int(ext.get("cx", "0")) / EMU_PER_PIXEL if ext is not None else 1.0
        h = int(ext.get("cy", "0")) / EMU_PER_PIXEL if ext is not None else 1.0
        raw.update({"cx": int(ext.get("cx", "0")) if ext is not None else 0, "cy": int(ext.get("cy", "0")) if ext is not None else 0})
        return x1, y1, max(w, 1.0), max(h, 1.0), raw
    x2, y2, to_raw = _marker(anchor, "to", cols, rows, default_col, default_row)
    raw["to"] = to_raw
    raw["editAs"] = anchor.get("editAs")
    return min(x1, x2), min(y1, y2), max(abs(x2 - x1), 1.0), max(abs(y2 - y1), 1.0), raw


def _shape_text(element) -> str:
    paragraphs: list[str] = []
    for paragraph in element.findall(".//a:p", NS):
        text = "".join(t.text or "" for t in paragraph.findall(".//a:t", NS))
        if text:
            paragraphs.append(text)
    if paragraphs:
        return "\n".join(paragraphs)
    return "".join(t.text or "" for t in element.findall(".//a:t", NS))


def _solid_color(parent, default: str) -> str:
    solid = parent.find("a:solidFill", NS) if parent is not None else None
    if solid is None:
        return default
    srgb = solid.find("a:srgbClr", NS)
    return normalize_color(srgb.get("val") if srgb is not None else None, default)


def _style(element, *, edge: bool = False) -> Style:
    sppr = element.find("xdr:spPr", NS)
    fill = "none" if edge else "#ffffff"
    stroke = "#000000"
    stroke_width = 1.0
    dashed = False
    rotation = 0.0
    arrow_start = "none"
    arrow_end = "none"
    if sppr is not None:
        fill = _solid_color(sppr, fill)
        if sppr.find("a:noFill", NS) is not None:
            fill = "none"
        line = sppr.find("a:ln", NS)
        if line is not None:
            stroke = _solid_color(line, stroke)
            stroke_width = int(line.get("w", str(int(EMU_PER_PIXEL)))) / EMU_PER_PIXEL
            dashed = line.find("a:prstDash", NS) is not None and line.find("a:prstDash", NS).get("val", "solid") != "solid"
            head = line.find("a:headEnd", NS)
            tail = line.find("a:tailEnd", NS)
            arrow_start = head.get("type", "none") if head is not None else "none"
            arrow_end = tail.get("type", "none") if tail is not None else "none"
    first_run = element.find(".//a:rPr", NS)
    if first_run is None:
        first_run = element.find(".//a:defRPr", NS)
    font_size = float(first_run.get("sz", "1200")) / 100.0 if first_run is not None else 12.0
    font_color = _solid_color(first_run, "#000000") if first_run is not None else "#000000"
    return Style(fill=fill, stroke=stroke, stroke_width=max(stroke_width, 0.1), dashed=dashed,
                 font_color=font_color, font_size=font_size, arrow_start=arrow_start, arrow_end=arrow_end)


def _rotation(element) -> float:
    xfrm = element.find("xdr:spPr/a:xfrm", NS)
    return int(xfrm.get("rot", "0")) / 60000.0 if xfrm is not None else 0.0


def _connector_points(element, x: float, y: float, width: float, height: float, *, preset: str | None = None) -> list[list[float]]:
    xfrm = element.find("xdr:spPr/a:xfrm", NS)
    flip_h = xfrm is not None and xfrm.get("flipH", "0") in {"1", "true"}
    flip_v = xfrm is not None and xfrm.get("flipV", "0") in {"1", "true"}
    # Some producers, including generic worksheet drawing APIs, serialize connectors
    # as ordinary xdr:sp elements with a connector preset rather than xdr:cxnSp.
    # lineInv encodes the inverse diagonal without xfrm flip flags.
    if preset == "lineInv":
        flip_v = not flip_v
    start_x, end_x = (x + width, x) if flip_h else (x, x + width)
    start_y, end_y = (y + height, y) if flip_v else (y, y + height)
    return [[start_x, start_y], [end_x, end_y]]


def _distance_to_node(point: list[float], node: Node) -> float:
    px, py = point
    nearest_x = min(max(px, node.x), node.x + node.width)
    nearest_y = min(max(py, node.y), node.y + node.height)
    return hypot(px - nearest_x, py - nearest_y)


def _infer_endpoint(point: list[float], nodes: list[Node], *, exclude: str | None = None) -> str | None:
    candidates = [(_distance_to_node(point, node), node.id) for node in nodes if node.id != exclude]
    if not candidates:
        return None
    distance, node_id = min(candidates)
    return node_id if distance <= 80.0 else None


def _preset_shape(element, default: str) -> str:
    geom = element.find("xdr:spPr/a:prstGeom", NS)
    return geom.get("prst", default) if geom is not None else default


def read_xlsx(path: Path) -> Diagram:
    preflight_xlsx(path)
    with ZipFile(path) as zf:
        workbook_part = "xl/workbook.xml"
        workbook = _parse(zf.read(workbook_part))
        workbook_rels = _rels(zf, _rels_path(workbook_part))
        pages: list[Page] = []
        for page_index, sheet in enumerate(workbook.findall("s:sheets/s:sheet", NS), start=1):
            rid = sheet.get(f"{{{NS['r']}}}id")
            if not rid or rid not in workbook_rels:
                continue
            target, _, mode = workbook_rels[rid]
            if mode == "External":
                raise ValueError("External worksheet relationship is not allowed")
            sheet_part = resolve_part(workbook_part, target)
            sheet_root = _parse(zf.read(sheet_part))
            cols, rows, default_col, default_row = _grid_metrics(sheet_root)
            sheet_rels = _rels(zf, _rels_path(sheet_part))
            drawing_ref = sheet_root.find("s:drawing", NS)
            page = Page(id=f"page_{page_index}", name=sheet.get("name", f"Sheet{page_index}"))
            if drawing_ref is None:
                page.warnings.append("No drawing part found; cell contents were intentionally ignored.")
                pages.append(page)
                continue
            drawing_rid = drawing_ref.get(f"{{{NS['r']}}}id")
            if not drawing_rid or drawing_rid not in sheet_rels:
                page.warnings.append("Drawing relationship is missing.")
                pages.append(page)
                continue
            drawing_target, _, drawing_mode = sheet_rels[drawing_rid]
            if drawing_mode == "External":
                raise ValueError("External drawing relationship is not allowed")
            drawing_part = resolve_part(sheet_part, drawing_target)
            drawing = _parse(zf.read(drawing_part))
            id_map: dict[str, str] = {}
            pending_edges: list[tuple[Edge, str | None, str | None]] = []
            z = 0
            for anchor in list(drawing):
                local = anchor.tag.rsplit("}", 1)[-1]
                if local not in {"absoluteAnchor", "oneCellAnchor", "twoCellAnchor"}:
                    page.warnings.append(f"Ignored unsupported drawing anchor: {local}")
                    continue
                x, y, w, h, anchor_raw = _anchor_geometry(anchor, cols, rows, default_col, default_row)
                shape = anchor.find("xdr:sp", NS)
                connector = anchor.find("xdr:cxnSp", NS)
                group = anchor.find("xdr:grpSp", NS)
                picture = anchor.find("xdr:pic", NS)
                if shape is not None:
                    c_nv = shape.find("xdr:nvSpPr/xdr:cNvPr", NS)
                    xml_id = c_nv.get("id", str(z + 1)) if c_nv is not None else str(z + 1)
                    preset = _preset_shape(shape, "rect")
                    if preset in CONNECTOR_PRESETS:
                        edge = Edge(
                            id=safe_id(f"{page.id}_edge_{xml_id}", "e"), source=None, target=None,
                            label=_shape_text(shape), points=_connector_points(shape, x, y, w, h, preset=preset), z=z,
                            style=_style(shape, edge=True),
                            metadata={"source": "xlsx", "drawing_part": drawing_part,
                                      "excel_shape_id": xml_id, "anchor": anchor_raw,
                                      "preset": preset, "serialized_as": "xdr:sp"},
                        )
                        pending_edges.append((edge, None, None))
                    else:
                        node_id = safe_id(f"{page.id}_shape_{xml_id}")
                        id_map[xml_id] = node_id
                        page.nodes.append(Node(
                            id=node_id, label=_shape_text(shape), shape=preset,
                            x=x, y=y, width=w, height=h, rotation=_rotation(shape), z=z,
                            style=_style(shape), metadata={"source": "xlsx", "drawing_part": drawing_part,
                                                           "excel_shape_id": xml_id, "anchor": anchor_raw},
                        ))
                elif connector is not None:
                    c_nv = connector.find("xdr:nvCxnSpPr/xdr:cNvPr", NS)
                    xml_id = c_nv.get("id", str(z + 1)) if c_nv is not None else str(z + 1)
                    cprops = connector.find("xdr:nvCxnSpPr/xdr:cNvCxnSpPr", NS)
                    start = cprops.find("a:stCxn", NS) if cprops is not None else None
                    end = cprops.find("a:endCxn", NS) if cprops is not None else None
                    edge = Edge(
                        id=safe_id(f"{page.id}_edge_{xml_id}", "e"), source=None, target=None,
                        label=_shape_text(connector), points=_connector_points(connector, x, y, w, h, preset=_preset_shape(connector, "line")), z=z,
                        style=_style(connector, edge=True),
                        metadata={"source": "xlsx", "drawing_part": drawing_part,
                                  "excel_shape_id": xml_id, "anchor": anchor_raw,
                                  "preset": _preset_shape(connector, "line")},
                    )
                    pending_edges.append((edge, start.get("id") if start is not None else None,
                                          end.get("id") if end is not None else None))
                elif group is not None:
                    page.warnings.append("Group shape was ignored in v1; ungroup it in Excel for conversion.")
                elif picture is not None:
                    page.warnings.append("Picture was ignored; this profile is shape-only.")
                else:
                    page.warnings.append("Unsupported drawing object was ignored.")
                z += 1
            for edge, start_id, end_id in pending_edges:
                edge.source = id_map.get(start_id or "")
                edge.target = id_map.get(end_id or "")
                if edge.points:
                    if edge.source is None:
                        edge.source = _infer_endpoint(edge.points[0], page.nodes)
                    if edge.target is None:
                        edge.target = _infer_endpoint(edge.points[-1], page.nodes, exclude=edge.source)
                if edge.source is None or edge.target is None:
                    page.warnings.append(f"Connector {edge.id} has unresolved endpoint(s).")
                elif start_id is None or end_id is None:
                    edge.metadata["endpoint_resolution"] = "geometry-inferred"
                page.edges.append(edge)
            if page.nodes:
                page.width = max(n.x + n.width for n in page.nodes) + 80
                page.height = max(n.y + n.height for n in page.nodes) + 80
            page = Page(id=page.id, name=page.name, width=page.width, height=page.height,
                        nodes=list(page.nodes), edges=list(page.edges), warnings=list(page.warnings))
            pages.append(page)
    return Diagram(title=path.stem, pages=pages, metadata={"source_format": "xlsx", "cells_ignored": True})


def _xml(tag: str, attrs: dict[str, object] | None = None, text: str | None = None):
    el = WET.Element(tag, {k: str(v) for k, v in (attrs or {}).items()})
    if text is not None:
        el.text = text
    return el


def _append_text_body(parent, label: str, style: Style) -> None:
    tx = WET.SubElement(parent, f"{{{NS['xdr']}}}txBody")
    WET.SubElement(tx, f"{{{NS['a']}}}bodyPr", {"wrap": "square"})
    WET.SubElement(tx, f"{{{NS['a']}}}lstStyle")
    lines = label.splitlines() or [""]
    for line in lines:
        p = WET.SubElement(tx, f"{{{NS['a']}}}p")
        r = WET.SubElement(p, f"{{{NS['a']}}}r")
        rpr = WET.SubElement(r, f"{{{NS['a']}}}rPr", {"lang": "ja-JP", "sz": str(int(style.font_size * 100))})
        solid = WET.SubElement(rpr, f"{{{NS['a']}}}solidFill")
        WET.SubElement(solid, f"{{{NS['a']}}}srgbClr", {"val": style.font_color.lstrip("#")})
        WET.SubElement(r, f"{{{NS['a']}}}t").text = line
        WET.SubElement(p, f"{{{NS['a']}}}endParaRPr", {"lang": "ja-JP", "sz": str(int(style.font_size * 100))})


def _drawingml_arrow(value: str) -> str:
    mapped = DRAWINGML_ARROW_ALIASES.get(value, value)
    return mapped if mapped in DRAWINGML_ARROW_TYPES else "none"


def _append_sppr(parent, shape: str, style: Style, width_emu: int, height_emu: int, rotation: float = 0.0,
                  *, flip_h: bool = False, flip_v: bool = False) -> None:
    sppr = WET.SubElement(parent, f"{{{NS['xdr']}}}spPr")
    xattrs: dict[str, str] = {}
    if rotation:
        xattrs["rot"] = str(int(rotation * 60000))
    if flip_h:
        xattrs["flipH"] = "1"
    if flip_v:
        xattrs["flipV"] = "1"
    xfrm = WET.SubElement(sppr, f"{{{NS['a']}}}xfrm", xattrs)
    WET.SubElement(xfrm, f"{{{NS['a']}}}off", {"x": "0", "y": "0"})
    WET.SubElement(xfrm, f"{{{NS['a']}}}ext", {"cx": str(width_emu), "cy": str(height_emu)})
    geom = WET.SubElement(sppr, f"{{{NS['a']}}}prstGeom", {"prst": shape})
    WET.SubElement(geom, f"{{{NS['a']}}}avLst")
    if style.fill == "none":
        WET.SubElement(sppr, f"{{{NS['a']}}}noFill")
    else:
        solid = WET.SubElement(sppr, f"{{{NS['a']}}}solidFill")
        WET.SubElement(solid, f"{{{NS['a']}}}srgbClr", {"val": style.fill.lstrip("#")})
    line = WET.SubElement(sppr, f"{{{NS['a']}}}ln", {"w": str(max(1, int(style.stroke_width * EMU_PER_PIXEL)))})
    line_fill = WET.SubElement(line, f"{{{NS['a']}}}solidFill")
    WET.SubElement(line_fill, f"{{{NS['a']}}}srgbClr", {"val": style.stroke.lstrip("#")})
    if style.dashed:
        WET.SubElement(line, f"{{{NS['a']}}}prstDash", {"val": "dash"})
    arrow_start = _drawingml_arrow(style.arrow_start)
    arrow_end = _drawingml_arrow(style.arrow_end)
    if arrow_start != "none":
        WET.SubElement(line, f"{{{NS['a']}}}headEnd", {"type": arrow_start})
    if arrow_end != "none":
        WET.SubElement(line, f"{{{NS['a']}}}tailEnd", {"type": arrow_end})


def _absolute_anchor(root, x: float, y: float, width: float, height: float):
    anchor = WET.SubElement(root, f"{{{NS['xdr']}}}absoluteAnchor")
    WET.SubElement(anchor, f"{{{NS['xdr']}}}pos", {"x": str(int(x * EMU_PER_PIXEL)), "y": str(int(y * EMU_PER_PIXEL))})
    WET.SubElement(anchor, f"{{{NS['xdr']}}}ext", {"cx": str(max(1, int(width * EMU_PER_PIXEL))), "cy": str(max(1, int(height * EMU_PER_PIXEL)))})
    return anchor


def _drawing_xml(page: Page) -> bytes:
    root = WET.Element(f"{{{NS['xdr']}}}wsDr")
    numeric_ids: dict[str, int] = {}
    next_id = 2
    for node in sorted(page.nodes, key=lambda n: n.z):
        numeric_ids[node.id] = next_id
        next_id += 1
        anchor = _absolute_anchor(root, node.x, node.y, node.width, node.height)
        sp = WET.SubElement(anchor, f"{{{NS['xdr']}}}sp", {"macro": "", "textlink": ""})
        nv = WET.SubElement(sp, f"{{{NS['xdr']}}}nvSpPr")
        WET.SubElement(nv, f"{{{NS['xdr']}}}cNvPr", {"id": str(numeric_ids[node.id]), "name": node.id})
        WET.SubElement(nv, f"{{{NS['xdr']}}}cNvSpPr")
        _append_sppr(sp, node.shape or "rect", node.style, int(node.width * EMU_PER_PIXEL), int(node.height * EMU_PER_PIXEL), node.rotation)
        _append_text_body(sp, node.label, node.style)
        WET.SubElement(anchor, f"{{{NS['xdr']}}}clientData")
    for edge in sorted(page.edges, key=lambda e: e.z):
        if len(edge.points) >= 2:
            sx, sy = edge.points[0]
            tx, ty = edge.points[-1]
        else:
            source = next((n for n in page.nodes if n.id == edge.source), None)
            target = next((n for n in page.nodes if n.id == edge.target), None)
            sx, sy = ((source.x + source.width / 2, source.y + source.height / 2) if source else (0.0, 0.0))
            tx, ty = ((target.x + target.width / 2, target.y + target.height / 2) if target else (sx + 100.0, sy))
        x, y = min(sx, tx), min(sy, ty)
        w, h = max(abs(tx - sx), 1.0), max(abs(ty - sy), 1.0)
        anchor = _absolute_anchor(root, x, y, w, h)
        cxn = WET.SubElement(anchor, f"{{{NS['xdr']}}}cxnSp", {"macro": ""})
        nv = WET.SubElement(cxn, f"{{{NS['xdr']}}}nvCxnSpPr")
        WET.SubElement(nv, f"{{{NS['xdr']}}}cNvPr", {"id": str(next_id), "name": edge.id})
        next_id += 1
        cnv = WET.SubElement(nv, f"{{{NS['xdr']}}}cNvCxnSpPr")
        if edge.source in numeric_ids:
            WET.SubElement(cnv, f"{{{NS['a']}}}stCxn", {"id": str(numeric_ids[edge.source]), "idx": "1"})
        if edge.target in numeric_ids:
            WET.SubElement(cnv, f"{{{NS['a']}}}endCxn", {"id": str(numeric_ids[edge.target]), "idx": "1"})
        _append_sppr(cxn, "line", edge.style, int(w * EMU_PER_PIXEL), int(h * EMU_PER_PIXEL),
                     flip_h=tx < sx, flip_v=ty < sy)
        if edge.label:
            _append_text_body(cxn, edge.label, edge.style)
        WET.SubElement(anchor, f"{{{NS['xdr']}}}clientData")
    return WET.tostring(root, encoding="utf-8", xml_declaration=True)


def _safe_sheet_name(name: str, used: set[str]) -> str:
    cleaned = re.sub(r"[\\/*?:\[\]]", "_", name).strip("'")[:31] or "Diagram"
    base = cleaned
    index = 2
    while cleaned.casefold() in used:
        suffix = f"_{index}"
        cleaned = base[:31 - len(suffix)] + suffix
        index += 1
    used.add(cleaned.casefold())
    return cleaned


def write_xlsx(diagram: Diagram, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    pages = diagram.pages or [Page(id="page_1", name="Diagram")]
    used: set[str] = set()
    sheet_names = [_safe_sheet_name(p.name, used) for p in pages]
    content_types = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>',
                     '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">',
                     '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
                     '<Default Extension="xml" ContentType="application/xml"/>',
                     '<Override PartName="/xl/workbook.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet.main+xml"/>',
                     '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
                     '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>']
    for i in range(1, len(pages) + 1):
        content_types.append(f'<Override PartName="/xl/worksheets/sheet{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.spreadsheetml.worksheet+xml"/>')
        content_types.append(f'<Override PartName="/xl/drawings/drawing{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.drawing+xml"/>')
    content_types.append('</Types>')
    root_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">
<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="xl/workbook.xml"/>
<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>
<Relationship Id="rId3" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/extended-properties" Target="docProps/app.xml"/>
</Relationships>'''
    sheets_xml = "".join(f'<sheet name="{escape(name, quote=True)}" sheetId="{i}" r:id="rId{i}"/>' for i, name in enumerate(sheet_names, 1))
    workbook = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<workbook xmlns="{NS['s']}" xmlns:r="{NS['r']}"><sheets>{sheets_xml}</sheets></workbook>'''
    wb_rels = ['<?xml version="1.0" encoding="UTF-8" standalone="yes"?>', '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">']
    for i in range(1, len(pages) + 1):
        wb_rels.append(f'<Relationship Id="rId{i}" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/worksheet" Target="worksheets/sheet{i}.xml"/>')
    wb_rels.append('</Relationships>')
    now = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    core = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><dc:title>{escape(diagram.title)}</dc:title><dc:creator>excel-diagram-interchange</dc:creator><dcterms:created xsi:type="dcterms:W3CDTF">{now}</dcterms:created><dcterms:modified xsi:type="dcterms:W3CDTF">{now}</dcterms:modified></cp:coreProperties>'''
    app = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>excel-diagram-interchange</Application></Properties>'''
    with ZipFile(path, "w", ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", "".join(content_types))
        zf.writestr("_rels/.rels", root_rels)
        zf.writestr("docProps/core.xml", core)
        zf.writestr("docProps/app.xml", app)
        zf.writestr("xl/workbook.xml", workbook)
        zf.writestr("xl/_rels/workbook.xml.rels", "".join(wb_rels))
        for i, page in enumerate(pages, 1):
            sheet = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><worksheet xmlns="{NS['s']}" xmlns:r="{NS['r']}"><sheetData/><drawing r:id="rId1"/></worksheet>'''
            sheet_rels = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/drawing" Target="../drawings/drawing{i}.xml"/></Relationships>'''
            zf.writestr(f"xl/worksheets/sheet{i}.xml", sheet)
            zf.writestr(f"xl/worksheets/_rels/sheet{i}.xml.rels", sheet_rels)
            zf.writestr(f"xl/drawings/drawing{i}.xml", _drawing_xml(page))
