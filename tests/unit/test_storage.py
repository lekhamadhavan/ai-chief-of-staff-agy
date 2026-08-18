import tempfile
from pathlib import Path
import pytest
from datetime import datetime, timezone

from cos_core.storage.store import DataStore
from cos_core.models.profile import UserProfile
from cos_core.models.goal import Goal, GoalPriority
from cos_core.models.task import Task, TaskStatus, TaskPriorityTier
from cos_core.models.contact import Contact, StalenessTier

def test_datastore_profile_roundtrip():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        profile = store.load_profile()
        assert profile.user_id == "default_user"
        
        profile.full_name = "Jane Executive"
        store.save_profile(profile)
        
        reloaded = store.load_profile()
        assert reloaded.full_name == "Jane Executive"

def test_datastore_tasks_lifecycle():
    with tempfile.TemporaryDirectory() as tmpdir:
        store = DataStore(data_dir=tmpdir)
        task = Task(
            task_id="t1",
            title="Review Q3 Strategy",
            status=TaskStatus.PENDING,
            priority_tier=TaskPriorityTier.TIER_1,
        )
        store.save_task(task)
        
        loaded = store.load_tasks()
        assert len(loaded) == 1
        assert loaded[0].status == TaskStatus.PENDING

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now(timezone.utc)
        store.save_task(task)

        reloaded = store.load_tasks()
        assert reloaded[0].status == TaskStatus.COMPLETED
        assert reloaded[0].completed_at is not None
