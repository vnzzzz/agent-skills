# agent-skills

複数のrepositoryから再利用するAgent Skillの正本を管理し、Codex / Claude CodeのPluginとして配布するrepositoryです。

## Scope

- 特定のproductやconsumerに依存しない、再利用可能なSkillを管理します。
- Skill本文の正本は`plugins/agent-skills/skills/<skill-name>/SKILL.md`です。
- Codex / Claude Code向けPlugin metadataは同じ`plugins/agent-skills`を配布するadapterとして管理します。
- consumer固有の設定、用語、path、運用ルール、overlayは各consumer repositoryで管理します。
- Skillの開発環境や横断的な検証手順は`agent-skills-development`側で扱います。

```text
agent-skills/
├── .agents/plugins/marketplace.json
├── .claude-plugin/marketplace.json
└── plugins/
    └── agent-skills/
        ├── .codex-plugin/plugin.json
        ├── .claude-plugin/plugin.json
        └── skills/
            └── <skill-name>/
                └── SKILL.md
```

両marketplaceは同じ`./plugins/agent-skills`を指します。
Plugin metadataに個別Skill名を列挙しないため、`plugins/agent-skills/skills/`へSkillを追加してもconsumer側の設定変更は不要です。

## Distribution

配布元はpublic GitHub repository `vnzzzz/agent-skills`だけです。
Universal Plugin Directory、Anthropic公式marketplace、npm等の別registryへの公開は必須としません。

public repositoryのHTTPS取得にはGitHub認証情報を要求しません。
利用環境にはGitHubへの外向きHTTPS通信と`git`が必要です。

認証方式への暗黙依存を避けるため、自動化ではGitHub shorthandではなくHTTPS Git URLを使用します。

### Codex

Codex CLIではmarketplaceを追加し、Pluginを導入します。

```bash
codex plugin marketplace add https://github.com/vnzzzz/agent-skills.git --json
codex plugin add agent-skills@agent-skills --json
```

marketplaceを更新する場合は次を実行します。

```bash
codex plugin marketplace upgrade agent-skills --json
```

### Claude Code

Claude Codeでは同じGitHub repositoryをmarketplaceとして追加し、Pluginをuser scopeへ導入します。

```bash
claude plugin marketplace add https://github.com/vnzzzz/agent-skills.git --scope user
claude plugin install agent-skills@agent-skills --scope user
```

更新する場合は次を実行します。

```bash
claude plugin marketplace update agent-skills
claude plugin update agent-skills@agent-skills --scope user
```

## Development

Skill固有の追加resourceが必要な場合は、そのSkill directory内に自己完結する形で配置します。

Codex / Claude Code固有のPlugin metadataへSkill本文やSkill一覧を複製しません。
Plugin metadataの整合性と実CLIでの横断検証は`agent-skills-development`で行います。
