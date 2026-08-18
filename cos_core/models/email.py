from datetime import datetime, timezone
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
    received_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    triage_tier: EmailTriageTier = EmailTriageTier.TIER_3
    triage_rationale: str = "Unprocessed"
    is_replied: bool = False
    draft_response: Optional[str] = None
    draft_status: str = "none"  # "none", "pending_approval", "approved", "sent"
