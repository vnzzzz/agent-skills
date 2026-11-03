# agent-skills

**同じ開発の作法を、CodexでもClaude Codeでも。**

バグ調査、変更計画、テスト、根拠のある報告を支える、小さく独立したSkill集。両方のPluginから同じ指示を利用できます。

[インストール](#インストール) · [Skill一覧](#skills) · [English](README.md)

## やりたいことを依頼する

- 「このテストが不安定な原因を調べて、修正を検証して」
- 「このリファクタリングを安全でレビューしやすい手順に分けて」
- 「この技術的な主張を一次情報で裏付けて」

内容に応じてSkillを使えます。Skill名を指定することもできます。

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

Skillはそれぞれ独立したワークフローです。以下から内容を確認できます。

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

Skillの追加・改善は[貢献ガイド](CONTRIBUTING.ja.md)を参照してください。
