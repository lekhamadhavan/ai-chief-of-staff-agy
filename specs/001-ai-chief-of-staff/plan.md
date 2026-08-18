# Implementation Plan: AI Chief of Staff

**Branch**: `001-ai-chief-of-staff` | **Date**: 2026-08-18 | **Spec**: [specs/001-ai-chief-of-staff/spec.md](spec.md)

**Input**: Feature specification from `specs/001-ai-chief-of-staff/spec.md`

## Summary

Build an executive-grade AI Chief of Staff (CoS) implemented on Google Antigravity as the agent runtime/orchestration environment. The system maintains durable filesystem-backed context in `cos-data/` (Pydantic-validated YAML storage) across user profile, hard constraints, active goals, persistent 4-state tasks, contact relationships, communication style rules, and workflow state cursors.

Domain services (goals, tasks, contacts, email triage, calendar analysis, meeting prep, briefings, nudges) are completely insulated from specific Model Context Protocol (MCP) tool names through a clean connector abstraction layer. All external mutations (sending emails, modifying external services) require explicit human approval boundaries.

## Technical Context

**Language/Version**: Python 3.12+

**Primary Dependencies**: Pydantic v2 (schema validation), PyYAML (YAML persistence), Antigravity Agent Runtime (rules, skills, workflows, MCP integrations)

**Storage**: Project-local filesystem storage in `cos-data/` containing structured YAML files validated against Pydantic schemas

**Testing**: `pytest` for unit, contract, and behavioral workflow testing

**Target Platform**: Linux / macOS / Windows CLI & Antigravity Agent IDE Environment

**Project Type**: Hybrid Python Service Library + Antigravity Agent Customization System (Rules, Skills, Workflows, MCP Connectors)

**Performance Goals**: Morning briefing synthesis generation <30 seconds for initial performance objective; schema persistence validation <50ms

**Constraints**: Zero unauthorized external mutations (strict approval boundary); v1 connectors restricted to Gmail and Google Calendar; zero dependency on model conversation memory for persistent state

**Scale/Scope**: Single executive profile; ~10-50 active goals; ~50-500 persistent tasks; ~100-1000 contact entities; 100% testable domain services

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- **Principle I (Concept Fidelity)**: PASS — All 13 core CoS concepts mapped to explicit services, skills, and data schemas.
- **Principle II (Persistent Context First-Class)**: PASS — All durable context stored in project-local `cos-data/` directory.
- **Principle III (Goals Source of Truth)**: PASS — Goals service injected as primary prioritization parameter across triage, briefings, and prep.
- **Principle IV (Human Control)**: PASS — Outgoing emails and external mutations require explicit human approval via approval boundary.
- **Principle V (Source-Agnostic Core Architecture)**: PASS — Connector interfaces (`IGmailConnector`, `IGoogleCalendarConnector`) decouple domain logic from MCP tool names.
- **Principle VI (Minimum Necessary Access)**: PASS — Connectors retrieve only active workflow scopes and record summarized durable context.
- **Principle VII (Relationship Continuity)**: PASS — Durable `Contact` entity tracks interaction logs, staleness tiers (14, 30, 60 days), and goal relevance.
- **Principle VIII (Explainable Prioritization)**: PASS — All triage and briefing recommendations include explicit `prioritization_rationale` fields.
- **Principle IX (Deterministic State Changes)**: PASS — Pydantic schemas validate all YAML reads and writes.
- **Principle X (Testable CoS Behavior)**: PASS — Comprehensive behavioral test suite planned under `tests/`.
- **Principle XI (No Hidden Scope Reduction)**: PASS — Core CoS capabilities fully preserved without simplification.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-chief-of-staff/
├── plan.md              # Implementation plan (this file)
├── research.md          # Phase 0 technical choices and architecture decisions
├── data-model.md        # Phase 1 Pydantic schema & entity specifications
├── quickstart.md        # Phase 1 validation and execution guide
├── contracts/           # Phase 1 connector & service interface specifications
│   └── connectors.md    # Gmail and Google Calendar connector contracts
└── tasks.md             # Phase 2 implementation task decomposition (via /speckit-tasks)
```

### Source Code (repository root)

```text
cos_core/                # Python Core Business Logic & Domain Services
├── __init__.py
├── models/              # Pydantic Schemas & Domain Models
│   ├── profile.py
│   ├── goal.py
│   ├── task.py
│   ├── contact.py
│   ├── email.py
│   ├── calendar.py
│   └── workflow.py
├── storage/             # Schema-validated File-Based Persistence
│   ├── __init__.py
│   ├── store.py
│   └── serializers.py
├── connectors/          # Source-Agnostic Connector Interfaces & Adapters
│   ├── __init__.py
│   ├── base.py
│   ├── gmail.py
│   └── calendar.py
├── services/            # Pure Business Logic Services
│   ├── __init__.py
│   ├── goals.py
│   ├── tasks.py
│   ├── contacts.py
│   ├── triage.py
│   ├── calendar_analysis.py
│   ├── meeting_prep.py
│   ├── briefing.py
│   └── nudge.py
└── orchestration/       # Helper CLI & Orchestration Bridge
    ├── __init__.py
    └── cli.py

.agents/                 # Antigravity Agent Environment Customizations
├── rules/               # Always-on Operating Principles
│   └── cos-operating-principles.md
├── skills/              # Modular CoS Capabilities
│   ├── cos-morning-briefing/
│   ├── cos-weekly-briefing/
│   ├── cos-inbox-triage/
│   ├── cos-meeting-prep/
│   ├── cos-relationship-management/
│   └── cos-task-nudge/
└── workflows/           # Explicit User-Invoked Workflow Slash Commands
    ├── morning-briefing.md
    ├── weekly-briefing.md
    ├── inbox-triage.md
    ├── meeting-prep.md
    └── relationship-audit.md

cos-data/                # Local Persistent Storage (Git-ignored user data)
├── profile.yaml
├── goals.yaml
├── tasks.yaml
├── contacts/
├── workflow_state.yaml
└── cache/

tests/                   # Test Suite
├── unit/                # Domain service unit tests
├── contract/            # Connector contract tests
├── integration/         # Storage & end-to-end service tests
└── behavioral/          # CoS workflow behavioral tests
```

**Structure Decision**: Selected modular Python service library architecture paired with Antigravity Agent Customizations (`.agents/rules/`, `.agents/skills/`, `.agents/workflows/`). The Python core (`cos_core`) encapsulates all deterministic domain logic, schema validation, and storage operations, while Antigravity orchestrates agent interaction, MCP tools, and user workflows.

## Complexity Tracking

> **No Constitution violations identified.** Architecture strictly adheres to all 11 constitutional principles.
