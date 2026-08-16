---
name: github-issue-workflow
description: GitHub Issueをtask SSOTとして、branch、Pull Request、review、CI、human handoffまで進めるときに使用する。Provider非依存の進め方はissue-workflowを正本とする。
---

# GitHub Issue Workflow

GitHubで `issue-workflow` を具体化するadapter。GitHub固有のdelivery mechanicsだけを扱い、repository-local rules、Issue本文、user instructionを優先する。

## Workflow

1. **Repository / Issue / baseを確定する**
   Issue本文、関連comment / PR、repository-local rulesを確認する。PR baseは user instruction → local rule → Issue / established convention の順で決め、default branchや `main` を決め打ちしない。

2. **既存workを確認してissue branchを作る**
   同じIssueを扱うopen PR / remote branch / current workがあれば理由なく重複させない。Branch namingはlocal ruleを使い、確認済みbaseから作る。

3. **実装してPRへ届ける**
   実装・validationは `issue-workflow` に従う。Commit / push前にunrelated changesやsecretがないことを確認する。PRは正しいbaseへ作る。GitHubのclosing keywordはPRがdefault branchをtargetするときだけ解釈されるため、非default baseでは自動link / closeを仮定せずrepository固有のtrace / close運用に従う。Draft / readyの扱いもlocal ruleに従う。

4. **GitHubへ必要な経緯を残す**
   Issue commentには重要なscope / approach変更、blocker、operator action、follow-upだけを残す。PRには変更概要、key decisions、validation、skipped / unavailable checks、remaining risk、Issue traceabilityを必要十分に書く。同じ説明を重複させない。

5. **Reviewとchecksを完了する**
   Configured reviewerがある場合だけ実際のtrigger方法でreviewを依頼する。Review submission / inline thread / requested changes / task-relevant checksを確認し、actionable feedbackは修正・再検証・返信し、必要ならre-reviewする。CI successを実環境確認と同一視しない。

6. **Human review可能な状態で停止する**
   Issue / base / branch / PRの対応、validation結果、未確認事項、operator action、review結果がPRから判断でき、重大なactionable feedbackが残っていない状態にする。明示委任がない限りmergeやIssue closeは行わない。

## Tool choice

利用可能ならGitHub connector / APIをIssue・PR・review取得やcommentに使い、local `git` / `gh` をcheckout、branch、commit、push、current-branch PR discovery、Actions log確認に使う。Repository / branch contextを混同しない。

## Related skills

Tracker非依存のlifecycleは `issue-workflow`。Planning / execution / validation / debugging / reportingは対応するshared skillへ委ねる。
