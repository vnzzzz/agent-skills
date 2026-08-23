# Incident Status Board

`incident-response` でcurrent stateを一覧化するときの表示形式を定義する。
目的は、incidentに参加した人が長いtimelineやchatを読み返さなくても「今どうなっていて、次に何をするか」を判断できる状態を作ることである。

## 原則

- 一画面でcurrent stateを把握できる程度に絞る。
- Raw logや会話履歴をdashboardへ転載しない。
- Unknownを空欄や推測で埋めない。`Unknown` / `未確認` と明示する。
- Fact、reported fact、hypothesis、decisionを混同しない。
- Timestampはtimezoneを含める。
- 各status boardの表示・更新には `Last updated` または `As of` を必ず含め、その時点のfreshnessを明示する。
- Local severity定義がなければSEV番号を作らない。
- Status boardはcurrent stateの正本として扱い、同じ情報を複数の表へ重複させない。
- Suspected / confirmed security compromiseでは、sensitive evidenceやcontainment detailをgeneral boardへ載せず、need-to-knowのrestricted board / workstreamへ分離する。

## Security incidentのaccess boundary

Security incidentでは「single source of truth」と「全員が全情報を読めること」を同一視しない。
Organization-localのsecurity incident process、access control、legal / privacy ruleを優先する。

Restricted boardへ置く例:

- forensic evidence / indicator
- credential / secret関連情報
- attackerに知られるとcontainmentを妨げるdetail
- exploit / persistence information
- sensitive customer / personal data
- detailed containment plan

General command post / boardには、必要に応じて次のsanitized stateだけを載せる。

- current user / business impact
- incident state
- high-level containment status
- owner / liaison
- responderが取るべきaction
- next update

Restricted informationの存在自体を隠す必要はないが、必要以上にdetailを複製しない。

## Default view

Non-trivial incidentでは、まず次の形を使う。

```markdown
## Incident Status

| Item | Current state |
|---|---|
| Last updated | 2026-08-23 23:35 JST |
| Impact | ... |
| Severity | ... / 未判定 |
| Started | ... |
| State | Investigating / Mitigating / Recovering / Monitoring / Resolved |
| Current mitigation | ... |
| Critical unknown | ... |
| Leading hypothesis | ... |
| External dependency | ... |
| Next action | ... |
| Next update | ... |
```

`Last updated` / `As of` は省略しない。その他の項目は不要なら削ってよい。固定templateを埋めること自体を目的にしない。
Security incidentのgeneral boardでは、sensitiveな `Critical unknown` や `Leading hypothesis` のdetailをsanitizedな表現へ置き換えるか、restricted boardへの参照だけを示す。

## Evidence view

Factsとhypothesesの混同が起きやすい場合は追加する。

```markdown
### Evidence

| Type | Finding | Source / evidence | State |
|---|---|---|---|
| Confirmed fact | ... | metric / log / trace | Confirmed |
| Reported fact | ... | operator / vendor | Reported |
| Hypothesis | ... | supporting evidence | Active |
| Critical unknown | ... | needed evidence | Open |
| Unknown | ... | needed evidence | Open |
```

Evidenceがないhypothesisをconfirmed factのように表示しない。
Sensitive evidenceをgeneral boardへ複製しない。

## Workstream view

複数team / vendor / sub-teamが並行している場合は追加する。

```markdown
### Active Workstreams

| Workstream | Owner | Objective | State | Next check-in |
|---|---|---|---|---|
| Application | ... | ... | Investigating | ... |
| Network | ... | ... | Waiting | ... |
| Vendor | ... | ... | Escalated | ... |
```

Ownerなしのactionを残さない。
`Waiting` の場合も、何待ちかと次のcheck-inを明確にする。

## Action / decision view

Mitigationや重要decisionを追う必要がある場合に使う。

```markdown
### Actions / Decisions

| Time | Action / decision | Owner | Expected result | Result |
|---|---|---|---|---|
| ... | ... | ... | ... | Pending / Success / Failed / Partial |
```

Timeline全量ではなく、incidentの進行や因果判断に必要なactionだけを載せる。
Security incidentでは、攻撃者に察知されると不利なcontainment actionをgeneral boardへ事前掲載しない。

## Missing information

User / operatorから情報提示が必要な場合は、status board内で明示する。

```markdown
### Needed Information

| Information | Why needed | Best source | Priority |
|---|---|---|---|
| ... | ... | operator / monitoring / vendor | Critical / High / Normal |
```

質問を散発的に投げるより、必要情報と理由をまとめて提示する。
Criticalなものから先に確認する。

## External dependency

Vendor / SaaS / 他teamが関係する場合は、待ち状態を見えなくしない。

```markdown
### External Dependencies

| Dependency | Observed impact | External status | Escalation | Next update |
|---|---|---|---|---|
| ... | ... | Reported / Unknown | case #... / owner | ... |
```

Vendor statusは `Reported` として扱い、自serviceのobserved impactと分ける。

## Update rule

Status boardは次のeventで更新する。

- impact / severity変化
- new confirmed fact
- critical unknown解消
- hypothesisの優先順位変化
- mitigation開始 / 結果判明
- workstream owner / state変化
- vendor / external update
- recovery state変化
- command transfer

細かなlog entryごとには更新しない。

Major incidentでは新情報がなくてもregular cadenceでcurrent stateを再提示する。
その場合は `No material change` と明示し、`Last updated` / `As of` を現在の更新時刻へ進める。古いtimestampのboardをcurrent stateとして再利用しない。

## Recovery表示

`Resolved` へ直接飛ばさず、必要に応じて次を区別する。

- **Investigating** — scope / causeを調査中
- **Mitigating** — impact reduction actionを実行中
- **Recovering** — service indicatorsが改善中
- **Monitoring** — symptom解消後、再発 / backlog / secondary impactを確認中
- **Resolved** — active responseを終了できる

Temporary workaroundだけで正常化している場合は `Mitigated` / `Degraded` 等、local terminologyに合わせて残存状態を明示する。

## Compactness

Dashboardは読みやすさのために情報を削るのではなく、detailを別のartifactへ分離する。

Status boardに残すのは:

- 今のimpact
- 今のfacts / critical unknown
- 今のaction
- owner
- next decision / update

詳細なinvestigation log、full timeline、postmortem notesは別に扱う。

## 参考資料

- PagerDuty, *During an Incident*: https://response.pagerduty.com/during/during_an_incident/
- PagerDuty, *Different Roles*: https://response.pagerduty.com/before/different_roles/
- PagerDuty, *Incident Commander Training*: https://response.pagerduty.com/training/incident_commander/
