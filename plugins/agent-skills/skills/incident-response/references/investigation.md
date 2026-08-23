# Cross-Boundary Investigation

`incident-response` でSaaS、cloud、network、shared platform、他team、vendor等を含むincidentを調査するときの切り分け方法を定義する。
目的は、自teamのcodebaseを前提にせず、service pathとresponsibility boundaryをまたいでfailure domainを狭めることである。

## 不足情報を推測で埋めない

環境固有情報は、利用者・operator・system ownerが最も正確に把握している場合が多い。
次のような情報が必要なら、内部知識や過去事例から補完せず提示を求める。

- exact timestamp + timezone
- affected / unaffected user、tenant、region、function
- exact error / status / output
- request / trace / correlation ID
- source / destination
- environment / version / configuration
- recent deployment / change
- dependency / vendor contract
- network path / proxy / DNS構成
- user-visible behavior

質問するときは「何を教えてください」だけでなく、何の判断に必要かを示す。

例:

```text
発生時刻を秒単位で確認したいです。
Vendor incident / deployment / network eventとの時系列を比較するために必要です。
Monitoringまたは実行ログから確認できますか。
```

## Information model

調査中の情報は次を区別する。

### Confirmed fact

自分で観測した、またはartifact / metric / log等のevidenceで確認できる内容。

### Reported fact

Operator、service owner、vendor、status page等が報告している内容。
重要な情報として利用してよいが、sourceを明示し、自incidentとの因果を自動的に確定しない。

### Hypothesis

Factsを説明するための反証可能な仮説。
不足情報を穴埋めするための断定に使わない。

### Unknown

現時点で分からない事項。

### Critical unknown

成立した場合にcontainment、severity、security、data integrity等の対応が変わるunknown。
通常のroot cause探索より優先して確認する。

## Service pathを描く

まずuser request / business transactionが通る主要boundaryを並べる。

例:

```text
Client
  -> DNS
  -> CDN / WAF
  -> Load Balancer
  -> Application
  -> Identity Provider
  -> Database
  -> External SaaS API
```

実際のarchitectureを確認せず、この例をsystem構成として使わない。

各boundaryについて、可能なら次を確認する。

- inputは到達しているか
- outputは返っているか
- latency / error / saturationはどこで変化するか
- healthy pathとの差分は何か
- ownerは誰か
- independent evidenceは何か

「componentがhealthy」というdashboardだけで、そのcomponentを通るspecific transactionが正常と判断しない。

## Affected / unaffectedを比較する

原因探索では、bad caseだけでなくgood caseを探す。

有効な比較軸:

- region A / B
- tenant A / B
- endpoint A / B
- IPv4 / IPv6
- proxyあり / なし
- old / new version
- one AZ / another AZ
- specific identity provider / another provider
- one vendor endpoint / another endpoint
- request success / failure

差分がfailure boundaryを狭めるかを見る。

## Critical unknownを先に切る

Root cause候補を広く列挙する前に、緊急性を変える可能性を確認する。

例:

- write failureはretry可能か、data lossを起こしているか
- authentication failureはavailability issueかcredential compromiseか
- queue停止はbacklogだけかmessage lossを伴うか
- network failureはsingle pathか全経路か
- external API failureはread-onlyかirreversible operation途中か

Worst-case scenarioは `hypothesis` / `critical unknown` として扱い、evidenceなしに断定しない。

## Boundaryごとにhypothesisを作る

Hypothesisはcomponent名だけではなく、観測可能なfailure modeとして書く。

悪い例:

```text
Vendorが悪い
Networkっぽい
```

良い例:

```text
Hypothesis: Tokyo regionからVendor APIへのTLS handshakeだけが失敗している。
Expected evidence: 同regionのhandshake failure増加、別regionでは成功。
Disconfirming evidence: 同じconnection pathで別requestが継続成功している。
```

## Evidenceの強さを意識する

