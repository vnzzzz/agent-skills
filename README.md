# agent-skills

[![CI](https://github.com/vnzzzz/agent-skills/actions/workflows/ci.yml/badge.svg)](https://github.com/vnzzzz/agent-skills/actions/workflows/ci.yml) · [日本語](README.ja.md)

Reusable development workflows for Codex and Claude Code — plan changes, debug problems, test behavior, and write clear documentation with one shared Plugin.

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

Then ask your agent to use a Skill, for example: "Use `debugging` to identify why this test fails."

## Skills

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

Skills are maintained in [`plugins/agent-skills/skills/`](plugins/agent-skills/skills/). See [Contributing](CONTRIBUTING.md) to add or improve one.
