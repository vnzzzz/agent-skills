# agent-skills

Codex / Claude Codeで共通利用する、開発ワークフロー向けAgent Skillsを管理・配布します。

## インストール

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
- [change-planning](plugins/agent-skills/skills/change-planning/SKILL.md)
- [debugging](plugins/agent-skills/skills/debugging/SKILL.md)
- [development-guidelines](plugins/agent-skills/skills/development-guidelines/SKILL.md)
- [excel-diagram-interchange](plugins/agent-skills/skills/excel-diagram-interchange/SKILL.md)
- [product-thinking](plugins/agent-skills/skills/product-thinking/SKILL.md)
- [readable-code](plugins/agent-skills/skills/readable-code/SKILL.md)
- [technical-research](plugins/agent-skills/skills/technical-research/SKILL.md)
- [technical-writing](plugins/agent-skills/skills/technical-writing/SKILL.md)
- [testing](plugins/agent-skills/skills/testing/SKILL.md)
<!-- END GENERATED SKILLS -->

## ディレクトリ構成

```text
plugins/agent-skills/
├── .codex-plugin/plugin.json
├── .claude-plugin/plugin.json
└── skills/
    └── <skill-name>/
        └── SKILL.md
```

`plugins/agent-skills/skills/`がSkillの正本です。Codex / Claude Codeは同じPluginを参照します。
