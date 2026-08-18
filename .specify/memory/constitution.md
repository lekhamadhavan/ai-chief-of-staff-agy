<!--
Sync Impact Report:
- Version change: Initial Scaffold (0.0.0) → 1.0.0
- Added Principles:
  - I. Chief of Staff Concept Fidelity
  - II. Persistent Context Is First-Class
  - III. Goals Are the Prioritization Source of Truth
  - IV. Human Control of External Actions
  - V. Source-Agnostic Core Architecture
  - VI. Minimum Necessary Access
  - VII. Relationship Continuity
  - VIII. Explainable Prioritization
  - IX. Deterministic State Changes
  - X. Testable CoS Behavior
  - XI. No Hidden Scope Reduction
- Added Sections: Core Principles, Governance
- Removed Sections: Template placeholders
- Deferred Items: None
-->

# AI Chief of Staff Constitution

## Core Principles

### I. Chief of Staff Concept Fidelity
The project MUST preserve:
- persistent context
- goals
- tasks
- communication management
- meeting preparation
- calendar analysis
- relationship/context management
- briefings
- nudges
- goal alignment
- hard constraints
- writing-style awareness
- proactive surfacing of relevant context

No implementation decision may silently simplify these concepts out of the system.

### II. Persistent Context Is First-Class
The Chief of Staff MUST NOT depend solely on model conversation history. Durable user context MUST be stored outside the model.

### III. Goals Are the Prioritization Source of Truth
Active goals MUST influence task prioritization, email triage, meeting importance, focus recommendations, nudges, relationship suggestions, and calendar-alignment analysis.

### IV. Human Control of External Actions
The system MUST distinguish read, analyze, draft, propose, and execute. Sending email or mutating external systems requires explicit approval.

### V. Source-Agnostic Core Architecture
Core business logic MUST access external systems through connector interfaces. Initial connectors: Gmail and Google Calendar.

### VI. Minimum Necessary Access
Only data required for the active workflow SHOULD be retrieved. Raw source data SHOULD NOT be persisted when a summarized durable record is sufficient.

### VII. Relationship Continuity
Contacts are durable entities with identity, relationship context, interaction history, last interaction, follow-up state, and goal relevance.

### VIII. Explainable Prioritization
Recommendations SHOULD identify the relevant urgency, deadline, relationship importance, blocker, goal, constraint, or calendar condition.

### IX. Deterministic State Changes
Structured state MUST be schema-validated. Agent prose MUST NOT directly corrupt YAML/JSON state.

### X. Testable CoS Behavior
Critical CoS workflows MUST have behavioral tests.

### XI. No Hidden Scope Reduction
Connector limitations may reduce available data, but MUST NOT remove the architectural representation of a CoS capability.

## Governance

Every spec, plan, task set, and implementation is checked against this constitution. Amendments must be explicit and documented.

**Version**: 1.0.0 | **Ratified**: 2026-08-18 | **Last Amended**: 2026-08-18
