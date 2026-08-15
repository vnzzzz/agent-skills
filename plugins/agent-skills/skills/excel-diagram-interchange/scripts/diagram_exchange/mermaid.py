from __future__ import annotations

from collections import defaultdict, deque
from html import unescape
import json
from pathlib import Path
import re

from .model import Diagram, Edge, Node, Page, Style
from .util import normalize_color, safe_id

HEADER_RE = re.compile(r"^(?:flowchart|graph)\s+(TB|TD|BT|LR|RL)\s*$", re.I)
META_RE = re.compile(r"^%%\s*diagram-interchange:\s*(\{.*\})\s*$")
STYLE_RE = re.compile(r"^style\s+([A-Za-z][\w-]*)\s+(.+)$")
EDGE_RE = re.compile(
    r"^\s*([A-Za-z][\w-]*)(.*?)\s*(-->|---|-.->|==>|<-->|<--|<-.->)\s*(?:\|([^|]*)\|)?\s*([A-Za-z][\w-]*)(.*?)\s*$"
)
NODE_ONLY_RE = re.compile(r"^\s*([A-Za-z][\w-]*)(.+)\s*$")
FORBIDDEN_PREFIXES = ("click ", "classdef ", "class ", "linkstyle ", "accdescr", "acctitle", "%%{")


def _quoted_text(value: str) -> str:
    value = value.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {'"', "'", "`"}:
        value = value[1:-1]
    return unescape(value.replace("<br/>", "\n").replace("<br>", "\n"))


def _parse_node_suffix(suffix: str) -> tuple[str, str]:
    s = suffix.strip()
    patterns = [
        (r'^\[\("(.*)"\)\]$', "can"),
        (r'^\(\("(.*)"\)\)$', "ellipse"),
        (r'^\{"(.*)"\}$', "diamond"),
        (r'^\(\["(.*)"\]\)$', "roundRect"),
        (r'^\("(.*)"\)$', "roundRect"),
        (r'^\["(.*)"\]$', "rect"),
        (r'^\[/(.*)/\]$', "parallelogram"),
        (r'^\[\\(.*)\\\]$', "parallelogram"),
        (r'^\[([^\]]*)\]$', "rect"),
        (r'^\(([^)]*)\)$', "roundRect"),
        (r'^\{([^}]*)\}$', "diamond"),
    ]
    for pattern, shape in patterns:
        match = re.match(pattern, s)
        if match:
            return _quoted_text(match.group(1)), shape
    return "", "rect"


def _parse_style(value: str, current: Style) -> Style:
    raw = {item.split(":", 1)[0].strip(): item.split(":", 1)[1].strip()
           for item in value.split(",") if ":" in item}
    return Style(
        fill=normalize_color(raw.get("fill"), current.fill) if raw.get("fill") != "none" else "none",
        stroke=normalize_color(raw.get("stroke"), current.stroke),
        stroke_width=float(raw.get("stroke-width", str(current.stroke_width)).replace("px", "") or current.stroke_width),
        dashed="dash" in raw.get("stroke-dasharray", "") or current.dashed,
        font_color=normalize_color(raw.get("color"), current.font_color),
        font_size=current.font_size,
        arrow_start=current.arrow_start,
        arrow_end=current.arrow_end,
    )


def _layout(page: Page, direction: str) -> None:
    if all("mermaid_geometry" in n.metadata for n in page.nodes):
        for n in page.nodes:
            geom = n.metadata["mermaid_geometry"]
            n.x, n.y = float(geom["x"]), float(geom["y"])
            n.width, n.height = float(geom["width"]), float(geom["height"])
            n.rotation = float(geom.get("rotation", 0))
        return
    node_ids = [n.id for n in page.nodes]
    indegree = {node_id: 0 for node_id in node_ids}
    outgoing: dict[str, list[str]] = defaultdict(list)
    for edge in page.edges:
        if edge.source in indegree and edge.target in indegree:
            outgoing[edge.source].append(edge.target)
            indegree[edge.target] += 1
    queue = deque(sorted([node for node, degree in indegree.items() if degree == 0]))
    rank = {node: 0 for node in queue}
    visited: set[str] = set()
    while queue:
        current = queue.popleft(); visited.add(current)
        for target in outgoing[current]:
            rank[target] = max(rank.get(target, 0), rank.get(current, 0) + 1)
            indegree[target] -= 1
            if indegree[target] == 0:
                queue.append(target)
    for node_id in node_ids:
        if node_id not in visited:
            rank[node_id] = max(rank.values(), default=0) + 1
    buckets: dict[int, list[str]] = defaultdict(list)
    for node_id in node_ids:
        buckets[rank.get(node_id, 0)].append(node_id)
    by_id = {n.id: n for n in page.nodes}
    horizontal = direction.upper() in {"LR", "RL"}
    reverse = direction.upper() in {"RL", "BT"}
    max_rank = max(buckets, default=0)
    for r, ids in sorted(buckets.items()):
        display_rank = max_rank - r if reverse else r
        for index, node_id in enumerate(sorted(ids)):
            node = by_id[node_id]
            if horizontal:
                node.x, node.y = 80 + display_rank * 240, 80 + index * 120
            else:
                node.x, node.y = 80 + index * 220, 80 + display_rank * 140
    page.width = max((n.x + n.width for n in page.nodes), default=800) + 80
    page.height = max((n.y + n.height for n in page.nodes), default=500) + 80


