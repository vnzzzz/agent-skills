# Incident Status Board

Incidentの現在状態を、装飾ではなく**構造化・情報の取捨選択・時系列**で把握するための表示形式を定義する。
Markdownの見出し、表、箇条書きを使い、Mermaidは使用しない。

## 原則

- 一画面で現在状態と次の判断が分かる程度に絞る。
- Raw logや会話履歴を転載しない。
- 確認済み事実、報告情報、仮説、不明事項、判断を混同しない。
- タイムラインは原因判断や対応判断に効くeventだけを残す。
- 仮説は有力候補を優先し、弱い候補を増やし続けない。
- Timestampはtimezoneを含める。
- Active incidentのboardには`最終更新`を含める。
- Local severity定義がなければSEV番号を作らない。

固定templateを全項目埋めることを目的にしない。不要なsectionは省略する。

## 基本表示

```markdown
## 障害ステータス

| 項目 | 現在の状態 |
|---|---|
| 最終更新 | 2026-08-24 07:30 JST |
| 影響 | ... |
| 状態 | 調査中 / 影響緩和中 / 復旧中 / 監視中 / 収束 |
| 最有力原因 | ... / 不明 |
| 重要な未確認事項 | ... / 現時点なし |
| 次の確認 | ... |
```

原因推定が主目的なら`影響`より`最有力原因`、`重要な未確認事項`、`次の確認`を重視する。
指揮モードでなければroleやowner欄を無理に追加しない。

## タイムライン

事象の因果関係を判断するために使う。

```markdown
### タイムライン

| 時刻 | 事象 | 種別 | 意味 |
|---|---|---|---|
| 07:10 JST | ... | 確認済み | first known bad |
| 07:14 JST | ... | 報告情報 | vendor eventと時間的に近い |
```

- 時刻不明を推測で補わない。
- 単なるlog entryは載せない。
- 同時刻であることをcauseと断定しない。

## 原因仮説

```markdown
### 原因仮説

| 順位 | 仮説 | 根拠 | 反証・未確認事項 | 確度 |
|---:|---|---|---|---|
| 1 | ... | ... | ... | 高 |
| 2 | ... | ... | ... | 中 |
```

確度はevidenceの強さを表す。根拠のない数値確率は使わない。

## 不足情報

追加情報が原因判断を大きく変える場合だけ載せる。

```markdown
### 不足情報

| 情報 | 必要な理由 | 最適な確認先 |
|---|---|---|
| ... | 仮説1 / 仮説2を切り分けるため | monitoring / operator / vendor |
```

質問だけでboardを埋めず、現時点の見立ても併記する。

## 現在の対応

Mitigationや調査actionを追う必要がある場合に使う。

```markdown
### 現在の対応

- Vendor側へ対象traceのrequest到達有無を確認する。
- 障害regionと正常regionを比較する。
- 復旧を遅らせない範囲でrestart前にprocess stateを保全する。
```

指揮モードでowner / check-in管理が必要なら表へ拡張する。

```markdown
| 対応 | 担当 | 状態 | 次回確認 |
|---|---|---|---|
| ... | ... | 調査中 | ... |
```

## セキュリティインシデント時の扱い

Suspected / confirmed compromiseでは、general boardへforensic evidence、credential、indicator、exploit detail、具体的containment plan等を載せない。
Need-to-knowのrestricted board / workstreamへ分離し、general boardにはsanitizedなimpact、state、high-level containment status、liaison、next updateだけを載せる。

## 更新条件

次のようなmaterial changeで更新する。

- impact / state変化
- new confirmed fact
- 重要な未確認事項の解消
- leading hypothesis変化
- mitigation開始 / 結果
- external status変化
- recovery state変化

Major incidentでは新情報がなくても必要なcadenceで再提示し、`重要な変更なし`と最終更新時刻を更新する。
調査だけを依頼されている場合、定期update cadenceを勝手に開始しない。

## 復旧状態の表示

必要に応じて次を区別する。

- **調査中** — scope / causeを調査中
- **影響緩和中** — impact reduction中
- **復旧中** — service signalが改善中
- **監視中** — symptom解消後の再発 / backlog確認中
- **収束** — active response終了可能

Temporary workaroundやdegraded modeが残る場合は、`影響緩和済み`、`縮退中`、`機能制限中`など実態が分かる日本語で明示する。

## 参考資料

- Google SRE, *Managing Incidents*: https://sre.google/sre-book/managing-incidents/
- PagerDuty, *During an Incident*: https://response.pagerduty.com/during/during_an_incident/
- PagerDuty, *Incident Commander Training*: https://response.pagerduty.com/training/incident_commander/
