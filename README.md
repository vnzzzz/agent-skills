# agent-skills

Shared Agent Skills for Codex and Claude Code.

複数のrepositoryで再利用するSkillを、1つのPluginとして配布するためのrepositoryです。

## Install

### Codex

```bash
codex plugin marketplace add https://github.com/vnzzzz/agent-skills.git --json
codex plugin add agent-skills@vnzzzz-agent-skills --json
```

### Claude Code

```bash
claude plugin marketplace add https://github.com/vnzzzz/agent-skills.git --scope user
claude plugin install agent-skills@vnzzzz-agent-skills --scope user
```

## Skills

<!-- BEGIN GENERATED SKILLS -->
- [development-guidelines](plugins/agent-skills/skills/development-guidelines/SKILL.md)
- [product-thinking](plugins/agent-skills/skills/product-thinking/SKILL.md)
- [readable-code](plugins/agent-skills/skills/readable-code/SKILL.md)
- [technical-writing](plugins/agent-skills/skills/technical-writing/SKILL.md)
- [testing](plugins/agent-skills/skills/testing/SKILL.md)
<!-- END GENERATED SKILLS -->

## Layout

```text
plugins/agent-skills/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
└── skills/
    └── <skill-name>/
        └── SKILL.md
```

`plugins/agent-skills/skills/` がSkillの正本です。Codex / Claude Codeは同じPluginを参照します。
