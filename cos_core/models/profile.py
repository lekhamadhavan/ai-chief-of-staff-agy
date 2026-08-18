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
    start_time: Optional[str] = None  # HH:MM format e.g. "09:00"
    end_time: Optional[str] = None    # HH:MM format e.g. "17:00"
    max_value: Optional[int] = None   # e.g., max 4 meeting hours per day

class WritingStyleRules(BaseModel):
    tone: str = "concise, direct, professional"
    preferred_greetings: List[str] = Field(default_factory=lambda: ["Hi", "Hello"])
    sign_off: str = "Best,"
    avoid_phrases: List[str] = Field(default_factory=list)

class UserProfile(BaseModel):
    user_id: str = "default_user"
    full_name: str = "Executive User"
    email: str = "user@example.com"
    timezone: str = "UTC"
    working_hours_start: str = "09:00"
    working_hours_end: str = "17:00"
    hard_constraints: List[HardConstraint] = Field(default_factory=list)
    writing_style: WritingStyleRules = Field(default_factory=WritingStyleRules)
