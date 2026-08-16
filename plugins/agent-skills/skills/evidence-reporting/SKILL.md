---
name: evidence-reporting
description: 実施した変更・検証・未実施事項・残存リスクを、確認済み事実と推測を混同せず簡潔に報告するときに使用する。何を検証すべきかはtestingやrepository-local rulesへ委ね、evidenceに基づくreporting styleだけを扱う。
---

# Evidence Reporting

作業報告では、実際に確認したことと確認していないことを明確に分ける。commandを実行した事実だけをsuccessの根拠にせず、その結果から何が確認できたかを必要十分に示す。

このSkillはvalidationの選択やtest strategyを決めない。何を検証するかは `testing`、repository-local rules、task-specific contractを優先する。commandの安全な実行と状態判定は `command-execution` の責務とする。

## 確認したことだけを報告する

実行・観測していない内容を確認済みとして書かない。

区別する例:

- static inspectionで確認したこと
- automated testで確認したこと
- actual runtimeで確認したこと
- external serviceで確認したこと
- artifact / metricsから観測したこと
- 推測、未確認事項

例えばconfiguration syntaxがvalidでも、clean rebuildが成功したとは書かない。mock testが通ってもexternal APIの実接続を確認したとは書かない。

`CI success`や`command completed`のような状態を示す場合は、必要に応じて対象workflow、check、artifact等を示し、その状態から直接言える範囲だけを結論にする。

## Evidenceより強く断定しない

一部sampleだけを確認した場合は全体保証と書かない。特定environmentだけで確認した結果を、他environmentでも成立する一般仕様として扱わない。

Before/afterを比較する場合は、入力data、dataset、seed、model、cache、configuration、environment等の比較条件が揃っているかを確認し、条件が異なる場合は単純な数値差をregressionやimprovementとして断定しない。

比較不能または部分比較である場合は、その制約を報告する。

## 状態を曖昧にしない

作業やcheckの状態は必要に応じて次を区別する。

- completed / passed
- failed
- skipped
- blocked
- interrupted / cancelled
- still running
- not run
- unavailable

`skipped`と`passed`、`blocked`と`failed`を同一視しない。

実施できなかった重要なcheckは隠さず、理由と結果へ与える影響を必要に応じて短く示す。

## 最終報告

必要十分な情報に絞る。非自明な変更では、原則として次から必要な項目だけを使う。

1. **Summary** — 何を変え、現在何が成立しているか
2. **Changed scope** — 主要な変更対象
3. **Key decisions / evidence** — 結論に必要な判断と根拠
4. **Validation results** — 実際に実行したcheckと結果
5. **Skipped / unavailable** — 実行していない重要なcheck
6. **Remaining risks / follow-up** — 未確認事項、残存risk、後続作業

すべての項目を機械的に出力しない。trivialな変更では、結論と確認結果だけで十分な場合がある。

Repositoryがcommit、artifact path、metrics、deployment status等の追加report contractを持つ場合は、そのlocal ruleを優先する。

Raw logを大量に貼るより、判断に必要なerror、status、metric、artifactを優先する。

## 他Skillとの関係

- 何をどのlevelで検証するかは `testing`。
- commandを安全に実行し状態を判定する方法は `command-execution`。
- 原因不明のfailureを調査する場合は `debugging`。
- boundedな反復改善の進め方は `iterative-improvement`。
- durableな技術文書の構成や記述は `technical-writing`。
