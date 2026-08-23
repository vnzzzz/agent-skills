# Incident Command

このreferenceは、ユーザーがIncident Commander、incident command、指揮、進行管理、IC補佐等を**明示的に依頼した場合だけ**使用する。
Incidentが重大、長時間、multi-teamという理由だけではCommand modeへ切り替えない。

目的は、ICがresolverになることではなく、response全体をrecoveryへ進めることである。

## 3Cs

Incident commandでは次を維持する。

- **Coordinate** — priority、workstream、ownerを整理する
- **Communicate** — responders / stakeholdersへtimelyにstateを共有する
- **Control** — production changeや調査の重複・競合を抑える

## Role structure

規模に応じて必要なroleだけ使う。

| Role | 主な責務 |
|---|---|
| Incident Commander | current state / priority / decisionを統括し、resolverにならない |
| Operations / Resolver Lead | technical mitigation / investigationをまとめる |
| Communications / Liaison | stakeholder / customer updateと問い合わせ窓口 |
| Deputy | timer、pending item、handoffを補助する |
| Scribe | key fact、decision、action、timestampを記録する |
| SME | assigned domainを調査し、finding / risk / needを返す |

小規模incidentではroleを兼務してよい。
AgentがICを支援しても、production change権限や組織上のauthorityを自動的に取得したとは扱わない。

## Command postとlive state

Primary incident channel / bridge等、coordinationの正本を一つ決める。Chatやcallの全履歴ではなく、[status-board.md](status-board.md) のようなcompactなcurrent stateを維持する。

少なくとも次を追えるようにする。

- impact / severity
- active mitigation
- critical facts / unknowns
- workstreams / owners
- pending decisions / timers
- next update

Security incidentではsingle source of truthと全情報公開を同一視しない。Forensic evidence、credential、indicator、具体的containment plan等はneed-to-knowのrestricted workstream / boardへ分離し、general channelにはsanitized stateだけを載せる。

## Decision cycle

1. **Size-up** — impact、scope、critical unknownを把握する
2. **Stabilize** — containment / mitigation候補とriskを比較する
3. **Assign** — specific ownerへtaskを割り当てる
4. **Update** — current stateを共有する
5. **Verify** — action結果を確認する
6. 必要ならSize-upへ戻る

Root cause確定を待たずcycleを回す。

## Task assignment

「誰か確認して」ではなく、次を明確にする。

- owner
- specific question / action
- expected result
- next check-in / time-box
- acknowledgement

例:

```text
Network owner: 10分以内にaffected requestのegress pathを確認し、
healthy pathとの差分を返してください。
```

Time-boxは強制deadlineではなく、incidentを停滞させないcheck-in pointとして使う。

## Decision making

Expert inputを集めるが、全員一致を待って停止しない。重要decisionでは必要に応じて次を確認する。

- expected effect
- operational / data / security risk
- reversibility
- fallback
- success / failureの観測方法

重大な見落としを拾うため、必要ならstrong objectionを求める。新しいevidenceが出ればplanを更新する。

## Communication

Timelinessとclarityを両立する。Confirmed impactや利用者が取るべきactionが分かったら、root causeやscopeの完全確定を待たずinitial updateを出す。未確定事項は`Unknown` / `Investigating`と明示する。

Regular updateは必要な範囲で次を含める。

- impact / severity
- what changed
- current mitigation
- critical unknown
- outstanding action / owner
- next update

Security / privacy上sensitiveな内容はgeneral / external updateへそのまま載せない。

## Span of control

ICがindividual responderや並行taskを追えなくなったらworkstream / sub-teamへ分ける。

分割時は次だけ決める。

- leader
- objective
- next check-in
- ICへのprimary contact

Team内の詳細はleaderが集約する。

## External / cross-company incident

Vendorや他社が関係しても「回答待ち」で停止しない。

- escalation ownerを決める
- investigation packageを送る
- workaround / containmentを並行検討する
- vendor statementはreported factとして扱う
- 自serviceのimpact / recoveryを独立に観測する

自社ICがvendorや他組織へのcommand authorityを持つとは扱わない。複数組織に権限が分かれる場合は、各組織のauthority boundaryを保ったままdecision pointとliaisonを明確にする。

## Transfer of command

Fatigue、長時間化、timezone change、complexity変化等ではhandoffする。

最低限渡す。

- current impact / severity
- active mitigation
- critical facts / unknowns
- active workstreams / owners
- pending decisions / timers
- external escalations
- next communication timing

Outgoing / incoming双方がtransferを明示し、incident channelでも新しいcommand ownerを共有する。Seniorityだけで自動的にcommandを移さない。

## End of active command

次を確認してからactive commandを終了する。

- user-facing symptomと主要service signalがrecoverした
- immediate security / data / safety concernがcontrolled
- remaining workがtime-criticalではない
- temporary mitigation / degraded modeが明示されている
- follow-up ownerが決まっている

Postmortemとlong-term corrective actionはactive commandから分離する。

## アンチパターン

- ICがlog調査やproduction操作へ没頭する
- owner不明のtaskを投げる
- root cause確定までmitigationや初報を待つ
- seniorityだけでcommandを奪う
- vendor回答待ちでresponse全体を止める
- sensitive security stateをgeneral channelへ公開する
- fatigueしてもhandoffしない

## 参考資料

- Google SRE, *Managing Incidents*: https://sre.google/sre-book/managing-incidents/
- Google SRE Workbook, *Incident Response*: https://sre.google/workbook/incident-response/
- PagerDuty, *Incident Commander Training*: https://response.pagerduty.com/training/incident_commander/
- PagerDuty, *Different Roles*: https://response.pagerduty.com/before/different_roles/
- PagerDuty, *During an Incident*: https://response.pagerduty.com/during/during_an_incident/
- PagerDuty, *Complex Incidents*: https://response.pagerduty.com/before/complex_incidents/
