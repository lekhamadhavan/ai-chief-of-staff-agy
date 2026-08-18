import tempfile
from datetime import datetime, timezone, timedelta
import pytest

from cos_core.storage.store import DataStore
from cos_core.models.profile import UserProfile, HardConstraint, HardConstraintType
from cos_core.models.calendar import CalendarEvent
from cos_core.services.nudge import NudgeService

def test_hard_constraint_evaluation():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        profile = store.load_profile()
        profile.hard_constraints.append(
            HardConstraint(
                constraint_id="c_cap",
                type=HardConstraintType.MAX_DAILY_MEETINGS,
                description="Max 2 hours of meetings per day",
                max_value=2,
            )
        )
        store.save_profile(profile)

        now = datetime.now(timezone.utc)
        # Create 3-hour meeting
        evt = CalendarEvent(
            event_id="e_heavy",
            title="Heavy All-Hands",
            start_time=now.replace(hour=10, minute=0),
            end_time=now.replace(hour=13, minute=0),
        )
        store.save_cached_events([evt])

        nudge_svc = NudgeService(store=store)
        violations = nudge_svc.evaluate_hard_constraints()

        assert len(violations) == 1
        assert "Daily meeting cap exceeded" in violations[0]["message"]


def test_generate_proactive_nudges():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        nudge_svc = NudgeService(store=store)
        nudges = nudge_svc.generate_proactive_nudges()
        assert isinstance(nudges, list)

