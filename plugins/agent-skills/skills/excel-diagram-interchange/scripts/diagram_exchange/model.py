from __future__ import annotations

from dataclasses import asdict, dataclass, field
from math import isfinite
import re
from typing import Any

SCHEMA_VERSION = "1.0"
ID_RE = re.compile(r"^[A-Za-z][A-Za-z0-9_-]{0,119}$")
COLOR_RE = re.compile(r"^#[0-9a-fA-F]{6}$")
ALLOWED_SHAPES = {
    "rect", "roundRect", "ellipse", "diamond", "can", "cloud", "hexagon",
    "triangle", "parallelogram", "trapezoid", "pentagon", "octagon",
}
ALLOWED_ARROWS = {"none", "classic", "block", "open", "oval", "diamond", "stealth", "triangle", "arrow"}


def _number(value: float, name: str, *, minimum: float | None = None, maximum: float = 10_000_000.0) -> float:
    value = float(value)
    if not isfinite(value):
        raise ValueError(f"{name} must be finite")
    if minimum is not None and value < minimum:
        raise ValueError(f"{name} must be >= {minimum}")
    if abs(value) > maximum:
        raise ValueError(f"{name} exceeds supported range")
    return value


def _identifier(value: str, name: str) -> str:
    value = str(value)
    if not ID_RE.fullmatch(value):
        raise ValueError(f"Invalid {name}: {value!r}")
    return value


def _color(value: str, default: str, *, allow_none: bool = False) -> str:
    value = str(value)
    if allow_none and value == "none":
        return value
    return value.lower() if COLOR_RE.fullmatch(value) else default


@dataclass
class Style:
    fill: str = "#ffffff"
    stroke: str = "#000000"
    stroke_width: float = 1.0
    dashed: bool = False
    font_color: str = "#000000"
    font_size: float = 12.0
    arrow_start: str = "none"
    arrow_end: str = "none"

    def __post_init__(self) -> None:
        self.fill = _color(self.fill, "#ffffff", allow_none=True)
        self.stroke = _color(self.stroke, "#000000")
        self.font_color = _color(self.font_color, "#000000")
        self.stroke_width = _number(self.stroke_width, "stroke_width", minimum=0.1, maximum=1000)
        self.font_size = _number(self.font_size, "font_size", minimum=1, maximum=1000)
        self.dashed = bool(self.dashed)
        self.arrow_start = self.arrow_start if self.arrow_start in ALLOWED_ARROWS else "none"
        self.arrow_end = self.arrow_end if self.arrow_end in ALLOWED_ARROWS else "none"


@dataclass
class Node:
    id: str
    label: str
    shape: str
    x: float
    y: float
    width: float
    height: float
    rotation: float = 0.0
    z: int = 0
    style: Style = field(default_factory=Style)
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.id = _identifier(self.id, "node id")
        self.label = str(self.label)[:100_000]
        self.shape = self.shape if self.shape in ALLOWED_SHAPES else "rect"
        self.x = _number(self.x, "x")
        self.y = _number(self.y, "y")
        self.width = _number(self.width, "width", minimum=1)
        self.height = _number(self.height, "height", minimum=1)
        self.rotation = _number(self.rotation, "rotation", maximum=360_000)
        self.z = int(self.z)
        self.metadata = dict(self.metadata)


@dataclass
class Edge:
    id: str
    source: str | None
    target: str | None
    label: str = ""
    points: list[list[float]] = field(default_factory=list)
    z: int = 0
    style: Style = field(default_factory=lambda: Style(fill="none"))
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.id = _identifier(self.id, "edge id")
        self.source = _identifier(self.source, "edge source") if self.source is not None else None
        self.target = _identifier(self.target, "edge target") if self.target is not None else None
        self.label = str(self.label)[:100_000]
        normalized: list[list[float]] = []
        for point in self.points:
            if len(point) < 2:
                raise ValueError("Edge point requires x and y")
            normalized.append([_number(point[0], "point.x"), _number(point[1], "point.y")])
        self.points = normalized
        self.z = int(self.z)
        self.metadata = dict(self.metadata)


@dataclass
class Page:
    id: str
    name: str
    width: float = 1600.0
    height: float = 900.0
    nodes: list[Node] = field(default_factory=list)
    edges: list[Edge] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        self.id = _identifier(self.id, "page id")
        self.name = str(self.name)[:255]
        self.width = _number(self.width, "page.width", minimum=1)
        self.height = _number(self.height, "page.height", minimum=1)
        node_ids = {node.id for node in self.nodes}
        if len(node_ids) != len(self.nodes):
            raise ValueError("Duplicate node ids")
        edge_ids = {edge.id for edge in self.edges}
        if len(edge_ids) != len(self.edges):
            raise ValueError("Duplicate edge ids")
        for edge in self.edges:
            if edge.source is not None and edge.source not in node_ids:
                raise ValueError(f"Unknown edge source: {edge.source}")
            if edge.target is not None and edge.target not in node_ids:
                raise ValueError(f"Unknown edge target: {edge.target}")
        self.warnings = [str(w)[:2000] for w in self.warnings]


@dataclass
class Diagram:
    title: str
    pages: list[Page]
    schema_version: str = SCHEMA_VERSION
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.title = str(self.title)[:255]
        if self.schema_version != SCHEMA_VERSION:
            raise ValueError(f"Unsupported schema version: {self.schema_version}")
        page_ids = {page.id for page in self.pages}
        if len(page_ids) != len(self.pages):
            raise ValueError("Duplicate page ids")
        self.metadata = dict(self.metadata)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _style(value: dict[str, Any] | None) -> Style:
    raw = value or {}
    allowed = Style.__dataclass_fields__
    return Style(**{key: raw[key] for key in raw if key in allowed})


def diagram_from_dict(raw: dict[str, Any]) -> Diagram:
    if raw.get("schema_version", SCHEMA_VERSION) != SCHEMA_VERSION:
        raise ValueError(f"Unsupported schema version: {raw.get('schema_version')}")
    pages: list[Page] = []
    for p in raw.get("pages", []):
        nodes = [Node(**{**n, "style": _style(n.get("style"))}) for n in p.get("nodes", [])]
        edges = [Edge(**{**e, "style": _style(e.get("style"))}) for e in p.get("edges", [])]
        pages.append(Page(
            id=str(p["id"]), name=str(p.get("name", p["id"])),
            width=float(p.get("width", 1600)), height=float(p.get("height", 900)),
            nodes=nodes, edges=edges, warnings=list(p.get("warnings", [])),
        ))
    return Diagram(
        title=str(raw.get("title", "Diagram")), pages=pages,
        schema_version=SCHEMA_VERSION, metadata=dict(raw.get("metadata", {})),
    )
