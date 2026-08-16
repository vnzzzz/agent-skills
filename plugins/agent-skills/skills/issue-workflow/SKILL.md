---
name: issue-workflow
description: Issue、ticket、local task recordを作業の正本として、scope確認から実装、検証、review、human handoffまで一貫して進めるときに使用する。GitHub等のprovider固有操作はadapter skillへ委ねる。
---

# Issue Workflow

Issue-drivenな変更では、task recordを **問題・scope・acceptance criteria・判断経緯のSSOT** として扱う。

このSkillはprovider非依存の進め方だけを定義する。Repository-local rules、task-specific instruction、user instructionを優先する。

## Workflow

1. **Task contractを確認する**
   - problem / expected outcome
   - acceptance criteria
   - scope / non-goal
   - permission / safety boundary
   - dependency / blocker
   - delivery / review rule
   Taskと実装が食い違う場合は現状を確認し、完了条件へ影響する差異だけtask recordへ残す。

2. **Preflightする**
   - expected base / workspace / uncommitted work
   - 同じtaskの既存work
   - 必要なtool / credential / runtime
   重複作業やunrelated changesを持ち込まない。

3. **必要十分に実装する**
   非自明な変更は `change-planning` を使う。Acceptance criteriaに不要なcleanupや別問題は混ぜず、必要ならfollow-upへ分離する。Permission boundaryを超えるexternal / production / destructive actionは行わない。

4. **Acceptance criteriaを検証する**
   Test strategyは `testing`、command実行は `command-execution` に従う。実環境確認をagentが実行できない場合は、代替確認だけで完了扱いせずoperator actionとして残す。

5. **重要な経緯だけ記録する**
   Scope / approach変更、blocker、operator action、重要なvalidation evidence、follow-upをtask recordへ残す。Command実況やdelivery artifactとの重複説明は避ける。報告は `evidence-reporting` に従う。

6. **Review可能なartifactへまとめる**
   Provider / repositoryに応じてPR、MR、patch、review branch等を作る。Changed scope、validation、未確認事項、risk、operator action、task traceabilityが判断できればよい。

7. **Independent reviewを受ける**
   Reviewerが設定されている場合はreviewを依頼する。Actionable feedbackは修正・再検証し、suggestionやout-of-scope requestは必要性を判断する。必要ならre-reviewを依頼する。

8. **Human handoffで止める**
   明示委任がない限り、merge / task close / production deploy / destructive managed change / irreversible migrationは行わない。Humanが変更、validation、未確認事項、review結果、残存riskを判断できる状態で停止する。

## Provider boundary

Branch naming、PR/MR、closing keyword、status transition、reviewer API等は `github-issue-workflow` などのadapterで具体化する。Local issue / task fileはこのSkill単独で扱える。

## Related skills

`change-planning` / `development-guidelines` / `command-execution` / `testing` / `debugging` / `evidence-reporting` / `iterative-improvement` を必要な場面だけ利用する。
