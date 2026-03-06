# Implementation

## Context
Implement the approved plan using test-driven development. Each component from the plan gets its own agent that writes tests first, then implements.

## Agents

### Agent: component-implementer (one per component)
- **Parallel group**: implementation
- **Type**: general-purpose
- **Instructions**: |
    Implement component: {{component.name}}

    Files to create/modify: {{component.files}}

    Follow TDD strictly:
    1. Write failing tests first based on the test strategy
    2. Run tests to confirm they fail (RED)
    3. Write minimal implementation to pass tests (GREEN)
    4. Refactor if needed (REFACTOR)
    5. Verify all tests pass

    Testing patterns to follow:
    {{phases.planning.data.test_infrastructure}}

    Architectural patterns to follow:
    {{phases.planning.data.architecture.patterns}}

    Prior art to reference:
    {{component.prior_art}}

    Acceptance criteria this component addresses:
    {{component.acceptance_criteria}}

    Use `jj` for any VCS operations. Do not create branches or commits -- the orchestrator handles that.

- **Output**: List of files created/modified, test results, coverage for this component

### Agent: component-reviewer (one per component, after its implementer)
- **Type**: general-purpose
- **After**: corresponding component-implementer completes
- **Instructions**: |
    Review the implementation of component: {{component.name}}

    Check for:
    1. Correctness: Does the implementation satisfy the acceptance criteria?
    2. Test quality: Are edge cases covered? Are tests meaningful (not just happy path)?
    3. Code quality: Follows project patterns? No mutation? Proper error handling?
    4. Security: No hardcoded secrets, validated inputs, safe queries

    Files to review: {{component.files}}

    Report issues as a list with severity (CRITICAL, HIGH, MEDIUM, LOW) and suggested fixes.
    If CRITICAL issues found, the component must be re-implemented.

- **Output**: Review findings with severity and suggested fixes

## Coordination
For each component in the plan:
1. Spawn a component-implementer agent
2. All component-implementers run in parallel
3. After each implementer completes, spawn a component-reviewer for that component
4. If any reviewer reports CRITICAL issues, re-spawn the implementer with the review feedback
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
