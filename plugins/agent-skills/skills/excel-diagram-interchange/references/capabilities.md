# Capability reference

A local-only, shape-focused interchange tool for diagrams drawn on an Excel worksheet as if it were a canvas. The same distributable Skill directory is compatible with Claude Code and Codex.

It converts among:

- Excel `.xlsx`
- canonical `diagram.json`
- canonical `diagram.xml`
- Mermaid `.mmd`
- draw.io `.drawio`

No ExStruct, Excel, LibreOffice, COM, browser, remote API, or network access is used at runtime.

## Architecture

```text
.xlsx ───────┐
.drawio ─────┤
.mmd ────────┼──> canonical diagram.json ──> any supported output
.xml ────────┤
.json ───────┘
```

`diagram.json` is the canonical internal representation. The other formats are adapters.

## Why the model is asymmetric

Excel, canonical JSON/XML, and draw.io can carry explicit coordinates and sizes. Standard Mermaid flowcharts are laid out by a renderer and do not have a general absolute-position model.

The generated Mermaid therefore includes ignored comments like:

```text
%% diagram-interchange: {"type":"node","id":"web","x":80,"y":100,"width":180,"height":80,...}
```

Ordinary Mermaid renderers ignore these comments. This converter uses them to restore geometry when its own `.mmd` output is converted back. Third-party Mermaid without these comments receives deterministic automatic layout.

## Capability matrix

| Feature | JSON/XML | draw.io | Excel | Mermaid |
|---|---:|---:|---:|---:|
| Node/edge topology | Full | Full within profile | Full within profile | Full within supported syntax |
| Absolute geometry | Full | Full | Full/approximated for cell anchors | Metadata comments only |
| Shape text | Full | Full | Full | Full |
| Basic fill/stroke/font | Full | Mostly | Mostly | Basic node styles |
| Connector labels/arrows | Full | Mostly | Mostly | Basic |
| Multiple pages/sheets | Full | Full | Full | First page only |
| Cell values/formulas | Not modeled | N/A | Deliberately ignored | N/A |
| Images/SmartArt/charts | Not supported | Not supported | Ignored with warning | Not supported |
| Grouped shapes | Not modeled | Flattened only if input is already flat | v1: ignored with warning | Not supported |
| Custom/freeform geometry | Normalized | Normalized | Normalized/ignored | Normalized |

## Supported profile

### Nodes

- rectangle / rounded rectangle
- ellipse
- diamond
- cylinder (`can`)
- basic preset shapes such as cloud, hexagon, triangle, parallelogram, trapezoid, pentagon, and octagon
- shape text
- x/y, width/height, rotation, z-order
- fill, stroke, line width/dash, font color/size

### Edges

- source and target node IDs
- connector label
- optional points
- line width/dash
- start/end arrowheads
- native `xdr:cxnSp` connectors
- connector presets serialized as ordinary `xdr:sp` shapes by generic workbook writers; endpoints are then inferred from geometry

### Deliberately excluded

- all cell values, formulas, comments, tables, and formatting
- `.xls`, `.xlsm`, `.xlsb`
- VBA, OLE, ActiveX, external links, embedded files
- pictures and external icon downloads
- charts, SmartArt, WordArt
- arbitrary Mermaid directives, callbacks, hyperlinks, or JavaScript
- complete DrawingML styling/effects

## Round-trip expectations

- JSON ↔ canonical XML: intended to be structurally equivalent.
- JSON ↔ draw.io: geometry and topology are retained within the supported profile.
- JSON ↔ Excel: geometry and topology are retained within the supported DrawingML profile. Cell-based anchors may be normalized to absolute anchors on output.
- JSON ↔ generated Mermaid: topology and profile geometry comments are retained.
- Arbitrary Mermaid ↔ other formats: topology is retained; layout is generated.

## Scope boundary

A complete implementation of SpreadsheetDrawingML would be an unnecessary reinvention. This Skill implements a narrow interoperability profile for ordinary shapes, text, connectors, geometry, and basic styles.

The custom canonical model is necessary because Excel DrawingML, draw.io `mxGraphModel`, and Mermaid do not share a standard interchange model. If the scope later expands to grouped shapes, pictures, custom geometry, or advanced Office effects, replace the direct OOXML adapter with a dedicated component based on Microsoft's Open XML SDK rather than continuing to enlarge this parser indefinitely.
