from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class GoalPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"

class Goal(BaseModel):
    goal_id: str
    title: str
    description: str
    category: str = "Strategic"  # e.g., "Strategic", "Operational", "Personal"
    priority: GoalPriority = GoalPriority.HIGH
    target_date: Optional[datetime] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
