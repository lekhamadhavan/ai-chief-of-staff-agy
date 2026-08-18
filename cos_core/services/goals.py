from typing import List, Optional
from cos_core.models.goal import Goal, GoalPriority
from cos_core.storage.store import DataStore

class GoalsService:
    def __init__(self, store: Optional[DataStore] = None):
        self.store = store or DataStore()

    def get_active_goals(self) -> List[Goal]:
        goals = self.store.load_goals()
        active = [g for g in goals if g.is_active]
        # Sort by priority: HIGH > MEDIUM > LOW
        priority_weight = {GoalPriority.HIGH: 3, GoalPriority.MEDIUM: 2, GoalPriority.LOW: 1}
        return sorted(active, key=lambda g: priority_weight.get(g.priority, 0), reverse=True)

    def add_goal(self, goal: Goal) -> Goal:
        self.store.save_goal(goal)
        return goal

    def deactivate_goal(self, goal_id: str) -> bool:
        goals = self.store.load_goals()
        updated = False
        for g in goals:
            if g.goal_id == goal_id:
                g.is_active = False
                updated = True
        if updated:
            self.store.save_goals(goals)
        return updated
