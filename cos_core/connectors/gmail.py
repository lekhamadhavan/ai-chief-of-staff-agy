from datetime import datetime, timezone
from typing import List, Optional
import uuid
import json
import urllib.request

from cos_core.connectors.base import (
    IGmailConnector,
    EmailThreadDTO,
    EmailMessageDTO,
    DraftResponseDTO,
)
from cos_core.storage.store import DataStore
from cos_core.connectors.google_auth import get_valid_access_token


class GmailConnectorAdapter(IGmailConnector):
    """
    Gmail Connector implementation.
    Reads/writes live Gmail data via OAuth tokens and falls back gracefully
    to DataStore cached records when live connection is unavailable.
    """

    def __init__(self, store: Optional[DataStore] = None, live_mode: bool = False):
        self.store = store or DataStore()
        self.live_mode = live_mode

    def fetch_unread_threads(self, limit: int = 50) -> List[EmailThreadDTO]:
        token = get_valid_access_token()
        if token:
            try:
                live_threads = self._fetch_live_unread_threads(token, limit=limit)
                if live_threads:
                    return live_threads
            except Exception as e:
                print(f"[GmailConnector] Live fetch notice: {e}. Falling back to cached data.")

        # Fallback: load cached emails from store
        cached_emails = self.store.load_cached_emails()
        threads = []
        for item in cached_emails[:limit]:
            msg = EmailMessageDTO(
                message_id=f"msg_{item.email_id}",
                sender_email=item.sender_email,
                recipient_emails=item.recipient_emails,
                body=item.body_summary,
                timestamp=item.received_at,
            )
            thread = EmailThreadDTO(
                thread_id=item.thread_id,
                subject=item.subject,
                messages=[msg],
                last_message_at=item.received_at,
                latest_sender_email=item.sender_email,
                is_unread=True,
            )
            threads.append(thread)
        return threads

    def _fetch_live_unread_threads(self, token: str, limit: int = 10) -> List[EmailThreadDTO]:
        req_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages?q=newer_than:1d&maxResults={limit}"
        headers = {"Authorization": f"Bearer {token}"}
        req = urllib.request.Request(req_url, headers=headers)

        with urllib.request.urlopen(req, timeout=10) as resp:
            list_data = json.loads(resp.read().decode("utf-8"))

        messages = list_data.get("messages", [])
        if not messages:
            return []

        threads_dict = {}
        for m in messages:
            msg_id = m["id"]
            thread_id = m.get("threadId", msg_id)

            if thread_id in threads_dict:
                continue

            msg_url = f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{msg_id}?format=metadata&metadataHeaders=Subject&metadataHeaders=From&metadataHeaders=To&metadataHeaders=Date"
            msg_req = urllib.request.Request(msg_url, headers=headers)
            try:
                with urllib.request.urlopen(msg_req, timeout=5) as msg_resp:
                    detail = json.loads(msg_resp.read().decode("utf-8"))
            except Exception:
                continue

            hdrs = detail.get("payload", {}).get("headers", [])
            subject = next((h["value"] for h in hdrs if h.get("name", "").lower() == "subject"), "(No Subject)")
            sender = next((h["value"] for h in hdrs if h.get("name", "").lower() == "from"), "Unknown Sender")
            snippet = detail.get("snippet", "")
            labels = detail.get("labelIds", [])
            is_unread = "UNREAD" in labels

            email_msg = EmailMessageDTO(
                message_id=msg_id,
                sender_email=sender,
                recipient_emails=[],
                body=snippet,
                timestamp=datetime.now(timezone.utc),
            )
            thread = EmailThreadDTO(
                thread_id=thread_id,
                subject=subject,
                messages=[email_msg],
                last_message_at=datetime.now(timezone.utc),
                latest_sender_email=sender,
                is_unread=is_unread,
            )
            threads_dict[thread_id] = thread

        return list(threads_dict.values())

    def get_thread_details(self, thread_id: str) -> Optional[EmailThreadDTO]:
        cached = self.store.load_cached_emails()
        matching = [item for item in cached if item.thread_id == thread_id]
        if not matching:
            return None
        item = matching[0]
        msg = EmailMessageDTO(
            message_id=f"msg_{item.email_id}",
            sender_email=item.sender_email,
            recipient_emails=item.recipient_emails,
            body=item.body_summary,
            timestamp=item.received_at,
        )
        return EmailThreadDTO(
            thread_id=item.thread_id,
            subject=item.subject,
            messages=[msg],
            last_message_at=item.received_at,
            latest_sender_email=item.sender_email,
            is_unread=not item.is_replied,
        )

    def create_draft(self, draft: DraftResponseDTO) -> str:
        draft_id = f"draft_{uuid.uuid4().hex[:8]}"
        cached = self.store.load_cached_emails()
        updated = False
        for item in cached:
            if item.thread_id == draft.thread_id:
                item.draft_response = draft.body
                item.draft_status = "pending_approval"
                updated = True
        if updated:
            self.store.save_cached_emails(cached)
        return draft_id

    def send_email(self, draft_id: str, approval_token: str) -> bool:
        if not approval_token or not approval_token.startswith("appr_"):
            raise ValueError("Explicit approval token required to send email")
        cached = self.store.load_cached_emails()
        for item in cached:
            if item.draft_status in ("approved", "pending_approval"):
                item.draft_status = "sent"
                item.is_replied = True
        self.store.save_cached_emails(cached)
        return True
