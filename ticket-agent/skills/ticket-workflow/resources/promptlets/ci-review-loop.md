# CI + Review Loop

## Context
After the PR is created, monitor CI status and PR review comments in parallel. Fix CI failures and address review comments autonomously. This phase loops until CI is green and reviews are addressed, or 3 CI fix attempts are exhausted.

## Agents

### Agent: ci-monitor
- **Parallel group**: monitor
- **Type**: general-purpose
- **Instructions**: |
    Monitor CI status for PR {{pr_url}}.

    1. Check CI status:
       ```
       gh pr checks {{pr_number}} --watch
       ```
       Or poll with:
       ```
       gh pr checks {{pr_number}}
       ```

    2. If all checks pass, report SUCCESS

    3. If any check fails:
       - Get the failure details from the check run
       - Use `gh run view <run-id> --log-failed` to get failure logs
       - Report the failure with: check name, failure type, relevant log lines

    4. Wait up to 10 minutes for CI to complete before reporting timeout

- **Output**: CI status (pass/fail/timeout) with failure details if applicable

### Agent: review-monitor
- **Parallel group**: monitor
- **Type**: general-purpose
- **Instructions**: |
    Check for PR review comments on {{pr_url}}.

    1. List PR reviews and comments:
       ```
       gh pr view {{pr_number}} --json reviews,comments
       gh api repos/{owner}/{repo}/pulls/{{pr_number}}/comments
       ```

    2. Identify unresolved review comments and change requests

    3. For each unresolved comment, extract:
       - Reviewer name
       - File and line reference
       - Comment text
       - Whether it's a change request or suggestion

    4. Report all unresolved review items

- **Output**: List of unresolved review items (reviewer, file, line, comment, type)

### Agent: ci-fixer (spawned on CI failure)
- **Type**: general-purpose
- **Instructions**: |
    Fix CI failure for {{ticket_id}}.

    Failure details:
    {{ci_failure_details}}

    1. Analyze the failure
    2. Find the root cause in the code
    3. Apply the fix
    4. Run the failing check locally if possible to verify
    5. Push the fix:
       ```
       jj describe -m "fix: address CI failure - {{failure_summary}}"
       jj new
       jj git push
       ```

    Report what was fixed and whether local verification passed.

- **Output**: Fix description, files modified, local verification result

### Agent: review-responder (spawned on review comments)
- **Type**: general-purpose
- **Instructions**: |
    Address PR review comments for {{ticket_id}}.

    Review items to address:
    {{review_items}}

    For each item:
    1. Read the reviewer's comment carefully
    2. Understand the requested change
    3. Make the change in the code
    4. If you disagree with the suggestion, prepare a clear explanation why

    After addressing all items, push:
    ```
    jj describe -m "fix: address review feedback"
    jj new
    jj git push
    ```

- **Output**: List of addressed items with changes made

## Coordination
1. Run ci-monitor and review-monitor in parallel (monitor group)
2. When ci-monitor reports failure, spawn ci-fixer
3. When review-monitor reports comments, spawn review-responder
4. After any fix/response is pushed, restart the monitor loop
5. Loop exits when: CI green AND no unresolved reviews
6. Track CI fix attempts. After 3 failures, save state and end session

## Output Contract
Store in `phases.ci_review_loop.data`:
- ci_attempts (number)
- ci_status (string: "pass" | "fail" | "timeout")
- review_items_addressed (number)
- final_status (string: "complete" | "ci_failure_limit" | "timeout")

## Failure Handling
- CI timeout (>10 min): Retry poll once, then report
- CI fix attempt fails: Increment counter, try again (max 3)
- 3 CI fix attempts exhausted: Save state, report to human, end session
- Review comments that require design decisions: Flag for human input, don't auto-fix
