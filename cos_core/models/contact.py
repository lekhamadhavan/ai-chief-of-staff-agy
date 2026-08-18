from datetime import datetime, timezone
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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
