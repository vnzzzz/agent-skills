# Cross-Boundary Investigation

`incident-response` でSaaS、cloud、network、shared platform、他team、vendor等を含むfailure domainを狭めるための調査方法を定義する。

## 情報の扱い

調査中は次を分ける。

| Type | Meaning |
|---|---|
| Confirmed fact | artifact / metric / log等で確認した事実 |
| Reported fact | operator / owner / vendor等からの報告 |
| Hypothesis | factsを説明する反証可能な推定 |
| Unknown | 現時点で不明な事項 |
| Critical unknown | 成立するとcontainment / severity / security / data integrity等の判断が変わるunknown |

情報不足を事実として補完しない。一方、原因推定を求められた場合は、現在のevidenceからhypothesisを作り、確度と確認方法を示す。

## 1. Looseな事象をtimelineへ正規化する

ユーザーから断片的に共有された事象を、原因判断に効く順序へ整理する。

| Time | Event | Type | Relevance |
|---|---|---|---|
| ... | ... | Confirmed / Reported / Unknown | 原因候補との関係 |

- timezoneを明示する
- 時刻不明を推測で補わない
- 同時刻でも因果とは限らない
- first known bad / last known goodが分かれば残す

## 2. Service boundaryを並べる

User request / business transactionが通る主要boundaryを実際の構成に基づいて並べる。

| Boundary | Input observed | Output observed | Affected / healthy difference | Owner |
|---|---|---|---|---|
| Client → DNS | ... | ... | ... | ... |
| Application → External API | ... | ... | ... | ... |

各boundaryで「どこから異常が始まるか」を見る。Component dashboardがhealthyでも、specific transactionが正常とは限らない。

## 3. Affected / unaffectedを比較する

Bad caseだけでなくgood caseとの差分を探す。

有効な比較軸の例:

- region / AZ
- tenant / account
- endpoint / function
- version / configuration
- proxyあり / なし
- identity provider
- request success / failure

差分がfailure boundaryを狭めるかを見る。

## 4. 原因仮説を順位付けする

仮説は`component名`ではなく、観測可能なfailure mechanismとして書く。

```text
Hypothesis: Tokyo regionからVendor APIへのTLS handshakeだけが失敗している。
Supporting: 同regionのhandshake failureが増加。
Contradicting / unknown: 別pathの結果は未確認。
Check: healthy regionと同一requestを比較する。
```

複数候補がある場合は、根拠、反証、不足情報、confidenceを並べる。数値確率は根拠がある場合だけ使う。

## 5. Evidenceの直接性を優先する

一般に次の順で、incidentとの直接性が高いevidenceを優先する。

- same requestのend-to-end trace / reproduction
- affected / unaffected比較
- boundary-specific log / metric
- owner / vendorからのspecific confirmation
- status page / broad announcement
- 時間的に近いchange
- 過去の類似事例

直前deploymentやvendor incidentとの時間的一致はhypothesis priorityを上げる材料にはなるが、単独でcauseを確定しない。

## 6. External dependencyを確認する

SaaS / cloud / external APIが疑わしい場合は必要に応じて確認する。

- official status / incident notice
- affected product / region / feature
- incident start / update time
- 自incidentとのsymptom / scope一致
- request / trace ID
- API response / rate limit / quota
- auth / certificate / DNS
- tenant-specific issue
- support case / escalation path

Vendorがincidentを認めていなくても、自systemのevidenceがexternal boundaryを示すなら調査依頼を出す。

## 7. Escalation packageを作る

他team / vendorへは、相手がすぐ調査開始できる最小情報を渡す。

- impact
- exact timestamp + timezone
- affected scope
- error / request / trace ID
- affected / unaffected comparison
- already checked / attempted mitigation
- recent relevant changes
- desired response: investigation / status / workaround等

Secret、credential、不要なcustomer sensitive dataは共有しない。

他teamへ依頼した後も、回答待ちだけにせず自team側で確認可能なboundaryを並行して進める。

## 8. Critical unknownを優先する

Root cause候補を広げる前に、対応方針を変える可能性を確認する。

例:

- write failureがdata lossを伴うか
- auth failureがavailability issueかcompromiseか
- queue停止がbacklogだけかmessage lossを伴うか
- failover先も同じfailure modeを持つか
- irreversible operationが途中か

Worst-caseを事実認定せず、critical unknownとして扱う。

## 9. Local debuggingへ切り替える

Failure domainがlocal implementationへ十分に絞れたら`debugging`を使う。

例:

- resource leak
- deployment間regression
- concurrency / ordering failure
- connection pool misuse
- validation / state transition bug

Incident全体のimpactやexternal dependencyは引き続き`incident-response`で扱う。

## 10. Recoveryを独立に確認する

External dependencyが`resolved`になっても、自serviceで確認する。

- original requestが成功する
- error rate / latencyが戻る
- backlogがdrainする
- stale cache / broken session等のsecondary impactがない
- retry storm等のrecovery loadが問題を起こしていない

## 参考資料

- Google SRE, *Effective Troubleshooting*: https://sre.google/sre-book/effective-troubleshooting/
- Google SRE Workbook, *Incident Response*: https://sre.google/workbook/incident-response/
- PagerDuty, *During an Incident*: https://response.pagerduty.com/during/during_an_incident/
- AWS Well-Architected, *Responding to events*: https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/responding-to-events.html
