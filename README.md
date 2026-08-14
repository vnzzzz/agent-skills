# agent-skills

複数のrepositoryから再利用するAgent Skillの正本を管理するrepositoryです。

## Scope

- 特定のproductやconsumerに依存しない、再利用可能なSkillを管理します。
- Skillはcollection形式で`skills/<skill-name>/SKILL.md`に配置します。
- Claude CodeやCodexなど、複数のAgentから利用できるportableなSkillを基本とします。
- consumer固有の設定、用語、path、運用ルール、overlayは各consumer repositoryで管理します。

```text
agent-skills/
└── skills/
    └── <skill-name>/
        └── SKILL.md
```

## Consumption

このrepositoryを利用するconsumerは、必要な再現性に応じて特定のGit revisionを固定して利用します。shared側の変更だけでconsumerの利用内容が意図せず変わる構成にはしません。

Skill固有の追加resourceが必要な場合は、そのSkill directory内に自己完結する形で配置します。

## Development policy

開発時のrepository rulesは[`AGENTS.md`](./AGENTS.md)を参照してください。CI、release、contribution運用などは、実際に必要になった時点で追加します。
