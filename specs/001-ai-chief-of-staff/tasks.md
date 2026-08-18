# Tasks: AI Chief of Staff

**Input**: Design documents from `specs/001-ai-chief-of-staff/` (`spec.md`, `plan.md`, `research.md`, `data-model.md`, `contracts/connectors.md`, `quickstart.md`)

**Prerequisites**: Python 3.12+, Pydantic v2, PyYAML, pytest

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization, directory scaffolding, and environment configuration.

- [x] T001 Create project package directory structure per implementation plan (`cos_core/`, `cos_core/models/`, `cos_core/storage/`, `cos_core/connectors/`, `cos_core/services/`, `cos_core/orchestration/`, `cos-data/`, `.agents/rules/`, `.agents/skills/`, `.agents/workflows/`, `tests/unit/`, `tests/contract/`, `tests/integration/`, `tests/behavioral/`)
- [x] T002 Initialize Python package setup and dependency configuration in `pyproject.toml` (Pydantic v2, PyYAML, pytest, pytest-mock)
- [x] T003 [P] Create gitignore configuration for local data isolation in `.gitignore` (ignoring user data in `cos-data/` while keeping default directory templates)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core data models, schema validation, persistence engine, connector abstraction interfaces, and approval boundary framework. MUST be complete before user stories execute.

- [x] T004 Implement UserProfile and HardConstraint Pydantic models in `cos_core/models/profile.py` (FR-004, FR-005, FR-022)
- [x] T005 [P] Implement Goal Pydantic model in `cos_core/models/goal.py` (FR-004, FR-005, FR-020)
- [x] T006 [P] Implement Task Pydantic model with strict 4-state lifecycle (`Pending`, `In Progress`, `Blocked`, `Completed`) in `cos_core/models/task.py` (FR-004, FR-005, FR-006a)
- [x] T007 [P] Implement Contact and InteractionLog Pydantic models in `cos_core/models/contact.py` (FR-004, FR-005, FR-016, FR-018)
- [x] T008 [P] Implement EmailItem and EmailTriageTier Pydantic models in `cos_core/models/email.py` (FR-004, FR-005, FR-009)
- [x] T009 [P] Implement CalendarEvent Pydantic model in `cos_core/models/calendar.py` (FR-004, FR-005, FR-013a)
- [x] T010 [P] Implement WorkflowState and ApprovalRequest Pydantic models with timestamp cursors (`last_triage_at`, `last_morning_brief_at`, `last_weekly_brief_at`, `last_contact_enrichment_at`) in `cos_core/models/workflow.py` (FR-004, FR-006, FR-006b, FR-011)
- [x] T011 Implement YAML Serializers and File Storage Engine in `cos_core/storage/serializers.py` and `cos_core/storage/store.py` with schema-validation on all reads and writes (FR-004, FR-005)
- [x] T012 Implement Abstract Base Connector Interfaces (`IGmailConnector`, `IGoogleCalendarConnector`) and DTOs in `cos_core/connectors/base.py` (FR-001, FR-003)
- [x] T013 Implement Cached Degraded Mode fallback handling in `cos_core/connectors/base.py` and `cos_core/storage/store.py` (FR-003a)
- [x] T014 Implement Gmail Connector Adapter in `cos_core/connectors/gmail.py` implementing `IGmailConnector` (FR-002)
- [x] T015 Implement Google Calendar Connector Adapter in `cos_core/connectors/calendar.py` implementing `IGoogleCalendarConnector` (FR-002, FR-013a)
- [x] T016 Implement Goals Service in `cos_core/services/goals.py` for goal management and prioritization ranking (FR-020)
- [x] T017 Implement Tasks Service in `cos_core/services/tasks.py` for task CRUD and 4-state lifecycle transitions (FR-006a)
- [x] T018 Implement Approval Boundary Engine and CLI Commands in `cos_core/orchestration/cli.py` to enforce human-in-the-loop approval before external mutations (FR-011)
- [x] T019 Write Foundational Unit and Contract Tests in `tests/unit/test_storage.py` and `tests/contract/test_connectors.py` validating persistence and connector abstractions

**Checkpoint**: Foundation ready — core storage, domain models, connector interfaces, and approval engine operational.

---

## Phase 3: User Story 1 - Morning Executive Briefing & Focus Prioritization (Priority: P1) 🎯 MVP

**Goal**: Synthesize calendar events, active goals, pending tasks, urgent emails, and conflicts into a ranked morning executive briefing (<30s performance target).

**Independent Test**: Execute `cos-cli morning-briefing` with mock data and verify generated briefing contains schedule, goals, tasks, urgent emails, conflicts, and explainable focus recommendation.

