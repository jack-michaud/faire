# Intake

## Context
Read the ticket and extract structured information for downstream phases. This is the first phase -- gather everything needed to start planning.

## Agents

### Agent: ticket-reader
- **Type**: general-purpose
- **Instructions**: |
    Read ticket {{ticket_id}} using available MCP tools or CLI commands (e.g., Linear MCP, GitHub Issues CLI, Jira CLI).

    Extract the following information:
    - Title
    - Full description
    - Acceptance criteria (as a list)
    - Labels/tags
    - Priority level
    - Assignee
    - Any linked tickets or dependencies
    - Attached files or design references

    If the ticket system is not accessible via MCP, try CLI tools (e.g., `linear issue view`, `gh issue view`, `jira issue view`).
    If neither works, ask the user to paste the ticket contents.

- **Output**: JSON object with: title, description, acceptance_criteria (array), labels (array), priority, assignee, dependencies (array), attachments (array)

## Coordination
Single agent. No coordination needed.

## Output Contract
Store in `phases.intake.data`:
- title (string)
- description (string)
- acceptance_criteria (string[])
- labels (string[])
- priority (string)
- assignee (string)
- dependencies (string[])
- attachments (string[])

## Failure Handling
If the ticket cannot be read through any method, stop and ask the user to provide ticket details manually. Do not proceed to planning without intake data.
