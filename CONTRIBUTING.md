# Contributing

[日本語](CONTRIBUTING.ja.md)

Use the official Skill Creator for general guidance on creating and improving Skills. This document defines only the conventions specific to `agent-skills`.

## Skill structure

- One Skill should cover one coherent capability or workflow that triggers independently. Split variants of the same workflow into `references/` when appropriate.
- Keep decisions and procedures that are always required in `SKILL.md`, and move conditional detail into `references/`.
- Do not duplicate the same rule in multiple places.
- Require `name` and `description` in `SKILL.md` frontmatter, and keep `name` identical to the directory name. Use other standard fields only after confirming that they are needed and compatible with both Codex and Claude Code.
- Include both what the Skill does and the trigger or context needed to invoke it in `description`. Do not remove trigger information merely to make the description shorter.

## Style

- Use an English Title Case H1 as the identifier for a Skill or reference.
- Skill bodies are primarily written in Japanese, but do not force common technical terms into Japanese.
- Prefer established terms such as `foreground`, `retry`, `root cause`, `completed` / `blocked`, `Node` / `Edge`, and `Repository` / `Issue` / `Pull Request` when they are common, identifying, or part of a cross-Skill contract.
- Prefer natural Japanese for H2 and lower headings in Skill runtime documents.
- Make the main sequential workflow directly traceable with `## 1. ...` headings.
- Describe responsibility boundaries with other Skills under `## 他Skillとの関係`.

## References and sources

- Do not add frontmatter to references, and use an English Title Case H1.
- State in `SKILL.md` when a reference should be read.
- Use `## 関連資料` for indexes of internal references and `## 参考資料` for external sources.
- Add an appropriate language tag to code blocks.

## Documentation localization

- English repository documentation is canonical. A Japanese translation mirror uses the corresponding `*.ja.md` path.
- A pull request that changes a canonical document must update its Japanese mirror in the same pull request.
- Japanese-only wording corrections may be made without changing the canonical document.
- Runtime Skill files under `plugins/agent-skills/skills/` are not localization mirrors and remain governed by the Skill authoring rules above.
- Generated content, including the README Skill list, must be updated from its generator rather than maintained independently per language.

## Validation

CI validates durable structural requirements such as `name` / `description`, the manifest, and the presence of an H1. It does not reject standard optional fields without reason. Style choices such as Title Case and terminology are reviewed by humans.