### Tests for User Story 1
- [x] T020 [P] [US1] Unit test for morning briefing assembly logic in `tests/unit/test_briefing_service.py` (FR-007, FR-021)
- [x] T021 [P] [US1] Behavioral end-to-end test for morning briefing in `tests/behavioral/test_morning_briefing.py` (SC-001)

### Implementation for User Story 1
- [x] T022 [US1] Implement Briefing Service core in `cos_core/services/briefing.py` for morning briefing compilation (FR-007)
- [x] T023 [US1] Implement Goal-Aligned Focus Prioritization algorithm in `cos_core/services/briefing.py` with explainable rationale (FR-020, FR-021)
- [x] T024 [US1] Integrate Calendar events and urgent Gmail items into Morning Briefing assembly in `cos_core/services/briefing.py` (FR-007)
- [x] T025 [US1] Wire Morning Briefing command to CLI in `cos_core/orchestration/cli.py` updating `last_morning_brief_at` cursor in `WorkflowState` (FR-006b, FR-007)

**Checkpoint**: Morning Executive Briefing fully operational and testable independently.

---

## Phase 4: User Story 2 - Goal-Aligned Inbox Triage & Draft Response Generation (Priority: P1)

**Goal**: Categorize incoming Gmail messages into Tier 1/2/3, perform Thread Message Audit, generate response drafts in user's writing style, and enforce approval-before-send.

**Independent Test**: Process unread emails, assert correct triage tiers (Tier 1/2/3), verify draft responses match style rules, verify Thread Message Audit suppresses duplicate drafts, and confirm zero emails are sent without explicit approval token.

### Tests for User Story 2
- [x] T026 [P] [US2] Unit tests for email triage categorization and Thread Message Audit in `tests/unit/test_triage_service.py` (FR-009, FR-009a)
- [x] T027 [P] [US2] Contract test for email draft creation and approval boundary enforcement in `tests/contract/test_email_approval.py` (FR-011, SC-003)

### Implementation for User Story 2
- [x] T028 [US2] Implement Communication Triage Service in `cos_core/services/triage.py` for Tier 1, 2, and 3 categorization (FR-009)
- [x] T029 [US2] Implement Thread Message Audit in `cos_core/services/triage.py` checking if the latest message was sent by user or matches pending draft (FR-009a)
- [x] T030 [US2] Implement Writing-Style-Aware Response Drafting Engine in `cos_core/services/triage.py` applying `WritingStyleRules` from `UserProfile` (FR-010)
- [x] T031 [US2] Implement Stage Draft & Approval Request Handler in `cos_core/services/triage.py` queuing drafts to `WorkflowState.pending_approvals` (FR-011)
- [x] T032 [US2] Wire Inbox Triage command to CLI in `cos_core/orchestration/cli.py` updating `last_triage_at` cursor in `WorkflowState` (FR-006b, FR-009)

**Checkpoint**: Goal-Aligned Inbox Triage and Draft Generation functional with strict approval boundary.

---

## Phase 5: User Story 3 - Comprehensive Strategic Meeting Preparation (Priority: P1)

**Goal**: Compile strategic meeting preparation briefs for calendar events with external participants or strategic tags, combining relationship context, email thread summaries, open commitments, talking points, and target outcomes.

**Independent Test**: Trigger meeting prep for a test external calendar event, verifying that attendee history, previous email interactions, talking points, and desired outcomes are compiled.

### Tests for User Story 3
- [x] T033 [P] [US3] Unit test for meeting prep compilation and eligibility filter in `tests/unit/test_meeting_prep_service.py` (FR-013, FR-013a, FR-014)
- [x] T034 [P] [US3] Behavioral test for strategic meeting prep generation in `tests/behavioral/test_meeting_prep.py` (SC-005)

### Implementation for User Story 3
- [x] T035 [US3] Implement Meeting Eligibility Filter in `cos_core/services/meeting_prep.py` targeting external attendees or strategic tags (FR-013a)
- [x] T036 [US3] Implement Strategic Meeting Prep Compiler in `cos_core/services/meeting_prep.py` aggregating attendee history, past emails, goals/tasks, open commitments, talking points, and outcomes (FR-013, FR-014)
- [x] T037 [US3] Wire Meeting Prep command to CLI in `cos_core/orchestration/cli.py` (FR-013)

**Checkpoint**: Strategic Meeting Preparation briefs generated for all eligible calendar events.

---

## Phase 6: User Story 4 - Relationship Management & Staleness Detection (Priority: P2)

**Goal**: Manage persistent contact records, enrich contacts automatically from Gmail/Calendar, auto-create unrecognized contacts, track staleness tiers (14d, 30d, 60d), and suggest proactive touchpoints.

**Independent Test**: Provide contact recency data, assert staleness alerts trigger accurately for Tier 1 (14d), Tier 2 (30d), and Tier 3 (60d), assert unrecognized email auto-creates a new Contact entity, and verify suggested touchpoints are generated.

