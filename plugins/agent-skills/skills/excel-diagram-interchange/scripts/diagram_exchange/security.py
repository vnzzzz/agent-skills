from __future__ import annotations

from pathlib import Path, PurePosixPath
import stat
from zipfile import BadZipFile, ZipFile

from .safe_xml import parse_xml_bytes, validate_xml_bytes

BLOCKED_PART_FRAGMENTS = (
    "vbaproject", "activex", "embeddings/", "oleobject", "externallinks/",
)
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
BLOCKED_CONTENT_TYPE_MARKERS = ("macroenabled", "vbaproject", "oleobject", "activex")


def _validate_package_xml(zf: ZipFile, infos) -> None:
    for info in infos:
        lowered = info.filename.lower()
        if not lowered.endswith((".xml", ".rels")):
            continue
        try:
            validate_xml_bytes(zf.read(info))
        except ValueError as exc:
            raise ValueError(f"Unsafe XML in OOXML part: {info.filename}: {exc}") from exc


def preflight_xlsx(
    path: Path,
    *,
    max_file_mib: int = 50,
    max_uncompressed_mib: int = 200,
    max_entry_mib: int = 50,
    max_entries: int = 3000,
    max_ratio: float = 200.0,
) -> None:
    if path.suffix.lower() != ".xlsx":
        raise ValueError("Only .xlsx is accepted")
    if path.is_symlink() or not path.is_file():
        raise ValueError("Input must be a regular .xlsx file")
    if path.stat().st_size > max_file_mib * 1024 * 1024:
        raise ValueError("Input exceeds compressed size limit")
    try:
        with ZipFile(path) as zf:
            infos = zf.infolist()
            if len(infos) > max_entries:
                raise ValueError("Workbook contains too many ZIP entries")
            total = 0
            seen: set[str] = set()
            for info in infos:
                name = info.filename.replace("\\", "/")
                pure = PurePosixPath(name)
                normalized = "/".join(pure.parts)
                if pure.is_absolute() or ".." in pure.parts:
                    raise ValueError(f"Unsafe ZIP member: {name}")
                if normalized in seen:
                    raise ValueError(f"Duplicate ZIP member: {name}")
                seen.add(normalized)
                mode = (info.external_attr >> 16) & 0xFFFF
                if mode and stat.S_ISLNK(mode):
                    raise ValueError(f"ZIP symbolic link is not allowed: {name}")
                if info.flag_bits & 0x1:
                    raise ValueError(f"Encrypted ZIP member is not allowed: {name}")
                lowered = name.lower()
                if any(fragment in lowered for fragment in BLOCKED_PART_FRAGMENTS):
                    raise ValueError(f"Blocked workbook part: {name}")
                if info.file_size > max_entry_mib * 1024 * 1024:
                    raise ValueError(f"ZIP member exceeds size limit: {name}")
                total += info.file_size
                if total > max_uncompressed_mib * 1024 * 1024:
                    raise ValueError("Workbook exceeds uncompressed size limit")
                if info.compress_size and info.file_size / info.compress_size > max_ratio:
                    raise ValueError(f"Suspicious compression ratio: {name}")
            if "[Content_Types].xml" not in seen:
                raise ValueError("OOXML content types are missing")

            _validate_package_xml(zf, infos)

            content_types = parse_xml_bytes(zf.read("[Content_Types].xml"))
            for element in content_types.iter():
                content_type = element.get("ContentType", "").lower()
                if any(marker in content_type for marker in BLOCKED_CONTENT_TYPE_MARKERS):
                    raise ValueError("Blocked OOXML content type")

            for info in infos:
                if not info.filename.endswith(".rels"):
                    continue
                try:
                    root = parse_xml_bytes(zf.read(info))
                except ValueError as exc:
                    raise ValueError(f"Invalid relationship XML: {info.filename}") from exc
                for rel in root.findall(f"{{{REL_NS}}}Relationship"):
                    if rel.get("TargetMode", "").lower() == "external":
                        raise ValueError(f"External relationship is not allowed: {info.filename}")
    except BadZipFile as exc:
        raise ValueError("Input is not a valid OOXML ZIP package") from exc
