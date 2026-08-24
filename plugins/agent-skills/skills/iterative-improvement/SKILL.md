---
name: iterative-improvement
description: 明確なgoal、baseline、success criteria、最大cycle数を持つboundedな反復改善を実行するときに使用する。open-endedな自律反復ではなく、各cycleで仮説・最小変更・validation・before/after判断を行う。
---

# Iterative Improvement

反復改善は「良くなるまで続ける」ではなく、明確なgoalとstop conditionを持つbounded workflowとして扱う。

このSkillはrepository非依存のiteration protocolだけを扱う。Domain layer、command、artifact、metricの意味はrepository-local docsやtask-specific rulesを優先する。

## 開始前に決める

少なくとも次を確認する。

- **目標**: 何を改善するか
- **基準状態**: 現在の状態を何で観測するか
- **成功条件**: 何が成立したら成功か
- **許可範囲**: どの種類の変更まで許されるか
- **対象外**: 今回触らないもの
- **最大サイクル数**: 最大反復回数

Userやowning Issueが最大サイクル数を定義していない場合でも、無制限に反復しない。taskのcost、risk、validation時間に応じて、必要十分な小さい上限を明示する。

成功条件を定義できない場合は、まずtask scopeやobservable outcomeを整理する。要求自体の妥当性を見直す必要がある場合は`product-thinking`、変更計画が必要なら`change-planning`を使う。

## 1回のサイクル

各サイクルは一つの小さな仮説を持つ。

1. 基準状態または前サイクルのevidenceを確認する
2. 現在の主要blockerを一つ選ぶ
3. 改善仮説を立てる
4. 最小のactionを選ぶ
5. 必要ならfocused test / assertionを先に用意する
6. 変更を実施する
7. 変更に対応するvalidationを行う
8. Before / after evidenceを比較する
9. 継続 / 成功 / blocked / 停止を判断する

複数の独立したblockerを一度に直し、どの変更が効いたか分からなくしない。

## サイクルの完了条件

Fileを編集しただけではサイクル完了としない。

少なくとも次のどちらかが必要。

- observableなbefore / after evidenceが得られた
- validation不能・external dependency等により進めない理由を特定できた

No-op cycleは、調査によって安全な変更が存在しないことを示す場合だけ許容する。連続してno-opになる場合は、同じlayerで反復せずpivotまたはstopする。

## 停止条件

次のいずれかで停止する。

- 成功条件を満たした
- 最大サイクル数に達した
- 次の有効なactionがcurrent scope外
- External dependency、credential、environment不足で進めない
- Evidenceが不足し、変更の妥当性を判断できない
- Validationが失敗し、current scope内で安全に解決できない
- 次の変更が過度に大きく、別Issue / planへ分離すべき

「まだ何か改善できそう」だけを理由に継続しない。

## 回帰を見落とさない

Target metricだけでなく、変更によって壊れ得る重要なbehavior / guardrailも確認する。

改善値が上がっていても、比較条件が変わった場合や別のcritical behaviorがregressした場合はsuccessと断定しない。必要なtest strategyは`testing`、実施した検証結果の報告は`evidence-reporting`を使う。

## 報告

反復を行った場合は簡潔に次を残す。

- 目標 / 成功条件 / 最大サイクル数
- 基準状態
- 各サイクルのblocker、仮説、action、validation、result
- 停止理由
- 残作業

サイクル数そのものを成果にしない。成功条件を早く満たした場合は残りサイクルを消化せず停止する。

## 他Skillとの関係

- `change-planning`: 実装前の計画を作る。
- `development-guidelines`: 最小実装とabstractionを判断する。
- `testing`: テスト方針を決める。
- `command-execution`: commandを安全に実行する。
- `evidence-reporting`: 実施したvalidationと最終evidenceを報告する。
- `debugging`: failureのroot causeが不明な場合に調査する。
