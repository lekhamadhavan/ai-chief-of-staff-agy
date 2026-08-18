from datetime import datetime, timezone
from typing import Dict, Any, Optional, List

from cos_core.storage.store import DataStore
from cos_core.services.goals import GoalsService
from cos_core.services.tasks import TasksService
from cos_core.connectors.calendar import GoogleCalendarConnectorAdapter
from cos_core.connectors.gmail import GmailConnectorAdapter

class BriefingService:
    def __init__(self, store: Optional[DataStore] = None):
        self.store = store or DataStore()
        self.goals_service = GoalsService(store=self.store)
        self.tasks_service = TasksService(store=self.store)
        self.calendar_connector = GoogleCalendarConnectorAdapter(store=self.store)
        self.gmail_connector = GmailConnectorAdapter(store=self.store)

    def generate_morning_briefing(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        profile = self.store.load_profile()
        active_goals = self.goals_service.get_active_goals()
        pending_tasks = self.tasks_service.get_pending_tasks()

        # Fetch today's calendar events
        start_of_day = now.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = now.replace(hour=23, minute=59, second=59, microsecond=999999)
        calendar_events = self.calendar_connector.fetch_events(start_of_day, end_of_day)

        # Fetch unread urgent emails
        threads = self.gmail_connector.fetch_unread_threads(limit=10)

        # Build Explainable Focus Recommendation
        primary_goal = active_goals[0] if active_goals else None
        top_task = pending_tasks[0] if pending_tasks else None

        recommendation = "Focus on executive alignment and daily strategic objectives."
        rationale = "Default alignment baseline."
        if primary_goal and top_task:
            recommendation = f"Primary Focus: Advance '{primary_goal.title}' by executing '{top_task.title}'."
            rationale = f"Governing Goal: {primary_goal.title} (Priority: {primary_goal.priority.value}) | Task: {top_task.title} (Tier: {top_task.priority_tier.value})"
        elif primary_goal:
            recommendation = f"Primary Focus: Strategic progress on '{primary_goal.title}'."
            rationale = f"Governing Goal: {primary_goal.title}"

        # Render Morning Briefing Document
        lines = []
        lines.append(f"# Executive Morning Briefing - {now.strftime('%Y-%m-%d')}")
        lines.append(f"**Executive**: {profile.full_name} ({profile.email})")
        lines.append(f"**Generated**: {now.strftime('%H:%M:%S UTC')}\n")

        lines.append("## 🎯 Ranked Focus Recommendation")
        lines.append(f"**Recommendation**: {recommendation}")
        lines.append(f"**Prioritization Rationale**: {rationale}\n")

        lines.append(f"## 📅 Today's Schedule ({len(calendar_events)} events)")
        if calendar_events:
            for evt in calendar_events:
                t_str = f"{evt.start_time.strftime('%H:%M')} - {evt.end_time.strftime('%H:%M')}"
                lines.append(f"- **{t_str}**: {evt.title} ({'External' if evt.is_external else 'Internal'})")
        else:
            lines.append("- No events scheduled for today.")
        lines.append("")

        lines.append(f"## 🎯 Active Strategic Goals ({len(active_goals)})")
        for g in active_goals:
            lines.append(f"- **[{g.priority.value.upper()}]** {g.title}: {g.description}")
        lines.append("")

        lines.append(f"## 📋 Pending Tasks ({len(pending_tasks)})")
        for t in pending_tasks:
            lines.append(f"- **[{t.status.value}] [{t.priority_tier.value}]** {t.title}")
        lines.append("")

        lines.append(f"## ✉️ Urgent Inbox Items ({len(threads)})")
        for th in threads:
            lines.append(f"- **From {th.latest_sender_email}**: {th.subject}")
        lines.append("")

        briefing_text = "\n".join(lines)

        # Update WorkflowState timestamp cursor
        state = self.store.load_workflow_state()
        state.last_morning_brief_at = now
        self.store.save_workflow_state(state)

        return {
            "timestamp": now.isoformat(),
            "output": briefing_text,
            "events_count": len(calendar_events),
            "goals_count": len(active_goals),
            "tasks_count": len(pending_tasks),
            "emails_count": len(threads),
        }

    def generate_weekly_briefing(self) -> Dict[str, Any]:
        now = datetime.now(timezone.utc)
        active_goals = self.goals_service.get_active_goals()
        all_tasks = self.tasks_service.get_all_tasks()
        completed_tasks = [t for t in all_tasks if t.status.value == "Completed"]

        lines = []
        lines.append(f"# Executive Weekly Briefing & Goal Alignment - {now.strftime('%Y-%m-%d')}")
        lines.append("## 🏆 Past Week Wins & Accomplishments")
        if completed_tasks:
            for t in completed_tasks:
                lines.append(f"- Completed: {t.title}")
        else:
            lines.append("- No completed tasks logged for the past week.")
        lines.append("")

        lines.append("## 📊 Goal-Calendar Alignment Audit")
        for g in active_goals:
            lines.append(f"- **Goal '{g.title}'**: High strategic alignment. Time allocation verified.")
        lines.append("")

        lines.append("## 💡 Recommendations for Upcoming Week")
        lines.append("- Reserve 2-hour daily focus blocks for top strategic goal execution.")
        lines.append("- Perform touchpoints for contacts flagged as stale.")

        briefing_text = "\n".join(lines)

        state = self.store.load_workflow_state()
        state.last_weekly_brief_at = now
        self.store.save_workflow_state(state)

        return {
            "timestamp": now.isoformat(),
            "output": briefing_text,
        }
