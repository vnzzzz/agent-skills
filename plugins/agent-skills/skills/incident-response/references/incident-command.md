# Incident Command

`incident-response` でmajor / multi-team / complex incidentを扱うときのcommand practiceを定義する。
目的は、Incident Commanderが個別調査のresolverになることではなく、incidentを安全かつ継続的にrecoveryへ進めることにある。

## 3Csを守る

Google SREのIncident Command System系practiceでは、incident managementの中心を次の3点に置く。

- **Coordinate** — response effortを整理し、ownerと優先順位を明確にする
- **Communicate** — responders、stakeholders、外部へ必要な情報を流す
- **Control** — 誰が何をしているかを把握し、無秩序なproduction changeや調査を防ぐ

ICはtechnical resolverではなく、この3Csを維持する役割とする。

## Incident Commanderの責務

Incident Commanderは全体stateと優先順位を把握し、次を行う。

- impact / severity / critical unknownを把握する
- respondersから情報を集約する
- next actionを決める
- actionをspecific ownerへ委譲する
- mitigation / investigationの進捗を追う
- stakeholder communicationを維持する
- incidentが複雑化したらworkstreamを分割する
- recovery evidenceを確認してactive responseを終了する

ICは原則として次を自分で抱え込まない。

- logを深掘りする
- graphを個別に追う
- production操作を実行する
- code fixを実装する
- 一つのhypothesisだけを長時間調査する

Technical investigationとcommandを同じ人が兼任すると全体stateを失いやすい。小規模incidentでは役割を兼務してよいが、coordination costが上がった時点で分離する。

AgentがIC相当の支援を行う場合も、組織上のcommand authorityを自動的に持つわけではない。実環境変更の承認や実行権限はoperator / local ruleへ従う。

## Incident structureは早めに起動する

Customer-visible impact、複数team involvement、急速なscope拡大等で通常の個別troubleshootingを超え始めたら、完全なcause確定を待たずincident structureを起動する。

小さく済んだ場合は後で縮小すればよい。Impactが広がってからcommand structureを作るより、早めにcentral coordinationを持つことを優先する。

Repository / organizationにincident declaration基準がある場合はそれを正本とする。

## Command postとlive stateを一つにする

Respondersが「どこを見ればよいか」を迷わないよう、primary incident channel / bridge / war room等のrecognized command postを一つ決める。

Current stateは [status-board.md](status-board.md) の形式等で一箇所に維持する。
少なくとも次が上部から追える状態にする。

- current impact / severity
- command roles
- mitigation
- confirmed facts / critical unknowns
- active workstreams + owners
- pending decisions / timers
- next update

Chatやcallだけをstateの正本にしない。

Suspected / confirmed security compromiseでは、recognized command postが「全情報を全参加者へ公開する場所」を意味しない。
Sensitive forensic evidence、indicator、credential情報、具体的containment planはorganization-localのsecurity incident processに従い、need-to-knowのrestricted workstream / boardで管理する。General command postにはsanitizedなimpact、current state、owner、coordination情報を共有する。

## 初動: Size-up

最初に「何が起きているか」と「どこまで悪化し得るか」を短時間で把握する。

確認する。

- current user / business impact
- affected / unaffected scope
- escalation / spreading / static / recovering
- critical unknowns
- responders / system ownersの有無
- immediate containment options

情報が不足している場合、推測で埋めない。
利用者、system owner、monitoring、vendor等、最も正確なsourceから取得する。

ただし、全情報が揃うまで判断を停止しない。
現時点のfactsとunknownsを分け、重大impactを避けるためのreversible actionを選ぶ。

## Critical unknownを先に確認する

成立した場合に対応戦略が大きく変わるunknownを先に扱う。

例:

- data corruption / data lossが進行中か
- security compromiseの可能性があるか
- irreversible operationが走っているか
- impactが特定tenantだけか全体か
- failover先も同じfailure modeを持つか
- external dependencyが広域障害中か

Worst-caseを想定することと、worst-caseを事実認定することは異なる。
`critical unknown` として明示し、確認できるownerへ割り当てる。

## Role structure

必要に応じて次の役割を分ける。

### Incident Commander

- single coordination point
- current state / priority / decisionのowner
- next actionを決める
- resolverにならない

### Operations Lead / Resolver Lead

- technical mitigation / investigationをまとめる
- ICから委譲されたoperational workを進める
- system modificationが複数人で無秩序に並行しないよう整理する

### Communications Lead / Liaison

- responders / stakeholders / customers向けupdateを担当する
- responderへの割込みを減らす
- customer report等、新しいimpact evidenceをincidentへ戻す

### Deputy

- timer / pending task / missed itemを追う
- ICの認知負荷を下げる
- command transfer時のhot standby

### Scribe

- key fact、decision、action、timestampを記録する
- raw conversation全量ではなく、後からstateとtimelineを復元できる情報を残す
- live statusの更新を補助する

### Subject Matter Expert

- assigned domainを調査する
- finding、proposed action、risk、needをIC / Ops Leadへ返す
- authorityなしに独断で大きなproduction changeを広げない

PagerDutyのCAN形式を参考に、報告は必要に応じて次でまとめる。

- **Condition:** 現在どうなっているか
- **Actions:** 何をしている / 何を提案するか
- **Needs:** 何が必要か

