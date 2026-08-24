# Incident Command

このreferenceは、ユーザーがIncident Commander、incident command、指揮、進行管理、IC補佐等を**明示的に依頼した場合だけ**使用する。
Incidentが重大、長時間、multi-teamという理由だけでは指揮モードへ切り替えない。

目的は、ICがresolverになることではなく、response全体をrecoveryへ進めることである。

## 3Cs

Incident commandでは次を維持する。

- **Coordinate** — priority、workstream、ownerを整理する
- **Communicate** — responders / stakeholdersへtimelyにstateを共有する
- **Control** — production changeや調査の重複・競合を抑える

## 役割

規模に応じて必要なroleだけ使う。

| 役割 | 主な責務 |
|---|---|
| Incident Commander | current state / priority / decisionを統括し、resolverにならない |
| Operations / Resolver Lead | technical mitigation / investigationをまとめる |
| Communications / Liaison | stakeholder / customer updateと問い合わせ窓口 |
| Deputy | timer、pending item、handoffを補助する |
| Scribe | key fact、decision、action、timestampを記録する |
| SME | assigned domainを調査し、finding / risk / needを返す |

小規模incidentではroleを兼務してよい。
AgentがICを支援しても、production change権限や組織上のauthorityを自動的に取得したとは扱わない。

## 指揮拠点と現在状態

Primary incident channel / bridge等、coordinationの正本を一つ決める。Chatやcallの全履歴ではなく、[status-board.md](status-board.md)のようなcompactなcurrent stateを維持する。

少なくとも次を追えるようにする。

- 影響 / severity
- 実施中の影響緩和
- 重要な確認済み事実 / 未確認事項
- workstream / 担当
- 保留中の判断 / timer
- 次回更新

Security incidentではsingle source of truthと全情報公開を同一視しない。Forensic evidence、credential、indicator、具体的containment plan等はneed-to-knowのrestricted workstream / boardへ分離し、general channelにはsanitized stateだけを載せる。

## 判断サイクル

1. **状況把握（Size-up）** — 影響、scope、重要な未確認事項を把握する
2. **安定化（Stabilize）** — containment / mitigation候補とriskを比較する
3. **割当（Assign）** — specific ownerへtaskを割り当てる
4. **更新（Update）** — current stateを共有する
5. **確認（Verify）** — action結果を確認する
6. 必要なら状況把握へ戻る

Root cause確定を待たずcycleを回す。

## タスクの割当

「誰か確認して」ではなく、次を明確にする。

- 担当
- 具体的な質問 / 対応
- 期待結果
- 次回確認 / time-box
- 受領確認

例:

```text
Network owner: 10分以内にaffected requestのegress pathを確認し、
healthy pathとの差分を返してください。
```

Time-boxは強制deadlineではなく、incidentを停滞させないcheck-in pointとして使う。

## 判断

Expert inputを集めるが、全員一致を待って停止しない。重要decisionでは必要に応じて次を確認する。

- 期待効果
- operational / data / security risk
- 可逆性
- fallback
- 成功 / 失敗の観測方法

重大な見落としを拾うため、必要ならstrong objectionを求める。新しいevidenceが出ればplanを更新する。

## コミュニケーション

Timelinessとclarityを両立する。Confirmed impactや利用者が取るべきactionが分かったら、root causeやscopeの完全確定を待たずinitial updateを出す。未確定事項は`不明` / `調査中`と明示する。

定期更新は必要な範囲で次を含める。

- 影響 / severity
- 変化したこと
- 現在の影響緩和
- 重要な未確認事項
- 未完了の対応 / 担当
- 次回更新

Security / privacy上sensitiveな内容はgeneral / external updateへそのまま載せない。

## 管理範囲（span of control）

ICがindividual responderや並行taskを追えなくなったらworkstream / sub-teamへ分ける。

分割時は次だけ決める。

- leader
- objective
- next check-in
- ICへのprimary contact

Team内の詳細はleaderが集約する。

## 外部組織との連携

Vendorや他社が関係しても「回答待ち」で停止しない。

- escalation ownerを決める
- investigation packageを送る
- workaround / containmentを並行検討する
- vendor statementは報告情報として扱う
- 自serviceのimpact / recoveryを独立に観測する

自社ICがvendorや他組織へのcommand authorityを持つとは扱わない。複数組織に権限が分かれる場合は、各組織のauthority boundaryを保ったままdecision pointとliaisonを明確にする。

## 指揮の引継ぎ

Fatigue、長時間化、timezone change、complexity変化等ではhandoffする。

最低限渡す。

- 現在の影響 / severity
- 実施中の影響緩和
- 重要な確認済み事実 / 未確認事項
- 稼働中のworkstream / 担当
- 保留中の判断 / timer
- external escalation
- 次回communication時刻

Outgoing / incoming双方がtransferを明示し、incident channelでも新しいcommand ownerを共有する。Seniorityだけで自動的にcommandを移さない。

## 指揮対応の終了

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
