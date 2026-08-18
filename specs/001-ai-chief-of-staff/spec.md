# Feature Specification: AI Chief of Staff

**Feature Branch**: `001-ai-chief-of-staff`

**Created**: 2026-08-18

**Status**: Draft

**Input**: User description: "Build an AI Chief of Staff modeled on the concepts and workflows of mimurchison/claude-chief-of-staff. Do not simplify or redesign the core Chief of Staff concept. The initial implementation has exactly two external data sources: 1. Gmail 2. Google Calendar. The system must maintain persistent profile, preferences, hard constraints, goals, tasks, relationship/contact information, communication style, workflow execution state. Required behavior: morning briefing, weekly briefing, inbox triage, email prioritization, email response drafting, goal-aligned prioritization, persistent task management, proactive task awareness, meeting preparation, calendar analysis, calendar/goal alignment analysis, relationship/contact management, interaction history, contact enrichment using Gmail and Calendar, relationship staleness detection, suggested relationship touchpoints, proactive nudges, hard-constraint conflict detection, writing-style-aware drafting, source routing, persisted workflow state. Email triage: Tier 1 = respond now, Tier 2 = handle today, Tier 3 = FYI / low priority. Relationship staleness: Tier 1 = 14 days, Tier 2 = 30 days, Tier 3 = 60 days. Never send an email without explicit user approval. Before proposing specific meeting times, verify Calendar availability. Morning briefing combines: today's calendar, active tasks, active goals, urgent Gmail items, deadlines/conflicts, ranked focus recommendation. Meeting prep combines: calendar event metadata, attendees, persistent relationship context, previous Gmail interactions, relevant tasks/goals, unresolved commitments, talking points, desired outcome. The architecture must allow future connectors without redesigning core CoS logic. Do not implement any external source other than Gmail and Calendar in this specification."

## Clarifications

### Session 2026-08-18
- Q: What is the supported lifecycle state machine for persistent tasks? → A: 4-State Lifecycle: Pending, In Progress, Blocked, Completed.
- Q: How should the system detect whether a Gmail thread has already received a reply before recommending or drafting another response? → A: Thread Message Audit (verifying if the latest thread message is from user or matches a pending/approved draft).
- Q: When encountering an unrecognized email address or calendar participant, should the system automatically create a new persistent contact record or enrich existing contacts only? → A: Auto-Create & Enrich (automatically creating a new contact for unrecognized email addresses and enriching existing contact records).
- Q: What exact fallback behavior should the Chief of Staff execute when Gmail or Google Calendar is temporarily unavailable? → A: Cached Degraded Mode (use persistent local context, display connector warnings, and queue external sync operations).
- Q: What is the Google Calendar mutation policy and meeting prep eligibility criteria for V1? → A: Read-Only Calendar & External Focus (Calendar is read-only in V1; meeting prep is compiled for events with external participants or tagged strategic).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Morning Executive Briefing & Focus Prioritization (Priority: P1)

As an executive user, I want a daily morning briefing that synthesizes my schedule, active goals, open tasks, urgent communications, and potential conflicts into a clear focus recommendation so that I can start my day with immediate strategic clarity.

**Why this priority**: The morning briefing is the foundational daily entry point for executive alignment. It brings immediate clarity by combining live calendar events, active goals, pending tasks, and critical unread communications into a single ranked focus recommendation.

**Independent Test**: Can be tested by providing mock or connected calendar events, active goals, persistent tasks, and urgent emails, then validating that a structured morning briefing is generated containing all required synthesis sections and ranked focus recommendations.

**Acceptance Scenarios**:

1. **Given** active goals, pending tasks, today's Google Calendar schedule, and urgent Gmail messages, **When** the morning briefing workflow runs, **Then** the system produces a briefing containing today's calendar events, active tasks, active goals, urgent Gmail items, deadlines/conflicts, and a ranked focus recommendation.
2. **Given** a scheduling conflict or upcoming hard deadline on today's calendar, **When** the morning briefing is assembled, **Then** the system highlights the conflict and factors it into the ranked focus recommendation with explicit rationale.

---

### User Story 2 - Goal-Aligned Inbox Triage & Draft Response Generation (Priority: P1)

As an executive user, I want my incoming Gmail communications automatically triaged into actionable urgency tiers and drafted in my personal writing style so that I can process email rapidly without compromising human control or communication quality.

**Why this priority**: Communication management is a primary CoS function. Triaging incoming emails into Tier 1 (respond now), Tier 2 (handle today), and Tier 3 (FYI / low priority) while drafting responses dramatically reduces executive cognitive load while preserving approval controls.

**Independent Test**: Can be tested by processing a set of incoming emails against user goals, verifying tier categorization (Tier 1, 2, 3), and asserting that response drafts are generated for Tier 1/2 items without any unauthorized sending.

