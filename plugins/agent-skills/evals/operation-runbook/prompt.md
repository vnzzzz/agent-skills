---
max_turns: 10
allowed_tools: [Skill]
---

Draft a short operations runbook for a service with nightly database backups. The current verified behavior is: backup starts at 02:00 UTC, objects are stored in a private bucket, and backup job failures alert the on-call engineer. Restore must first be rehearsed in a non-production environment. The exact restore command and retention period have not yet been confirmed.

Write the runbook so operators can distinguish verified steps, prerequisites, missing facts, and recovery checks. Do not invent commands, and do not write a repository landing page.
