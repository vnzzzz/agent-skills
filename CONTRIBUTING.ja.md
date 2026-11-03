# Contributing

[English](CONTRIBUTING.md)

Skillの作成・改善方法そのものは公式のSkill Creatorを利用し、この文書では`agent-skills`固有の規約だけを定義する。

## Skill構成

- 1つのSkillは、独立して発火する1つのcoherentなcapability / workflowを扱う。同じworkflowのvariantは必要に応じて`references/`へ分離する。
- `SKILL.md`には常に必要な判断と手順を置き、条件付き詳細は`references/`へ分離する。
- 同じ規則を複数箇所へ重複させない。
- `SKILL.md`のfrontmatterでは`name`と`description`を必須とし、`name`はdirectory名と一致させる。その他の標準fieldは、Codex / Claude Code双方で必要性と互換性を確認した場合だけ使用する。
- `description`には「何をするか」と発火に必要なtrigger / contextを必要十分に含める。短さのためにtrigger情報を削らない。

## 記法

- H1はSkill / referenceの識別名として英語Title Caseを使う。
- 本文は日本語を基本とするが、一般的なtechnical termを無理に翻訳しない。
- `foreground`、`retry`、`root cause`、`completed` / `blocked`、`Node` / `Edge`、`Repository` / `Issue` / `Pull Request`など、一般的・識別的・Skill間contractとなる語は原語を優先する。
- H2以下は日本語として自然に読めることを優先する。
- 主要な逐次workflowは`## 1. ...`形式で直接追える構造にする。
- 他Skillとの責務境界は`## 他Skillとの関係`に記載する。

## Referenceと出典

- referenceにはfrontmatterを付けず、H1は英語Title Caseとする。
- `SKILL.md`側でreferenceを読む条件を明示する。
- 内部referenceの索引は`## 関連資料`、外部出典は`## 参考資料`を使う。
- code blockには内容に合うlanguage tagを付ける。

## ドキュメントの多言語化

- repository利用者向けdocumentationは英語をcanonicalとし、日本語translation mirrorは対応する`*.ja.md`で管理する。
- canonical文書を変更するPull Requestでは、対応する日本語mirrorも同じPull Requestで更新する。
- 日本語側だけの表現修正はcanonical文書を変更せずに行ってよい。
- `plugins/agent-skills/skills/`配下のruntime Skillはtranslation mirrorではなく、上記のSkill authoring ruleに従う。
- READMEのSkill一覧などgenerated contentは、言語ごとに独立管理せず同じgeneratorから更新する。

## Validation

CIは`name` / `description`、manifest、H1の存在など壊れにくい構造条件を検証する。標準optional fieldを理由なく拒否せず、Title Caseや語彙選択などのstyleは人間レビューで確認する。

## Skillの暗黙発火評価（手動実行）

`plugins/agent-skills/evals/` の6ケースは、Claude Codeが狙ったSkillを発火し、隣接する別Skillを誤発火しないか測定する。Anthropic公式の[plugin eval形式](https://code.claude.com/docs/en/plugin-evals)と、`tool_used: Skill`による機械判定を使う。PromptでSkill名を直接指定せず、空の隔離workspaceでSkill toolだけを許可する。

Plugin rootで、認証済みの**Claude Code v2.1.269以降**を使う。

```bash
cd plugins/agent-skills
claude plugin eval . --runs 1 --ablation none --no-publish --max-cost-usd 2
# ケースの動作を確認できたら、試行回数を増やす：
claude plugin eval . --runs 3 --ablation none --no-publish --max-cost-usd 10
```

各試行はモデルの利用枠・API料金を消費する。費用上限に達するとpartial resultになり得る。利用アカウントによってplugin eval自体が使用不可の場合もある。結果はGit管理対象外の`evals/results/`に保存される。model、Claude Codeのversion、plugin commit、ケース別発火率、失敗内容を記録する。1回だけのsmoke testやpartial resultを発火の信頼性が証明されたものと扱わない。隔離環境の結果は、実際のproject instructionや他Pluginとの併用時の結果を保証しない。

**Codex**では同じ`prompt.md`の本文（YAML frontmatterを除く）を、Pluginを導入したclean sessionで入力する。実行traceにおけるSkill発火または対応する`SKILL.md`の読取を確認する。最終回答がもっともらしいだけでは発火の証拠にならない。Codex version/model、plugin commit、ケース別の期待/実際のSkill、誤発火を記録する。ここでのCodex評価は**手動**であり、Claude CodeのgraderはCodex上では動かない。
