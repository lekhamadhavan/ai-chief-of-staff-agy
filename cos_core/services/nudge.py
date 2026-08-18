from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from cos_core.storage.store import DataStore
from cos_core.models.profile import HardConstraintType
from cos_core.connectors.calendar import GoogleCalendarConnectorAdapter
from cos_core.services.tasks import TasksService
from cos_core.services.contacts import ContactsService

class NudgeService:
    def __init__(self, store: Optional[DataStore] = None):
        self.store = store or DataStore()
        self.calendar_connector = GoogleCalendarConnectorAdapter(store=self.store)
        self.tasks_service = TasksService(store=self.store)
        self.contacts_service = ContactsService(store=self.store)

    def evaluate_hard_constraints(self) -> List[Dict[str, str]]:
        """Evaluates focus blocks, non-working hours, and meeting caps against hard constraints."""
        profile = self.store.load_profile()
        now = datetime.now(timezone.utc)
        start_of_day = now.replace(hour=0, minute=0, second=0)
        end_of_day = now.replace(hour=23, minute=59, second=59)

        events = self.calendar_connector.fetch_events(start_of_day, end_of_day)
        violations = []

        total_meeting_hours = sum((e.end_time - e.start_time).total_seconds() / 3600.0 for e in events)

        for c in profile.hard_constraints:
            if c.type == HardConstraintType.MAX_DAILY_MEETINGS and c.max_value:
                if total_meeting_hours > c.max_value:
                    violations.append({
                        "constraint_id": c.constraint_id,
                        "type": c.type.value,
                        "message": f"Daily meeting cap exceeded: {total_meeting_hours:.1f} hours scheduled vs max {c.max_value} hours allowed.",
                    })
            elif c.type == HardConstraintType.NON_WORKING_HOURS:
                for evt in events:
                    if evt.start_time.strftime("%H:%M") < profile.working_hours_start or evt.end_time.strftime("%H:%M") > profile.working_hours_end:
                        violations.append({
                            "constraint_id": c.constraint_id,
                            "type": c.type.value,
                            "message": f"Meeting '{evt.title}' scheduled outside working hours ({profile.working_hours_start}-{profile.working_hours_end}).",
                        })

        return violations

    def generate_proactive_nudges(self) -> List[Dict[str, str]]:
        now = datetime.now(timezone.utc)
        pending_tasks = self.tasks_service.get_pending_tasks()
        nudges = []

        # Check approaching deadlines
        for t in pending_tasks:
            if t.due_date:
                due_in = (t.due_date.astimezone(timezone.utc) - now).total_seconds() / 3600.0
                if 0 < due_in <= 24:
                    nudges.append({
                        "type": "task_deadline",
                        "message": f"Task '{t.title}' is due in {due_in:.1f} hours.",
                    })

        # Check hard constraint violations
        violations = self.evaluate_hard_constraints()
        for v in violations:
            nudges.append({
                "type": "hard_constraint_violation",
                "message": v["message"],
            })

        return nudges
