from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class EmailMessageDTO(BaseModel):
    message_id: str
    sender_email: str
    recipient_emails: List[str] = Field(default_factory=list)
    body: str
    timestamp: datetime

class EmailThreadDTO(BaseModel):
    thread_id: str
    subject: str
    messages: List[EmailMessageDTO] = Field(default_factory=list)
    last_message_at: datetime
    latest_sender_email: str
    is_unread: bool = True

class DraftResponseDTO(BaseModel):
    thread_id: str
    recipient_email: str
    subject: str
    body: str

class CalendarEventDTO(BaseModel):
    event_id: str
    title: str
    description: Optional[str] = None
    start_time: datetime
    end_time: datetime
    attendees: List[str] = Field(default_factory=list)
    location: Optional[str] = None
    is_external: bool = False
    is_strategic: bool = False

class ConnectorUnavailableError(Exception):
    """Raised when an external connector is unreachable or unauthenticated."""
    def __init__(self, connector_name: str, message: str = "Connector unavailable"):
        self.connector_name = connector_name
        self.message = message
        super().__init__(f"{connector_name} unavailable: {message}")

class IGmailConnector(ABC):
    @abstractmethod
    def fetch_unread_threads(self, limit: int = 50) -> List[EmailThreadDTO]:
        """Fetches unread email threads for triage."""
        pass

    @abstractmethod
    def get_thread_details(self, thread_id: str) -> Optional[EmailThreadDTO]:
        """Fetches full message history for Thread Message Audit."""
        pass

    @abstractmethod
    def create_draft(self, draft: DraftResponseDTO) -> str:
        """Stages a draft response in Gmail. Returns draft_id."""
        pass

    @abstractmethod
    def send_email(self, draft_id: str, approval_token: str) -> bool:
        """
        Sends an approved email draft.
        MUST fail if approval_token is invalid or absent.
        """
        pass

class IGoogleCalendarConnector(ABC):
    @abstractmethod
    def fetch_events(self, start_date: datetime, end_date: datetime) -> List[CalendarEventDTO]:
        """Fetches calendar events for specified date range."""
        pass

    @abstractmethod
    def get_event_details(self, event_id: str) -> Optional[CalendarEventDTO]:
        """Fetches detailed metadata for a specific calendar event."""
        pass

    @abstractmethod
    def check_availability(self, start_time: datetime, end_time: datetime) -> bool:
        """Verifies whether the user is free during the specified time slot."""
        pass
