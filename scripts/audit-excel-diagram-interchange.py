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
STDLIB_MODULES = set(sys.stdlib_module_names) | {"__future__"}


def dotted_name(node: ast.AST) -> str:
    parts: list[str] = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
    return ".".join(reversed(parts))


def check_import(findings: list[str], path: Path, module: str, line: int) -> None:
    top = module.split(".", 1)[0]
    if top in FORBIDDEN_IMPORTS or module == "urllib.request":
        findings.append(f"{path}:{line}: forbidden import {module}")
    elif top not in STDLIB_MODULES:
        findings.append(f"{path}:{line}: third-party import is not allowed: {module}")


def main() -> int:
    findings: list[str] = []
    for path in sorted(SKILL.rglob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    check_import(findings, path, alias.name, node.lineno)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                check_import(findings, path, node.module, node.lineno)
            elif isinstance(node, ast.Call):
                name = dotted_name(node.func)
                if name in FORBIDDEN_CALLS or name in {"os.system", "os.popen"}:
                    findings.append(f"{path}:{node.lineno}: forbidden call {name}")

    if (ROOT / "requirements.lock").exists():
        findings.append("requirements.lock must not exist; excel-diagram-interchange runtime is stdlib-only")

    if findings:
        print("Security audit failed:")
        print("\n".join(f"- {item}" for item in findings))
        return 1
    print("Security audit passed: stdlib-only runtime with no network/subprocess/dynamic-execution APIs detected.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
