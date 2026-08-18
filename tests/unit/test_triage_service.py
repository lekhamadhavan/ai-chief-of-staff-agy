import tempfile
from datetime import datetime, timezone
import pytest

from cos_core.storage.store import DataStore
from cos_core.models.email import EmailItem, EmailTriageTier
from cos_core.services.triage import CommunicationTriageService

def test_triage_classification():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        svc = CommunicationTriageService(store=store)

        tier, rationale = svc.classify_email("URGENT: Server Down", "Immediate action needed", "ops@co.com")
        assert tier == EmailTriageTier.TIER_1

        tier_fyi, _ = svc.classify_email("Weekly Newsletter", "Here is your update", "news@co.com")
        assert tier_fyi == EmailTriageTier.TIER_3

def test_thread_message_audit_prevents_duplicate_drafts():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        svc = CommunicationTriageService(store=store)

        email = EmailItem(
            email_id="e1",
            thread_id="th1",
            sender_email="partner@org.com",
            subject="Urgent Proposal",
            body_summary="Please review urgent proposal",
            triage_tier=EmailTriageTier.TIER_1,
        )
        store.save_cached_emails([email])

        res = svc.run_triage()
        assert res["drafts_created"] == 1

        # Second triage run should recognize pending approval for thread and skip duplicate draft creation
        res2 = svc.run_triage()
        assert res2["drafts_created"] == 0
        assert res2["skipped_replied"] == 1
