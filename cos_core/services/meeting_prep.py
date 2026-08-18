from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from cos_core.storage.store import DataStore
from cos_core.connectors.calendar import GoogleCalendarConnectorAdapter
from cos_core.connectors.base import CalendarEventDTO
from cos_core.services.goals import GoalsService
from cos_core.services.tasks import TasksService
from cos_core.services.contacts import ContactsService

class MeetingPrepService:
    def __init__(self, store: Optional[DataStore] = None):
        self.store = store or DataStore()
        self.calendar_connector = GoogleCalendarConnectorAdapter(store=self.store)
        self.goals_service = GoalsService(store=self.store)
        self.tasks_service = TasksService(store=self.store)
        self.contacts_service = ContactsService(store=self.store)

    def is_eligible_meeting(self, event: CalendarEventDTO) -> bool:
        """
        Meeting Prep Eligibility Filter (FR-013a):
        Targets meetings with external attendees OR explicitly tagged as strategic.
        Suppresses internal 1:1s / routine syncs lacking strategic tags.
        """
        return event.is_external or event.is_strategic

    def generate_meeting_prep(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        start_range = now
        end_range = now + timedelta(days=1)  # Look ahead 24 hours

        events = self.calendar_connector.fetch_events(start_range, end_range)
        eligible_events = [evt for evt in events if self.is_eligible_meeting(evt)]

        active_goals = self.goals_service.get_active_goals()
        pending_tasks = self.tasks_service.get_pending_tasks()

        lines = []
        lines.append(f"# Executive Strategic Meeting Preparation Brief ({now.strftime('%Y-%m-%d')})")
        lines.append(f"Eligible Strategic Meetings: {len(eligible_events)}\n")

        if not eligible_events:
            lines.append("- No external or strategic meetings scheduled for the upcoming 24 hours.")
        else:
            for evt in eligible_events:
                lines.append(f"## 📌 Meeting: {evt.title}")
                lines.append(f"**Time**: {evt.start_time.strftime('%H:%M')} - {evt.end_time.strftime('%H:%M UTC')}")
                lines.append(f"**Location**: {evt.location or 'Online'}")
                lines.append(f"**Attendees**: {', '.join(evt.attendees) if evt.attendees else 'None specified'}\n")

                lines.append("### 👥 Attendee Context & Interaction History")
                for email in evt.attendees:
                    contact = self.contacts_service.store.load_contact(email)
                    if contact:
                        lines.append(f"- **{contact.full_name}** ({contact.email}): {contact.role_or_title or 'Executive Contact'}")
                        lines.append(f"  Notes: {contact.relationship_notes or 'No special relationship notes.'}")
                        if contact.interaction_history:
                            last_int = contact.interaction_history[-1]
                            lines.append(f"  Last Interaction ({last_int.timestamp.strftime('%Y-%m-%d')}): {last_int.summary}")
                    else:
                        lines.append(f"- **{email}**: External participant (contact auto-created)")
                lines.append("")

                lines.append("### 🎯 Governing Goals & Strategic Alignment")
                if active_goals:
                    top_g = active_goals[0]
                    lines.append(f"- Governing Strategic Goal: **{top_g.title}** ({top_g.description})")
                else:
                    lines.append("- No explicit governing goal mapped.")
                lines.append("")

                lines.append("### 📋 Open Commitments & Tasks")
                relevant_tasks = [t for t in pending_tasks if any(a.split('@')[0].lower() in t.title.lower() for a in evt.attendees)]
                if relevant_tasks:
                    for t in relevant_tasks:
                        lines.append(f"- Pending Task: [{t.status.value}] {t.title}")
                else:
                    lines.append("- No outstanding action items or open commitments flagged.")
                lines.append("")

                lines.append("### 💡 Recommended Talking Points & Desired Outcomes")
                lines.append("1. **Opening Alignment**: Re-confirm mutual objectives and timeframe.")
                lines.append("2. **Core Discussion**: Review progress against strategic deliverables.")
                lines.append("3. **Target Outcome**: Establish clear ownership and next steps before adjourning.")
                lines.append("-" * 60 + "\n")

        prep_text = "\n".join(lines)
        return {
            "timestamp": now.isoformat(),
            "output": prep_text,
            "eligible_meetings_count": len(eligible_events),
        }
