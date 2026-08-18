from datetime import datetime, timezone
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