**Acceptance Scenarios**:

1. **Given** new incoming emails in Gmail, **When** inbox triage executes, **Then** emails are categorized into Tier 1 (respond now), Tier 2 (handle today), and Tier 3 (FYI / low priority) based on urgency, relationship context, and goal relevance.
2. **Given** a Tier 1 or Tier 2 email requiring a response, **When** response drafting runs, **Then** a draft response is generated adhering to the user's persisted communication style, and the system queues the draft for explicit user approval before sending.
3. **Given** a proposed email response, **When** the system processes it, **Then** it NEVER sends the email externally without receiving explicit user approval.

---

### User Story 3 - Comprehensive Strategic Meeting Preparation (Priority: P1)

As an executive user, I want detailed meeting preparation briefs automatically compiled for upcoming calendar events, including attendee relationship histories, past email context, open commitments, talking points, and desired outcomes, so that I enter every meeting fully prepared.

**Why this priority**: Executive meetings require high-context prep. Combining attendee relationship records, past Gmail threads, unresolved commitments, active goals, talking points, and target outcomes transforms meeting prep from manual search into instant executive readiness.

**Independent Test**: Can be tested by selecting an upcoming Google Calendar meeting with specific attendees, verifying that the system aggregates meeting metadata, attendee interaction history, past emails, open commitments, talking points, and desired outcomes into a unified meeting prep document.

**Acceptance Scenarios**:

1. **Given** an upcoming meeting on Google Calendar with specific attendees, **When** meeting prep is triggered, **Then** the system extracts calendar metadata, attendee context, previous Gmail interactions, relevant goals/tasks, unresolved commitments, talking points, and desired outcomes into a prep brief.
2. **Given** meeting prep generation where past email threads contain open promises or deliverables, **When** the brief is compiled, **Then** those unresolved commitments are explicitly surfaced under talking points and commitments.

---

### User Story 4 - Relationship Management & Staleness Detection (Priority: P2)

As an executive user, I want persistent tracking of contact relationships and interaction history with automatic staleness alerts based on defined touchpoint tiers so that key professional relationships never accidentally decay.

**Why this priority**: Maintaining key relationships is vital for executive effectiveness. Tracking contact context, interaction recency, and triggering staleness alerts ensures key allies, advisors, and team members are engaged consistently.

**Independent Test**: Can be tested by simulating last interaction dates for contacts across Tier 1 (14 days), Tier 2 (30 days), and Tier 3 (60 days), verifying that staleness alerts and suggested touchpoints are triggered when thresholds are exceeded.

**Acceptance Scenarios**:

1. **Given** contacts with interaction history enriched from Gmail and Google Calendar, **When** staleness detection runs, **Then** contacts with no interaction past their threshold (Tier 1 = 14 days, Tier 2 = 30 days, Tier 3 = 60 days) are flagged as stale.
2. **Given** a contact flagged as stale, **When** proactive touchpoint suggestions are generated, **Then** the system proposes context-aware touchpoints based on past interaction history, shared goals, and calendar availability.
3. **Given** new emails or calendar events involving a contact, **When** contact enrichment runs, **Then** the contact's interaction history, role context, and last interaction timestamp are automatically updated in persistent memory.

---

### User Story 5 - Weekly Briefing & Calendar-Goal Alignment Analysis (Priority: P2)

As an executive user, I want a weekly briefing that analyzes how my spent calendar time and completed tasks aligned with my active strategic goals so that I can audit time allocation and adjust future focus.

**Why this priority**: Long-term executive alignment requires weekly reflection on time allocation versus strategic goals.

**Independent Test**: Can be tested by providing a week of calendar data, task completions, and active goals, verifying that the weekly briefing outputs quantitative and qualitative alignment metrics highlighting over/under-invested goals.

**Acceptance Scenarios**:

1. **Given** completed calendar events and task logs for the past week alongside active strategic goals, **When** the weekly briefing is compiled, **Then** the system delivers a comprehensive report detailing time distribution across goals, key wins, unaddressed priorities, and goal-calendar misalignments.
2. **Given** identified gaps where critical goals received minimal calendar time, **When** recommendations are generated, **Then** the system proposes calendar adjustments for the upcoming week aligned with open availability.

---

### User Story 6 - Proactive Task Awareness, Nudges & Conflict Resolution (Priority: P3)

As an executive user, I want proactive nudges for approaching deadlines, unfulfilled commitments, and hard-constraint violations so that operational risks are resolved before becoming urgent crises.

**Why this priority**: Proactive nudging ensures open loops and calendar/personal boundary violations are caught automatically without human oversight failure.

**Independent Test**: Can be tested by creating conflicting commitments or boundary violations (e.g. proposed meeting during buffer time or personal hard constraints), asserting that proactive nudges and availability checks prevent or flag the conflict.

