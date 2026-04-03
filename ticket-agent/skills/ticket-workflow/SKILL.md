---
name: ticket-workflow
description: "Autonomous ticket-to-production lifecycle with promptlet-driven phases. Use when executing /ticket commands, working on ticket-driven development, or orchestrating multi-phase workflows from intake through planning, implementation, CI review, and production validation."
---

# Ticket Workflow

## Overview

The ticket workflow drives an autonomous agent through 10 phases from ticket intake to production validation. Each phase is defined by a **promptlet** — a markdown template that specifies what agents to spawn, how they coordinate, and what they produce.

## Phases

| # | Phase | Key | Session Boundary |
|---|-------|-----|-----------------|
| 1 | Intake | intake | no |
| 2 | Planning | planning | YES - human reviews plan |
| 3 | Implementation | implementation | no |
| 4 | Verification | verification | no |
| 5 | PR Creation | pr-creation | no |
| 6 | CI + Review Loop | ci-review-loop | YES - if 3 fix attempts fail |
| 7 | Human Merge Gate | human-merge-gate | YES - always |
| 8 | Deploy Watch | deploy-watch | YES - conditional |
| 9 | Production Validation | production-validation | no |
| 10 | Completion | completion | no |

## Phase Transitions

- Phases execute sequentially from 1 to 10
- The orchestrator reads the promptlet for the current phase, spawns agents as specified, collects results, updates state, and transitions to the next phase
- Session boundaries cause the agent to save state and stop. Human resumes with `/ticket <id>`
- The agent NEVER auto-merges. Phase 7 (human-merge-gate) always requires human action

## Promptlet Resolution

Two-tier resolution, project-local overrides defaults:

1. **Project-local**: `.claude/ticket-agent/promptlets/<phase>.md`
2. **Plugin default**: `${CLAUDE_PLUGIN_ROOT}/skills/ticket-workflow/resources/promptlets/<phase>.md`

If a project-local promptlet exists, use it (it already contains project-specific knowledge from `/ticket-learn`). Otherwise, fall back to the generic default.

## State Management

State is stored at `.claude/ticket-agent/state/<ticket-id>.json` in the target project. The state file is immutable-write (full replace each time). It tracks:

- `ticket_id`: The ticket identifier
- `current_phase`: Which phase the ticket is in
- `branch_name`: The VCS branch (created during implementation)
- `pr_number` and `pr_url`: PR details (set during pr-creation)
- `phases`: Per-phase status and data

## VCS

All VCS operations use `jj` by default. Projects using git can override via learned promptlets.

## Agent Topology

All sub-agents are `general-purpose` type. The promptlet defines:
- Which agents to spawn and their instructions
- Whether agents work in parallel or sequentially
- What each agent reports back
- How failures are handled

The `/ticket` command in the main session IS the orchestrator. Sub-agents cannot spawn sub-agents.

**CRITICAL ORCHESTRATOR RULE**: The orchestrator MUST delegate work to sub-agents as defined by each promptlet. During phases that define agents (especially implementation), the orchestrator MUST NOT directly use Edit, Write, Grep, or Bash tools for code changes. It should only use tools for state management (reading/writing state files) and spawning agents. Each promptlet's agent templates contain literal prompt text — the orchestrator fills in values from state data and passes the constructed prompt to the Agent tool. If a promptlet defines per-component agents, the orchestrator iterates over the components array and spawns one agent per component.

## Session Boundaries

The agent saves state and ends at these natural breakpoints:
- After **planning** phase (human reviews plan before coding starts)
- After **CI failures** exhaust 3 fix attempts
- At **human merge gate** (human must merge the PR)
- When **waiting for deploy** to complete

## CI + Review Monitoring Loop

After the PR is created, the ci-review-loop phase forms a continuous monitoring loop:
1. Push the PR
2. Poll CI status and PR comments in parallel
3. If CI fails → analyze, fix, push (restarts CI check)
4. If review comments arrive → address them, push
5. Loop exits when: CI green AND PR approved (or no outstanding comments)
6. Max 3 CI fix attempts before session boundary

## Resources

Reference documents for this workflow:
- `resources/phase-reference.md` — Detailed phase definitions and transition rules
- `resources/promptlet-format.md` — How to write and customize promptlets
- Default promptlets in `resources/promptlets/` — Generic implementations for each phase
