import tempfile
import pytest
from datetime import datetime, timezone

from cos_core.storage.store import DataStore
from cos_core.models.email import EmailItem, EmailTriageTier
from cos_core.connectors.gmail import GmailConnectorAdapter
from cos_core.connectors.calendar import GoogleCalendarConnectorAdapter

def test_gmail_connector_degraded_mode():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        email = EmailItem(
            email_id="e1",
            thread_id="th1",
            sender_email="alex@partner.com",
            subject="Partnership Discussion",
            body_summary="Let's align on Q4 targets.",
            triage_tier=EmailTriageTier.TIER_1,
        )
        store.save_cached_emails([email])

        adapter = GmailConnectorAdapter(store=store)
        threads = adapter.fetch_unread_threads()
        assert len(threads) == 1
        assert threads[0].subject == "Partnership Discussion"

def test_gmail_send_approval_token_required():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        adapter = GmailConnectorAdapter(store=store)
        
        with pytest.raises(ValueError, match="Explicit approval token required"):
            adapter.send_email("draft_123", approval_token="")
