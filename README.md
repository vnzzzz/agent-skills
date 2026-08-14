# agent-skills

複数のrepositoryから再利用するAgent Skillの正本を管理するrepositoryです。

## Scope

- 特定のproductやconsumerに依存しない、再利用可能なSkillを管理します。
- Skillはcollection形式で`skills/<skill-name>/SKILL.md`に配置します。
- Claude CodeやCodexなど、複数のAgentから利用できるportableなSkillを基本とします。
- consumer固有の設定、用語、path、運用ルール、overlayは各consumer repositoryで管理します。
- Skillの開発環境や横断的な検証手順はこのrepositoryでは管理せず、`agent-skills-development`側で扱います。

```text
agent-skills/
└── skills/
    └── <skill-name>/
        └── SKILL.md
```

## Consumption

このrepositoryを利用するconsumerは、必要な再現性に応じて特定のGit revisionを固定して利用します。shared側の変更だけでconsumerの利用内容が意図せず変わる構成にはしません。

Skill固有の追加resourceが必要な場合は、そのSkill directory内に自己完結する形で配置します。
