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

## Development

- ここにはconsumer非依存の再利用可能なSkillだけを置きます。
- consumer固有の設定・overlayは各consumer repositoryで管理します。
- Skillの開発・横断検証は [`agent-skills-development`](https://github.com/vnzzzz/agent-skills-development) で行います。
