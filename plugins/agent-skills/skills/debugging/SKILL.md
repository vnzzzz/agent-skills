---
name: debugging
description: Bug・regression・test failure・局所的なunexpected behaviorやperformance degradationのroot causeを、再現・仮説検証・切り分け・修正前後の検証で特定するときに使用する。稼働中の本番障害や他team・vendorを含むincident全体の対応はincident-responseを優先する。
---

# Debugging

症状を隠すpatchではなく、観測した事実から原因を説明し、原因へ作用する修正を検証する。原因が明白な局所bugは軽量に扱い、調査手順を儀式化しない。

稼働中の本番障害や複数system・teamをまたぐincidentは`incident-response`を優先する。局所実装にfailure domainが絞れた場合はこのSkillでroot causeを調べる。

## 1. 症状・影響・権限を確認する

可能な範囲で次を整理する。

- expected / actual behavior、exact error、status、output
- affected / unaffected input、environment、version、発生頻度
- first known bad / last known good、関連する変更
- user impact、data integrity、security、resource exhaustion

観測していないことを事実にしない。Production等で被害が続く場合は影響緩和を先に検討する。実環境へ変更する操作は、userが依頼した範囲または委任された権限内だけで実行し、それ以外は提案・preflightに留める。

Rollbackやrestartで失われ得るlog、trace、metric、process state等は、復旧を不必要に遅らせない範囲で保全する。Mitigationによる症状消失をroot causeの確定と混同しない。

## 2. 再現と実装を調べる

安全かつ費用対効果が合う場合、input、dependency、configuration、concurrency等を固定・縮小し、症状が保たれる最小の再現条件を探す。Productionで危険な再現実験は行わない。

関連entry pointから症状までのcode / data flowを読み、必要に応じて次を追う。

- caller / callee、external boundary、persistence、cache
- resource lifecycle、concurrency、ordering、state transition
- relevant tests、最近の変更、commentやdocsのconstraint / invariant

再現できない場合はその事実を明示し、観測済みlogやaffected / unaffected比較から進める。実在を確認していないcomponentを原因として断定しない。

## 3. 仮説を立て、情報利得の高い切り分けをする

各仮説を反証可能にする。正しければ何が観測され、何が否定材料となるかを決め、安全でcostの低い確認から選ぶ。

有効な手段:

- known-good / known-bad input・version・configurationの比較
- component境界の入出力、request単位のtrace
- failure条件を保ったdata / feature / dependencyの縮小
- resourceの所有権、release path、concurrencyの観測
- 回帰を導入したcommitの探索（必要なら`git bisect`）

同時に複数の仮説を修正して効果が不明になる実験は避ける。Negative resultも候補を減らす証拠として残す。

## 4. 直接原因と根本原因を分ける

Errorを発生させた直接原因と、それを許した根本原因を区別する。例えば`nil dereference`と上流validation欠落、timeoutとconnection leakは別の層の原因になり得る。

Deploymentやdependency update直後という時間的相関だけで因果関係を確定しない。Rollbackで症状が消えた場合も、何が変わったのか確認する。複数条件が重なったbugの可能性も考える。

根本原因は、症状へ至るfailure mechanismと観測・実験の対応から説明する。完全な歴史説明より、正しい修正を判断できる確度を優先する。

## 5. 根本原因へ作用する修正を選ぶ

修正前に、(1)原因、(2)修正の作用点、(3)変わるcontractやriskを説明できるか確認する。

Configurationだけで直るなら不要なcodeを変えない。無関係なrefactorを混ぜない。原因不明のretry・fallback・timeout延長・catch・guard追加で症状を隠すだけの変更は恒久修正として扱わない。

一時的なmitigationが必要なら原因未解決と終了条件を明示する。単純化のために必要なvalidation、error handling、resource safetyを省略しない。

## 6. 同条件で修正を検証する

可能なら修正前に失敗した条件で再実行する。変更riskに応じてrelated tests、integration boundary、known-good behavior、performance / resource状態も確認する。

Regression testは再発時に実害のあるbehavior / contractを安定して守れる場合に追加する。Bug修正ごとに専用testを機械的に増やさない。Testの期待値をbuggy behaviorへ合わせない。

症状だけが消えて、error / log抑制、retryの増加、fallbackの誤結果、cacheのstale data、monitoring threshold変更でfailureを見えなくしていないか確認する。

## 7. 止め時と報告を決める

原因と修正の因果が証拠で説明でき、必要なvalidationを終えたら調査を止める。実験が仮説と矛盾したら、修正へ進まず仮説を更新する。

原因が確定しない場合は`未特定`と記し、確認済み事実、除外した候補、最も有効な次の確認を示す。未実施の検証をpassと書かない。

非自明な調査結果は必要な項目だけ簡潔に残す。

- 症状と再現条件
- 根拠、棄却した仮説、root cause（または未特定）
- 修正が原因へ作用する理由
- 実施した検証、未実施、残るrisk

## 他Skillとの関係

- 外部仕様やversion依存挙動は必要に応じて`technical-research`で確認する。
- 複数責務へ広がる変更では`change-planning`、複雑さの比較には`development-guidelines`を使う。
- 独立したtest設計や文書化が必要なら`testing`、`technical-writing`、`code-comments`を使う。

他Skillを全件読むことを前提にしない。
