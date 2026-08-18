---
name: "cos-inbox-triage"
description: "Goal-aligned email triage into Tier 1/2/3 with Thread Audit, response draft staging, and human approval boundary verification."
---

# Inbox Triage Skill

## Execution Steps

1. Run the inbox triage orchestrator:
   ```bash
   python3 -m cos_core.orchestration.cli inbox-triage
   ```

2. **Antigravity AI Triage Synthesis**:
   Analyze the rendered triage summary (Tier 1/2/3 categorization, staged drafts, contact enrichments) and append an **"💡 Executive AI Triage Insights & Approval Actions"** section containing:
   
   - **🎯 Goal-Aligned Urgency Summary**: Flag high-impact Tier 1 (Respond Now) and Tier 2 (Handle Today) emails.
   - **✍️ Staged Draft Review**: Present staged response drafts awaiting human approval with single-click approval prompts (`Approve draft [ID]`).
   - **👤 Contact Enrichment Notes**: Highlight new contact records automatically created or updated in `cos-data/contacts/`.
