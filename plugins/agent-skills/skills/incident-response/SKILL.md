---
name: incident-response
description: 本番障害、service degradation、SaaS / cloud / external API障害、network / platform障害、他team・他社をまたぐincidentを、impact把握、mitigation、情報整理、切り分け、coordination、recovery確認まで一貫して進めるときに使用する。原因が明らかなisolated local bugやtest failureだけを扱う場合はdebuggingを優先する。
---

# Incident Response

Active incidentでは、root causeの完全解明より先に利用者影響と被害拡大を抑え、system全体を安全にrecoveryへ進める。
原因が自teamのcodebaseにあることを前提にしない。SaaS、cloud、network、shared platform、他team、vendor等の責任境界をまたぐfailureも同じincidentとして扱う。

## 原則

1. **Service recoveryを最優先する。**
   Root cause investigationとmitigationを並行できる場合でも、継続中の重大impactを放置して原因解明だけを優先しない。
2. **不足情報を推測で埋めない。**
   Operator、system owner、monitoring、vendor等から得られる情報は、取得可能なら提示・確認を求める。
3. **情報の種類を分ける。**
   Confirmed fact、reported fact、hypothesis、unknown、decision / actionを混同しない。
4. **重大なunknownを先に潰す。**
   Security compromise、data loss / corruption、safety impact、irreversible side effect、広範囲outage等、成立した場合に対応優先度が変わる可能性は `critical unknown` として早期に確認する。可能性を事実として扱わない。
5. **原因候補と責任主体を混同しない。**
   他teamやvendorが原因候補でも、責任の押し付けよりservice recoveryに必要な情報・owner・next actionを明確にする。
6. **Incident commandとtechnical investigationを分離する。**
   Major / multi-team incidentでは、全体をcoordinationする役割が個別調査へ没頭しない。
7. **Recoveryはend-to-endで確認する。**
   一componentのmetric回復だけでなく、user-facing symptom、service-level signal、queue / backlog、data integrity等から実際の復旧を確認する。

## 1. Size-upする

最初に、分かる範囲で次を整理する。

- user / business impact
- affected / unaffected users、regions、tenants、functions
- start time、first known bad、last known good
- ongoing / intermittent / recovering / resolved
- exact symptom、error、latency、availability、data issue
- recent deployment / configuration / dependency / traffic change
- security、data integrity、safety等のcritical unknown
- repository-localのseverity基準がある場合はseverity

Severity定義がない場合、独自のSEV番号を作らない。Impactを事実として示し、severityは未判定とする。

## 2. 不足情報を明示して取得する

判断に必要な情報が不足している場合、埋め合わせて進めない。
可能ならoperator / userへ次の形式で提示を求める。

| 不足情報 | 何の判断に必要か | 想定source | 優先度 |
|---|---|---|---|
| 例: 正確な発生時刻 | deployment / vendor eventとの時系列比較 | monitoring / operator | High |

特に、利用者やsystem ownerが最も正確に把握している環境固有情報は、推測せず確認を求める。

情報不足でもincident response全体を停止しない。確認待ちの事項は `unknown` のまま保持し、観測済み事実だけから安全なmitigationや追加確認を進める。

## 3. Incident stateを共有する

Non-trivial incidentでは、現在のstateを一箇所に集約する。
少なくとも次を追えるようにする。

- impact / severity
- current state
- confirmed / reported facts
- hypotheses
- critical unknowns / other unknowns
- mitigation / recovery actions
- owners / workstreams
- external dependencies / escalations
- next decision / next update

一覧表示が有用な場合は [references/status-board.md](references/status-board.md) を読む。

## 4. Command structureを必要十分に作る

複数team、複数workstream、重大impact、長時間化等でcoordination costが高い場合は、Incident Commander相当の役割を明示する。
Incident Commanderのbest practiceは [references/incident-command.md](references/incident-command.md) を読む。

小規模incidentへ不要なrole ceremonyを持ち込まない。一人で十分なincidentでは役割を統合してよい。

Agentがcoordinationを支援する場合も、組織上のauthorityやproduction change権限を勝手に持つとみなさない。実環境変更はuser instruction、repository-local rule、既存authority boundaryに従う。

## 5. Mitigation / containmentを検討する

原因確定前でも、impactを安全に抑えられる場合はmitigationを検討する。

例:

- rollback / failover
- traffic shift / isolation
- feature disable
- rate limiting / load shedding
- dependency bypass
- queue intake停止
- capacity adjustment

候補ごとに、期待効果、risk、reversibility、必要authority、観測すべき成功条件を確認する。

