---
name: debugging
description: Bug、regression、unexpected behavior、test failure、performance degradation等の原因を、再現・観測・仮説・切り分け・root cause確認・最小fix・再検証の順で証拠に基づいて特定するときに使用する。
---

# Debugging

症状を消すのではなく、なぜ問題が発生したかを十分な確度で理解し、root causeへ直接作用する最小の修正で正しい挙動を回復する。

randomなpatch、過剰なretry、fallback、guard、例外握り潰しで問題を見えなくしない。

単純なtypoや明白な局所bugのように、原因と修正が直接対応する場合はこのprocessを軽量に適用する。debugging ceremonyを目的にしない。

## 1. 影響とmitigationを先に判断する

production incident等で利用者影響、data corruption、security impact、resource exhaustion等が継続している場合は、root cause investigationより先に被害拡大を止める必要がある。

可能な範囲で以下を確認する。

- severity
- affected users / systems
- failure scope
- data integrityへの影響
- ongoingか収束済みか

実環境へ変更を加えるmitigationは、明示的なoperator承認または事前に委任されたincident authorityがある場合だけ実行する。
それ以外は、mitigationの提案・影響評価・実行手順の準備までに留める。

承認された範囲で必要ならrollback、traffic isolation、feature disable、capacity追加等のmitigationを行う。

ただし、mitigationとroot cause fixを区別する。

mitigation前後でも安全な範囲で次の証拠を保全する。

- error / stack trace
- log / trace / metric
- input
- version / deployment state
- relevant configuration
- process / resource state
- first known bad / last known good

サービスが復旧しただけで原因解明済みと扱わない。

## 2. 症状を観測可能な形で定義する

原因を推測する前にproblem statementを作る。

可能な範囲で以下を整理する。

- expected behavior
- actual behavior
- exact error / status / output
- 発生条件
- 発生しない条件
- version / environment
- first known bad / last known good
- frequency / intermittency
- affected / unaffected inputs

「動かない」「遅い」「たまに失敗する」のような曖昧な表現だけで原因候補を決めない。

観測していない内容は事実として書かない。

## 3. reproductionを作る

安全かつ費用対効果が合う場合、問題を再現できる最小条件を作る。

- 不要なcomponentを外す
- inputを縮小する
- option / featureを減らす
- concurrencyを制御する
- dependencyやconfigurationを固定する
- 同じ症状が維持される範囲でsystemを単純化する

productionで危険な再現実験を無理に行わない。

再現できない場合は、再現できないこと自体を事実として扱い、観測済み事実と不足情報を分けて進める。

reproduction作成が大規模作業になる場合は、原因特定への情報価値を考えて実施する。

## 4. systemを理解する

仮説を立てる前に、症状に関係する実装とsystem boundaryを確認する。

少なくとも必要に応じて以下を見る。

- entry point
- symptomまでのcode path
- major data / control flow
- caller / callee boundary
- external dependency
- configuration
- persistence / cache
- resource ownership / lifecycle
- concurrency / ordering
- relevant tests
- recent code / dependency / configuration changes
- commentやdocsに残されたconstraint / invariant / rationale

存在を確認していないcomponentやpathを推測で原因候補にしない。

外部componentの仕様やversion依存挙動が重要なら `technical-research` を利用する。

変更範囲や既存責務の把握が必要なら `change-planning` を利用する。

## 5. 事実と仮説を分ける

観測済み事実から、短い仮説リストを作る。

各仮説は反証可能な形にする。

- 仮説が正しければ何が観測されるはずか
- 何が観測されれば否定できるか
- 最小で安全な確認方法は何か

例:

- Fact: connection数が上限に張り付いている
- Hypothesis: connectionが正常にreleaseされていない
- Test: request完了後のpool stateとclose pathを確認する

仮説を事実として書かない。

一度に複数の仮説へ対応する変更を入れない。結果から何が分かったか判別できる実験を優先する。

negative resultは失敗ではない。原因候補を減らした証拠として残す。

## 6. 情報利得の高い切り分けを優先する

randomなpatchより、探索空間を大きく狭める確認を選ぶ。

有効な方法の例:

- component境界のinput / output比較
- known-good / known-bad比較
- version差分比較
- configuration差分比較
- featureのenable / disable比較
- dependency境界の切り分け
- data setの縮小
- request単位のtrace
- resource lifecycleの追跡
- regressionの `git bisect`

問題を導入したcommitがgood / badで判定可能なら、`git bisect` 等のbinary searchを検討する。

ただし、候補を半分にできるという理由だけで危険なproduction experimentを行わない。

## 7. correlationとcausationを分ける

時間的に近い変化を自動的に原因とみなさない。

避ける例:

- deployment直後だからdeploymentが原因と断定する
- dependency updateと同時期だからdependencyが原因と断定する
- 過去に同じerrorだったため同じroot causeと決めつける
- rollbackで症状が消えたため、rollback対象のすべてを原因とみなす

rollbackや設定変更で症状が消えた場合も、必要に応じて「何が変わったことで問題が消えたか」を確認する。

単一原因を前提にしない。複数条件の組合せでのみ発生するbugもある。

## 8. proximate causeとroot causeを分ける

