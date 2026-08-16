from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

from .canonical import read_json, read_xml, write_json, write_xml
from .drawio import read_drawio, write_drawio
from .excel_ooxml import read_xlsx, write_xlsx
from .mermaid import read_mermaid, write_mermaid
from .safe_xml import parse_xml_file

FORMATS = {"json", "xml", "mmd", "drawio", "xlsx"}


def detect_format(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".xlsx":
        return "xlsx"
    if suffix == ".json":
        return "json"
    if suffix in {".mmd", ".mermaid"}:
        return "mmd"
    if suffix == ".drawio":
        return "drawio"
    if suffix == ".xml":
        root = parse_xml_file(path)
        local_name = root.tag.rsplit("}", 1)[-1]
        if local_name in {"mxfile", "mxGraphModel"}:
            return "drawio"
        return "xml"
    raise ValueError(f"Unsupported input extension: {suffix}")


def load(path: Path, fmt: str):
    return {
        "xlsx": read_xlsx,
        "json": read_json,
        "xml": read_xml,
        "drawio": read_drawio,
        "mmd": read_mermaid,
    }[fmt](path)


def write(diagram, fmt: str, path: Path) -> None:
    {
        "xlsx": write_xlsx,
        "json": write_json,
        "xml": write_xml,
        "drawio": write_drawio,
        "mmd": write_mermaid,
    }[fmt](diagram, path)


def _digest(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Shape-only Excel/draw.io/Mermaid/JSON/XML interchange")
    parser.add_argument("input", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--formats", default="json,xml,mmd,drawio,xlsx",
                        help="Comma-separated outputs: json,xml,mmd,drawio,xlsx")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args(argv)
    try:
        input_arg = args.input.expanduser()
        if input_arg.is_symlink():
            raise ValueError("Symbolic-link input is not allowed")
        input_path = input_arg.resolve(strict=True)
        if not input_path.is_file():
            raise ValueError("Input must be a regular file")
        if input_path.stat().st_size > 50 * 1024 * 1024:
            raise ValueError("Input exceeds 50 MiB limit")
        input_format = detect_format(input_path)
        requested = [item.strip().lower() for item in args.formats.split(",") if item.strip()]
        unknown = set(requested) - FORMATS
        if unknown:
            raise ValueError(f"Unknown output formats: {', '.join(sorted(unknown))}")
        output_dir = args.output_dir or input_path.with_name(f"{input_path.stem}-diagram")
        output_dir = output_dir.resolve()
        if output_dir.exists() and any(output_dir.iterdir()) and not args.force:
            raise ValueError(f"Output directory is not empty: {output_dir}; use --force")
        output_dir.mkdir(parents=True, exist_ok=True)
        diagram = load(input_path, input_format)
        extensions = {"json": "json", "xml": "xml", "mmd": "mmd", "drawio": "drawio", "xlsx": "xlsx"}
        outputs: dict[str, dict[str, str]] = {}
        global_warnings: list[dict[str, str]] = []
        if "mmd" in requested and len(diagram.pages) > 1:
            global_warnings.append({"page": "*", "warning": "Mermaid output contains only the first page."})
        for fmt in requested:
            target = output_dir / f"diagram.{extensions[fmt]}"
            if target.exists() and not args.force:
                raise ValueError(f"Output exists: {target}")
            write(diagram, fmt, target)
            outputs[fmt] = {"path": str(target), "sha256": _digest(target)}
        warnings = global_warnings + [{"page": page.name, "warning": warning} for page in diagram.pages for warning in page.warnings]
        report = {
            "status": "review_required" if warnings else "ok",
            "input": str(input_path), "input_format": input_format,
            "shape_only": True, "cells_ignored": input_format == "xlsx",
            "canonical_format": "json", "outputs": outputs,
            "pages": [{"name": p.name, "nodes": len(p.nodes), "edges": len(p.edges)} for p in diagram.pages],
            "warnings": warnings,
            "fidelity": {
                "json": "canonical",
                "xml": "canonical-equivalent",
                "drawio": "geometry-and-topology within supported shape profile",
                "xlsx": "geometry-and-topology within supported DrawingML profile",
                "mmd": "logical view; coordinates retained only in diagram-interchange comments",
            },
        }
        report_path = output_dir / "conversion-report.json"
        report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except Exception as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
