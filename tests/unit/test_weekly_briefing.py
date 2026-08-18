import tempfile
import pytest
from datetime import datetime, timezone

from cos_core.storage.store import DataStore
from cos_core.services.briefing import BriefingService
from cos_core.services.calendar_analysis import CalendarAnalysisService

def test_weekly_briefing_generation_and_calendar_analysis():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        brief_svc = BriefingService(store=store)
        res = brief_svc.generate_weekly_briefing()

        assert "Past Week Wins & Accomplishments" in res["output"]
        assert "Goal-Calendar Alignment Audit" in res["output"]

        state = store.load_workflow_state()
        assert state.last_weekly_brief_at is not None

        analysis_svc = CalendarAnalysisService(store=store)
        analysis_res = analysis_svc.analyze_goal_alignment(days=7)
        assert "goal_hours" in analysis_res
