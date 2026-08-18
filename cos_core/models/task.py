from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field

class TaskStatus(str, Enum):
    PENDING = "Pending"
    IN_PROGRESS = "In Progress"
    BLOCKED = "Blocked"
    COMPLETED = "Completed"

class TaskPriorityTier(str, Enum):
    TIER_1 = "Tier 1"  # Urgent / Respond Now
    TIER_2 = "Tier 2"  # Today / Handle Today
    TIER_3 = "Tier 3"  # FYI / Low Priority

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
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    completed_at: Optional[datetime] = None
