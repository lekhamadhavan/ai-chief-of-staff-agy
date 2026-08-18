---
name: "cos-relationship-management"
description: "Audit contact interaction history, contact enrichment, and staleness tiers."
---

# Relationship Management Skill

## Execution
Run relationship staleness audit:
```bash
python3 -m cos_core.orchestration.cli relationship-audit
```
Report stale contact records (14d, 30d, 60d thresholds) and suggest proactive touchpoints.
