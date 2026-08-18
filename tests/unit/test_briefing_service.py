import tempfile
from datetime import datetime, timezone
import pytest

from cos_core.storage.store import DataStore
from cos_core.models.goal import Goal, GoalPriority
from cos_core.models.task import Task, TaskStatus, TaskPriorityTier
from cos_core.services.briefing import BriefingService

def test_morning_briefing_generation():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        goal = Goal(goal_id="g1", title="Expand Enterprise Sales", description="Reach 50 ARR", priority=GoalPriority.HIGH)
        task = Task(task_id="t1", title="Prepare Pitch Deck", priority_tier=TaskPriorityTier.TIER_1)
        store.save_goal(goal)
        store.save_task(task)

        svc = BriefingService(store=store)
        res = svc.generate_morning_briefing()

        assert res["goals_count"] == 1
        assert res["tasks_count"] == 1
        assert "Expand Enterprise Sales" in res["output"]
        assert "Prepare Pitch Deck" in res["output"]

        # Verify cursor update
        state = store.load_workflow_state()
        assert state.last_morning_brief_at is not None
