# PR Creation

## Context
Create a VCS branch, push changes, and open a pull request with a comprehensive description.

## Agents

### Agent: pr-creator
- **Type**: general-purpose
- **Instructions**: |
    Create a pull request for ticket {{ticket_id}}.

    1. **Create branch**:
       ```
       jj new main
       jj bookmark create feat/{{ticket_id}}-{{branch_slug}}
       ```
       Where branch_slug is derived from the ticket title (lowercase, hyphens, max 50 chars).

    2. **Describe the change**:
       ```
       jj describe -m "feat: {{phases.intake.data.title}}"
       ```

    3. **Push**:
       ```
       jj git push --bookmark feat/{{ticket_id}}-{{branch_slug}}
       ```

    4. **Create PR** using `gh pr create`:
       - Title: `{{phases.intake.data.title}}`
       - Body should include:
         - Summary of changes (from planning phase)
         - List of files modified
         - Test coverage results
         - Acceptance criteria checklist
         - Link to ticket
       - Use heredoc format for the body

    5. **Record PR details**: Capture the PR URL and number from the `gh pr create` output.

- **Output**: branch_name, pr_number, pr_url

## Coordination
Single agent. No coordination needed.

## Output Contract
Store in state (top-level):
- branch_name (string)
- pr_number (number)
- pr_url (string)

Store in `phases.pr_creation.data`:
- branch_name (string)
- pr_number (number)
- pr_url (string)
- pr_body (string)

## Failure Handling
- If branch creation fails, check if branch already exists and use it
- If push fails, check for conflicts and report
- If PR creation fails, report the error (may need to authenticate with `gh auth`)
- Do not proceed to CI monitoring without a valid PR
