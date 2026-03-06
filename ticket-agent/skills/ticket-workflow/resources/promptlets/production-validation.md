# Production Validation

## Context
After deployment succeeds, verify the change works correctly in production. This phase runs checks specific to what was changed.

## Agents

### Agent: production-validator
- **Type**: general-purpose
- **Instructions**: |
    Validate the production deployment for ticket {{ticket_id}}.

    Based on the acceptance criteria:
    {{phases.intake.data.acceptance_criteria}}

    Perform these validation steps:

    1. **Smoke test**: If there's a production URL, make basic HTTP requests to verify the service is responding
       - Check health endpoints
       - Verify API responses for relevant endpoints

    2. **Acceptance criteria verification**: For each acceptance criterion, describe how to verify it and whether it can be automated
       - If the criterion can be checked programmatically, do so
       - If it requires manual verification, note it for the human

    3. **Error monitoring**: If error tracking is available (Sentry, DataDog, etc.), check for new errors related to the deployment
       - Look for increased error rates
       - Check for new error types

    4. **Summary**: Provide a clear pass/fail for each verification step

- **Output**: Validation results per acceptance criterion, smoke test results, error check results

## Coordination
Single agent. No coordination needed.

## Output Contract
Store in `phases.production_validation.data`:
- smoke_test (object: {status, details})
- acceptance_results (array of {criterion, status, details, manual_check_needed})
- error_check (object: {status, details})
- overall_status (string: "pass" | "partial" | "fail")

## Failure Handling
- If production URL is unknown, ask the human
- If smoke test fails, report immediately (may indicate rollback needed)
- If some acceptance criteria need manual verification, note them but continue
- Mark overall status as "partial" if some checks couldn't be automated
