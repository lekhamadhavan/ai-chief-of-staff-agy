# Data Model & Schema Specification: AI Chief of Staff

**Feature Branch**: `001-ai-chief-of-staff` | **Date**: 2026-08-18 | **Spec**: [spec.md](spec.md)

## Overview

This document specifies the Pydantic v2 data models and YAML file schemas for the AI Chief of Staff (CoS) persistent storage layer in `cos-data/`.

---

## Data Schemas

### 1. UserProfile (`cos-data/profile.yaml`)

Represents executive preferences, working hours, communication rules, and hard boundary constraints.

```python
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class HardConstraintType(str, Enum):
    FOCUS_BLOCK = "focus_block"
    NON_WORKING_HOURS = "non_working_hours"
    MAX_DAILY_MEETINGS = "max_daily_meetings"
    BUFFER_TIME = "buffer_time"

class HardConstraint(BaseModel):
    constraint_id: str
    type: HardConstraintType
    description: str
    start_time: Optional[str] = None  # HH:MM format
    end_time: Optional[str] = None    # HH:MM format
    max_value: Optional[int] = None   # e.g., max 4 meeting hours

class WritingStyleRules(BaseModel):
    tone: str = "concise, direct, professional"
    preferred_greetings: List[str] = Field(default_factory=lambda: ["Hi", "Hello"])
    sign_off: str = "Best,"
    avoid_phrases: List[str] = Field(default_factory=list)

class UserProfile(BaseModel):
    user_id: str = "default_user"
    full_name: str
    email: str
    timezone: str = "UTC"
    working_hours_start: str = "09:00"
    working_hours_end: str = "17:00"
    hard_constraints: List[HardConstraint] = Field(default_factory=list)
    writing_style: WritingStyleRules = Field(default_factory=WritingStyleRules)
```

---

### 2. Goal (`cos-data/goals.yaml`)

Represents active and archived strategic objectives serving as the primary source of truth for prioritization.

```python
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class GoalPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Goal(BaseModel):
    goal_id: str
    title: str
    description: str
    category: str  # e.g., "Strategic", "Operational", "Personal"
    priority: GoalPriority = GoalPriority.HIGH
    target_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 3. Task (`cos-data/tasks.yaml`)

Represents actionable work items enforcing a strict 4-state lifecycle (`Pending`, `In Progress`, `Blocked`, `Completed`).

```python
from datetime import datetime
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    BLOCKED = "Blocked"
    COMPLETED = "Completed"

class TaskPriorityTier(str, Enum):
    TIER_1 = "Tier 1"  # Urgent / Immediate
    TIER_2 = "Tier 2"  # Today
    TIER_3 = "Tier 3"  # Low / Someday

class Task(BaseModel):
    task_id: str
    title: str
    description: Optional[str] = None
    status: TaskStatus = TaskStatus.PENDING
    priority_tier: TaskPriorityTier = TaskPriorityTier.TIER_2
    goal_id: Optional[str] = None
    due_date: Optional[datetime] = None
    estimated_duration_minutes: int = 30
    origin_source: str = "manual"  # "gmail", "calendar", "briefing", "manual"
    origin_reference_id: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
```

---

### 4. Contact (`cos-data/contacts/<email_hash>.yaml`)

Durable representation of a professional relationship with interaction log and staleness tracking.

```python
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class StalenessTier(str, Enum):
    TIER_1 = "14_days"  # Alert after 14 days
    TIER_2 = "30_days"  # Alert after 30 days
    TIER_3 = "60_days"  # Alert after 60 days

class InteractionType(str, Enum):
    EMAIL_RECEIVED = "email_received"
    EMAIL_SENT = "email_sent"
    MEETING = "meeting"

class InteractionLog(BaseModel):
    interaction_id: str
    type: InteractionType
    timestamp: datetime
    summary: str
    reference_id: Optional[str] = None

class Contact(BaseModel):
    contact_id: str
    email: str
    full_name: str
    role_or_title: Optional[str] = None
    organization: Optional[str] = None
    staleness_tier: StalenessTier = StalenessTier.TIER_1
    relevant_goal_ids: List[str] = Field(default_factory=list)
    relationship_notes: Optional[str] = None
    last_interaction_at: Optional[datetime] = None
    interaction_history: List[InteractionLog] = Field(default_factory=list)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
```

---

### 5. EmailItem & Triage (`cos-data/cache/email_items.yaml`)

Represents Gmail threads categorized into triage tiers (Tier 1, Tier 2, Tier 3).

```python
from datetime import datetime
from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class EmailTriageTier(str, Enum):
    TIER_1 = "Tier 1: Respond Now"
    TIER_2 = "Tier 2: Handle Today"
    TIER_3 = "Tier 3: FYI / Low Priority"

class EmailItem(BaseModel):
    email_id: str
    thread_id: str
    sender_email: str
    sender_name: Optional[str] = None
    recipient_emails: List[str] = Field(default_factory=list)
    subject: str
    body_summary: str
    received_at: datetime
    triage_tier: EmailTriageTier
    triage_rationale: str
    is_replied: bool = False
    draft_response: Optional[str] = None
    draft_status: str = "none"  # "none", "pending_approval", "approved", "sent"
```

---

### 6. CalendarEvent (`cos-data/cache/calendar_events.yaml`)

Represents Google Calendar events for briefing and prep evaluation.

```python
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class CalendarEvent(BaseModel):
    event_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    location: Optional[str] = None
    attendee_emails: List[str] = Field(default_factory=list)
    is_external: bool = False
    is_strategic: bool = False
    meeting_prep_generated: bool = False
```

---

### 7. WorkflowState & ApprovalRequest (`cos-data/workflow_state.yaml`)

Stores workflow run timestamp cursors and pending human approval requests.

```python
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field

class ActionType(str, Enum):
    SEND_EMAIL = "send_email"
    UPDATE_CALENDAR = "update_calendar"

class ApprovalStatus(str, Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"

class ApprovalRequest(BaseModel):
    approval_id: str
    action_type: ActionType
    target_summary: str
    payload: Dict[str, Any]
    status: ApprovalStatus = ApprovalStatus.PENDING
    created_at: datetime = Field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None

class WorkflowState(BaseModel):
    last_triage_at: Optional[datetime] = None
    last_morning_brief_at: Optional[datetime] = None
    last_weekly_brief_at: Optional[datetime] = None
    last_contact_enrichment_at: Optional[datetime] = None
    pending_approvals: List[ApprovalRequest] = Field(default_factory=list)
    active_workflow_name: Optional[str] = None
```