一般に、次のように直接性の高いevidenceを優先する。

- end-to-end reproduction / trace
- same requestのboundary間correlation
- affected / unaffected comparison
- component-specific log / metric
- vendor / ownerからのspecific confirmation
- status page / broad announcement
- 時間的に近いchange
- 過去の類似事例

Status pageは重要だが、自incidentの因果を単独では証明しない。

## External dependencyを調査する

SaaS / cloud / external APIが疑わしい場合、少なくとも必要に応じて確認する。

- official status / incident notice
- affected product / region / feature
- incident start / update time
- 自incidentのsymptomとの一致
- request / trace IDs
- API response / headers
- rate limit / quota / capacity
- authentication / certificate / DNS
- account / tenant-specific issue
- support case / escalation path

Vendorがincidentを認めていなくても、自systemのevidenceがexternal boundaryを示しているなら調査依頼を出す。

## Escalation package

他team / vendorへ依頼するときは「調べてください」だけにしない。
相手がすぐ確認できる最小packageを作る。

```text
Impact:
- checkout requestsの約30%が失敗

Time:
- 2026-08-23 22:14–ongoing JST

Scope:
- ap-northeast path only; another region is healthy

Evidence:
- HTTP 503
- request IDs: ...
- trace IDs: ...

Our checks:
- application ingress is healthy
- failure starts at external API call
- retry from healthy region succeeds

Recent changes:
- none known / <change>

Request:
- confirm whether these requests reached your service
- current incident / workaround status
```

Secret、credential、customer sensitive dataは不要に共有しない。

## 他teamとの調査

他team管理componentが疑わしい場合も、owner境界で調査を投げて待つだけにしない。

- ownerを一人決める
- questionを具体化する
- evidenceを渡す
- desired resultを明示する
- next check-inを決める
- parallelに自team側で確認可能なboundaryを進める

Ownershipはinvestigation responsibilityの分担であり、blame assignmentではない。

## Correlationとcausation

次をcauseと即断しない。

- deployment直後
- vendor incidentと同時刻
- traffic spike
- certificate更新
- network maintenance
- 他team change

時間的一致はhypothesis priorityを上げる材料にはなるが、affected path / symptom / recoveryとの因果を確認する。

## 仮説の更新

新しいfactが入ったら、調査boardを更新する。

| Hypothesis | Supporting | Contradicting | Needed evidence | State |
|---|---|---|---|---|
| H1 | ... | ... | ... | active / weakened / rejected / confirmed |

Hypothesis数を増やし続けない。
Evidenceで弱くなった候補を下げ、information gainの高い確認へ集中する。

## Local debuggingへ切り替える条件

Boundary investigationにより、local implementationがfailure domainとして十分に狭まった場合は `debugging` を使う。

例:

- specific code pathでresource leakが発生
- deployment間regression
- application concurrency / ordering failure
- local connection pool misuse
- validation / state transition bug

Incident全体のimpact、coordination、external workstreamは引き続き `incident-response` で管理する。

## Recovery validation

External dependencyが回復した場合も、自service側で確認する。

- original requestが成功する
- error rate / latencyが戻る
- backlogがdrainしている
- stale cache / broken session等のsecondary impactがない
- retry storm等のrecovery loadが問題を起こしていない

Vendorの `resolved` noticeはrecoveryの一つのsignalであり、end-to-end確認の代替ではない。

## 参考資料

- PagerDuty, *During an Incident*: https://response.pagerduty.com/during/during_an_incident/
- PagerDuty, *Different Roles*: https://response.pagerduty.com/before/different_roles/
- Google SRE, *Effective Troubleshooting*: https://sre.google/sre-book/effective-troubleshooting/
- Google SRE Workbook, *Incident Response*: https://sre.google/workbook/incident-response/
- AWS Well-Architected, *Responding to events*: https://docs.aws.amazon.com/wellarchitected/latest/operational-excellence-pillar/responding-to-events.html
