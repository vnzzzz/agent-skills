from __future__ import annotations

import ast
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "plugins" / "agent-skills" / "skills" / "excel-diagram-interchange"

FORBIDDEN_IMPORTS = {
    "aiohttp",
    "ftplib",
    "httpx",
    "requests",
    "socket",
    "subprocess",
    "webbrowser",
}
FORBIDDEN_CALLS = {"eval", "exec", "compile", "__import__"}


def dotted_name(node: ast.AST) -> str:
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def main() -> int:
    findings: list[str] = []
    for path in sorted(SKILL.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".", 1)[0] in FORBIDDEN_IMPORTS:
                        findings.append(f"{path}: forbidden import {alias.name}")
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".", 1)[0] in FORBIDDEN_IMPORTS or node.module == "urllib.request":
                    findings.append(f"{path}: forbidden import {node.module}")
            elif isinstance(node, ast.Call):
                name = dotted_name(node.func)
                if name in FORBIDDEN_CALLS or name in {"os.system", "os.popen"}:
                    findings.append(f"{path}:{node.lineno}: forbidden call {name}")

    lock = (ROOT / "requirements.lock").read_text(encoding="utf-8").strip()
    if not lock.startswith("defusedxml==0.7.1") or "--hash=sha256:" not in lock:
        findings.append("requirements.lock must contain only hash-pinned defusedxml==0.7.1")

    if findings:
        print("Security audit failed:")
        print("\n".join(f"- {item}" for item in findings))
        return 1
    print("Security audit passed: no network/subprocess/dynamic-execution APIs detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
