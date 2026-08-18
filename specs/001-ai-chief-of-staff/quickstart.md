# Quickstart & Validation Guide: AI Chief of Staff

**Feature Branch**: `001-ai-chief-of-staff` | **Date**: 2026-08-18 | **Spec**: [spec.md](spec.md)

## Overview

This guide provides step-by-step instructions to set up, run, and validate the AI Chief of Staff (CoS) implementation using Python 3.12+ and Antigravity Agent Customizations.

---

## 1. Prerequisites & Environment Setup

Ensure Python 3.12+ and `pip` are available on your Linux system.

```bash
# Clone/Navigate to workspace root
cd /home/lekha/Documents/ai-chief-of-staff-agy

# Create & activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install dependencies (Pydantic, PyYAML, pytest)
pip install pydantic pyyaml pytest pytest-mock
```

---

## 2. Initialize Persistent Storage (`cos-data/`)

Initialize default filesystem-backed storage schemas in `cos-data/`:

```bash
# Initialize storage directory structure and default YAML files
python3 -m cos_core.orchestration.cli init
```

This creates:
- `cos-data/profile.yaml` (Executive Profile & Rules)
- `cos-data/goals.yaml` (Active Strategic Goals)
- `cos-data/tasks.yaml` (Persistent Task Store)
- `cos-data/contacts/` (Contact Entity Store)
- `cos-data/workflow_state.yaml` (Workflow Cursors & Approvals)

---

## 3. Running the Test Suite

Validate data model schemas, domain services, connector interfaces, and workflow state handling:

```bash
# Run all unit, contract, and behavioral tests
pytest tests/ -v

# Run specific test suites
pytest tests/unit/ -v          # Unit tests for domain services
pytest tests/contract/ -v      # Connector contract tests
pytest tests/behavioral/ -v    # Workflow behavioral tests
```

---

## 4. Executing CoS Core CLI Workflows

You can invoke Chief of Staff workflows directly via the Python CLI or via Antigravity Agent Workflows.

### Morning Briefing Workflow
```bash
python3 -m cos_core.orchestration.cli morning-briefing
```
*Expected Output*: Displays today's calendar events, active tasks, active goals, triaged emails, scheduling conflicts, and ranked focus recommendation.

### Inbox Triage Workflow
```bash
python3 -m cos_core.orchestration.cli inbox-triage
```
*Expected Output*: Categorizes unread emails into Tier 1 (respond now), Tier 2 (handle today), Tier 3 (FYI), performs Thread Message Audits, and stages draft responses pending human approval.

### Meeting Preparation Workflow
```bash
python3 -m cos_core.orchestration.cli meeting-prep --event-id <event_id>
```
*Expected Output*: Generates a structured prep brief including attendee relationship histories, past emails, open commitments, talking points, and target outcomes.

### Human Approval Boundary Test
```bash
# List pending approval requests
python3 -m cos_core.orchestration.cli approvals list

# Approve an email draft (explicit human control)
python3 -m cos_core.orchestration.cli approve --id <approval_id>

# Reject an email draft
python3 -m cos_core.orchestration.cli reject --id <approval_id>
```

---

## 5. Antigravity Agent Workflow Commands

In the Antigravity Agent IDE or CLI environment, invoke the following slash commands:

- `/morning-briefing` — Triggers `cos-morning-briefing` skill and synthesizes daily focus.
- `/inbox-triage` — Triggers `cos-inbox-triage` skill and stages draft responses.
- `/meeting-prep` — Triggers `cos-meeting-prep` skill for upcoming meetings.
- `/weekly-briefing` — Triggers `cos-weekly-briefing` skill for goal-calendar alignment review.
- `/relationship-audit` — Triggers `cos-relationship-management` skill for contact staleness review.
