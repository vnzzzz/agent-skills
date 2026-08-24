---
name: incident-response
description: 本番障害、service degradation、SaaS / cloud / external API障害、network / platform障害、他team・他社をまたぐincidentについて、事象整理、原因仮説、cross-boundary切り分け、mitigation、recovery確認を行うときに使用する。既定は原因推定・調査支援であり、Incident Commanderやcommand補佐は明示的に依頼された場合だけ行う。isolated local bugやtest failureだけならdebuggingを優先する。
---

# Incident Response

Active incidentを、自teamのcodeだけに限定せず、SaaS、cloud、network、shared platform、他team、vendorを含むsystem全体の問題として扱う。

## 動作モード

### 調査モード（既定）

「事象を整理して原因を推定して」「この障害の原因候補は」「ログと発生事象をつなげて」のような依頼では、原因推定と切り分けを行う。

- 事象を時系列へ整理する
- 確認済み事実 / 報告情報と仮説を分ける
- 原因候補を根拠付きで順位付けする
- 反証材料と不足情報を示す
- 次に情報利得の高い確認を提案する
- 必要なら影響緩和 / 復旧確認を提案する

情報が不足していても推定依頼そのものを止めない。不足部分を事実として補完せず、仮説として推定し、確度と確認方法を示す。

このmodeでは、重大incidentであっても自動的にIncident Commanderを名乗らない。Role assignment、command post、定期update cadence、task ownerの指揮管理も、依頼されていなければ開始しない。

### 指揮モード（明示依頼時のみ）

ユーザーが「ICして」「Incident Commanderとして進めて」「障害対応を指揮して」「ICを補佐して」「進行管理して」等、command / coordinationを明示的に依頼した場合だけ [references/incident-command.md](references/incident-command.md) を読む。

依頼が曖昧なら調査モードを維持する。Incidentの重大度や関係team数だけを理由に指揮モードへ切り替えない。

## 原則

1. **Harm containmentとservice recoveryをroot cause解明より優先する。** Security compromise、data loss / corruption、safety impactが確認された場合はcontainmentをavailability回復より優先する。
2. **事実と推定を混同しない。** 確認済み事実、報告情報、仮説、不明事項、判断 / 対応を区別する。
3. **重要な未確認事項を先に確認する。** 成立すると対応方針が変わるsecurity、data integrity、irreversible side effect等を優先する。
4. **原因を自teamのcodeへ限定しない。** External dependencyや他team管理componentも同じfailure domain候補として扱う。
5. **不足情報を推測で事実化しない。** 必要なら「何の判断に必要か」と合わせてoperator / ownerへ確認する。
6. **Recoveryはend-to-endで確認する。** 一componentの回復ではなく、user-facing symptom、service-level signal、backlog、data integrityまで見る。

## 1. 影響と重要な未確認事項を確認する

まず分かる範囲で整理する。

- user / business impact
- affected / unaffected scope
- start time / first known bad / last known good
- exact symptom / error / latency / availability / data issue
- 継続中 / 断続的 / 復旧中 / 収束
- security / data integrity / safety上の重要な未確認事項

Local severity定義がなければ独自のSEV番号を作らない。

## 2. 事象をtimelineへ並べる

Looseな情報でも、時刻と順序が分かる範囲で整理する。

| 時刻 | 事象 | 種別 | 原因推定との関係 |
|---|---|---|---|
| ... | ... | 確認済み / 報告情報 / 不明 | ... |

Timestampはtimezoneを含める。時刻不明の事象を推測で並べず、順序だけ判明している場合はその旨を示す。

## 3. 原因仮説を作る

単なるcomponent名ではなく、`事象 → failure mechanism → symptom` がつながる形で仮説を書く。

| 順位 | 仮説 | 根拠 | 反証・未確認事項 | 確度 |
|---:|---|---|---|---|
| 1 | ... | ... | ... | 高 / 中 / 低 |

数値確率は根拠がある場合だけ使う。新しい事実が入ったら順位と確度を更新する。

## 4. Failure boundaryを狭める

SaaS、vendor、network、他team等を含むcross-boundary調査では [references/investigation.md](references/investigation.md) を読む。

有効な確認を優先する。

- affected / unaffected比較
- same requestのboundary間trace
- known-good / known-bad比較
- version / configuration差分
- external statusと自incidentの時刻・scope・symptom比較

Status pageや直前deploymentとの時間的一致だけでcauseを確定しない。

## 5. 不足情報を絞って確認する

追加情報が必要なら、判断への寄与が高いものだけを聞く。

| 必要な情報 | 必要な理由 | 最適な確認先 |
|---|---|---|
| ... | ... | operator / monitoring / vendor |

既に十分な仮説が立つ場合、質問だけして原因推定を先送りしない。

## 6. Mitigationとevidence preservationを考える

Impactやharmが継続している場合は、原因確定前でも安全なcontainment / mitigationを検討する。

Restart、rollback、failover、queue reset、instance replacement等でvolatile evidenceを失う場合は、containmentやrecoveryを実質的に遅らせない範囲で必要なlog、trace、process state、configuration、audit evidence等を先に保全する。

重大な被害が継続している場合、証拠保全のために緊急containmentを不必要に遅らせない。

## 7. Recoveryを確認する

Mitigation / fix後は必要に応じて確認する。

- original symptom
- error rate / latency / availability
- backlog / queue / replication lag
- data integrity
- secondary impact / recovery load
- observation window中の再発

Vendorの`resolved`通知だけで自serviceのrecovery確認を代替しない。

## 出力

原因推定では、必要なsectionだけを使い、長い調査日誌にしない。基本は次の順でまとめる。

1. **現時点の見立て** — 最有力原因と確度
2. **タイムライン** — 原因判断に効く事象だけ
3. **原因仮説** — 根拠、反証、不足情報
4. **次に確認すること** — 情報利得が高い順
5. **影響緩和 / 復旧** — 必要な場合だけ

一覧性が必要なら [references/status-board.md](references/status-board.md) を使う。
Markdownの見出し、表、箇条書きを優先し、Mermaidは使用しない。装飾より、情報の選別、関係、時系列が一読で分かることを優先する。

Suspected / confirmed security compromiseでは、sensitive evidenceやcontainment detailをgeneralな出力へ無条件に載せず、organization-localのsecurity processとneed-to-know境界を優先する。

## 他Skillとの関係

- `debugging`: local implementationへfailure domainが絞れた後のroot cause investigation
- `technical-research`: external specification、vendor status、support policy等の確認
- `command-execution`: commandやmutating operationの安全な実行
- `evidence-reporting`: 実施内容・検証・未確認事項の報告
- `technical-writing`: durableなrunbookやincident procedureの執筆

## 参考資料

- Google SRE, *Managing Incidents*: https://sre.google/sre-book/managing-incidents/
- Google SRE Workbook, *Incident Response*: https://sre.google/workbook/incident-response/
- Google SRE, *Effective Troubleshooting*: https://sre.google/sre-book/effective-troubleshooting/
- PagerDuty, *Incident Commander Training*: https://response.pagerduty.com/training/incident_commander/
- PagerDuty, *During an Incident*: https://response.pagerduty.com/during/during_an_incident/
- AWS Well-Architected, *Responding to events*: https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/responding-to-events.html
