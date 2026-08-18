from datetime import datetime, timezone, timedelta
from typing import Dict, Any, List, Optional

from cos_core.storage.store import DataStore
from cos_core.connectors.calendar import GoogleCalendarConnectorAdapter
from cos_core.services.goals import GoalsService

class CalendarAnalysisService:
    def __init__(self, store: Optional[DataStore] = None):
        self.store = store or DataStore()
        self.calendar_connector = GoogleCalendarConnectorAdapter(store=self.store)
        self.goals_service = GoalsService(store=self.store)

    def analyze_goal_alignment(self, days: int = 7) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        start_date = now - timedelta(days=days)
        events = self.calendar_connector.fetch_events(start_date, now)
        active_goals = self.goals_service.get_active_goals()

        goal_time_allocation: Dict[str, float] = {g.title: 0.0 for g in active_goals}
        unaligned_hours = 0.0

        for evt in events:
            duration_hours = (evt.end_time - evt.start_time).total_seconds() / 3600.0
            title_lower = evt.title.lower()
            matched = False
            for g in active_goals:
                if any(w in title_lower for w in g.title.lower().split() if len(w) > 3):
                    goal_time_allocation[g.title] += duration_hours
                    matched = True
                    break
            if not matched:
                unaligned_hours += duration_hours

        return {
            "period_days": days,
            "total_events": len(events),
            "goal_hours": goal_time_allocation,
            "unaligned_hours": round(unaligned_hours, 1),
        }
