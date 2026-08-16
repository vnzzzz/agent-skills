---
name: issue-workflow
description: Issue、ticket、task recordを作業の正本として、scope確認、実装、検証、review、human handoffまでを一貫して進めるときに使用する。GitHub、GitLab、JIRA等のtracker固有操作はadapter skillへ委ねる。
---

# Issue Workflow

Issue-drivenな変更では、task recordを単なる作業メモではなく、**解決する問題、scope、acceptance criteria、判断経緯を共有する正本**として扱う。

このSkillはtracker / forge非依存のworkflowだけを扱う。GitHub Pull Request、GitLab Merge Request、JIRA transition、Redmine status等のprovider固有操作は対応するadapter skillへ委ねる。

Repository-localの `AGENTS.md`、contributing guide、branch policy、security rule、task-specific instruction等がある場合は、それらをこのSkillより優先する。

## 1. Task contractを確定する

作業開始時にtask recordとrepository-local rulesを読み、最低限次を確認する。

- 解決する問題 / expected outcome
- acceptance criteria
- 明示されたscope / non-goal
- permission boundary
- production / managed service / destructive operation等の安全境界
- dependency / blocker
- delivery / review / completionのlocal rule

Task recordとrepositoryの実装が食い違う場合は、実装をtaskへ機械的に合わせない。現在の実装を確認し、差異がacceptance criteriaへ影響するならtask recordへ事実を残す。

不足情報を推測で埋めるより、実装判断に必要な範囲で `confirmed / assumption / unknown` を分ける。ただし、低影響な曖昧さのために作業全体を止めない。

非自明な変更計画は `change-planning` を利用する。

## 2. Existing workとworkspaceをpreflightする

重複作業や誤ったbaseからの変更を避ける。

利用可能な範囲で確認する。

- current workspace / revision / branch
- expected base
- uncommitted or unrelated work
- 同じtaskを扱う既存branch / change request / worktree / agent session
- dependency taskの状態
- 必要なtool / credential / runtime

既存作業がある場合は、理由なく別実装を並行して作らない。継続すべき作業か、古い作業か、別scopeかを判定する。

Provider固有のbranch / change request discoveryはadapter skillの責務とする。

## 3. Issue scopeの中で実装する

Task recordのacceptance criteriaを満たす最小の変更を優先する。

- 無関係なcleanupを混ぜない
- 新しい問題を見つけた場合、現在taskの完了に必要でなければfollow-upへ分離する
- task scopeが実装中に実質変更された場合は、変更理由と影響をtask recordへ残す
- external / production / destructive actionはtaskまたはuserから明示されたpermission boundaryを超えない

実装上の抽象化判断は `development-guidelines`、原因不明のfailureは `debugging` を利用する。

長時間・状態変更commandは `command-execution` に従う。

## 4. Task recordをdecision logとして使う

すべてのcommandや細かな進捗を逐次書き込まない。後から作業を理解するために意味がある事実だけを残す。

Task recordへ残す価値が高いもの:

- issue記載と異なる重要な現状事実
- scope / approachを変えた理由
- blocker / external dependency
- operatorやhumanにしかできないaction
- production / managed environmentで確認すべき事項
- acceptance criteriaへ影響するvalidation結果
- follow-up taskへ分離した問題

Raw logの貼り付けではなく、判断に必要なevidenceを要約する。報告の強さは `evidence-reporting` に従う。

## 5. Validationを完了条件へ接続する

Validationは「何かtestを実行した」ではなく、taskのexpected outcomeとacceptance criteriaを確認するために行う。

何をどのlevelで検証するかは `testing` を利用する。

最低限、最終handoff時に次を区別できる状態にする。

- verified / passed
- failed
- skipped
- blocked
- unavailable
- not run

実環境確認が必要だがpermissionやcredentialの都合でagentが実行できない場合は、代替mockだけで完了扱いせず、operator actionとして明示する。

## 6. Delivery artifactを作る

変更を他者がreviewできるdelivery artifactへまとめる。

Delivery artifactの具体形はprovider / repositoryに従う。例:

- Pull Request / Merge Request
- patch / change list
- local review branch
- task tracker上のreview state

Delivery artifactには必要に応じて以下を含める。

- changed scope
- key decisions
- validation results
- skipped / unavailable checks
- remaining risks
- operator action / follow-up
- task recordへのtraceability

Formattingやevidence reportingは `evidence-reporting` を利用し、同じ説明をtask recordとdelivery artifactへ無意味に複製しない。

## 7. Independent reviewを受ける

Repositoryやuserがreviewerを指定・設定している場合は、delivery後にindependent reviewを受ける。

Reviewでは次を区別する。

- actionable defect / requested change
- clarification question
- suggestion / optional improvement
- stale / already-addressed feedback
- out-of-scope request

Actionable feedbackは実装とvalidationへ戻して対応する。修正後は必要に応じてreviewerへ再確認を依頼する。

Reviewを通すこと自体を目的にして、無関係な変更を追加しない。Reviewerが利用できない場合は、その事実をhandoffへ残す。

## 8. Human-reviewableな状態で停止する

明示的な委任がない限り、次のfinal actionは行わない。

- merge / land
- task close
- production deploy / release
- managed environmentへのdestructive change
- irreversible migration / data cleanup

通常の完了状態は、**task scopeの変更がreview可能で、validation evidenceと残存riskが明示され、actionable review feedbackへ対応済み**の状態とする。

Humanへhandoffするときは、最低限以下が分かればよい。

- 何を変更したか
- acceptance criteriaをどう確認したか
- 何を確認していないか
- reviewで何が指摘されどう処理したか
- merge / deploy前にhumanが判断すべきこと

## Provider adapterとの境界

このSkillは次を定義しない。

- branch naming
- default / base branch
- Pull Request / Merge Request API
- closing keyword
- issue status transition
- reviewer botの呼び出し方法
- comment / thread resolution API
- provider固有permission model

これらは `github-issue-workflow` 等のadapter skillとrepository-local rulesで具体化する。

将来別providerへ対応するときも、このcore workflowをcopyせず、provider固有部分だけをadapterへ追加する。

## 他Skillとの関係

- 実装前の変更計画は `change-planning`。
- 最小実装・abstraction判断は `development-guidelines`。
- commandの安全な実行は `command-execution`。
- test / validation strategyは `testing`。
- failure調査は `debugging`。
- 実施結果・未実施・riskの報告は `evidence-reporting`。
- boundedな反復改善は `iterative-improvement`。
- GitHub固有のdeliveryは `github-issue-workflow`。
