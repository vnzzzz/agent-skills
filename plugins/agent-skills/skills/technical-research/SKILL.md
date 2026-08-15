---
name: technical-research
description: 技術仕様・挙動・制約・support範囲を調査するときに、対象versionと時点を固定し、一次資料を中心に確認済み事実・推論・提案・未確認事項を分離して実装判断に使える根拠を得るために使用する。
---

# Technical Research

技術調査の目的は、資料を多く集めることではなく、実装や運用上の意思決定に必要な問いへ十分な確度で答えることである。

library、framework、SDK、CLI、API、cloud service、protocol等の仕様は変化するため、内部知識や検索結果だけで補完せず、対象version・時点・support範囲を確認する。

## まず判断する問いを定義する

検索を始める前に、何を判断するための調査かを一文で表せるようにする。

例:

- 対象versionでこのAPIを利用できるか
- optionが導入・deprecated・removedされたversionはどこか
- component A/Bの組合せはsupport対象か
- error conditionは仕様上どのように扱われるか
- 候補A/Bのどちらが現在の制約を満たすか

広いtopicを漫然と調べない。
問いが複数ある場合は、意思決定へ影響する単位へ分解する。

既存codebaseだけで確認できる事項に、不要な外部調査を持ち込まない。

## 対象versionと時点を固定する

調査対象を曖昧な「現在仕様」のまま扱わない。

最低限、必要に応じて次を確認する。

- product / library / runtime / API version
- release channelやedition
- managed serviceのregionや提供形態
- 関係するcomponentのversion組合せ
- 調査時点
- support / maintenance window

version指定がない場合も、その回答がversion依存かを判断する。

`latest`、`current`、`supported`を扱う場合は、実際のrelease情報やsupport policyを確認する。
current documentationがrolling docsの場合、過去versionへそのまま適用しない。

導入・変更・deprecated・removedの時点が判断へ影響する場合は、version-specific documentation、release notes、migration guide等で確認する。

複数component間のcompatibilityは、各component単体ではなく組合せとして確認する。

## 一次資料を優先する

根拠は、問いに最も直接答える一次資料から探す。

一般的な優先候補:

1. 公式のnormative specification / API reference / product documentation
2. 公式のsupport policy / compatibility policy
3. 公式release notes / changelog / migration guide
4. standards bodyの仕様やregistry
5. upstream source code / tests
6. upstream issue / PR / maintainer discussion
7. vendor / maintainerによる公式engineering article
8. 信頼できるsecondary source

この順序は絶対ではない。
例えばprotocolの規範要件ならstandards bodyのspecificationが最も強く、実装bugの有無ならupstream issueやsourceが有用な場合がある。

blog、Q&A、forum、検索snippetは発見の手掛かりには使えるが、一次資料で確認可能な仕様の最終根拠にはしない。

## 根拠の種類を区別する

資料に書かれているという理由だけで、同じ強さの根拠として扱わない。

区別する例:

- normative specification: 準拠条件やprotocol上の要求
- API reference: 公開interfaceと契約
- support policy: vendor / projectがsupportすると明示する範囲
- release notes / changelog: version間の変更履歴
- migration guide: 移行時に必要な変更
- tutorial / quickstart: 代表的な利用方法
- example: 動作例でありsupport範囲そのものではない
- source / test: 現在の実装挙動の根拠
- issue / PR: bug、変更意図、未解決事項等の一次情報

source codeで動くことと、public contractとしてsupportされることを同一視しない。
exampleに登場する構成を、明示されたsupport contractとみなさない。

releaseとtag、publish dateとeffective version等、似ているが意味の異なる時点も区別する。

## 重要な事実は必要に応じて突き合わせる

実装判断へ大きく影響する事実は、単一ページだけで不十分なら補完関係にある一次資料を確認する。

例:

- API reference + release notes
- support policy + version-specific docs
- deprecation policy + migration guide
- docs + upstream source / tests
- specification + implementation notes

同じ事実を多数のsourceで反復確認すること自体を目的にしない。
追加sourceが新しい確度や観点を与えないなら止める。

## 一次資料同士の不一致を隠さない

資料が食い違う場合、都合のよい方を選ばない。

確認するもの:

