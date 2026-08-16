---
name: command-execution
description: 長時間・破壊的・状態変更を伴うコマンドを安全に実行し、重複実行、回収不能なbackground処理、誤ったsuccess/failure判定を避けるために使用する。repository固有のcommand名やartifact pathはlocal docsを正本とする。
---

# Command Execution

長時間または状態変更を伴うコマンドは、実行そのものよりも「何を実行したか」「現在どういう状態か」「結果をどの根拠で判断したか」を追跡可能にすることを優先する。

このSkillはrepository非依存の実行ルールだけを扱う。具体的なcommand、process pattern、artifact path、service名はrepository-localのdocs、scripts、`--help`、AGENTS.md等を優先する。

## 実行前

1. 実行するcommandの正本を確認する。記憶だけでflagやsubcommandを補わない。
2. working tree、target environment、必要なcredentialやdependencyを確認する。
3. 同じ処理がすでに進行中でないか確認できる場合は確認する。
4. production、managed service、database、external APIなど不可逆性や外部影響がある操作では、対象environmentと実行権限を確認する。

production等へ変更を加える操作は、userの明示的な依頼、または事前に委任されたscopeであることを確認してから実行する。確認できない場合は、preflight、影響確認、実行手順の提示までに留める。

同一目的のjob/processがすでに進行中なら、原則として重複起動しない。既存processやartifactを観測し、継続・停止・再実行のどれが妥当か判断する。

## Foregroundを原則とする

Agentが完了状態を回収できる作業はforegroundで実行する。

理由なく次のような回収不能なdetached executionへ逃がさない。

```bash
nohup ... &
... &
disown
setsid ...
```

長時間かかること自体はbackground化の理由にならない。

一方、dev serverを起動したまま別commandを実行するなど、task上concurrent executionが必要な場合はbackground実行を禁止しない。その場合は、processやjobを継続して観測でき、終了時に確実に停止・回収できるmanagedなsession、job handle、task機能等を使用する。

scheduled/background taskを将来継続させる場合は、利用可能な明示的なtask機能を使い、unmanaged processを残さない。

## 状態判定

Sparse stdout、途中までのlog、長い無出力時間だけでsuccess/failureを推測しない。

可能な限り次を組み合わせて判断する。

- exit status
- process state
- commandが生成するstatus / manifest / report / artifact
- external serviceやdatabaseの観測可能な状態
- test / validator結果

「processが終了した」と「期待する処理が成功した」を同一視しない。

## 中断と停止

Userが停止を求めた場合や、継続が安全でないと判断した場合はgraceful terminationを優先する。

1. toolやapplication固有のstop方法
2. graceful signal / cancellation
3. 一定時間後に状態再確認
4. graceful stopが失敗した場合だけforce termination

広いprocess patternで無関係なprocessまで終了させない。

## 失敗時

失敗した場合は、同じcommandを機械的に繰り返す前に実際のerrorを読む。

- dependency不足
- credential / permission
- network / external service
- invalid input
- stale process / lock
- application bug

を区別し、再実行で改善する根拠がある場合だけretryする。原因特定が必要な場合は `debugging` を使う。

## 報告

最終報告では必要に応じて次を区別する。

- completed
- failed
- skipped
- blocked
- interrupted / cancelled
- still running
- not run

実行していないcommandやexternal validationを実行済みとして扱わない。長時間commandでは、foreground/backgroundの別、重複実行確認、結果判断に使ったartifactやstatusも必要に応じて示す。

報告の構造やevidenceの表現は `evidence-reporting` を利用する。

## 他Skillとの関係

- 実装前の変更計画は `change-planning`。
- 原因不明の失敗解析は `debugging`。
- test strategyは `testing`。
- 実行・検証結果の報告スタイルは `evidence-reporting`。
