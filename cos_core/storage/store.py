import os
from pathlib import Path
from typing import List, Optional
import hashlib

from cos_core.models.profile import UserProfile
from cos_core.models.goal import Goal
from cos_core.models.task import Task, TaskStatus
from cos_core.models.contact import Contact
from cos_core.models.workflow import WorkflowState, ApprovalRequest, ApprovalStatus
from cos_core.models.email import EmailItem
from cos_core.models.calendar import CalendarEvent
from cos_core.storage.serializers import (
    model_to_yaml,
    yaml_to_model,
    model_list_to_yaml,
    yaml_to_model_list,
)

class DataStore:
    def __init__(self, data_dir: Optional[str] = None):
        if data_dir:
            self.data_dir = Path(data_dir)
        else:
            self.data_dir = Path(os.getcwd()) / "cos-data"
        
        self.contacts_dir = self.data_dir / "contacts"
        self.cache_dir = self.data_dir / "cache"

        # Ensure directories exist
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.contacts_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    # --- Profile ---
    @property
    def profile_path(self) -> Path:
        return self.data_dir / "profile.yaml"

    def load_profile(self) -> UserProfile:
        if not self.profile_path.exists():
            default_profile = UserProfile()
            self.save_profile(default_profile)
            return default_profile
        content = self.profile_path.read_text(encoding="utf-8")
        return yaml_to_model(content, UserProfile)

    def save_profile(self, profile: UserProfile) -> None:
        content = model_to_yaml(profile)
        self.profile_path.write_text(content, encoding="utf-8")

    # --- Goals ---
    @property
    def goals_path(self) -> Path:
        return self.data_dir / "goals.yaml"

    def load_goals(self) -> List[Goal]:
        if not self.goals_path.exists():
            return []
        content = self.goals_path.read_text(encoding="utf-8")
        return yaml_to_model_list(content, Goal)

    def save_goals(self, goals: List[Goal]) -> None:
        content = model_list_to_yaml(goals)
        self.goals_path.write_text(content, encoding="utf-8")

    def save_goal(self, goal: Goal) -> None:
        goals = self.load_goals()
        goals = [g for g in goals if g.goal_id != goal.goal_id]
        goals.append(goal)
        self.save_goals(goals)

    # --- Tasks ---
    @property
    def tasks_path(self) -> Path:
        return self.data_dir / "tasks.yaml"

    def load_tasks(self) -> List[Task]:
        if not self.tasks_path.exists():
            return []
        content = self.tasks_path.read_text(encoding="utf-8")
        return yaml_to_model_list(content, Task)

    def save_tasks(self, tasks: List[Task]) -> None:
        content = model_list_to_yaml(tasks)
        self.tasks_path.write_text(content, encoding="utf-8")

    def save_task(self, task: Task) -> None:
        tasks = self.load_tasks()
        tasks = [t for t in tasks if t.task_id != task.task_id]
        tasks.append(task)
        self.save_tasks(tasks)

    # --- Contacts ---
    def _contact_file(self, email: str) -> Path:
        email_hash = hashlib.md5(email.lower().strip().encode("utf-8")).hexdigest()
        return self.contacts_dir / f"{email_hash}.yaml"

    def load_contacts(self) -> List[Contact]:
        contacts = []
        for file_path in self.contacts_dir.glob("*.yaml"):
            try:
                content = file_path.read_text(encoding="utf-8")
                contacts.append(yaml_to_model(content, Contact))
            except Exception:
                continue
        return contacts

    def load_contact(self, email: str) -> Optional[Contact]:
        file_path = self._contact_file(email)
        if not file_path.exists():
            return None
        content = file_path.read_text(encoding="utf-8")
        return yaml_to_model(content, Contact)

    def save_contact(self, contact: Contact) -> None:
        file_path = self._contact_file(contact.email)
        content = model_to_yaml(contact)
        file_path.write_text(content, encoding="utf-8")

    # --- Workflow State & Approvals ---
    @property
    def workflow_state_path(self) -> Path:
        return self.data_dir / "workflow_state.yaml"

    def load_workflow_state(self) -> WorkflowState:
        if not self.workflow_state_path.exists():
            default_state = WorkflowState()
            self.save_workflow_state(default_state)
            return default_state
        content = self.workflow_state_path.read_text(encoding="utf-8")
        return yaml_to_model(content, WorkflowState)

    def save_workflow_state(self, state: WorkflowState) -> None:
        content = model_to_yaml(state)
        self.workflow_state_path.write_text(content, encoding="utf-8")

    # --- Cache (Degraded Mode & Offline Operations) ---
    @property
    def cached_emails_path(self) -> Path:
        return self.cache_dir / "email_items.yaml"

    def load_cached_emails(self) -> List[EmailItem]:
        if not self.cached_emails_path.exists():
            return []
        content = self.cached_emails_path.read_text(encoding="utf-8")
        return yaml_to_model_list(content, EmailItem)

    def save_cached_emails(self, emails: List[EmailItem]) -> None:
        content = model_list_to_yaml(emails)
        self.cached_emails_path.write_text(content, encoding="utf-8")

    @property
    def cached_events_path(self) -> Path:
        return self.cache_dir / "calendar_events.yaml"

    def load_cached_events(self) -> List[CalendarEvent]:
        if not self.cached_events_path.exists():
            return []
        content = self.cached_events_path.read_text(encoding="utf-8")
        return yaml_to_model_list(content, CalendarEvent)

    def save_cached_events(self, events: List[CalendarEvent]) -> None:
        content = model_list_to_yaml(events)
        self.cached_events_path.write_text(content, encoding="utf-8")
