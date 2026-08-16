---
name: github-issue-workflow
description: GitHub Issueをtask SSOTとして、repository-local rulesに従いbranch作成、実装、push、Pull Request、review対応、人間へのhandoffまでを進めるときに使用する。tracker非依存の状態遷移はissue-workflowを正本とする。
---

# GitHub Issue Workflow

GitHub repositoryでIssue-drivenな変更を行うとき、`issue-workflow` のgeneric contractをGitHubのIssue / branch / Pull Request / reviewへ具体化する。

このSkillはGitHub固有のdelivery mechanicsだけを扱う。Planning、testing、command safety、reporting等は既存shared skillsを利用し、内容を重複させない。

Repository-localの `AGENTS.md`、CONTRIBUTING、branch strategy、PR template、security rule、Issue本文、user instructionをこのSkillより優先する。

## 1. GitHub task contextを解決する

作業開始時に、対象repositoryとIssueを明示的に確認する。

最低限確認するもの:

- repository
- Issue number / URL
- Issue state
- Issue本文とacceptance criteria
- linked / dependent IssueやPR
- repository-local workflow rule
- expected PR base
- merge / review / permission boundary

Issue番号だけから別repositoryを推測しない。

`issue-workflow` に従いtask contractを整理し、非自明な変更では `change-planning` を利用する。

## 2. Base branchを推測しない

GitHub repositoryのdefault branchが、変更PRのbaseとは限らない。

Baseは次の優先順位で決める。

1. userの明示指示
2. repository-local rules
3. Issue本文 / linked workflowの明示
4. existing related PR / established repository convention
5. それでも不明な場合だけdefault branchを候補として確認する

`main` / `master` を機械的に選ばない。

作業branchを作る前にbaseを最新状態へ合わせ、unrelatedなlocal workを混ぜない。

## 3. Existing branch / PRとの重複を避ける

同じIssueを扱う既存workがないか、利用可能なGitHub API、connector、`gh`、local git contextで確認する。

確認候補:

- open PR whose body/title references the Issue
- Issue用branch naming conventionに合うremote branch
- current branchに紐づくPR
- Issue commentsに残された進行中work

既存の有効なPRがある場合、理由なく2本目を作らない。既存workを継続するか、stale / abandonedである根拠を確認する。

## 4. Issue branchを作る

Branch namingはrepository-local ruleを使う。

Local ruleがなければ、Issue番号と短いslugを含む識別可能な名前を使う。例:

```text
agent/issue-123-short-topic
issue/123-short-topic
```

具体prefixをshared ruleとして強制しない。

Branchは確認済みbaseから作成する。

## 5. 実装とGitHub上の経緯記録

実装は `issue-workflow` に従う。

GitHub Issueへのcommentは、細かなcommand実況ではなく、後から判断経緯を追う価値がある場合に使う。

Issueへ残す候補:

- Issue記載と異なる重要なrepository事実
- approach / scope変更
- blocker / external dependency
- operator action
- production / managed environmentで未実施の確認
- follow-up Issueへ分離した問題

Commentを増やすこと自体を成果にしない。PR本文で十分な情報をIssueへ重複投稿しない。

## 6. Commit / pushする

Repository-local commit policyを優先する。

Commit前にunrelated changesやsecretが含まれていないことを確認する。

Credential、token、private key、subscriber/customer data等をcommit、terminal report、Issue、PRへ出さない。

Push前後のcommand実行と状態判定は `command-execution` を利用する。

## 7. Pull Requestを正しいbaseへ作る

PRはtask scopeに対して1本を基本とし、repository ruleが `1 Issue = 1 PR` を要求する場合は厳守する。

PRには必要に応じて以下を含める。

- task / problem summary
- changed scope
- key decisions
- validation results
- skipped / unavailable validation
- remaining risks / operator action
- Issue traceability

Issue closing referenceはrepository policyに従う。

GitHub標準のclosing keywordを使う場合、同一repository Issueであり、merge時にcloseさせる意図があることを確認してから、例えば次を使う。

```text
Closes #123
```

単なる関連付けしか意図しないIssueへclosing keywordを付けない。

PR baseが正しいことを作成後にも確認する。

## 8. Draft / ready stateをrepository workflowに合わせる

Runtime validationやexternal operator actionが残っている場合、repositoryがDraft PRを使う運用ならDraftを維持する。

Ready for reviewへ切り替える条件を勝手に一般化しない。Repository-local ruleまたはtask contractに従う。

## 9. Automated / independent reviewを依頼する

Userまたはrepositoryがconfigured reviewerを持つ場合、その**実際に設定された呼び出し方法**を使う。

例:

- requested reviewer
- GitHub App / bot
- PR commentによるreview trigger
- repository-specific review command

`@codex review` のようなtriggerは、利用可能または明示されたrepositoryでのみ使う。Shared skillが特定botの存在を前提にしない。

Reviewを依頼したら、submission、top-level comment、inline thread、requested changesを確認する。

## 10. Review feedbackへ対応する

Feedbackを次へ分類する。

- actionable defect / requested change
- clarification
- optional suggestion
- stale / duplicate
- already addressed
- out of scope

Actionable feedbackは実装へ戻して修正し、関連validationを再実行する。

Inline threadには、対応内容または対応しない理由を簡潔に返す。Thread resolutionがrepository運用に含まれる場合、対応確認後にresolveする。単にcommentを消す目的でresolveしない。

変更後にreviewerの再確認が必要ならre-reviewを依頼する。

## 11. CI / checksを確認する

PRにchecksがある場合、required / task-relevant checksの状態を確認する。

Failureがある場合はlogやerrorを確認し、変更に起因するfailureか、external / unrelated failureかを区別する。CI failureの原因調査は `debugging` を利用する。

CIが存在しないことと、validation成功を同一視しない。

## 12. Human handoffで停止する

明示的なmerge委任がない限り、PRをmergeしない。

通常のhandoff状態:

- correct Issue / base / branch / PRが対応付いている
- task scopeの変更がpush済み
- task-relevant validation結果がPRから分かる
- skipped / blocked / operator actionが明示されている
- actionable review feedbackへ対応済み
- unresolvedな重大feedbackがない
- humanがmerge可否を判断できる

Repository ruleでIssue closeがmergeに連動する場合、手動closeもしない。

## GitHub toolの使い分け

利用可能なtoolに応じて最も直接的な方法を使う。

### GitHub connector / APIが適するもの

- Issue / PRの取得
- comments / reviews / threadsの確認
- Issue / PR comment
- PR metadata
- reviewer request
- PR作成（branch push済みの場合）

### local `git` / `gh` が適するもの

- current checkout / branch / working tree確認
- branch作成
- local commit
- push
- current branchに紐づくPR discovery
- repository固有のGitHub Actions log調査

同じ情報を複数経路から無意味に取り直さない。Connectorとlocal checkoutのrepository / branch contextを混同しない。

## やってはいけないこと

- default branchをPR baseと決め打ちする
- Issueを読まずにbranchだけ作る
- 同一Issueへ重複PRを作る
- unrelated changesを同じPRへ混ぜる
- review botが存在すると仮定する
- review commentを読まずに機械的にresolveする
- CI successだけでproduction behaviorまで保証したと書く
- credential / secretをIssueやPRへ貼る
- 明示委任なしにmerge / deployする

## 他Skillとの関係

- tracker非依存のtask lifecycleは `issue-workflow`。
- 実装計画は `change-planning`。
- command executionは `command-execution`。
- validation strategyは `testing`。
- failure investigationは `debugging`。
- evidence-based reportingは `evidence-reporting`。
- repeated improvementが必要なら `iterative-improvement`。