### Tests for User Story 4
- [x] T038 [P] [US4] Unit test for contact auto-creation and staleness calculation in `tests/unit/test_contacts_service.py` (FR-017a, FR-018, SC-006)

### Implementation for User Story 4
- [x] T039 [US4] Implement Contacts Service core in `cos_core/services/contacts.py` for durable contact entity management (FR-016)
- [x] T040 [US4] Implement Contact Auto-Creation & Enrichment Engine in `cos_core/services/contacts.py` auto-creating unrecognized emails and logging interaction history (FR-017, FR-017a)
- [x] T041 [US4] Implement Relationship Staleness Evaluator in `cos_core/services/contacts.py` for Tier 1 (14d), Tier 2 (30d), and Tier 3 (60d) thresholds (FR-018)
- [x] T042 [US4] Implement Proactive Touchpoint Suggestion Generator in `cos_core/services/contacts.py` tailored to interaction history and shared goals (FR-019)
- [x] T043 [US4] Wire Relationship Audit command to CLI in `cos_core/orchestration/cli.py` updating `last_contact_enrichment_at` cursor in `WorkflowState` (FR-006b, FR-018)

**Checkpoint**: Relationship management, contact auto-creation, staleness alerts, and touchpoints fully functional.

---

## Phase 7: User Story 5 - Weekly Briefing & Calendar-Goal Alignment Analysis (Priority: P2)

**Goal**: Analyze spent calendar time and completed tasks over the past week against active strategic goals, highlighting misalignments and proposing calendar adjustments.

**Independent Test**: Provide past week's calendar events and completed tasks, execute weekly briefing, and assert quantitative goal-calendar alignment breakdown is produced with corrective calendar suggestions.

### Tests for User Story 5
- [x] T044 [P] [US5] Unit test for weekly goal-calendar alignment calculation in `tests/unit/test_weekly_briefing.py` (FR-008, FR-015)

### Implementation for User Story 5
- [x] T045 [US5] Implement Weekly Calendar-Goal Alignment Analyzer in `cos_core/services/calendar_analysis.py` measuring time allocation across active goals (FR-008, FR-015)
- [x] T046 [US5] Implement Weekly Executive Briefing Generator in `cos_core/services/briefing.py` synthesizing wins, unaddressed priorities, and calendar adjustments (FR-008)
- [x] T047 [US5] Wire Weekly Briefing command to CLI in `cos_core/orchestration/cli.py` updating `last_weekly_brief_at` cursor in `WorkflowState` (FR-006b, FR-008)

**Checkpoint**: Weekly Executive Briefing and goal alignment analysis operational.

---

## Phase 8: User Story 6 - Proactive Task Awareness, Nudges & Conflict Resolution (Priority: P3)

**Goal**: Detect hard-constraint violations (focus blocks, non-working hours, meeting caps), pre-validate meeting availability against Google Calendar, and issue proactive nudges for deadlines and commitments.

**Independent Test**: Create schedule conflict against hard constraints or focus blocks, assert conflict alert triggers, and verify meeting availability pre-validation checks against Google Calendar.

### Tests for User Story 6
- [x] T048 [P] [US6] Unit test for hard-constraint conflict evaluator and availability check in `tests/unit/test_nudge_service.py` (FR-012, FR-022, FR-023)

### Implementation for User Story 6
- [x] T049 [US6] Implement Hard-Constraint Conflict Evaluator in `cos_core/services/nudge.py` checking focus blocks, non-working hours, and daily meeting caps (FR-022)
- [x] T050 [US6] Implement Calendar Availability Pre-validator in `cos_core/services/calendar_analysis.py` verifying open time slots before proposing meeting options (FR-012, SC-004)
- [x] T051 [US6] Implement Proactive Nudge Engine in `cos_core/services/nudge.py` for approaching deadlines, stale commitments, and high-priority unaddressed emails (FR-023)

**Checkpoint**: Proactive nudging, hard-constraint enforcement, and availability pre-validation complete.

---

## Phase 9: Antigravity Customizations (Rules, Skills & Workflows)

**Goal**: Implement native Antigravity Workspace Rules, Skills, and Workflows for seamless agent integration.

