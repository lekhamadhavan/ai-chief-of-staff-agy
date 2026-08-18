from datetime import datetime, timezone
from typing import List, Optional, Dict, Any
import hashlib

from cos_core.models.contact import Contact, InteractionLog, InteractionType, StalenessTier
from cos_core.storage.store import DataStore

class ContactsService:
    def __init__(self, store: Optional[DataStore] = None):
        self.store = store or DataStore()

    def enrich_or_create_contact(
        self,
        email: str,
        name: Optional[str] = None,
        interaction_summary: str = "Interaction logged",
        timestamp: Optional[datetime] = None,
    ) -> Contact:
        ts = timestamp or datetime.now(timezone.utc)
        contact = self.store.load_contact(email)

        if not contact:
            # Auto-create new contact record
            contact_id = f"c_{hashlib.md5(email.lower().encode('utf-8')).hexdigest()[:8]}"
            contact = Contact(
                contact_id=contact_id,
                email=email.lower().strip(),
                full_name=name or email.split("@")[0].capitalize(),
                staleness_tier=StalenessTier.TIER_1,
                last_interaction_at=ts,
            )

        # Update last interaction and log entry
        contact.last_interaction_at = ts
        log_entry = InteractionLog(
            interaction_id=f"int_{hashlib.md5(f'{email}{ts.isoformat()}'.encode('utf-8')).hexdigest()[:8]}",
            type=InteractionType.EMAIL_RECEIVED,
            timestamp=ts,
            summary=interaction_summary,
        )
        contact.interaction_history.append(log_entry)
        contact.updated_at = datetime.now(timezone.utc)

        self.store.save_contact(contact)
        return contact

    def check_staleness(self, contact: Contact) -> tuple[bool, int]:
        if not contact.last_interaction_at:
            return True, 999
        
        now = datetime.now(timezone.utc)
        last_ts = contact.last_interaction_at.astimezone(timezone.utc) if contact.last_interaction_at.tzinfo else contact.last_interaction_at.replace(tzinfo=timezone.utc)
        days_inactive = (now - last_ts).days

        thresholds = {
            StalenessTier.TIER_1: 14,
            StalenessTier.TIER_2: 30,
            StalenessTier.TIER_3: 60,
        }
        max_days = thresholds.get(contact.staleness_tier, 14)
        return days_inactive >= max_days, days_inactive

    def run_staleness_audit(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        contacts = self.store.load_contacts()
        stale_contacts = []

        for c in contacts:
            is_stale, days = self.check_staleness(c)
            if is_stale:
                stale_contacts.append((c, days))

        lines = []
        lines.append(f"=== Relationship Staleness Audit ({now.strftime('%Y-%m-%d')}) ===")
        lines.append(f"Total Contacts Evaluated: {len(contacts)}")
        lines.append(f"Stale Contacts Flagged: {len(stale_contacts)}\n")

        for c, days in stale_contacts:
            lines.append(f"- **{c.full_name}** ({c.email})")
            lines.append(f"  Inactive: {days} days (Threshold: {c.staleness_tier.value})")
            lines.append(f"  Suggested Touchpoint: Send catch-up email regarding shared strategic goals.")

        state = self.store.load_workflow_state()
        state.last_contact_enrichment_at = now
        self.store.save_workflow_state(state)

        return {
            "timestamp": now.isoformat(),
            "output": "\n".join(lines),
            "stale_count": len(stale_contacts),
        }
