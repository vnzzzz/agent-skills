---
name: iterative-improvement
description: 明確なgoal、baseline、success criteria、最大cycle数を持つboundedな反復改善を実行するときに使用する。open-endedな自律反復ではなく、各cycleで仮説・最小変更・validation・before/after判断を行う。
---

# Iterative Improvement

反復改善は「良くなるまで続ける」ではなく、明確なgoalとstop conditionを持つbounded workflowとして扱う。

このSkillはrepository非依存のiteration protocolだけを扱う。Domain layer、command、artifact、metricの意味はrepository-local docsやtask-specific rulesを優先する。

## 開始前に決める

少なくとも次を確認する。

- **Goal**: 何を改善するか
- **Baseline**: 現在の状態を何で観測するか
- **Success criteria**: 何が成立したら成功か
- **Allowed scope**: どの種類の変更まで許されるか
- **Forbidden scope**: 今回触らないもの
- **Max cycles**: 最大反復回数

Userやowning Issueがmax cyclesを定義していない場合、無制限に反復しない。小さな改善taskでは原則3 cycle程度を上限候補とし、複雑さに応じて必要最小限に設定する。

Success criteriaを定義できない場合は、まずtask scopeやobservable outcomeを整理する。要求自体の妥当性を見直す必要がある場合は `product-thinking`、変更計画が必要なら `change-planning` を使う。

## 1 cycleの構造

各cycleは一つの小さなhypothesisを持つ。

1. Baseline /前cycleのevidenceを確認する
2. 現在の主要blockerを一つ選ぶ
3. 改善仮説を立てる
4. 最小のactionを選ぶ
5. 必要ならfocused test/assertionを先に用意する
6. 変更を実施する
7. 変更に対応するvalidationを行う
8. Before/after evidenceを比較する
9. Continue / success / blocked / stopを判断する

複数の独立したblockerを一度に直し、どの変更が効いたか分からなくしない。

## Cycle completion

Fileを編集しただけではcycle完了としない。

少なくとも次のどちらかが必要。

- observableなbefore/after evidenceが得られた
- validation不能・external dependency等により進めない理由を特定できた

No-op cycleは、調査によって安全な変更が存在しないことを示す場合だけ許容する。連続してno-opになる場合は、同じlayerで反復せずpivotまたはstopする。

## Stop conditions

次のいずれかで停止する。

- Success criteriaを満たした
- Max cyclesに達した
- 次の有効なactionがcurrent scope外
- External dependency、credential、environment不足で進めない
- Evidenceが不足し、変更の妥当性を判断できない
- Validationが失敗し、current scope内で安全に解決できない
- 次の変更が過度に大きく、別Issue / planへ分離すべき

「まだ何か改善できそう」だけを理由に継続しない。

## Regressionを見落とさない

Target metricだけでなく、変更によって壊れ得る重要なbehavior / guardrailも確認する。

改善値が上がっていても、比較条件が変わった場合や別のcritical behaviorがregressした場合はsuccessと断定しない。Validationとevidenceの扱いは `validation-reporting` を使う。

## Report

反復を行った場合は簡潔に次を残す。

- Goal / success criteria / max cycles
- Baseline
- 各cycleのblocker、hypothesis、action、validation、result
- Stop reason
- Remaining work

Cycle数そのものを成果にしない。Success criteriaを早く満たした場合は残りcycleを消化せず停止する。

## 他Skillとの関係

- 実装前planningは `change-planning`。
- 最小実装とabstraction判断は `development-guidelines`。
- test strategyは `testing`。
- command executionは `command-execution`。
- validationと最終evidence reportは `validation-reporting`。
- failureのroot causeが不明なら `debugging`。
