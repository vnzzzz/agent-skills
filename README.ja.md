# agent-skills

[![CI](https://github.com/vnzzzz/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/vnzzzz/agent-skills/actions/workflows/ci.yml) · [English](README.md)

CodexとClaude Codeで共通利用する開発ワークフロー向けSkill集。変更計画、デバッグ、テスト、技術文書の作成を1つのPluginで支援します。

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

インストール後は、例えば「`debugging`を使ってこのテストが失敗する原因を調べて」と依頼できます。

## Skills

<!-- BEGIN GENERATED SKILLS -->
- [change-planning](plugins/agent-skills/skills/change-planning/SKILL.md)
- [code-comments](plugins/agent-skills/skills/code-comments/SKILL.md)
- [command-execution](plugins/agent-skills/skills/command-execution/SKILL.md)
- [debugging](plugins/agent-skills/skills/debugging/SKILL.md)
- [development-guidelines](plugins/agent-skills/skills/development-guidelines/SKILL.md)
- [evidence-reporting](plugins/agent-skills/skills/evidence-reporting/SKILL.md)
- [incident-response](plugins/agent-skills/skills/incident-response/SKILL.md)
- [issue-workflow](plugins/agent-skills/skills/issue-workflow/SKILL.md)
- [iterative-improvement](plugins/agent-skills/skills/iterative-improvement/SKILL.md)
- [product-thinking](plugins/agent-skills/skills/product-thinking/SKILL.md)
- [readme-writing](plugins/agent-skills/skills/readme-writing/SKILL.md)
- [technical-research](plugins/agent-skills/skills/technical-research/SKILL.md)
- [technical-writing](plugins/agent-skills/skills/technical-writing/SKILL.md)
- [testing](plugins/agent-skills/skills/testing/SKILL.md)
<!-- END GENERATED SKILLS -->

Skillの正本は[`plugins/agent-skills/skills/`](plugins/agent-skills/skills/)です。追加・改善方法は[CONTRIBUTING.ja.md](CONTRIBUTING.ja.md)を参照してください。
