---
description: Create an active workflow plan and sibling run directory from approved context without starting the workflow loop
---
Use the approved planning context already present in this conversation as the canonical handoff text.

Behavior:

- do not summarize or compress the approved context before delegation
- delegate to `launch` using the approved context from the current conversation, preserving it as literally as possible in `planning-handoff.md`
- check if launch agent create `plans/`, `plans/active/`, and `plans/archive/` if needed
- do not create `workflow-session.json`
- do not start `workflow`
- do not run `implementation`, `review`, or `analysis`

When you stop, report the plan path, run directory, `planning-handoff.md` path if created
