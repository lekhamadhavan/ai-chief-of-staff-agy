from datetime import datetime, timezone
from typing import List, Optional
from cos_core.models.task import Task, TaskStatus, TaskPriorityTier
from cos_core.storage.store import DataStore

class TasksService:
    def __init__(self, store: Optional[DataStore] = None):
        self.store = store or DataStore()

    def get_all_tasks(self) -> List[Task]:
        return self.store.load_tasks()

    def get_pending_tasks(self) -> List[Task]:
        tasks = self.store.load_tasks()
        return [t for t in tasks if t.status in (TaskStatus.PENDING, TaskStatus.IN_PROGRESS, TaskStatus.BLOCKED)]

    def create_task(self, task: Task) -> Task:
        self.store.save_task(task)
        return task

    def update_task_status(self, task_id: str, new_status: TaskStatus) -> Optional[Task]:
        tasks = self.store.load_tasks()
        updated_task = None
        for t in tasks:
            if t.task_id == task_id:
                t.status = new_status
                t.updated_at = datetime.now(timezone.utc)
                if new_status == TaskStatus.COMPLETED:
                    t.completed_at = datetime.now(timezone.utc)
                updated_task = t
        if updated_task:
            self.store.save_tasks(tasks)
        return updated_task
