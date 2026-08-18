import tempfile
from datetime import datetime, timezone, timedelta
import pytest

from cos_core.storage.store import DataStore
from cos_core.models.contact import Contact, StalenessTier
from cos_core.services.contacts import ContactsService

def test_contact_auto_creation_and_enrichment():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        svc = ContactsService(store=store)

        contact = svc.enrich_or_create_contact(
            email="newpartner@acme.com",
            name="New Partner",
            interaction_summary="Received introductory email",
        )
        assert contact.email == "newpartner@acme.com"
        assert contact.full_name == "New Partner"
        assert len(contact.interaction_history) == 1

        reloaded = store.load_contact("newpartner@acme.com")
        assert reloaded is not None
        assert reloaded.full_name == "New Partner"

def test_relationship_staleness_calculation():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        svc = ContactsService(store=store)

        now = datetime.now(timezone.utc)
        stale_date = now - timedelta(days=20)

        c = Contact(
            contact_id="c1",
            email="oldfriend@co.com",
            full_name="Old Friend",
            staleness_tier=StalenessTier.TIER_1,  # 14 days threshold
            last_interaction_at=stale_date,
        )
        store.save_contact(c)

        is_stale, days = svc.check_staleness(c)
        assert is_stale is True
        assert days >= 19

        audit_res = svc.run_staleness_audit()
        assert audit_res["stale_count"] == 1
        assert "Old Friend" in audit_res["output"]
