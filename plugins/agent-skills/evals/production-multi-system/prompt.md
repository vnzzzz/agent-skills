---
max_turns: 10
allowed_tools: [Skill]
---

Our production checkout API has returned intermittent HTTP 502 responses for the last 25 minutes. Users in two regions are affected. The API's application logs show no corresponding exceptions, but the ingress proxy logs contain `upstream connect timeout`. A shared network policy was updated shortly before the failures; there is not yet evidence that the change caused them. The payment provider status page reports no incident.

Investigate the most plausible failure domains, what to check first, and what safe mitigation/recovery confirmation looks like. This is an active user-impacting outage. Please help with diagnosis; do not assume an incident commander role or execute any operation.