**Acceptance Scenarios**:

1. **Given** hard constraints defined in user profile (e.g., focus blocks, max daily meeting hours, non-working hours), **When** a new meeting or task is proposed, **Then** the system evaluates hard constraints and flags any conflict.
2. **Given** proposed meeting times for an email reply or scheduling request, **When** time options are generated, **Then** the system verifies actual Google Calendar availability before presenting specific time options to the user.
3. **Given** a workflow execution state (e.g. pending email draft approval or unconfirmed meeting proposal), **When** the state is persisted, **Then** the system accurately resumes workflow execution from the persisted state without losing context.

---

### Edge Cases

- **Connector Downtime or Failure**: How does the system handle temporary unavailability or credential expiry of Gmail or Google Calendar? The core CoS logic must retain existing persistent context, operate in degraded mode with cached durable records, and clearly indicate connector status without crashing core workflows.
- **Empty Calendar / Inbox**: What happens if the user has no meetings or unread emails for today? The morning briefing must report zero scheduled events/urgent emails cleanly while focusing emphasis on active goals, persistent tasks, and relationship touchpoint opportunities.
- **Ambiguous Email Triage**: How does the system handle an email that spans multiple potential tiers or lacks clear intent? The system assigns the conservative higher-priority tier (e.g., Tier 1 over Tier 2) with explainable rationale for user review.
- **Conflicting Hard Constraints vs. High-Priority Goals**: What happens when an urgent Tier 1 request conflicts with a user-defined hard constraint (e.g., focus block)? The system flags the conflict explicitly in the briefing or nudge, proposing explicit user trade-off options rather than silently overriding the constraint.
- **Malformed External Data**: How does the system process incomplete email headers or missing calendar event descriptions? The CoS enriches missing fields gracefully from persistent contact records and marks missing data explicitly rather than failing state changes.

## Requirements *(mandatory)*

### Functional Requirements

#### Core Architecture & Connectors
- **FR-001**: Core business logic MUST access external systems strictly through connector interfaces.
- **FR-002**: The system MUST implement exactly two initial connectors: Gmail and Google Calendar.
- **FR-003**: The core architecture MUST allow the addition of future external connectors without redesigning core Chief of Staff workflows or data structures.
- **FR-003a**: If Gmail or Google Calendar is unavailable, the system MUST operate in Cached Degraded Mode using persistent local records, displaying connector warnings, and queuing sync operations until connection is restored.

#### Persistent Context & State Management
- **FR-004**: The system MUST persist durable context outside model conversation memory, maintaining user profile, preferences, hard constraints, active goals, persistent tasks, relationship/contact entities, communication style guidelines, and workflow execution state.
- **FR-005**: All structured state updates MUST be schema-validated before persistence, ensuring agent prose does not corrupt structured data.
- **FR-006**: Workflow execution states MUST be persisted across execution cycles to support multi-step human-in-the-loop workflows.
- **FR-006a**: Tasks MUST enforce a strict 4-state lifecycle (`Pending`, `In Progress`, `Blocked`, `Completed`) for all tracking, triage, and briefing operations.
- **FR-006b**: The system MUST maintain timestamp cursors (`last_triage_at`, `last_morning_brief_at`, `last_weekly_brief_at`, `last_contact_enrichment_at`) in workflow execution state to track workflow run recency.

#### Morning & Weekly Executive Briefings
- **FR-007**: The system MUST generate a Morning Briefing combining today's Google Calendar events, active tasks, active goals, urgent Gmail items, deadlines/conflicts, and a ranked focus recommendation.
- **FR-008**: The system MUST generate a Weekly Briefing reviewing the past week's accomplishments, analyzing goal-calendar alignment, and recommending calendar adjustments for upcoming strategic priorities.

#### Email Triage, Drafting & Human Approval Constraints
- **FR-009**: The system MUST categorize incoming Gmail communications into three distinct triage tiers: Tier 1 (respond now), Tier 2 (handle today), and Tier 3 (FYI / low priority).
- **FR-009a**: Inbox triage MUST perform a Thread Message Audit to verify whether the latest message in a Gmail thread was sent by the user or associated with a pending/approved draft before recommending or generating a new draft.
- **FR-010**: The system MUST draft email responses for triaged emails adhering to the user's persisted communication style guidelines.
- **FR-011**: The system MUST NEVER send an email or mutate external systems without receiving explicit human user approval.
- **FR-012**: Before proposing specific meeting times in email drafts or briefings, the system MUST verify actual availability against Google Calendar.