複数の大きな変更を同時に行い、何が効いたか分からない状態を避ける。ただし、重大impactが継続し逐次実験の余裕がない場合は、recovery優先で必要なmitigationを組み合わせ、その事実を記録する。

## 6. 責任境界をまたいで調査する

原因調査を自teamのcodeへ限定しない。

- application / service
- database / cache / queue
- network / DNS / proxy / load balancer
- cloud / managed service
- SaaS / external API
- shared platform
- identity / certificate / secret
- downstream / upstream system
- 他team / vendor管理component

複数boundaryをまたぐ、external dependencyが疑わしい、またはownerが分散している場合は [references/investigation.md](references/investigation.md) を読む。

Local implementationのbug、resource lifecycle、concurrency、regression等のroot causeを掘る必要がある場合は `debugging` を利用する。`debugging` はincident investigationの一手段であり、incident全体のorchestrationはこのSkillを正本とする。

外部serviceのcurrent status、仕様、support範囲等を確認する場合は `technical-research` を利用する。

## 7. 仮説を更新する

Hypothesisは不足情報の代替ではない。
各hypothesisについて必要に応じて次を持つ。

- supporting facts
- contradicting facts
- まだ必要なevidence
- 最小で安全な確認方法
- owner

新しいconfirmed factが入るたびに、仮説の優先順位と次の確認を更新する。
過去の類似障害、直前のdeployment、vendor status等へanchoringしない。

## 8. External escalationを早めに準備する

Vendor / SaaS / 他teamへの調査依頼が必要なら、原因確定を待たず、相手が調査開始できる情報を揃える。

必要に応じて次を含める。

- exact timestamp + timezone
- affected region / tenant / account / endpoint
- request / trace / correlation ID
- exact error / status code
- affected / unaffected comparison
- impact and frequency
- recent relevant changes
- already attempted mitigation
- sanitized logs / metrics
- desired response: investigation、status、workaround、ETA等

Status pageに障害情報があるだけで、自incidentのcauseと断定しない。時間、scope、症状等が一致するかを確認する。

## 9. 定期的にstateを更新する

Updateは新情報があるときだけではなく、major incidentでは一定cadenceで行う。

短く次を更新する。

- current impact
- what changed since last update
- current mitigation / investigation
- critical unknown
- next action / owner
- next update timing

同じraw logを繰り返さず、判断に必要なstateを更新する。

## 10. Recoveryを検証する

Mitigationや修正後は、少なくとも必要に応じて次を確認する。

- original user-facing symptomが消えたか
- error rate / latency / availabilityが期待範囲へ戻ったか
- backlog / queue / replication lag等が解消方向か
- data integrityに追加問題がないか
- affected scopeが本当に縮小したか
- workaround依存のtemporary recoveryか、normal operationへ戻ったか
- observation window中に再発していないか

Vendorが `resolved` と発表したことだけで自serviceのrecovery確認を代替しない。

## 11. Active responseを終了する

Incidentを閉じる前に、少なくとも次を明示する。

- current impact: resolved / mitigated / remaining
- recovery evidence
- temporary mitigation / degraded modeの有無
- unresolved unknowns
- external case / follow-up owner
- cleanup / rollback-back / monitoring action
- post-incident reviewが必要か

Postmortem、再発防止策の優先順位付け、long-term problem managementはactive incident responseと分離する。

## Reference routing

- **Major / multi-team / complex incident:** [references/incident-command.md](references/incident-command.md)
- **SaaS / vendor / network / 他teamを含むcross-boundary investigation:** [references/investigation.md](references/investigation.md)
- **一覧でcurrent stateを維持・提示する:** [references/status-board.md](references/status-board.md)

必要なreferenceだけ読む。

## 他Skillとの関係

- `debugging`: local code / implementationのroot cause investigation
- `technical-research`: external specification、vendor status、support policy等の確認
- `command-execution`: commandやmutating operationの安全な実行
- `evidence-reporting`: incident対応後の実施内容・検証・未確認事項の報告
- `technical-writing`: runbook、incident procedure等のdurable documentation

## 参考資料

- PagerDuty, *During an Incident*: https://response.pagerduty.com/during/during_an_incident/
- PagerDuty, *Different Roles*: https://response.pagerduty.com/before/different_roles/
- PagerDuty, *Incident Commander Training*: https://response.pagerduty.com/training/incident_commander/
- PagerDuty, *Complex Incidents*: https://response.pagerduty.com/before/complex_incidents/
- Google SRE, *Managing Incidents*: https://sre.google/sre-book/managing-incidents/
- Google SRE Workbook, *Incident Response*: https://sre.google/workbook/incident-response/
- AWS Well-Architected, *Responding to events*: https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/responding-to-events.html
