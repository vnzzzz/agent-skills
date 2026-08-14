#!/usr/bin/env python3
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PLUGIN_ROOT = ROOT / "plugins" / "agent-skills"
CODEX_MANIFEST = PLUGIN_ROOT / ".codex-plugin" / "plugin.json"
CLAUDE_MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
EXPECTED_MARKETPLACE = "vnzzzz-agent-skills"
EXPECTED_PLUGIN = "agent-skills"
EXPECTED_SOURCE = "./plugins/agent-skills"
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def fail(message: str) -> None:
    raise ValueError(message)


def find_plugin(marketplace: dict) -> dict:
    matches = [entry for entry in marketplace.get("plugins", []) if entry.get("name") == EXPECTED_PLUGIN]
    if len(matches) != 1:
        fail(f"marketplace must contain exactly one {EXPECTED_PLUGIN!r} entry")
    return matches[0]


def main() -> int:
    codex = load(CODEX_MANIFEST)
    claude = load(CLAUDE_MANIFEST)

    for field in ("name", "version", "description"):
        if codex.get(field) != claude.get(field):
            fail(f"Codex and Claude manifests must use the same {field}")

    if codex.get("name") != EXPECTED_PLUGIN:
        fail(f"Plugin name must be {EXPECTED_PLUGIN!r}")
    if not SEMVER.fullmatch(str(codex.get("version", ""))):
        fail("Plugin version must be strict MAJOR.MINOR.PATCH semver")
    if codex.get("skills") != "./skills/":
        fail("Codex manifest must expose the shared ./skills/ directory")
    if codex.get("author", {}).get("name") != "vnzzzz":
        fail("Codex manifest must declare author.name")

    interface = codex.get("interface", {})
    for field in (
        "displayName",
        "shortDescription",
        "longDescription",
        "developerName",
        "category",
    ):
        if not isinstance(interface.get(field), str) or not interface[field]:
            fail(f"Codex manifest interface.{field} must be a non-empty string")
    if not isinstance(interface.get("capabilities"), list):
        fail("Codex manifest interface.capabilities must be an array")
    default_prompt = interface.get("defaultPrompt")
    if not isinstance(default_prompt, list) or not default_prompt:
        fail("Codex manifest interface.defaultPrompt must be a non-empty array")

    codex_marketplace = load(CODEX_MARKETPLACE)
    claude_marketplace = load(CLAUDE_MARKETPLACE)
    if codex_marketplace.get("name") != EXPECTED_MARKETPLACE:
        fail("Codex marketplace name is inconsistent")
    if claude_marketplace.get("name") != EXPECTED_MARKETPLACE:
        fail("Claude marketplace name is inconsistent")

    codex_entry = find_plugin(codex_marketplace)
    claude_entry = find_plugin(claude_marketplace)
    if codex_entry.get("source", {}).get("path") != EXPECTED_SOURCE:
        fail("Codex marketplace must point to the canonical Plugin directory")
    if claude_entry.get("source") != EXPECTED_SOURCE:
        fail("Claude marketplace must point to the canonical Plugin directory")

    skill_roots = sorted(path for path in (PLUGIN_ROOT / "skills").iterdir() if path.is_dir())
    if not skill_roots:
        fail("Plugin must contain at least one Skill")
    for skill_root in skill_roots:
        if not (skill_root / "SKILL.md").is_file():
            fail(f"{skill_root}: missing SKILL.md")

    print(f"Validated {len(skill_roots)} shared Skill(s) in {EXPECTED_PLUGIN} {codex['version']}.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"Plugin validation failed: {exc}", file=sys.stderr)
        raise SystemExit(1)
