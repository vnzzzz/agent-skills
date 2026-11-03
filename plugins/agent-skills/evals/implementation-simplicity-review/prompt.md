---
max_turns: 10
allowed_tools: [Skill]
---

Review this proposed implementation shape for a one-off CSV exporter. There is only one output format, one consumer, and no planned alternative backend:

- `ExporterFactory` selects from registered strategies.
- `CsvExporterStrategy` delegates to `CsvExporterAdapter`.
- Three configuration flags toggle different factory behavior.
- A deprecated `LegacyCsvExporter` wrapper remains even though all internal callers can migrate together.

Identify which layers are unnecessary for the current requirements, which safety concerns still matter, and the simplest design. This is an implementation-design review, not a project plan.