表面で直接failureを発生させた事象と、その状態を生み出した原因を区別する。

例:

- proximate cause: nil dereferenceでprocessが停止した
- root cause: upstream validation欠落によりinvalid stateが流入した

別の例:

- proximate cause: request timeout
- root cause: connection leakによりpoolが枯渇した

error発生箇所だけを修正して、壊れたinvariantやstate transitionを残さない。

root causeは、確認済み事実と実験結果で説明できる程度まで特定する。

完全な歴史説明を作ることが目的ではない。正しいfixを選ぶために必要な因果関係を理解する。

## 9. root causeへ直接作用する最小fixを選ぶ

原因を特定した後、`development-guidelines` に従って最小の修正を行う。

- unrelated refactorを混ぜない
- 原因不明のretry / fallbackを追加しない
- errorをcatchして隠すだけにしない
- timeoutを伸ばすだけでresource problemを隠さない
- guardを追加するだけでinvalid stateの発生源を残さない
- configurationだけで直せるなら不要なcode変更をしない
- compatibility layerを「念のため」追加しない

fixについて、次を説明できる状態にする。

1. root causeは何か
2. fixのどの部分がroot causeへ作用するか
3. なぜより広い変更が不要か

## 10. regression validationを行う

修正前に問題を再現できる場合は、修正後に同じ条件で症状が消えることを確認する。

加えて必要に応じて以下を行う。

- related tests
- repository standard tests
- affected integration boundaryの確認
- known-bad inputの再実行
- known-good behaviorの非回帰確認
- performance / resource behaviorの再測定

regression testの追加は自動的な義務ではない。

`testing` に従い、以下を満たす場合に追加を検討する。

- 再発時の影響が重要
- behavior / contractとして安定して検証できる
- implementation detailへ過剰に結合しない
- 将来そのtestが落ちたとき、本当に重要なregressionだと言える

bugを修正したという理由だけで専用testを増やさない。

## 11. fixが問題を隠していないか確認する

症状が見えなくなっただけでは不十分である。

確認例:

- log / errorを抑制しただけではないか
- retryがload amplificationを起こさないか
- timeout延長がresource leakを隠していないか
- fallbackがincorrect resultやdata lossを隠していないか
- validation緩和がinvalid stateを受け入れていないか
- cacheがstale dataを見えにくくしていないか
- monitoring threshold変更がfailure detectionを遅らせていないか

mitigationとして意図的に症状を隠す場合は、それをtemporary mitigationとして明示する。

## 12. 調査を止める条件を持つ

非自明なdebuggingは、次を満たしたら追加調査より修正・検証を優先する。

- symptomとreproduction条件を必要十分に理解した
- root causeを証拠で説明できる
- fixがroot causeへどう作用するか説明できる
- relevant validationができる
- 残る重要なunknown / riskが明示されている

「もっと原因があるかもしれない」という理由だけで調査を無制限に広げない。

一方、実験結果が仮説と矛盾した場合は、fixへ進まず仮説を更新する。

## 調査結果の整理

非自明なdebuggingでは、必要に応じて次を簡潔に残す。

1. 症状
2. 再現条件 / 発生条件
3. 確認済み事実
4. 棄却した仮説
5. root cause
6. fixと因果関係
7. 検証
8. 残存リスク / 未確認事項

長い時系列logや調査日誌そのものを成果にしない。

原因の理解や将来の保守に必要なconstraint / invariantをcode commentへ残す場合は `readable-code` を利用する。

user-facing docs、runbook、運用手順、public contractを更新する必要がある場合は `technical-writing` を利用する。

## アンチパターン

次を避ける。

- stack traceの最後の行だけ見てpatchする
- 原因不明のままtry/catchでerrorを握り潰す
- とりあえずretry回数を増やす
- とりあえずtimeoutを伸ばす
- 複数箇所を同時に変更して何が効いたか分からなくする
- testを通すためにexpected resultをbuggy behaviorへ合わせる
- 過去の類似障害へanchoringする
- 時間的相関を因果関係として断定する
- reproduction可能なのに推測だけで修正する
- root causeを特定せず症状ごとにguardを増やす
- bug fixに無関係なcleanupやarchitecture rewriteを混ぜる
- mitigationをpermanent fixと呼ぶ
- source code上の偶然の挙動を外部仕様とみなす

## 他Skillとの関係

- external specification、version、support contract、dependency behaviorが調査へ大きく影響する場合は `technical-research` を利用する。
- system変更前に既存code path、責務境界、変更範囲の把握が必要な場合は `change-planning` を利用する。
- fixを最小に保ち、推測に基づくretry、fallback、abstraction、compatibility workを避ける場合は `development-guidelines` を利用する。
- regression testの価値と検証levelを判断する場合は `testing` を利用する。
- root causeから得た非自明なconstraintやinvariantを実装近傍へ残す場合は `readable-code` を利用する。
- fixがuser-facing documentation、運用手順、architecture-level behavior、public contractを変更する場合は `technical-writing` を利用する。

Debuggingは**実際に何が壊れ、なぜ壊れたか**を特定する。実装系Skillは、**不要な複雑さを増やさずどう修正するか**を決める。
