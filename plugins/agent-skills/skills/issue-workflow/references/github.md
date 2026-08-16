# GitHub Issue Workflow

`issue-workflow` をGitHub Issue / Pull Requestで実行するときのprovider固有ルールを定義する。
GitHubを使うtaskでだけ読み、tracker非依存のlifecycle、planning、implementation、validation、reportingは親Skillを正本とする。

## Repository / Issue / baseを確定する

- Userがrepository、Issue、PR、baseを指定している場合はそれを優先する。
- Issue本文、関連comment / PR、repository-local rulesを確認する。
- PR baseは user instruction → local rule → Issue / established convention の順で決める。
- default branchや`main`を理由なく決め打ちしない。

## 既存workを確認する

同じIssueを扱うopen PR、remote branch、current workがある場合は、理由なく重複したbranchやPRを作らない。

新しいbranchが必要な場合は、repository-localのnaming ruleを使い、確認済みbaseから作る。
Uncommitted workがあるlocal checkoutでは、unrelated changesを取り込まない。

## Commit / push / Pull Request

- Commit / push前に、diffへunrelated changesやsecretが含まれていないことを確認する。
- PRは確認済みの正しいbaseへ作る。
- Draft / ready for reviewの扱いはrepository-local ruleまたはuser instructionに従う。
- IssueとのtraceabilityをPR本文から判断できるようにする。

GitHubのclosing keywordによるIssue closeは、PRがdefault branchへ取り込まれるworkflowでのみ自動closeを前提にする。
非default baseをtargetするPRでは、repository固有のlink / close運用を確認し、自動closeを仮定しない。

## IssueとPRへ残す情報

Issue commentには、task recordとして後から必要になる情報だけを残す。

- 重要なscope / approach変更
- blocker
- operator action
- 独立したfollow-up
- 必要なvalidation evidence

PR本文には、review判断に必要な次の情報を必要十分にまとめる。

- 変更概要
- key decisions
- validation結果
- skipped / unavailable checks
- remaining risk / operator action
- Issue traceability

同じ説明をIssueとPRへ重複して保守しない。

## Reviewとchecks

- Repositoryでreviewerが設定されている場合だけ、実際に利用可能な方法でreviewを依頼する。
- Review submission、inline thread、requested changes、task-relevant checksを確認する。
- Actionable feedbackは修正・再検証・返信し、必要ならre-reviewを依頼する。
- Suggestionやout-of-scope requestは、必要性を判断して別taskへ分離できる。
- CI successをactual runtimeやexternal environmentの確認と同一視しない。

## Tool choice

利用可能ならGitHub connector / APIを、Issue・PR・review・comment・check等のstructured GitHub dataに使う。
Local checkoutが必要な操作では`git`を使い、`gh`はcurrent-branch PR discoveryやActions log等、connectorで不足する操作に限定する。

Connector stateとlocal checkoutのrepository / branch contextを混同しない。

## Human handoff

PRからIssue / base / branch / changed scope / validation / remaining risk / review結果を判断でき、重大なactionable feedbackが残っていない状態でhandoffする。

Merge、Issue close、production deploy等は、親`issue-workflow`のpermission boundaryに従う。
