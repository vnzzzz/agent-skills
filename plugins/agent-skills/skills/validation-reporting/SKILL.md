---
name: validation-reporting
description: 変更リスクに応じてvalidation depthを選び、実施した検証・未実施の検証・残存リスクを事実ベースで報告するときに使用する。framework固有commandやrepository固有report形式はlocal rulesを優先する。
---

# Validation Reporting

変更の完了条件は「何かを実行したこと」ではなく、変更による重要なriskを妥当な方法で確認できたこととする。

このSkillはrepository非依存のvalidation選択とevidence reportingを扱う。具体的なtest command、lint、schema check、CI、artifact path、report templateはrepository-localの定義を優先する。

## Validation depthを決める

変更範囲とfailure impactに応じて必要な検証を選ぶ。

例:

- docs-only / metadata-only: syntax、link、format、diff hygiene等の直接check
- 局所code変更: touched behaviorのfocused test + repository標準static check
- shared helper / public contract / broad refactor: focused testに加えてbroader test suite
- schema / persistence: migration、read/write contract、rollbackやcompatibility影響
- runtime / external integration: local testだけでは保証できない境界のintegration / E2E
- infrastructure / environment: clean setup / rebuild / version / permission / persistenceの確認

固定のchecklistを全変更へ一律適用しない。一方で、重要なboundaryをunit testだけで済ませない。

Test strategyそのものは `testing` を使う。

## Focused checkから始める

最初に変更へ最も直接関係するcheckを実行する。

Focused validationが失敗したまま、理由なくfull suiteへ進まない。直接原因を直してからbroader validationへ進む。

Broader validationは、変更のblast radius、shared ownership、public contract、integration riskに応じて追加する。

## Evidenceを区別する

次を混同しない。

- static inspectionで確認したこと
- automated testで確認したこと
- actual runtimeで確認したこと
- external serviceで確認したこと
- artifact / metricsから観測したこと
- 推測、未確認事項

例えばconfiguration syntaxがvalidでも、clean rebuildが成功する保証にはならない。mock testが通ってもexternal APIの実接続を確認したことにはならない。

## Metrics / artifact比較

Before/after比較を行う場合は、比較条件が同じか確認する。

入力data、dataset、seed、label、model、cache、configuration、environment等が変わっている場合、単純な数値差をregression/improvementとして断定しない。

比較不能または部分比較の場合は、その制約を明示する。

## Skipped / blockedを明記する

実施できなかったcheckは隠さない。

理由を次のように区別する。

- not applicable
- intentionally skipped
- unavailable tool / dependency
- credential / permission不足
- environment不足
- timeout / interruption
- external dependency unavailable
- deferred to another Issue / scope

未実施checkがmerge判断に重要なら、そのまま完了扱いにしない。

## Final report

必要十分な情報に絞る。原則として次を含める。

1. **Summary** — 何を変え、何が成立したか
2. **Changed scope** — 主要な変更対象
3. **Key decisions / evidence** — 判断に必要な根拠
4. **Validation** — 実行したcheckと結果
5. **Skipped / unavailable** — 実行していない重要check
6. **Remaining risks** — 未解消risk、follow-up

Repositoryがcommit message、artifact path、metrics、deployment status等の追加report contractを持つ場合だけ追加する。

Raw logを大量に貼るより、decision-criticalなerror、status、metric、artifactを優先する。

## 他Skillとの関係

- test設計は `testing`。
- commandを安全に実行・観測する方法は `command-execution`。
- 原因不明のfailureは `debugging`。
- boundedな反復改善でcycleごとにvalidationする場合は `iterative-improvement`。
