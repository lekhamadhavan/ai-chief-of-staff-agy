# Research & Architecture Decisions: AI Chief of Staff

**Feature Branch**: `001-ai-chief-of-staff` | **Date**: 2026-08-18 | **Spec**: [spec.md](spec.md)

## Overview

This document records technical research, architectural decisions, and design rationales for the AI Chief of Staff (CoS) implementation powered by Google Antigravity and a deterministic Python 3.12 helper stack.

---

## Technical Decisions & Rationales

### 1. Antigravity Orchestration Stack Architecture

- **Decision**: Structure the AI Chief of Staff around three core Antigravity customization primitives:
  - **Workspace Rules (`.agents/rules/`)**: Always-on CoS operating principles enforcing human control, goal-aligned prioritization, and explainability across all agent turns.
  - **Skills (`.agents/skills/`)**: Modular capability definitions (`cos-morning-briefing`, `cos-inbox-triage`, `cos-meeting-prep`, `cos-relationship-management`, `cos-task-nudge`) providing task execution instructions, Python CLI invocations, and output guidelines.
  - **Workflows (`.agents/workflows/`)**: User-invoked slash command entry points (`/morning-briefing`, `/inbox-triage`, `/meeting-prep`, `/weekly-briefing`, `/relationship-audit`).
  - **MCP Connectors**: Standardized Model Context Protocol servers for Gmail and Google Calendar.
- **Rationale**: Keeps executive workflows modular, repeatable, and maintainable within the native Antigravity environment while keeping domain logic testable via CLI.
- **Alternatives Considered**:
  - *Monolithic single agent prompt*: Rejected — fails maintainability, modularity, and explicit workflow boundaries.
  - *Hardcoded Python scripts without agent skills*: Rejected — loses agentic reasoning flexibility, context assembly, and natural writing style adaptation.

---

### 2. Source-Agnostic Connector Abstraction Layer

- **Decision**: Define pure Python abstract base interfaces (`IGmailConnector`, `IGoogleCalendarConnector`) in `cos_core/connectors/base.py`. Domain services interact *only* through these abstract methods (e.g., `fetch_unread_threads()`, `fetch_calendar_events()`, `stage_email_draft()`). MCP tools map to these interface methods via adapter classes or CLI bridge functions.
- **Rationale**: Fulfills Constitution Principle V (Source-Agnostic Core Architecture) and user constraints. Allows adding future connectors (Outlook, Slack, Apple Calendar) without modifying core CoS domain logic or data models.
- **Alternatives Considered**:
  - *Directly calling MCP tool names inside Python domain services*: Rejected — violates Constitutional Principle V and creates tight coupling to specific tool signatures.

---

### 3. Filesystem-Backed Persistent Storage (`cos-data/`)

- **Decision**: Store all durable context in structured, schema-validated YAML files located in `cos-data/` at the project root using Pydantic v2 models for serialization/deserialization.
  - `cos-data/profile.yaml` (UserProfile, hard constraints, writing style rules)
  - `cos-data/goals.yaml` (Active and archived Goal entities)
  - `cos-data/tasks.yaml` (Persistent Task entities with 4-state lifecycle)
  - `cos-data/contacts/*.yaml` (Per-contact entity records with interaction histories)
  - `cos-data/workflow_state.yaml` (Execution cursors and pending approval tokens)
- **Rationale**: Fulfills Constitution Principle II (Persistent Context Is First-Class) and Principle IX (Deterministic State Changes). Human-readable YAML files permit easy inspection, backup, and manual edit if required, while Pydantic guarantees strict schema validation on read/write.
- **Alternatives Considered**:
  - *SQLite or relational database*: Rejected — unnecessary complexity for single-user executive storage; YAML files provide transparent diffing and easy backup.
  - *In-memory model context only*: Rejected — explicitly violates Constitution Principle II.

---

### 4. Human-in-the-Loop Safety & Approval Boundary

- **Decision**: Implement a strict approval boundary pattern (`ApprovalRequest` state in `workflow_state.yaml`). Any action that mutates external systems (e.g. staging or sending an email) generates a pending proposal object with a unique approval ID. The system outputs a human-readable draft summary and halts execution until the user explicitly runs approval.
- **Rationale**: Fulfills Constitution Principle IV (Human Control of External Actions) and explicit user instruction: *"Never send an email without explicit user approval."*
- **Alternatives Considered**:
  - *Implicit sending for low-priority emails*: Rejected — strictly forbidden by Constitution and user prompt.
  - *Automated sending with undo timer*: Rejected — unsafe for executive communications.

---

### 5. Task Lifecycle & Thread Message Audit Rules

- **Decision**:
  - **Task Lifecycle**: Enforce a strict 4-state lifecycle state machine (`Pending` → `In Progress` → `Blocked` → `Completed`) enforced by Pydantic validators.
  - **Thread Message Audit**: Prior to generating an email response draft, the triage service executes a thread message audit verifying whether the last message in the thread was sent by the user or matches a pending/approved draft.
- **Rationale**: Eliminates task tracking ambiguity and prevents duplicate draft recommendations for threads already handled by the user.

---

### 6. Contact Auto-Creation & Staleness Tracking

- **Decision**:
  - **Auto-Creation**: Unrecognized email addresses detected in Gmail threads or Google Calendar events trigger auto-creation of a baseline `Contact` entity in `cos-data/contacts/<email_hash>.yaml`.
  - **Staleness Tracking**: Contacts evaluate interaction recency against three configurable staleness tiers: Tier 1 (14 days), Tier 2 (30 days), and Tier 3 (60 days). Flagged stale contacts surface in morning briefings and relationship audit workflows.
- **Rationale**: Prevents relationship decay without requiring manual contact entry overhead.

---

### 7. Cached Degraded-Mode Fallback

- **Decision**: If Gmail or Google Calendar APIs return authentication errors or network timeouts, the connector layer switches to `Cached Degraded Mode`. Services read cached calendar events and email summaries from `cos-data/cache/` and emit explicit warning headers in briefing outputs.
- **Rationale**: Guarantees system resilience during network or API outages without crashing core CoS workflows.
