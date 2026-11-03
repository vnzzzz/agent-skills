---
max_turns: 10
allowed_tools: [Skill]
---

We plan to change how a SaaS service stores a customer's account status. Today the API, database, and asynchronous event payload each carry a free-form string. We want to introduce a constrained set of statuses without breaking existing consumers; current consumer versions and existing data values have not yet been inventoried.

Before implementation, propose a decision-ready change plan: what to inspect, schema/API/event migration boundaries, compatibility decisions, failure risks, verification, and explicit non-goals. Do not implement anything and do not assume which modules already exist.