def read_mermaid(path: Path) -> Diagram:
    lines = path.read_text(encoding="utf-8").splitlines()
    direction = "LR"
    nodes: dict[str, Node] = {}
    edges: list[Edge] = []
    geometry_meta: dict[str, dict] = {}
    pending_styles: list[tuple[str, str]] = []
    warnings: list[str] = []
    z = 0
    for raw_line in lines:
        line = raw_line.strip()
        if not line:
            continue
        meta = META_RE.match(line)
        if meta:
            try:
                value = json.loads(meta.group(1))
                if value.get("type") == "node" and isinstance(value.get("id"), str):
                    geometry_meta[value["id"]] = value
            except json.JSONDecodeError:
                warnings.append("Invalid diagram-interchange metadata comment was ignored.")
            continue
        if line.startswith("%%"):
            continue
        header = HEADER_RE.match(line)
        if header:
            direction = header.group(1).upper().replace("TD", "TB")
            continue
        lowered = line.lower()
        if lowered.startswith(FORBIDDEN_PREFIXES):
            raise ValueError(f"Unsupported or unsafe Mermaid statement: {line[:80]}")
        style_match = STYLE_RE.match(line)
        if style_match:
            pending_styles.append((style_match.group(1), style_match.group(2)))
            continue
        edge_match = EDGE_RE.match(line)
        if edge_match:
            source_raw, source_suffix, arrow, label, target_raw, target_suffix = edge_match.groups()
            source_id = safe_id(source_raw)
            target_id = safe_id(target_raw)
            for raw_id, node_id, suffix in ((source_raw, source_id, source_suffix), (target_raw, target_id, target_suffix)):
                if node_id not in nodes:
                    node_label, shape = _parse_node_suffix(suffix)
                    nodes[node_id] = Node(id=node_id, label=node_label or raw_id, shape=shape,
                                          x=0, y=0, width=140, height=60, z=z,
                                          metadata={"source": "mermaid", "mermaid_id": raw_id})
                    z += 1
                elif suffix.strip():
                    node_label, shape = _parse_node_suffix(suffix)
                    if node_label:
                        nodes[node_id].label = node_label
                    nodes[node_id].shape = shape
            style = Style(fill="none", dashed="." in arrow, stroke_width=2.0 if "=" in arrow else 1.0,
                          arrow_start="classic" if arrow.startswith("<") else "none",
                          arrow_end="classic" if arrow.endswith(">") else "none")
            edges.append(Edge(id=f"e_{len(edges)+1}", source=source_id, target=target_id,
                              label=_quoted_text(label or ""), z=z, style=style,
                              metadata={"source": "mermaid", "operator": arrow}))
            z += 1
            continue
        node_match = NODE_ONLY_RE.match(line)
        if node_match:
            raw_id, suffix = node_match.groups()
            label, shape = _parse_node_suffix(suffix)
            if label or suffix.strip().startswith(("[", "(", "{")):
                node_id = safe_id(raw_id)
                nodes[node_id] = Node(id=node_id, label=label or raw_id, shape=shape,
                                      x=0, y=0, width=140, height=60, z=z,
                                      metadata={"source": "mermaid", "mermaid_id": raw_id})
                z += 1
                continue
        raise ValueError(f"Unsupported Mermaid line: {line[:120]}")
    for node_id, meta in geometry_meta.items():
        canonical = safe_id(node_id)
        if canonical in nodes:
            nodes[canonical].metadata["mermaid_geometry"] = meta
    for node_id, value in pending_styles:
        canonical = safe_id(node_id)
        if canonical in nodes:
            nodes[canonical].style = _parse_style(value, nodes[canonical].style)
    page = Page(id="page_1", name="Diagram", nodes=list(nodes.values()), edges=edges, warnings=warnings)
    _layout(page, direction)
    return Diagram(title=path.stem, pages=[page], metadata={"source_format": "mermaid", "direction": direction})


def _escape_label(value: str) -> str:
    return value.replace("&", "#38;").replace('"', "#34;").replace("<", "#60;").replace(">", "#62;").replace("\n", "<br/>")


def _node_syntax(node: Node) -> str:
    label = _escape_label(node.label)
    if node.shape == "ellipse":
        return f'{node.id}(("{label}"))'
    if node.shape == "diamond":
        return f'{node.id}{{"{label}"}}'
    if node.shape == "roundRect":
        return f'{node.id}("{label}")'
    if node.shape == "can":
        return f'{node.id}[("{label}")]'
    return f'{node.id}["{label}"]'


def write_mermaid(diagram: Diagram, path: Path) -> None:
    page = diagram.pages[0] if diagram.pages else Page(id="page_1", name="Diagram")
    lines = ["flowchart LR"]
    for node in sorted(page.nodes, key=lambda n: n.z):
        lines.append("    " + _node_syntax(node))
        meta = {"type": "node", "id": node.id, "x": node.x, "y": node.y,
                "width": node.width, "height": node.height, "rotation": node.rotation, "shape": node.shape}
        lines.append("    %% diagram-interchange: " + json.dumps(meta, ensure_ascii=False, separators=(",", ":")))
    for edge in sorted(page.edges, key=lambda e: e.z):
        if not edge.source or not edge.target:
            lines.append(f"    %% unresolved edge {edge.id}: {json.dumps(edge.label, ensure_ascii=False)}")
            continue
        operator = "-.->" if edge.style.dashed else ("==>" if edge.style.stroke_width >= 2 else "-->")
        if edge.style.arrow_end == "none":
            operator = "---"
        label = f'|{_escape_label(edge.label)}|' if edge.label else ""
        lines.append(f"    {edge.source} {operator}{label} {edge.target}")
    for node in sorted(page.nodes, key=lambda n: n.z):
        style = node.style
        if style.fill == "none":
            fill = "none"
        else:
            fill = style.fill
        extras = [f"fill:{fill}", f"stroke:{style.stroke}", f"stroke-width:{style.stroke_width:g}px", f"color:{style.font_color}"]
        if style.dashed:
            extras.append("stroke-dasharray:5 5")
        lines.append(f"    style {node.id} " + ",".join(extras))
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