- 対象versionが同じか
- rolling docsとversioned docsの違いがないか
- documentの更新日時
- normative ruleとtutorial/exampleの違い
- product本体とSDK / CLI等、対象componentが同じか
- support contractと実装上の挙動を混同していないか

解消できない場合は不一致を残し、どの判断が未確定かを明示する。

## SDK・CLI・REST API等を分ける

同じproduct名でもinterfaceごとに仕様が異なることがある。

- REST APIに存在するfieldがSDKで未対応の場合がある
- CLI optionはCLI versionに依存する
- console UIの制約とAPIの制約が異なる場合がある
- client libraryが独自のdefaultやvalidationを持つ場合がある

対象interfaceを固定し、別interfaceの仕様をそのまま流用しない。

## 安全に実環境で確認する

文書だけで判断しにくく、安全かつ現実的に確認できる場合は実測する。

例:

- CLIのversion / `--help`
- package metadata
- minimal reproduction
- API response
- repository内のtests
- small isolated sample

観測結果は「そのversion・environmentで確認した事実」として扱う。
一度動いたことを、support保証や全versionの仕様へ一般化しない。

production dataの変更、破壊的operation、security boundaryを越える検証等は、調査のためだけに無断で実行しない。

## 事実・推論・提案・未知を分離する

調査結果では、少なくとも次を混同しない。

### Confirmed fact

公式資料や直接観測で確認できた内容。
対象versionや条件も必要に応じて添える。

### Inference

複数の確認済み事実から導いた判断。
公式仕様そのものではないことが分かるようにする。

### Recommendation

制約、trade-off、project contextを踏まえた実装・運用上の提案。
「vendor推奨」と書くのは、vendorが実際にそう明示している場合だけにする。

### Unknown

確認できなかった点、資料が矛盾している点、追加検証が必要な点。

API名、option、limit、support範囲等が確認できない場合、もっともらしい値を補完しない。

## 実装への意味まで整理する

調査はsourceの要約で終わらせない。

確認した仕様が現在の判断へ何を意味するかを整理する。

例:

- このversionでは利用不可なので別手段が必要
- support対象だが特定version組合せに制約がある
- deprecatedだが即時削除ではないためmigration時期を分けられる
- 実装上は動くがsupport contract外なので採用しない
- 仕様では決まらず、project側のtrade-off判断が必要

実装変更へ進む場合は `change-planning` でscopeとvalidationを整理し、`development-guidelines` で必要十分なsolutionを選ぶ。

## 調査を止める条件

次を満たしたら、追加検索より結論整理を優先する。

- 判断対象の問いへ答えられる
- 主要な結論に一次資料の根拠がある
- version / 時点 / support範囲が十分に明確である
- 重要な不確実性が明示されている
- 追加sourceが意思決定を変える可能性が低い

「まだ資料があるかもしれない」だけを理由に調査を続けない。

## 調査結果の最小構成

必要に応じて次を簡潔に示す。

1. **Conclusion** — 問いへの回答
2. **Target** — version / 時点 / environment / 前提
3. **Verified facts** — 判断を支える確認済み事実
4. **Implications** — 実装・運用上の意味
5. **Uncertainties** — 未確認事項や残る不確実性
6. **Primary sources** — 主要な根拠と、それが何を支えるか

sourceの羅列ではなく、sourceと判断の対応が分かるようにする。

## 避けること

- 検索snippetだけで仕様を断定する
- 個人blogやQ&Aだけを現在仕様の根拠にする
- versionを確認せずcurrent docsを過去環境へ適用する
- staleな内部知識からoptionやlimitを補完する
- SDK / CLI / REST API / consoleの仕様を混同する
- source codeに存在するinternal behaviorをsupported contractとみなす
- tutorialやexampleをnormative requirementとして扱う
- release date、tag date、versionの意味を混同する
- source数や調査時間を品質指標にする
- recommendationを「公式best practice」と誤表示する
- 不確実性を埋めるために存在しない名前や値を作る

## 他Skillとの関係

- 調査が必要か、変更のどこへ影響するかは `change-planning` で整理する。
- problem / user outcome自体の妥当性は `product-thinking` の責務とする。
- 調査結果を文書へ残す場合は `technical-writing` を利用する。
- 調査結果を受けた実装は `development-guidelines` に従う。

このSkillは、project management、学術的systematic review、特定vendor固有の調査手順、障害の仮説検証processそのものを定義しない。
