from __future__ import annotations

from pathlib import Path, PurePosixPath
import re
from urllib.parse import unquote


def safe_id(value: str, prefix: str = "n") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9_-]+", "_", value).strip("_")
    if not cleaned or not cleaned[0].isalpha():
        cleaned = f"{prefix}_{cleaned}"
    return cleaned[:120]


def normalize_color(value: str | None, default: str) -> str:
    if not value:
        return default
    value = value.strip().lstrip("#")
    if re.fullmatch(r"[0-9A-Fa-f]{6}", value):
        return f"#{value.lower()}"
    if re.fullmatch(r"[0-9A-Fa-f]{8}", value):
        return f"#{value[:6].lower()}"
    return default


def resolve_part(base_part: str, target: str) -> str:
    if target.startswith("/"):
        return target.lstrip("/")
    base = PurePosixPath(base_part).parent
    result = base.joinpath(unquote(target))
    parts: list[str] = []
    for item in result.parts:
        if item in ("", "."):
            continue
        if item == "..":
            if not parts:
                raise ValueError("Relationship target escapes package root")
            parts.pop()
        else:
            parts.append(item)
    return "/".join(parts)


def ensure_parent(path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
