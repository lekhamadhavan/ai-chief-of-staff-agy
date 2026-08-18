from datetime import datetime, timezone
from typing import Dict, Any, List, Optional
import uuid

from cos_core.storage.store import DataStore
from cos_core.models.email import EmailItem, EmailTriageTier
from cos_core.models.workflow import ApprovalRequest, ActionType, ApprovalStatus
from cos_core.connectors.gmail import GmailConnectorAdapter
from cos_core.services.goals import GoalsService
from cos_core.services.contacts import ContactsService

class CommunicationTriageService:
    def __init__(self, store: Optional[DataStore] = None):
        self.store = store or DataStore()
        self.goals_service = GoalsService(store=self.store)
        self.contacts_service = ContactsService(store=self.store)
        self.gmail_connector = GmailConnectorAdapter(store=self.store)

    def classify_email(self, subject: str, body: str, sender: str) -> tuple[EmailTriageTier, str]:
        """Categorizes emails into Tier 1 (Respond Now), Tier 2 (Handle Today), or Tier 3 (FYI)."""
        active_goals = self.goals_service.get_active_goals()
        sub_lower = subject.lower()
        body_lower = body.lower()

        # Check for urgent/goal-aligned keywords
        is_urgent = any(kw in sub_lower or kw in body_lower for kw in ["urgent", "asap", "blocker", "critical", "approval", "meeting", "discussion"])
        goal_matched = False
        for g in active_goals:
            for word in g.title.lower().split():
                if len(word) > 3 and (word in sub_lower or word in body_lower):
                    goal_matched = True
                    break

        if is_urgent or (goal_matched and "urgent" in body_lower):
            return EmailTriageTier.TIER_1, "Urgent keyword or goal-blocking dependency detected."
        elif goal_matched:
            return EmailTriageTier.TIER_2, "Aligned with active strategic goals."
        else:
            return EmailTriageTier.TIER_3, "Informational message / lower priority."

    def perform_thread_message_audit(self, thread_id: str, sender_email: str) -> bool:
        """
        Audits message history for the thread.
        Returns True if thread has ALREADY been replied to by user (or has active pending draft).
        """
        profile = self.store.load_profile()
        state = self.store.load_workflow_state()

        # Check if user has already replied
        thread_details = self.gmail_connector.get_thread_details(thread_id)
        if thread_details and thread_details.messages:
            last_msg = thread_details.messages[-1]
            if last_msg.sender_email.lower() == profile.email.lower():
                return True  # User sent latest message

        # Check if there is already a pending approval for this thread
        for req in state.pending_approvals:
            if req.payload.get("thread_id") == thread_id and req.status == ApprovalStatus.PENDING:
                return True

        return False

    def draft_response(self, recipient_email: str, subject: str, original_body: str) -> str:
        profile = self.store.load_profile()
        style = profile.writing_style

        greeting = style.preferred_greetings[0] if style.preferred_greetings else "Hi"
        sign_off = style.sign_off or "Best,"

        body_lines = [
            f"{greeting},",
            "",
            f"Thank you for reaching out regarding '{subject}'.",
            "I have reviewed your message and will address this promptly.",
            "",
            sign_off,
            f"{profile.full_name}",
        ]
        return "\n".join(body_lines)

    def run_triage(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        profile = self.store.load_profile()
        state = self.store.load_workflow_state()

        # Fetch emails (live or cached)
        live_threads = self.gmail_connector.fetch_unread_threads(limit=50)

        processed_count = 0
        drafts_created = 0
        skipped_already_replied = 0

        triaged_items: List[EmailItem] = []
        tier_counts = {EmailTriageTier.TIER_1: 0, EmailTriageTier.TIER_2: 0, EmailTriageTier.TIER_3: 0}

        for th in live_threads:
            sender_email = th.latest_sender_email
            subject = th.subject
            body = th.messages[0].body if th.messages else ""
            thread_id = th.thread_id
            email_id = th.messages[0].message_id if th.messages else f"msg_{uuid.uuid4().hex[:6]}"

            # Contact Auto-Creation & Enrichment
            self.contacts_service.enrich_or_create_contact(
                email=sender_email,
                name=sender_email.split("<")[0].strip(),
                interaction_summary=f"Received email: {subject}",
                timestamp=now,
            )

            # Thread Message Audit
            if self.perform_thread_message_audit(thread_id, sender_email):
                skipped_already_replied += 1
                continue

            tier, rationale = self.classify_email(subject, body, sender_email)
            tier_counts[tier] += 1

            item = EmailItem(
                email_id=email_id,
                thread_id=thread_id,
                sender_email=sender_email,
                sender_name=sender_email.split("<")[0].strip(),
                recipient_emails=[profile.email],
                subject=subject,
                body_summary=body,
                received_at=now,
                triage_tier=tier,
                triage_rationale=rationale,
            )

            # Generate response draft for Tier 1 & Tier 2 emails
            if tier in (EmailTriageTier.TIER_1, EmailTriageTier.TIER_2):
                draft_text = self.draft_response(sender_email, subject, body)
                item.draft_response = draft_text
                item.draft_status = "pending_approval"

                # Stage Draft & Queue Approval Request
                approval_id = f"appr_{uuid.uuid4().hex[:8]}"
                appr_req = ApprovalRequest(
                    approval_id=approval_id,
                    action_type=ActionType.SEND_EMAIL,
                    target_summary=f"Send email response to {sender_email} regarding '{subject}'",
                    payload={
                        "thread_id": thread_id,
                        "recipient_email": sender_email,
                        "subject": f"Re: {subject}",
                        "draft_body": draft_text,
                        "draft_id": f"draft_{uuid.uuid4().hex[:6]}",
                    },
                    status=ApprovalStatus.PENDING,
                )
                state.pending_approvals.append(appr_req)
                drafts_created += 1

            triaged_items.append(item)
            processed_count += 1

        self.store.save_cached_emails(triaged_items)
        state.last_triage_at = now
        self.store.save_workflow_state(state)

        output_lines = [
            f"# 📥 Goal-Aligned Inbox Triage Summary",
            f"**Execution Timestamp**: {now.strftime('%Y-%m-%d %H:%M:%S UTC')}",
            f"**Total Emails Evaluated**: {len(live_threads)}",
            "",
            f"### 📊 Urgency Breakdown",
            f"- **[Tier 1 - Respond Now]**: {tier_counts[EmailTriageTier.TIER_1]} emails",
            f"- **[Tier 2 - Handle Today]**: {tier_counts[EmailTriageTier.TIER_2]} emails",
            f"- **[Tier 3 - FYI / Low Priority]**: {tier_counts[EmailTriageTier.TIER_3]} emails",
            "",
            f"### 📋 Actions & Approvals",
            f"- **Draft Responses Staged**: {drafts_created} (Pending Human Approval)",
            f"- **Already-Replied / Active Threads Skipped**: {skipped_already_replied}",
            f"- **Total Pending Approval Queue Items**: {len(state.pending_approvals)}",
        ]

        if triaged_items:
            output_lines.append("\n### ✉️ Triaged Communications List")
            for item in triaged_items:
                output_lines.append(f"- **[{item.triage_tier.value.upper()}]** From `{item.sender_email}`: *{item.subject}*")
                output_lines.append(f"  *Rationale*: {item.triage_rationale}")
                if item.draft_response:
                    output_lines.append(f"  *Staged Response Draft*: (Pending Approval `appr_{item.thread_id[:6]}`)")

        return {
            "timestamp": now.isoformat(),
            "output": "\n".join(output_lines),
            "processed": processed_count,
            "drafts_created": drafts_created,
            "skipped_replied": skipped_already_replied,
        }
