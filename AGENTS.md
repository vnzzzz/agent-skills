# Repository instructions

This repository is the canonical source for reusable Agent Skills shared across repositories.

## Boundaries

- Put each shared Skill under `skills/<skill-name>/SKILL.md`.
- Keep shared Skills independent of any specific product, consumer repository, repository path, terminology, or operational convention.
- Keep consumer-specific configuration and overlays in the consumer repository.
- Prefer the Agent Skills open format so the same Skill source remains usable from Claude Code and Codex.
- Agent-specific extensions are acceptable only when they are optional and do not make the Skill unusable by another supported agent.
- Keep each Skill as self-contained as practical. Do not introduce cross-Skill dependencies without a concrete need.
- Do not add infrastructure, release machinery, validation layers, or abstractions only for anticipated future use.

## Development workflow

- Use one Issue for one PR.
- Keep each change focused on the Issue scope.
- When adding or changing a Skill, verify it with the applicable development workspace and supported agents when such verification is available.
