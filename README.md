# agent-skills

**One set of engineering practices. Two coding agents.**

Focused Skills for investigating bugs, planning changes, testing behavior, and reporting evidence. The same instructions work in both Codex and Claude Code.

[Get started](#install) · [Explore Skills](#skills) · [日本語](README.ja.md)

## Ask for the outcome

- “Why is this test flaky? Find the cause and verify the fix.”
- “Plan this refactor in safe, reviewable steps.”
- “Check this technical claim against primary sources.”

Your agent can select relevant Skills, or you can request one by name.

## Install

### Codex

```bash
codex plugin marketplace add https://github.com/vnzzzz/agent-skills.git --json
codex plugin add agent-skills@vnzzzz-agent-skills --json
```

### Claude Code

```bash
claude plugin marketplace add https://github.com/vnzzzz/agent-skills.git --scope user
claude plugin install agent-skills@vnzzzz-agent-skills --scope user
```

## Skills

Each Skill covers one focused workflow. Browse the source below.

<!-- BEGIN GENERATED SKILLS -->
- [change-planning](plugins/agent-skills/skills/change-planning/SKILL.md)
- [code-comments](plugins/agent-skills/skills/code-comments/SKILL.md)
- [command-execution](plugins/agent-skills/skills/command-execution/SKILL.md)
- [debugging](plugins/agent-skills/skills/debugging/SKILL.md)
- [development-guidelines](plugins/agent-skills/skills/development-guidelines/SKILL.md)
- [evidence-reporting](plugins/agent-skills/skills/evidence-reporting/SKILL.md)
- [incident-response](plugins/agent-skills/skills/incident-response/SKILL.md)
- [issue-workflow](plugins/agent-skills/skills/issue-workflow/SKILL.md)
- [iterative-improvement](plugins/agent-skills/skills/iterative-improvement/SKILL.md)
- [product-thinking](plugins/agent-skills/skills/product-thinking/SKILL.md)
- [readme-writing](plugins/agent-skills/skills/readme-writing/SKILL.md)
- [technical-research](plugins/agent-skills/skills/technical-research/SKILL.md)
- [technical-writing](plugins/agent-skills/skills/technical-writing/SKILL.md)
- [testing](plugins/agent-skills/skills/testing/SKILL.md)
<!-- END GENERATED SKILLS -->

Want to add or improve a Skill? See [Contributing](CONTRIBUTING.md).
