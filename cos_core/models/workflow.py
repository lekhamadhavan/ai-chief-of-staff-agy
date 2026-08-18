from datetime import datetime, timezone
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    resolved_at: Optional[datetime] = None

class WorkflowState(BaseModel):
    last_triage_at: Optional[datetime] = None
    last_morning_brief_at: Optional[datetime] = None
    last_weekly_brief_at: Optional[datetime] = None
    last_contact_enrichment_at: Optional[datetime] = None
    pending_approvals: List[ApprovalRequest] = Field(default_factory=list)
    active_workflow_name: Optional[str] = None
