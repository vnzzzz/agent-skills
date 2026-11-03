---
max_turns: 10
allowed_tools: [Skill]
---

A local Python unit test started failing after a refactor. The function below should preserve the input order while removing duplicate IDs, but the test sometimes returns a different order.

```python
def unique_ids(rows):
    return list(set(row["id"] for row in rows))
```

Input: `[{"id": "c"}, {"id": "a"}, {"id": "c"}, {"id": "b"}]`
Expected: `["c", "a", "b"]`

Identify the root cause, propose the smallest correction, and explain what regression test would confirm it. Do not edit files.
