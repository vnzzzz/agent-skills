---
name: issue-workflow
description: Issue、ticket、local task recordを作業の正本として、scope確認から実装、検証、review、human handoffまで一貫して進めるときに使用する。GitHub Issue / Pull Requestで進める場合もこのSkillを使用し、GitHub固有手順はreferences/github.mdを参照する。
---

# Issue Workflow

Issue-drivenな変更では、task recordを**問題・対象範囲・完了条件・判断経緯のSSOT**として扱う。

このSkillはprovider非依存のlifecycleを正本とする。Repository-local rules、task-specific instruction、user instructionを優先する。

## 1. タスク契約を確認する

最低限、次を確認する。

- 問題 / 期待結果
- 完了条件
- 対象範囲 / 非目標
- 権限 / 安全境界
- 依存関係 / 阻害要因
- delivery / review rule

Taskと実装が食い違う場合は現状を確認し、完了条件へ影響する差異だけtask recordへ残す。

## 2. 事前確認を行う

- expected base / workspace / uncommitted work
- 同じtaskの既存work
- 必要なtool / credential / runtime

重複作業やunrelated changesを持ち込まない。

## 3. 必要十分に実装する

非自明な変更は`change-planning`を使う。完了条件に不要なcleanupや別問題は混ぜず、必要ならfollow-upへ分離する。権限境界を超えるexternal / production / destructive actionは行わない。

## 4. 完了条件を検証する

Test strategyは`testing`、command実行は`command-execution`に従う。実環境確認をagentが実行できない場合は、代替確認だけで完了扱いせずoperator actionとして残す。

## 5. 重要な経緯だけ記録する

対象範囲 / approach変更、blocker、operator action、重要なvalidation evidence、follow-upをtask recordへ残す。Command実況やdelivery artifactとの重複説明は避ける。報告は`evidence-reporting`に従う。

## 6. レビュー可能な成果物へまとめる

Provider / repositoryに応じてPR、MR、patch、review branch等を作る。変更範囲、検証、未確認事項、risk、operator action、task traceabilityが判断できればよい。

## 7. 独立レビューを受ける

Reviewerが設定されている場合はreviewを依頼する。Actionable feedbackは修正・再検証し、suggestionやout-of-scope requestは必要性を判断する。必要ならre-reviewを依頼する。

## 8. 人間への引継ぎで止める

明示委任がない限り、merge / task close / production deploy / destructive managed change / irreversible migrationは行わない。Humanが変更、validation、未確認事項、review結果、残存riskを判断できる状態で停止する。

## Provider固有のワークフロー

Branch naming、PR / MR、closing keyword、status transition、reviewer API等のprovider固有mechanicsは、core workflowへ混ぜず必要なreferenceから読む。

- **GitHub Issue / Pull Requestを使う場合:** provider固有操作へ入る前に[references/github.md](references/github.md)を読む。
- GitHubを使わないtaskではGitHub referenceを読み込まない。
- 将来別providerを追加する場合も、独立したjobでなければ`references/<provider>.md`を基本とし、top-level Skillを増やさない。

Provider referenceはこのSkillのlifecycleを上書きせず、そのproviderで必要なdelivery mechanicsだけを具体化する。

## 他Skillとの関係

- `change-planning`: 非自明な変更の実装計画を作る。
- `development-guidelines`: 実装を必要十分な範囲に保つ。
- `command-execution`: commandを安全に実行し、状態を判定する。
- `testing`: テスト方針と必要な検証levelを決める。
- `debugging`: 原因不明のfailureを調査する。
- `evidence-reporting`: 実施内容と検証結果を根拠付きで報告する。
- `iterative-improvement`: boundedな反復改善を行う。
