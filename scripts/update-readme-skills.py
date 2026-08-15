#!/usr/bin/env python3

import argparse
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"
SKILLS_DIR = ROOT / "plugins" / "agent-skills" / "skills"
START = "<!-- BEGIN GENERATED SKILLS -->"
END = "<!-- END GENERATED SKILLS -->"


def render_skill_list() -> str:
    skills = sorted(
        path.name
        for path in SKILLS_DIR.iterdir()
        if path.is_dir() and (path / "SKILL.md").is_file()
    )
    lines = [START]
    lines.extend(
        f"- [{name}](plugins/agent-skills/skills/{name}/SKILL.md)" for name in skills
    )
    lines.append(END)
    return "\n".join(lines)


def update_readme(text: str) -> str:
    if text.count(START) != 1 or text.count(END) != 1:
        raise SystemExit("README must contain exactly one generated Skills marker pair")

    start = text.index(START)
    end = text.index(END, start) + len(END)
    return text[:start] + render_skill_list() + text[end:]


def main() -> int:
    parser = argparse.ArgumentParser(description="Update the generated Skill links in README.md")
    parser.add_argument(
        "--check",
        action="store_true",
        help="fail instead of updating README.md when the generated list is stale",
    )
    args = parser.parse_args()

    current = README.read_text(encoding="utf-8")
    expected = update_readme(current)

    if args.check:
        if current != expected:
            print("README Skill list is out of date. Run scripts/update-readme-skills.py")
            return 1
        return 0

    if current != expected:
        README.write_text(expected, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
