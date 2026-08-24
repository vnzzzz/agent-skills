# Skill Authoring Guide

このrepositoryでAgent Skillを追加・更新するときの共通ルールを定義する。
Skill固有の要件を均一化することではなく、発火条件、実行手順、出力形式を同じ読み方で理解できる状態を目的とする。

## 基本方針

- Skillは1つの明確なjob-to-be-doneを扱う。
- `SKILL.md`には、そのSkillが発火したとき常に必要な判断と手順だけを置く。
- 特定条件でだけ必要な詳細は`references/`へ分離し、`SKILL.md`から読む条件を明示する。
- 内容を短くするために、条件、例外、安全境界、完了条件を削らない。
- 同じ規則を複数箇所へ複製せず、正本を1か所に置く。
- repository固有の規則は、汎用Skill本文ではなくrepository側の文書や設定を正本とする。

## Frontmatterの書き方

`SKILL.md`は`name`と`description`だけを持つ。

```yaml
---
name: example-skill
description: 何を行うSkillかと、どのような依頼で使用するかを簡潔に記載する。
---
```

- `name`はdirectory名と一致するkebab-caseとする。
- `description`は発火判断に使われるため、**何をするか**と**いつ使うか**を含める。
- 誤発火しやすい近接Skillがある場合は、使用しない条件も短く記載する。
- ユーザーが実際に使い得る技術用語、製品名、英語のtrigger語は、発火精度に寄与するなら無理に翻訳しない。
- 詳細な手順や背景説明を`description`へ詰め込まない。

## 見出し

### H1

H1はSkillまたはreferenceの識別名として**英語Title Case**を使う。

```markdown
# Technical Research
# Incident Response
# GitHub Issue Workflow
```

本文の言語とは分けて扱う。

### H2 / H3

H2以下は日本語の文として自然に読めることを基本とする。ただし、技術用語として英語表記の方が一般的な語を無理に翻訳しない。

- `## Related skills`ではなく`## 他Skillとの関係`
- `## Communication`ではなく`## コミュニケーション`
- `## Foregroundを原則とする`のように、技術用語を英語のまま組み込んでよい

API、CLI、TDD、GitHub、Incident Commander、foreground、background、retry、rollback、root causeなど、技術文脈で英語表記が一般的または識別性が高い語は原語を残してよい。
見出し全体を機械的に日本語化することより、対象読者が短時間で意味を認識できることを優先する。

## 本文の言語

本文は日本語を基本とする。

- API名、command名、file path、設定key、schema field、status code、product名等の**正確な識別子**は原語を維持する。
- 分野で日本語より英語が一般的な技術用語は、無理に不自然な訳語へ置き換えない。
- `foreground`、`background`、`retry`、`rollback`、`root cause`、`regression`など、開発・運用で一般的な語は英語のまま使ってよい。
- 通常の文章では、日本語と英語を装飾目的で混在させない。
- 同じ概念の日本語 / 英語表記を不用意に揺らさない。
- status、分類、表headerなど、実行時に繰り返し比較する**固定ラベル**は日本語を優先する。ただしliteralなstatus値や正式名称は原語を維持する。

特に緊急時や手順実行中に直接読む固定ラベルは、認知負荷を下げることを優先する。

## 手順

Skillの中心となる逐次手順は、H2の連番で表す。

```markdown
## 1. 対象を確認する

...

## 2. 変更する

...
```

- `## Workflow`の下へ長い番号付きlistを置くより、主要stepをH2として直接たどれる構造を優先する。
- section内の短いsubstepには番号付きlistを使ってよい。
- 順序に意味がない条件・候補・確認項目はbullet listを使う。
- 手順名は名詞だけでなく、何をするか分かる動詞を含める。
- trivialな処理へ不要なceremonyを追加しない。

## 表

比較、対応関係、状態一覧など、列の意味が安定している情報に使う。

- 表headerは日本語を基本とする。
- schema field等、literalな識別子そのものを示す場合は原語を維持する。
- narrativeな説明を無理に表へ押し込めない。
- 同じ情報を表と本文で重複して説明しない。

## コードブロック

内容に合うlanguage tagを付ける。

- 実行可能なshell command: `bash`
- JSON / YAML等の構造化データ: `json` / `yaml`
- Markdown template: `markdown`
- 疑似コード、概念schema、実行対象でないplain text: `text`
- 実コード: 対象言語名

実行例ではshell promptを含めない。
コードブロックを、単なる文章の強調や長い引用の代わりに使わない。

## 例

例はルールそのものと誤認されないようにする。

- 実際に実行する例か、説明用の疑似例かを区別する。
- 良い例 / 悪い例を示す場合は、何が判断基準か本文で説明する。
- 固定値、file名、component名が一般要件でない場合は、例であることを明示する。

## Referenceの扱い

`references/`は、同じSkillのjob-to-be-doneに属する条件付き詳細に使う。
独立して依頼されるjobをreferenceへ隠さない。

- referenceにはfrontmatterを付けない。
- H1は英語Title Caseとする。
- `SKILL.md`側で、**いつ読むか**を明示する。
- `SKILL.md`とreferenceへ同じ手順を重複して持たせない。
- referenceからさらに分割する場合も、読み込み条件が追えるようにする。

内部referenceへの索引は`## 関連資料`、外部資料の出典は`## 参考資料`を使う。

## 他Skillとの関係

他Skillとの責務境界を書く場合は、`## 他Skillとの関係`へ統一する。

```markdown
## 他Skillとの関係

- `testing`: テスト方針を決める。
- `technical-writing`: 永続的な技術文書を執筆する。
```

単なるSkill一覧にせず、どの判断を委譲するかを短く示す。

## 出典

外部資料を根拠として使う場合は、`technical-writing`の規則に従い、原則として文書末尾の`## 参考資料`へ集約する。
本文には根拠との対応が必要な場合だけ参照記号を置く。

## 推敲

変更後に次を確認する。

- H1は英語Title Caseか。
- H2以下は日本語の文として自然に読め、一般的な技術用語を不自然に翻訳していないか。
- status・分類・表header等の固定ラベルは、短時間で比較しやすい表記に統一されているか。
- 英語が正式名称・識別子・一般的な技術用語ではなく、単なる装飾として混在していないか。
- 中心手順を同じ粒度で追えるか。
- 表、list、コードブロックを目的に応じて使い分けているか。
- `SKILL.md`が条件付き詳細で肥大化していないか。
- 近接Skillとの責務境界が必要なら明示されているか。
- 重複や長い前置きを削っても、条件・例外・安全境界・完了条件が残っているか。

文章の簡潔さ、正確性、正本の扱いは`technical-writing`を基準とする。

## 参考資料

- OpenAI Academy, *Using skills*: https://openai.com/academy/skills/
- Anthropic, *Equipping agents for the real world with Agent Skills*: https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills
