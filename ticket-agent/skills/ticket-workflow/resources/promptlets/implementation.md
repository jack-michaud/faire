# Implementation

## Context
Implement the approved plan using test-driven development. The orchestrator MUST delegate all implementation work to sub-agents. The orchestrator MUST NOT directly read code, write code, run tests, or use Edit/Write/Grep/Bash tools for implementation. Its only job is to spawn agents and collect results.

## Orchestrator Instructions

**CRITICAL: You are an orchestrator, not an implementer.** Your role in this phase is strictly:
1. Read the plan from `phases.planning.data.plan.components`
2. For each component, construct an agent prompt (see template below)
3. Spawn all component-implementer agents in parallel using the Agent tool
4. Wait for all to complete
5. For each completed implementer, spawn a component-reviewer agent
6. Collect results and store in state

**You MUST NOT**: use Edit, Write, Grep, Read (except state files), or Bash tools yourself during this phase. All code work happens inside sub-agents.

## Agent Template: component-implementer

For EACH component in `phases.planning.data.plan.components`, spawn a `general-purpose` Agent with the following prompt (fill in the values from the plan data):

```
You are implementing a component for ticket {{ticket_id}}.

Component: [component name from plan]
Files to create/modify: [component files from plan]

Acceptance criteria this component addresses:
[component acceptance criteria from plan]

Prior art to reference:
[prior art from phases.planning.data.prior_art]

Testing infrastructure:
[from phases.planning.data.test_infrastructure]

Architectural patterns to follow:
[from phases.planning.data.architecture.patterns]

Follow TDD strictly:
1. Write failing tests first based on the test strategy
2. Run tests to confirm they fail (RED)
3. Write minimal implementation to pass tests (GREEN)
4. Refactor if needed (REFACTOR)
5. Verify all tests pass

Use `jj` for any VCS operations. Do not create branches or commits -- the orchestrator handles that.

Report back:
- List of files created/modified
- Test results (pass/fail with details)
- Coverage for this component
```

Spawn ALL component-implementer agents in a single parallel batch (multiple Agent tool calls in one response).

## Agent Template: component-reviewer

After EACH component-implementer completes, spawn a `general-purpose` Agent:

```
You are reviewing the implementation of a component for ticket {{ticket_id}}.

Component: [component name]
Files to review: [files the implementer reported creating/modifying]

Check for:
1. Correctness: Does the implementation satisfy these acceptance criteria? [criteria]
2. Test quality: Are edge cases covered? Are tests meaningful (not just happy path)?
3. Code quality: Follows project patterns? No mutation? Proper error handling?
4. Security: No hardcoded secrets, validated inputs, safe queries

Report issues as a list with severity (CRITICAL, HIGH, MEDIUM, LOW) and suggested fixes.
```

## Coordination

1. Read the components list from `phases.planning.data.plan.components`
2. Spawn one component-implementer agent per component — ALL in parallel
3. After each implementer completes, spawn a component-reviewer for that component
4. If any reviewer reports CRITICAL issues, re-spawn the implementer with the review feedback appended
5. Max 2 re-implementation attempts per component

## Output Contract
Store in `phases.implementation.data`:
- components (array of {name, files_modified, test_results, review_findings})
- total_files_modified (number)
- all_reviews_passed (boolean)

## Failure Handling
- If a component-implementer fails, retry once with error context
- If a component-reviewer finds CRITICAL issues, re-run implementer with feedback (max 2 retries)
- If max retries exhausted, report the issue and continue with other components
- Do not proceed to verification if any CRITICAL issues remain unresolved
