# Connector Contracts & Interface Specifications

**Feature Branch**: `001-ai-chief-of-staff` | **Date**: 2026-08-18 | **Spec**: [spec.md](../spec.md)

## Overview

This contract specification defines the source-agnostic abstract connector interfaces for Gmail and Google Calendar. Domain services in `cos_core/services/` interact exclusively through these interfaces, keeping core Chief of Staff logic completely insulated from specific Model Context Protocol (MCP) tool names or API SDK details.

---

## Connector Architecture

```text
[ CoS Domain Services ]
   ├── BriefingService
   ├── InboxTriageService
   ├── MeetingPrepService
   └── ContactService
           │
           ▼
[ Connector Interfaces (cos_core/connectors/base.py) ]
   ├── IGmailConnector
   └── IGoogleCalendarConnector
           │
           ▼
[ Adapters / MCP Bridge (cos_core/connectors/) ]
   ├── GmailMCPAdapter <──> Gmail MCP Server / API
   └── GoogleCalendarMCPAdapter <──> Google Calendar MCP Server / API
```

---

## 1. IGmailConnector Interface Contract

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class EmailThreadDTO(BaseModel):
    thread_id: str
    subject: str
    messages: List[dict]  # [{message_id, sender_email, recipient_emails, body, timestamp}]
    last_message_at: datetime
    latest_sender_email: str
    is_unread: bool

class DraftResponseDTO(BaseModel):
    thread_id: str
    recipient_email: str
    subject: str
    body: str

class IGmailConnector(ABC):
    @abstractmethod
    def fetch_unread_threads(self, limit: int = 50) -> List[EmailThreadDTO]:
        """Fetches unread email threads for triage."""
        pass

    @abstractmethod
    def get_thread_details(self, thread_id: str) -> Optional[EmailThreadDTO]:
        """Fetches full message history for a specific thread (Thread Message Audit)."""
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
```

---

## 2. IGoogleCalendarConnector Interface Contract

```python
from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel

class CalendarEventDTO(BaseModel):
    event_id: str
    title: str
    description: Optional[str]
    start_time: datetime
    end_time: datetime
    attendees: List[str]
    location: Optional[str]
    is_external: bool
    is_strategic: bool

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
```

---

## 3. Human Approval Boundary Contract

All actions that mutate external systems (such as sending an email or creating a meeting) require an explicit `ApprovalRequest` payload:

```json
{
  "approval_id": "appr_20260818_001",
  "action_type": "send_email",
  "target_summary": "Send response email to alex@partner.com re: Strategic Partnership",
  "payload": {
    "draft_id": "draft_9921",
    "recipient_email": "alex@partner.com",
    "subject": "Re: Strategic Partnership",
    "body_preview": "Hi Alex,\n\nThanks for reaching out..."
  },
  "status": "pending",
  "created_at": "2026-08-18T10:35:00Z"
}
```

- Executing `cos-cli approve --id appr_20260818_001` converts `status` to `approved` and passes the approval token to `send_email()`.
- Executing `cos-cli reject --id appr_20260818_001` converts `status` to `rejected` and purges the draft.

---

## 4. Degraded-Mode Failure Contract

If an MCP connector call fails due to authentication or network error:
1. Connector catches Exception and raises `ConnectorUnavailableError(connector_name="Gmail")`.
2. Service catches error, switches to `Cached Degraded Mode`.
3. Service loads fallback data from `cos-data/cache/`.
4. Output payload includes a `warnings` section:
   ```json
   {
     "degraded_mode": true,
     "warning": "Gmail connector unavailable. Briefing generated using cached data."
   }
   ```
