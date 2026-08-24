# Contributing

Skillの作成・改善方法そのものは公式のSkill Creatorを利用し、この文書では`agent-skills`固有の規約だけを定義する。

## Skill構成

- 1つのSkillは1つの明確なjob-to-be-doneを扱う。
- `SKILL.md`には常に必要な判断と手順を置き、条件付き詳細は`references/`へ分離する。
- 同じ規則を複数箇所へ重複させない。
- `SKILL.md`のfrontmatterは`name`と`description`だけとし、`name`はdirectory名と一致させる。
- `description`には「何をするか」「いつ使うか」を簡潔に含める。

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

## Validation

CIはfrontmatter、manifest、H1の存在など壊れにくい構造条件を検証する。Title Caseや語彙選択などのstyleは人間レビューで確認し、validatorを過度に複雑化しない。