- [x] T052 [P] Create Antigravity Always-On Operating Principles Rule in `.agents/rules/cos-operating-principles.md` enforcing CoS concept fidelity, persistent context, human approval, and explainable prioritization
- [x] T053 [P] Create Morning Briefing Antigravity Skill in `.agents/skills/cos-morning-briefing/SKILL.md` (FR-007)
- [x] T054 [P] Create Weekly Briefing Antigravity Skill in `.agents/skills/cos-weekly-briefing/SKILL.md` (FR-008)
- [x] T055 [P] Create Inbox Triage Antigravity Skill in `.agents/skills/cos-inbox-triage/SKILL.md` (FR-009)
- [x] T056 [P] Create Meeting Prep Antigravity Skill in `.agents/skills/cos-meeting-prep/SKILL.md` (FR-013)
- [x] T057 [P] Create Relationship Management Antigravity Skill in `.agents/skills/cos-relationship-management/SKILL.md` (FR-018)
- [x] T058 [P] Create Task Nudge Antigravity Skill in `.agents/skills/cos-task-nudge/SKILL.md` (FR-023)
- [x] T059 [P] Create Morning Briefing Antigravity Workflow in `.agents/workflows/morning-briefing.md` for `/morning-briefing` slash command
- [x] T060 [P] Create Weekly Briefing Antigravity Workflow in `.agents/workflows/weekly-briefing.md` for `/weekly-briefing` slash command
- [x] T061 [P] Create Inbox Triage Antigravity Workflow in `.agents/workflows/inbox-triage.md` for `/inbox-triage` slash command
- [x] T062 [P] Create Meeting Prep Antigravity Workflow in `.agents/workflows/meeting-prep.md` for `/meeting-prep` slash command
- [x] T063 [P] Create Relationship Audit Antigravity Workflow in `.agents/workflows/relationship-audit.md` for `/relationship-audit` slash command

**Checkpoint**: Antigravity customization stack (Rules, Skills, Workflows) fully configured.

---

## Phase 10: Polish, Integration & Quickstart Validation

**Purpose**: End-to-end integration validation, quickstart execution, and documentation verification.

- [x] T064 Run full `pytest` test suite across unit, contract, integration, and behavioral tests (asserting 100% pass rate)
- [x] T065 Validate Quickstart execution steps in `specs/001-ai-chief-of-staff/quickstart.md`
- [x] T066 Verify 100% Functional Requirement coverage mapping against `specs/001-ai-chief-of-staff/spec.md` (FR-001 through FR-023)
- [x] T067 Extend `init` CLI command in `cos_core/orchestration/cli.py` to auto-scaffold starter `goals.yaml`, `tasks.yaml`, and `cache/email_items.yaml` files when they do not exist, so new users get a fully ready `cos-data/` directory after running `init`
- [x] T068 Implement live Gmail & Calendar REST API connectors in `cos_core/connectors/google_auth.py`, `gmail.py`, and `calendar.py` to dynamically fetch live inbox and calendar data using OAuth tokens from `~/.gmail-mcp/credentials.json`
- [x] T069 Create comprehensive Google Cloud Console setup walkthrough in `docs/google-cloud-setup.md` covering Web application OAuth 2.0 configuration for Gmail + Calendar MCP integration
- [x] T070 Upgrade `.agents/skills/cos-morning-briefing/SKILL.md` and `.agents/workflows/morning-briefing.md` to perform multi-stage Antigravity Executive AI Strategic Synthesis (email response recommendations, calendar focus time suggestions, and interactive single-click actions)
- [x] T071 Configure Gmail live connector in `cos_core/connectors/gmail.py` to default to a 24-hour window (`newer_than:1d`) fetching all incoming emails (read and unread) with dynamic `UNREAD` label detection

---


## Dependencies & Execution Order

```text
Phase 1: Setup (T001 - T003)
   │
   ▼
Phase 2: Foundational (T004 - T019)  ──► BLOCKS ALL USER STORIES
   │
   ├──► Phase 3: User Story 1 (P1 - Morning Briefing) [T020 - T025] 🎯 MVP
   ├──► Phase 4: User Story 2 (P1 - Inbox Triage & Drafts) [T026 - T032]
   ├──► Phase 5: User Story 3 (P1 - Strategic Meeting Prep) [T033 - T037]
   ├──► Phase 6: User Story 4 (P2 - Relationship Staleness & Contacts) [T038 - T043]
   ├──► Phase 7: User Story 5 (P2 - Weekly Briefing & Goal Alignment) [T044 - T047]
   └──► Phase 8: User Story 6 (P3 - Proactive Nudges & Constraints) [T048 - T051]
   │
   ▼
Phase 9: Antigravity Customizations (Rules/Skills/Workflows) [T052 - T063]
   │
   ▼
Phase 10: Polish & Quickstart Validation [T064 - T066]
```

### Parallel Execution Opportunities
- Tasks marked `[P]` within Phase 2 (Pydantic Models T005-T010) can be implemented in parallel.
- Once Phase 2 (Foundational) completes, User Stories (Phases 3-8) can proceed in parallel or priority sequence.
- All Antigravity Skills & Workflows in Phase 9 marked `[P]` can be implemented in parallel.
