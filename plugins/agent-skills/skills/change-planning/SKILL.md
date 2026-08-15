---
name: change-planning
description: 非自明な新機能・仕様変更・バグ修正・リファクタリングの実装前に、解決する問題、既存実装、変更範囲、影響、検証方法、リスクを整理し、必要十分な変更計画を作るときに使用する。
---

# Change Planning

非自明な変更では、コードを書く前に「何を変えるか」より先に「なぜ変えるか」「現在どこが責務を持つか」「最小の変更は何か」を確認する。
計画の目的は文書を作ることではなく、誤った前提や不要な新規実装を実装前に減らすことである。

## 適用の強さを変える

変更の不確実性と影響に応じてplanningの深さを変える。

軽量に扱ってよい例:

- typoや明らかな局所修正
- 影響範囲が既知の機械的変更
- 既存patternに従う小さな変更

明示的なplanを作る例:

- 要求を満たす方法が複数ある
- codebaseのどこを変更すべきか明確でない
- 新しいmodule、service、abstractionを追加しようとしている
- public contract、永続data、external dependencyへ影響し得る
- 複数componentへ変更が波及し得る

planning ceremonyを一律に要求しない。

## 1. 解決する問題を確認する

表面上の実装要求と、期待する成果を分ける。

最低限確認するもの:

- 誰または何が困っているか
- 現在何が起きているか
- 変更後に何が成立すれば完了か
- 明示された制約は何か
- 要求されたsolutionが要件そのものなのか、解決案の一つなのか

要件の必要性、user need、solutionの妥当性に疑問がある場合は `product-thinking` を利用する。
要求されていない追加機能を「ついで」に計画へ入れない。

## 2. 現在の実装を読む

実装案を決める前に、関連する現在のコードを確認する。

必要に応じて次を追う。

- entry point
- 責務を持つmodule / component
- 主要なdata flow / control flow
- caller / consumer
- public contract
- persistenceやdata format
- external dependency
- 関連する既存テスト
- code comment / docstringに残された制約、不変条件、設計理由
- public behaviorや運用を説明するdocs

名前だけで責務を推測せず、実際の実装と利用箇所を確認する。
存在を確認していないfile名、class名、component名をplanへ書かない。

## 3. 変更しなくても解決できないか確認する

新しい実装を初期解にしない。
次の順で検討する。

1. 既存機能の現在の使い方で目的を達成できないか
2. configurationや利用方法の変更で解決できないか
3. 既存実装のbug fixや小さな修正で解決できないか
4. 既存componentの責務を自然に拡張できないか
5. それでも責務が異なる場合だけ新しい実装を追加する

新しいfile、class、service、interface、wrapperを要求の名詞から機械的に導かない。
新しいabstractionやcompatibility layerが必要かは `development-guidelines` で確認する。

## 4. 変更範囲を決める

採用方針を決めたら、直接変更と波及変更を分けて整理する。

確認するもの:

- 直接変更する責務と箇所
- 影響を受けるcaller / consumer
- contract、schema、data formatへの影響
- persistenceやmigrationの要否
- backward compatibilityの要否と理由
- external dependencyや運用への影響
- 更新すべきテスト
- public behavior、利用方法、architecture上の重要事項が変わる場合のdocs

同時に、今回**変更しないもの**も明示する。
無関係なcleanup、別問題の修正、将来向け拡張を同じ変更へ混ぜない。

## 5. 事実・推測・未知を分ける

planの前提を暗黙にしない。

- repositoryで確認した事実
- 現時点の推測
- まだ確認していない事項
- 誤ると影響が大きい前提

を区別する。

特に、並行処理、transaction、data migration、external API、version compatibility、resource lifecycleなど影響の大きい要素がある場合は、実装前に必要な確認を計画へ含める。

全ての未知をゼロにする必要はない。
ただし、高影響の未知を「たぶん大丈夫」として隠さない。

## 6. 検証方法を実装前に決める

「実装する」だけでなく、「正しく変わったと判断する方法」をplanへ含める。

- 変更後に観測すべきbehavior / contract
- 直接関係する既存テスト
- 追加するテストが必要か
- unit / integration / end-to-endのどこで検証するか
- repository標準のvalidation
- 必要なら実環境や最小再現で確認する事項

テスト量やtest levelの判断には `testing` を利用する。
実装詳細を固定するだけのテストをplan上の成果にしない。

## 7. 実装可能な最小planにする

非自明な変更のplanは、原則として次を含める。

1. **Problem / expected outcome** — 何を解決し、何が成立すれば完了か
2. **Current implementation** — 現在どこが責務を持ち、どう動いているか
3. **Approach** — 採用する変更方針と、その理由
4. **Change scope** — 直接変更する対象と波及対象
5. **Non-goals** — 今回変更しないもの
6. **Validation** — 何をどう確認するか
7. **Risks / unknowns** — 重要な前提、未確認事項、追加調査

確認済みの対象は具体名で書く。
一方で、実装前にfunction単位の処理順やprivate APIまで固定しすぎない。

## 実装へ移る条件

次が満たされたら、planningを続けるより実装へ進む。

- 解決する問題とexpected outcomeが明確
- 現在の責務と主要な変更箇所を確認済み
- 新規実装が必要か検討済み
- 変更対象と非対象を説明できる
- validation方法が決まっている
- 高影響の未知が解消済み、または明示されている

「もっと調べれば何か分かるかもしれない」だけを理由にplanningを延長しない。

## 実装中に前提が崩れた場合

実装中にplanと異なる事実が判明したら、planへ実装を無理に合わせない。

- 新しい事実を確認する
- approachやscopeへの影響を再評価する
- 必要ならplanを更新する
- 変更が別責務へ広がるなら、同じ変更に含めるべきか再判断する

planは固定契約ではなく、確認済み事実に基づく実装判断のための道具である。

## アンチパターン

- repositoryを読まずにmodule構成から設計する
- 要求された名詞ごとに新しいclass / serviceを作る
- feature requestと決めつけ、既存bugや既存機能で解決できないか確認しない
- 「将来必要そう」を理由に拡張ポイントを詳細設計する
- 変更対象だけを書き、non-goal、validation、riskを書かない
- 未確認のfile名やcomponent名を推測でplanへ書く
- plan documentを大きくすること自体を成果にする
- trivialな変更へ重いplanning processを要求する

## 他Skillとの関係

- 問題、user need、solutionの妥当性は `product-thinking` を利用する。
- 外部仕様、version、support範囲等の確認が実装判断へ影響する場合は `technical-research` を利用する。
- 最小実装、abstraction、backward compatibilityの判断は `development-guidelines` を利用する。
- 既存commentから制約や不変条件を読み、実装時に残す情報を判断する場合は `readable-code` を利用する。
- 必要十分なtest strategyは `testing` を利用する。
- public contract、利用方法、architecture上の重要事項が変わる場合のdocsは `technical-writing` を利用する。

このSkillはproject management、長期roadmap、resource allocation、詳細なarchitecture document作成そのものを扱わない。
