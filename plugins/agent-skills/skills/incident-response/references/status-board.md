# Incident Status Board

Incidentのcurrent stateを、装飾ではなく**構造化・情報の取捨選択・時系列**で把握するための表示形式を定義する。
Markdownの見出し、表、箇条書きを使い、Mermaidは使用しない。

## 原則

- 一画面でcurrent stateと次の判断が分かる程度に絞る。
- Raw logや会話履歴を転載しない。
- Fact、reported fact、hypothesis、unknown、decisionを混同しない。
- Timelineは原因判断や対応判断に効くeventだけを残す。
- Hypothesisは有力候補を優先し、弱い候補を増やし続けない。
- Timestampはtimezoneを含める。
- Active incidentのboardには`Last updated`または`As of`を含める。
- Local severity定義がなければSEV番号を作らない。

固定templateを全項目埋めることを目的にしない。不要なsectionは省略する。

## 基本表示

```markdown
## Incident Status

| Item | Current state |
|---|---|
| Last updated | 2026-08-24 07:30 JST |
| Impact | ... |
| State | Investigating / Mitigating / Recovering / Monitoring / Resolved |
| Most likely cause | ... / Unknown |
| Critical unknown | ... / None known |
| Next check | ... |
```

原因推定が主目的なら`Impact`より`Most likely cause`、`Critical unknown`、`Next check`を重視する。
Command modeでなければroleやowner欄を無理に追加しない。

## Timeline

事象の因果関係を判断するために使う。

```markdown
### Timeline

| Time | Event | Type | Significance |
|---|---|---|---|
| 07:10 JST | ... | Confirmed | first known bad |
| 07:14 JST | ... | Reported | vendor eventと時間的に近い |
```

- 時刻不明を推測で補わない。
- 単なるlog entryは載せない。
- 同時刻であることをcauseと断定しない。

## Cause hypotheses

```markdown
### Cause hypotheses

| Rank | Hypothesis | Supporting | Contradicting / unknown | Confidence |
|---:|---|---|---|---|
| 1 | ... | ... | ... | High |
| 2 | ... | ... | ... | Medium |
```

Confidenceはevidenceの強さを表す。根拠のない数値確率は使わない。

## Needed information

追加情報が原因判断を大きく変える場合だけ載せる。

```markdown
### Needed information

| Information | Why needed | Best source |
|---|---|---|
| ... | H1 / H2を切り分けるため | monitoring / operator / vendor |
```

質問だけでboardを埋めず、現時点の見立ても併記する。

## Current actions

Mitigationや調査actionを追う必要がある場合に使う。

```markdown
### Current actions

- Confirm vendor-side request arrival for trace `...`.
- Compare affected and healthy region.
- Preserve process state before restart if recoveryを遅らせない。
```

Command modeでowner / check-in管理が必要なら表へ拡張する。

```markdown
| Action | Owner | State | Next check-in |
|---|---|---|---|
| ... | ... | Investigating | ... |
```

## Security incident

Suspected / confirmed compromiseでは、general boardへforensic evidence、credential、indicator、exploit detail、具体的containment plan等を載せない。
Need-to-knowのrestricted board / workstreamへ分離し、general boardにはsanitizedなimpact、state、high-level containment status、liaison、next updateだけを載せる。

## Update rule

次のようなmaterial changeで更新する。

- impact / state変化
- new confirmed fact
- critical unknown解消
- leading hypothesis変化
- mitigation開始 / 結果
- external status変化
- recovery state変化

Major incidentでは新情報がなくても必要なcadenceで再提示し、`No material change`とfreshness timestampを更新する。
Investigationだけを依頼されている場合、定期update cadenceを勝手に開始しない。

## Recovery表示

必要に応じて次を区別する。

- **Investigating** — scope / causeを調査中
- **Mitigating** — impact reduction中
- **Recovering** — service signalが改善中
- **Monitoring** — symptom解消後の再発 / backlog確認中
- **Resolved** — active response終了可能

Temporary workaroundの場合は`Mitigated` / `Degraded`等、残存状態を明示する。

## 参考資料

- Google SRE, *Managing Incidents*: https://sre.google/sre-book/managing-incidents/
- PagerDuty, *During an Incident*: https://response.pagerduty.com/during/during_an_incident/
- PagerDuty, *Incident Commander Training*: https://response.pagerduty.com/training/incident_commander/