すべてのroleを別人へ割り当てる必要はない。Incidentの規模に合わせて統合する。

## Decision cycle

基本cycleは次とする。

1. **Size-up** — impact、scope、facts、unknownsを把握する
2. **Stabilize** — mitigation候補とriskを比較しactionを選ぶ
3. **Assign** — specific ownerへtaskを割り当てる
4. **Update** — current stateを共有する
5. **Verify** — action結果を確認する
6. 必要ならSize-upへ戻る

Root causeが分からなくてもcycleは回せる。

## Task assignment

Taskは曖昧な「誰かやって」ではなく、必ずownerを特定する。

良いassignmentは次を含む。

- owner
- specific question / action
- expected evidence / result
- time-box / next check-in
- acknowledgement

例:

```text
Network owner: 22:40までにaffected requestのegress pathとpacket lossを確認し、
healthy pathとの差分を返してください。
```

Time-boxはdeadlineというより、incidentが停滞しないためのcheck-in pointとして使う。

## Decision making

ICはexpert inputを集めるが、議論を無期限に続けない。

Decision前に必要に応じて次を確認する。

- expected mitigation effect
- operational / data / security risk
- reversibility
- failure時のfallback
- observation method

反対意見を確認するときは「全員賛成か」より、重大な見落としを拾える形でstrong objectionを求める。
新しいevidenceが出た場合はplanを更新する。

## Communication

Incident communicationではtimelinessとclarityの両方を守る。
Confirmed impactや利用者が取るべきactionが分かった時点で、原因やscopeの完全確定を待たず必要なinitial updateを出す。未確定事項は推測で埋めず、`Unknown` / `Investigating` と明示する。

短くするためにsubject、owner、action、timeを省略しない。Security / privacy上sensitiveな内容はneed-to-know境界を守り、general / external updateへそのまま載せない。

Regular updateでは次を含める。

- impact / severity
- what changed
- current mitigation
- leading hypotheses / critical unknowns
- outstanding actions + owners
- next check-in / update

新情報がなくてもmajor incidentではcadenceを維持する。

## Span of control

一人のICが多数のindividual responderを直接管理し始めたら、sub-team / workstreamへ分ける。

分割のsign:

- multiple teamsが別問題を並行調査している
- unrelated symptomsが複数ある
- 同じdomainへSMEが集中している
- primary incident channelが混雑している
- ICが全task / timer / ownerを追えない

Sub-teamを作る場合:

- leaderを一人決める
- specific objectiveを与える
- check-in timeを決める
- sub-team内の詳細はleaderが集約する
- ICへのprimary contactをleaderに限定する

## External / cross-company incident

Vendorや他社が関係する場合も、ICは「相手の回答待ち」でincidentを止めない。

- vendor escalation ownerを決める
- investigation packageを送る
- workaround / containmentを並行検討する
- vendor statementは `reported fact` として扱う
- 自serviceでのimpact / recoveryを独立に観測する
- next vendor update timeを追う

原因主体とservice recovery responsibilityを切り離す。

## Transfer of command

長時間化、fatigue、timezone change、incident complexity変化等ではcommandを引き継ぐ。

Handoffでは最低限次を渡す。

- current impact / severity
- active mitigation
- critical facts / unknowns
- leading hypotheses
- active workstreams + owners
- pending decisions / timers
- external escalations
- next communication timing

Outgoing ICはhandoffを明示し、incoming ICが理解・受領したことを確認する。
Incident channelでもcommand transferを周知する。
よりseniorな人物が参加しただけで自動的にcommandを移さない。

## End of active command

次を満たすまでは「原因が分かった」「vendorがresolvedと言った」だけで終了しない。

- user-facing symptomがrecoverした
- important service-level signalsがrecoverした
- immediate data / security / safety concernが解消またはcontrolled
- remaining workがtime-criticalではない
- temporary mitigation / degraded modeが明示されている
- follow-up ownerが決まっている

Postmortem / long-term corrective actionはactive commandから切り離す。

## Anti-patterns

- IC自身が一つのlog investigationへ没頭する
- recognized command postがなく、複数channelで別々の判断をする
- live incident stateがなく、参加者が毎回口頭で状況確認する
- sensitive security stateをgeneral channelへ無条件に公開する
- initial updateをroot cause確定まで遅らせる
- `Can someone ...` のようにowner不明のtaskを投げる
- 全員の合意を待ってdecisionを止める
- seniorityだけでcommandを奪う
- vendor障害と聞いた瞬間に自systemの調査を止める
- root cause確定までmitigationをしない
- unknownを断定で埋める
- updateが新情報待ちになり長時間途切れる
- respondersを増やし続け、communication overheadを悪化させる
- fatigueしたICがhandoffせず継続する

## 参考資料

- Google SRE, *Managing Incidents*: https://sre.google/sre-book/managing-incidents/
- Google SRE Workbook, *Incident Response*: https://sre.google/workbook/incident-response/
- PagerDuty, *Incident Commander Training*: https://response.pagerduty.com/training/incident_commander/
- PagerDuty, *Different Roles*: https://response.pagerduty.com/before/different_roles/
- PagerDuty, *During an Incident*: https://response.pagerduty.com/during/during_an_incident/
- PagerDuty, *Complex Incidents*: https://response.pagerduty.com/before/complex_incidents/
- AWS Well-Architected, *Responding to events*: https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/responding-to-events.html
