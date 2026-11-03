---
name: change-planning
description: 変更方法や影響範囲が自明でない機能追加・バグ修正・仕様変更・リファクタリングで、既存の責務、変更範囲、非目標、検証、リスクを整理した実装計画が必要なときに使用する。typoや単純rename、原因調査のみ、CI結果報告のみには使用しない。
---

# Change Planning

計画は文書を増やすためでなく、誤った前提と不要な実装を早期に避けるために作る。
不確実性と変更の影響に合わせて深さを変え、十分に判断できたら実装へ進む。

## いつ計画するか

次のような非自明な変更では、必要な範囲を調べて計画する。

- 複数の解決方法があり、選択理由が必要
- 現在の責務や変更箇所が不明
- public contract、永続データ、外部依存、複数componentに影響し得る
- 新しいmodule、service、abstraction、migrationが必要か判断する

typo、機械的なrename、影響が既知の局所変更には独立したplanを要求しない。
明白な変更なら簡潔に確認して作業する。planning ceremonyを完了条件にしない。

## 1. 目的と現在の実装を確認する

- 現状の問題、期待する振る舞い、完了条件、明示的制約を分ける
- 要求された実装方法が必須要件か、提案された解決策かを見極める
- 関連するentry point、責務、data/control flow、caller/consumerを実際のコードで追う
- 関連するcontract、永続化、外部依存、既存テスト、docs、commentに記された制約を必要に応じて読む

名前だけで責務を推測せず、未確認のfile名やclass名を実在するものとして書かない。
確認した事実、推測、未確認事項を分ける。並行処理、transaction、resource lifecycle、migration、version互換などの高影響な未知を見落とさない。
そもそものuser needや解決策の妥当性が未確定なら product-thinking を利用する。

## 2. 必要な変更を選ぶ

次の順で、現在の要件を満たす方法を検討する。

1. 既存機能の利用や設定変更で目的を達成できないか
2. 既存実装のbug修正や削除で解決できないか
3. 既存componentの責務を自然に拡張できないか
4. 責務が本当に異なる場合だけ新しい実装を追加する

新しいclass、interface、wrapper、compatibility layerを要求の名詞から機械的に導かない。
後方互換性が必要なら、守るconsumerやデータとその理由を明確にする。設計の単純さは development-guidelines の責務とする。

## 3. 影響範囲と非目標を決める

- 直接変更する責務と、影響するcaller/consumer
- public contract、schema、data format、persistence、migration、互換性
- external dependency、運用、重要なsecurity/failure modeへの影響
- 必要なテスト、利用方法や公開動作が変わる場合のdocs
- 今回は変更しないもの

無関係なcleanup、将来向け拡張、別問題の修正を同じ変更に混ぜない。
大きな変更では、各段階で成立するreview可能な単位を考える。

## 4. 検証を先に決める

期待する振る舞い・契約を何で観測すれば合格かを決める。
関連する既存テスト、必要な追加テスト、repository標準のvalidation、必要なら実環境での確認を挙げる。
unit / integration / end-to-endの選択とテスト量は testing に委ね、内部実装の形を固定するだけのテストを成果にしない。

## 計画の出力

必要な項目だけ、実装の判断に使える短さで示す。

1. **問題と完了条件** — 解決すること、期待する結果
2. **現状の事実** — 確認した責務・挙動・制約
3. **変更方針と理由** — 採用案と必要なら代替案
4. **範囲と非目標** — 直接変更、波及、変更しないもの
5. **検証** — 観測する振る舞いと確認方法
6. **リスクと未確認事項** — 高影響の前提、残る未知

確認済みの対象は具体名で書くが、実装前にprivate APIや処理順まで不必要に固定しない。

## 実装へ進む条件

問題と完了条件、現在の責務、採用案、変更範囲と非目標、検証方法が分かり、高影響の未知を解消または明示できたら進む。
すべての未知をゼロにするための追加調査はしない。
実装中に前提が崩れたら新事実に合わせて方針・範囲を見直す。計画に実装を無理に合わせない。

外部仕様・versionの確認は technical-research、公開docsの改訂は technical-writing、制約をcommentに残す判断は code-comments に委ねる。
このSkillはissue lifecycle、長期roadmap、resource allocation、詳細architecture documentの作成そのものを扱わない。