#### Meeting Preparation & Calendar Analysis
- **FR-013**: The system MUST compile Meeting Preparation briefs for scheduled Google Calendar events.
- **FR-013a**: In V1, Google Calendar access MUST be strictly read-only, and Meeting Preparation briefs MUST be generated for events containing external participants or explicitly tagged as strategic.
- **FR-014**: Meeting Preparation briefs MUST combine calendar event metadata, attendee list, persistent relationship context, previous Gmail interaction histories, relevant active tasks/goals, unresolved commitments, talking points, and desired outcomes.
- **FR-015**: The system MUST perform continuous calendar analysis to detect scheduling overlaps, tight buffers, and misalignment with active goals.

#### Relationship & Contact Management
- **FR-016**: Contacts MUST be managed as durable entities with identity, relationship context, interaction history, last interaction date/time, follow-up state, and goal relevance.
- **FR-017**: The system MUST automatically enrich persistent contact entities using incoming/outgoing data from Gmail messages and Google Calendar events.
- **FR-017a**: The system MUST automatically create a new persistent contact record when encountering an unrecognized email address in Gmail or Google Calendar, and update existing contact records with interaction history and role context.
- **FR-018**: The system MUST track relationship staleness using three configured thresholds: Tier 1 (14 days without interaction), Tier 2 (30 days without interaction), and Tier 3 (60 days without interaction).
- **FR-019**: The system MUST generate proactive touchpoint suggestions for contacts flagged as stale, tailoring suggestions to relationship history and shared goals.

#### Prioritization, Nudges & Constraint Enforcement
- **FR-020**: Active goals MUST serve as the primary source of truth for task prioritization, email triage ranking, focus recommendations, and calendar alignment.
- **FR-021**: The system MUST surface explainable prioritization rationale for all recommendations, identifying the governing urgency, deadline, goal, relationship weight, or constraint condition.
- **FR-022**: The system MUST detect conflicts between proposed schedules/tasks and user-defined hard constraints (such as non-working hours or focus blocks) and issue proactive conflict alerts.
- **FR-023**: The system MUST issue proactive nudges for approaching task deadlines, stale commitments, and unaddressed high-priority emails.

### Key Entities

- **UserProfile**: Represents user preferences, working hours, communication style rules, and hard constraints (e.g. focus blocks, daily meeting caps).
- **Goal**: Represents an active strategic objective with priority level, timeframe, target outcome, and metric alignment.
- **Task**: Represents an actionable work item linked to active goals, containing lifecycle status (`Pending`, `In Progress`, `Blocked`, `Completed`), deadline, estimated duration, priority tier, and origin context.
- **Contact**: Durable entity representing a professional relationship, containing name, email, role/organization, relationship notes, goal relevance, last interaction timestamp, staleness tier, and interaction history log.
- **EmailItem**: Represents a Gmail communication, containing thread metadata, sender/recipients, timestamp, body summary, triaged priority (Tier 1, Tier 2, Tier 3), draft response status, and extracted commitments.
- **CalendarEvent**: Represents a Google Calendar entry, containing event ID, title, start/end timestamps, attendee list, location/link, description, meeting prep brief status, and goal alignment tags.
- **WorkflowState**: Represents execution state of multi-step processes (e.g., pending user approval for email draft, awaiting meeting time confirmation, briefing draft state, and timestamp cursors `last_triage_at`, `last_morning_brief_at`, `last_weekly_brief_at`, `last_contact_enrichment_at`).

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: Morning briefing generation completes in under 30 seconds upon execution start (target performance objective), synthesizing 100% of today's calendar events, active goals, and unread urgent emails.
- **SC-002**: Inbox triage accurately categorizes 95%+ of incoming emails into correct tiers (Tier 1, Tier 2, Tier 3) as verified by user feedback logs.
- **SC-003**: 100% of outgoing email drafts strictly enforce human-in-the-loop approval with zero unauthorized email transmissions.
- **SC-004**: 100% of proposed meeting time suggestions are pre-validated against actual Google Calendar availability before being presented to the user.
- **SC-005**: Meeting preparation briefs are generated and available prior to scheduled meetings for 100% of eligible calendar events involving external contacts or strategic tags.
- **SC-006**: Relationship staleness detection correctly identifies 100% of contacts exceeding their assigned staleness threshold (14, 30, or 60 days) and generates context-aware touchpoint recommendations.

## Assumptions

- **Connector Scope**: Only Gmail and Google Calendar are integrated as active external sources for v1. No other communication channels (Slack, Teams, WhatsApp, etc.) are in scope for this specification.
- **Authentication**: OAuth2 user credentials for Gmail API and Google Calendar API are provided securely at runtime.
- **Persistence Storage**: Persistent context entities (Profile, Goals, Tasks, Contacts, WorkflowState) are stored in local, schema-validated structured files (YAML/JSON) in accordance with project constitution.
- **User Verification**: The user interacts with the system daily to review morning briefings, approve/reject draft responses, and review weekly reviews.
