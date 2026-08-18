import tempfile
import pytest

from cos_core.storage.store import DataStore
from cos_core.models.email import EmailItem, EmailTriageTier
from cos_core.services.triage import CommunicationTriageService
from cos_core.orchestration.cli import approve_command

def test_human_approval_enforcement_for_email_sending():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        svc = CommunicationTriageService(store=store)

        email = EmailItem(
            email_id="e_urgent",
            thread_id="th_urgent",
            sender_email="client@acme.com",
            subject="Urgent contract review",
            body_summary="Need approval asap",
            triage_tier=EmailTriageTier.TIER_1,
        )
        store.save_cached_emails([email])

        svc.run_triage()
        state = store.load_workflow_state()
        assert len(state.pending_approvals) == 1
        appr_id = state.pending_approvals[0].approval_id

        # Verify email is not sent until approval command executed
        cached = store.load_cached_emails()
        assert cached[0].draft_status == "pending_approval"

        # Execute approval
        approve_command(store, appr_id)

        state_after = store.load_workflow_state()
        assert len(state_after.pending_approvals) == 0

        cached_after = store.load_cached_emails()
        assert cached_after[0].draft_status == "sent"
        assert cached_after[0].is_replied is True
