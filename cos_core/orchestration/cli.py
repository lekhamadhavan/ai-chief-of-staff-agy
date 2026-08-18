import argparse
import json
import sys
from datetime import datetime, timezone
from typing import Optional

import yaml

from cos_core.storage.store import DataStore
from cos_core.models.workflow import ApprovalRequest, ApprovalStatus
from cos_core.connectors.gmail import GmailConnectorAdapter


STARTER_GOALS = [
    {
        "goal_id": "g_example_q3",
        "title": "Q3 Strategic Alignment",
        "description": "Define and execute on Q3 strategic priorities",
        "category": "Strategic",
        "priority": "high",
        "target_date": None,
        "is_active": True,
    }
]

STARTER_TASKS = [
    {
        "task_id": "t_example_kickoff",
        "title": "Example: Weekly Priorities Review",
        "description": "Review weekly priorities and align with Q3 strategic goals",
        "status": "Pending",
        "priority_tier": "Tier 1",
        "goal_id": "g_example_q3",
        "due_date": None,
        "estimated_duration_minutes": 30,
        "origin_source": "manual",
    }
]

def _scaffold_starter_files(store: DataStore) -> None:
    """Creates starter goals.yaml, tasks.yaml, and email_items.yaml if they don't exist."""
    # goals.yaml
    if not store.goals_path.exists():
        store.goals_path.write_text(
            yaml.safe_dump(STARTER_GOALS, sort_keys=False, default_flow_style=False),
            encoding="utf-8",
        )
        print(f"  [Created] {store.goals_path}")
    else:
        print(f"  [Exists]  {store.goals_path}")

    # tasks.yaml
    if not store.tasks_path.exists():
        store.tasks_path.write_text(
            yaml.safe_dump(STARTER_TASKS, sort_keys=False, default_flow_style=False),
            encoding="utf-8",
        )
        print(f"  [Created] {store.tasks_path}")
    else:
        print(f"  [Exists]  {store.tasks_path}")

    # cache/email_items.yaml
    if not store.cached_emails_path.exists():
        store.cached_emails_path.write_text("[]", encoding="utf-8")
        print(f"  [Created] {store.cached_emails_path}")
    else:
        print(f"  [Exists]  {store.cached_emails_path}")


def init_command(store: DataStore) -> None:
    # Scaffold starter data files first
    print("\n[DataStore Init] Scaffolding starter data files...")
    _scaffold_starter_files(store)

    # Load and report state
    profile = store.load_profile()
    goals = store.load_goals()
    tasks = store.load_tasks()
    state = store.load_workflow_state()
    print(f"\n[DataStore Init] Successfully initialized in {store.data_dir}")
    print(f"  Profile:           {profile.email}")
    print(f"  Active Goals:      {len(goals)}")
    print(f"  Pending Tasks:     {len(tasks)}")
    print(f"  Pending Approvals: {len(state.pending_approvals)}")
    print("\nEdit cos-data/profile.yaml to set your email and preferences.")
    print("Edit cos-data/goals.yaml and cos-data/tasks.yaml to add your data.")

def list_approvals_command(store: DataStore) -> None:
    state = store.load_workflow_state()
    if not state.pending_approvals:
        print("No pending approval requests.")
        return
    print(f"=== Pending Human Approval Requests ({len(state.pending_approvals)}) ===")
    for req in state.pending_approvals:
        print(f"ID: {req.approval_id} | Type: {req.action_type.value} | Status: {req.status.value}")
        print(f"Summary: {req.target_summary}")
        print(f"Payload: {json.dumps(req.payload, indent=2)}")
        print("-" * 50)

def approve_command(store: DataStore, approval_id: str) -> None:
    state = store.load_workflow_state()
    target_req: Optional[ApprovalRequest] = None
    for req in state.pending_approvals:
        if req.approval_id == approval_id:
            target_req = req
            break

    if not target_req:
        print(f"Error: Approval request '{approval_id}' not found.")
        sys.exit(1)

    target_req.status = ApprovalStatus.APPROVED
    target_req.resolved_at = datetime.now(timezone.utc)
    
    # Execute action based on action_type
    if target_req.action_type == "send_email":
        gmail = GmailConnectorAdapter(store=store)
        draft_id = target_req.payload.get("draft_id", "draft_default")
        gmail.send_email(draft_id=draft_id, approval_token=approval_id)
        print(f"[APPROVED & EXECUTED] Email draft '{draft_id}' sent successfully.")

    state.pending_approvals = [r for r in state.pending_approvals if r.approval_id != approval_id]
    store.save_workflow_state(state)

def reject_command(store: DataStore, approval_id: str) -> None:
    state = store.load_workflow_state()
    state.pending_approvals = [r for r in state.pending_approvals if r.approval_id != approval_id]
    store.save_workflow_state(state)
    print(f"[REJECTED] Approval request '{approval_id}' rejected and purged.")

def main():
    parser = argparse.ArgumentParser(description="AI Chief of Staff CLI Orchestrator")
    subparsers = parser.add_subparsers(dest="command", help="Available workflows")

    # init
    subparsers.add_parser("init", help="Initialize persistent context store")

    # approvals
    appr_parser = subparsers.add_parser("approvals", help="Manage pending human approvals")
    appr_sub = appr_parser.add_subparsers(dest="subcommand")
    appr_sub.add_parser("list", help="List pending approval requests")

    # approve
    approve_parser = subparsers.add_parser("approve", help="Approve and execute pending mutation")
    approve_parser.add_argument("--id", required=True, help="Approval ID to approve")

    # reject
    reject_parser = subparsers.add_parser("reject", help="Reject pending mutation")
    reject_parser.add_argument("--id", required=True, help="Approval ID to reject")

    # Workflow commands (wired in later phases)
    subparsers.add_parser("morning-briefing", help="Run Morning Executive Briefing workflow")
    subparsers.add_parser("inbox-triage", help="Run Goal-Aligned Inbox Triage workflow")
    subparsers.add_parser("meeting-prep", help="Run Strategic Meeting Preparation workflow")
    subparsers.add_parser("weekly-briefing", help="Run Weekly Executive Briefing workflow")
    subparsers.add_parser("relationship-audit", help="Run Relationship Staleness Audit workflow")

    args = parser.parse_args()
    store = DataStore()

    if args.command == "init":
        init_command(store)
    elif args.command == "approvals" and getattr(args, "subcommand", None) == "list":
        list_approvals_command(store)
    elif args.command == "approve":
        approve_command(store, args.id)
    elif args.command == "reject":
        reject_command(store, args.id)
    elif args.command == "morning-briefing":
        from cos_core.services.briefing import BriefingService
        svc = BriefingService(store=store)
        res = svc.generate_morning_briefing()
        print(res["output"])
    elif args.command == "inbox-triage":
        from cos_core.services.triage import CommunicationTriageService
        svc = CommunicationTriageService(store=store)
        res = svc.run_triage()
        print(res["output"])
    elif args.command == "meeting-prep":
        from cos_core.services.meeting_prep import MeetingPrepService
        svc = MeetingPrepService(store=store)
        res = svc.generate_meeting_prep()
        print(res["output"])
    elif args.command == "weekly-briefing":
        from cos_core.services.briefing import BriefingService
        svc = BriefingService(store=store)
        res = svc.generate_weekly_briefing()
        print(res["output"])
    elif args.command == "relationship-audit":
        from cos_core.services.contacts import ContactsService
        svc = ContactsService(store=store)
        res = svc.run_staleness_audit()
        print(res["output"])
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
