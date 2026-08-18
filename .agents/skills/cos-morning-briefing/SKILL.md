---
name: "cos-morning-briefing"
description: "Generate executive morning briefing incorporating calendar, goals, tasks, and email triage with AI Strategic Insights."
---

# Executive Morning Briefing Skill

## Execution Steps

1. Run the morning briefing service orchestrator:
   ```bash
   python3 -m cos_core.orchestration.cli morning-briefing
   ```

2. **Antigravity AI Strategic Synthesis**:
   Analyze the rendered briefing data (Schedule, Goals, Tasks, Live Urgent Emails) and append an **"💡 Executive AI Strategic Insights & Actions"** section containing:
   
   - **📧 Email Action Analysis**: Identify urgent emails that align with active strategic goals and suggest concrete draft responses or next steps.
   - **📅 Schedule & Focus Optimization**: Check today's schedule density and recommend reserving dedicated focus blocks for Tier 1 tasks when calendar availability permits.
   - **⚡ Immediate Action Prompts**: Provide up to 3 single-click natural language prompts the executive can run (e.g. *"Draft response to [Sender]"*, *"Block 2 hours for [Task]"*).
