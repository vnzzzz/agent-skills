---
name: technical-research
description: 外部の技術仕様、API・SDK・CLIのversion差、互換性・support範囲、releaseやCVE修正状況を一次資料で調べ、実装判断の根拠を整理するときに使用する。Repository内のコード参照だけで答えられる質問や、bugの再現・修正作業そのものには使用しない。
---

# Technical Research

外部技術の仕様とsupport範囲を、実装・運用の意思決定に使える根拠へ変える。資料数や調査時間ではなく、問いに答えられるかを基準にする。

## 1. 問いと対象を固定する

- 最初に「何を判断する調査か」を一文で定める。例: 「このSDK versionでAPI field Xを利用できるか」。
- 対象のproduct・component・interface（REST / SDK / CLI / console）、version、release channel、edition、region、調査時点を、結論に影響する範囲で特定する。
- 互換性は片方のcomponentだけでなく、**組合せ**を確認する。
- `latest` / `current` / `supported`を仮定せず、実際のrelease情報とsupport policyを確認する。
- Rolling docsを過去versionへ適用しない。追加・変更・deprecated・removedを論じる場合はversioned docs、release notes、migration guideを照合する。
- Release date、tag date、document update、effective versionを混同しない。
- Repository内の実装を読むだけで答えられる場合は、不要な外部調査を行わない。

## 2. 問いに合う一次資料を選ぶ

根拠の種類と強さを区別する。

| 問い | 主な一次資料 | 注意点 |
|---|---|---|
| 規範要件・公開API契約 | Standards bodyのspec、公式API reference、versioned docs | Tutorialやexampleを必須要件・support保証とみなさない |
| Vendorのsupport・互換性 | 公式support policy、compatibility matrix | 動いたという報告とsupport contractを分ける |
| 導入・廃止・修正version | Release notes、changelog、migration guide、advisory | Product・SDK・CLIそれぞれのversionを区別する |
| 現在の実装挙動・bug | Upstream source、tests、issue / PR、maintainer discussion | 実装上の挙動を公開保証へ昇格しない |

- 重要な主張は、それに直接答える一次資料へ結び付ける。Blog、Q&A、forum、検索snippetは発見の手掛かりとして使えるが、一次資料で確認可能な仕様の最終根拠にしない。
- 一次資料を順位通りに機械的に選ばない。Protocolの規範要件はspec、特定versionの実装bugはupstream sourceやissueが適切な場合がある。
- 別interfaceの仕様から未確認のfield、option、default、limit、support範囲を補完しない。

## 3. 重要な事実を照合する

- 判断を左右する主張は、必要なら補完関係にある資料を照合する。例: API reference＋release notes、support policy＋versioned docs、docs＋source/tests。
- 一次資料同士が食い違う場合は、対象version・component・時点、normative ruleとexample、support contractとobserved behaviorの差を確認する。
- 矛盾が残るときは解消したふりをせず、**何を決められないか**を明示する。
- 同じ結論を繰り返す資料を集めるだけなら検索を止める。

## 4. 安全に観測を補う

- 文書だけで不明であり、許可範囲内で安全に確認できる場合に限り、CLI `--version` / `--help`、package metadata、最小再現、isolated sample、API response、tests等を調べる。
- 観測結果にはversionとenvironmentを添え、その条件での挙動として記録する。単発の成功を全versionの仕様やvendorのsupport保証としない。
- Production dataの変更、破壊的操作、security boundaryを越える検証は、調査だけを理由に無断実施しない。

## 5. 判断できる形で回答する

必要な項目だけを短く示す。

1. **結論** — 元の問いへの回答。結論が出ない場合はその理由。
2. **対象** — version、interface、edition / region、時点など判断に効く条件。
3. **根拠** — 確認済み事実と、それを支える一次資料。出典と主張の対応を明示。
4. **解釈** — 事実からの推論と、projectの制約を踏まえた提案を分ける。
5. **残る不確実性** — 未確認、矛盾、実測不足、追加検証が必要な事項。

- 「Vendor推奨」と記すのは公式にそう明示されている場合だけにする。
- 根拠のないAPI名・option・limit・数値・修正versionを推測で埋めない。
- Specやsupport policyの要約で終えず、採用可否・制約・代替策・migration時期等、**この判断に何が変わるか**を伝える。

## 調査の終了条件

問いへの回答に必要な一次根拠・version条件が揃い、判断を変えうる不確実性を明示できたら終了する。重要な事実が未確認なら、その限界と次の確認方法を示して止める。

## 責務境界

- `debugging`: code pathの原因仮説、再現、修正と回帰検証。
- `incident-response`: active service incidentの影響、復旧、cross-boundary切り分け。
- `technical-writing`: 確認済み技術情報を仕様書・手順書として執筆する。
- このSkillは外部事実の確認と意思決定への意味を扱う。実装、project管理、学術的systematic reviewには拡張しない。
