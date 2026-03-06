# Completion

## Context
The final phase. Close the ticket, post a summary, and clean up.

## Agents

### Agent: ticket-closer
- **Type**: general-purpose
- **Instructions**: |
    Complete ticket {{ticket_id}}.

    1. **Post summary to ticket**: If the ticket system supports comments, post a summary:
       - PR link: {{pr_url}}
       - What was implemented (from planning phase)
       - Test coverage results
       - Production validation results
       - Any manual verification items still pending

    2. **Close/transition the ticket**:
       - Try: `linear issue update {{ticket_id}} --status Done`
       - Or: `gh issue close {{ticket_id}}`
       - Or suggest the human close it manually

    3. **Clean up state**: Report that the ticket workflow is complete so the orchestrator can mark the state file as done.

    4. **Summary for human**:
       Produce a final summary:
       ```
       Ticket: {{ticket_id}} - {{phases.intake.data.title}}
       PR: {{pr_url}}
       Status: Complete

       Phases completed:
       - Intake: OK
       - Planning: OK
       - Implementation: OK
       - Verification: OK
       - PR Creation: OK
       - CI/Review: OK
       - Deploy: {{phases.deploy_watch.data.deploy_status}}
       - Production: {{phases.production_validation.data.overall_status}}

       Manual follow-ups:
       - [list any manual verification items]
       ```

- **Output**: Completion summary, ticket closure status

## Coordination
Single agent. No coordination needed.

## Output Contract
Store in `phases.completion.data`:
- ticket_closed (boolean)
- summary (string)
- manual_followups (string[])

Set `current_phase` to "completed" in the top-level state.

## Failure Handling
- If ticket system is not accessible, report the summary and ask the human to close the ticket
- Completion should never fail fatally -- at worst, report what couldn't be automated
