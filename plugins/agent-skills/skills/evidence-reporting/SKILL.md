---
name: evidence-reporting
description: 実施した変更・検証・未実施事項・残存リスクを、確認済み事実と推測を混同せず簡潔に報告するときに使用する。何を検証すべきかはtestingやrepository-local rulesへ委ね、evidenceに基づくreporting styleだけを扱う。
---

# Evidence Reporting

作業報告では、実際に確認したことと確認していないことを明確に分ける。commandを実行した事実だけをsuccessの根拠にせず、その結果から何が確認できたかを必要十分に示す。

このSkillはvalidationの選択やtest strategyを決めない。何を検証するかは`testing`、repository-local rules、task-specific contractを優先する。commandの安全な実行と状態判定は`command-execution`の責務とする。

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

## 根拠より強く断定しない

一部sampleだけを確認した場合は全体保証と書かない。特定environmentだけで確認した結果を、他environmentでも成立する一般仕様として扱わない。

Before / afterを比較する場合は、input data、dataset、seed、model、cache、configuration、environment等の比較条件が揃っているかを確認し、条件が異なる場合は単純な数値差をregressionやimprovementとして断定しない。

比較不能または部分比較である場合は、その制約を報告する。

## 状態を曖昧にしない

作業やcheckの状態は必要に応じて次を区別する。

- 完了 / 成功
- 失敗
- スキップ
- 阻害中
- 中断 / キャンセル
- 実行中
- 未実行
- 利用不可

`スキップ`と`成功`、`阻害中`と`失敗`を同一視しない。

実施できなかった重要なcheckは隠さず、理由と結果へ与える影響を必要に応じて短く示す。

## 最終報告

必要十分な情報に絞る。非自明な変更では、原則として次から必要な項目だけを使う。

1. **概要** — 何を変え、現在何が成立しているか
2. **変更範囲** — 主要な変更対象
3. **主要な判断・根拠** — 結論に必要な判断と根拠
4. **検証結果** — 実際に実行したcheckと結果
5. **未実施・利用不可** — 実行していない重要なcheck
6. **残存リスク・後続作業** — 未確認事項、残存risk、follow-up

すべての項目を機械的に出力しない。trivialな変更では、結論と確認結果だけで十分な場合がある。

Repositoryがcommit、artifact path、metrics、deployment status等の追加report contractを持つ場合は、そのlocal ruleを優先する。

Raw logを大量に貼るより、判断に必要なerror、status、metric、artifactを優先する。

## 他Skillとの関係

- `testing`: 何をどのlevelで検証するか決める。
- `command-execution`: commandを安全に実行し、状態を判定する。
- `debugging`: 原因不明のfailureを調査する。
- `iterative-improvement`: boundedな反復改善を進める。
- `technical-writing`: durableな技術文書を構成・執筆する。
