---
description: "Teach the ticket agent about your project workflows. Usage: /ticket-learn [phase]"
---

# Ticket Learning Mode

You are helping the user customize the ticket workflow for their project. You'll interview them about their specific workflows and create project-local promptlets.

## Step 1: Determine Scope

{{#if args}}
Learning about phase: **{{args}}**
{{else}}
No specific phase provided. Let me check which phases need customization.

Scan for existing project-local promptlets at `.claude/ticket-agent/promptlets/`.

List all 9 phases and indicate which have project-local overrides:
- intake
- planning
- implementation
- verification
- pr-creation
- ci-review-loop
- deploy-watch
- production-validation
- completion

Ask the user which phase they'd like to teach, suggesting phases without local overrides first.
{{/if}}

## Step 2: Show Current Promptlet

Read the current promptlet that would be used for this phase:
1. Check `.claude/ticket-agent/promptlets/<phase>.md` (project-local)
2. Fall back to `${CLAUDE_PLUGIN_ROOT}/skills/ticket-workflow/resources/promptlets/<phase>.md` (plugin default)

Show the user a summary of what the current promptlet does. Ask if they want to start from scratch or modify the existing one.

## Step 3: Interview

Ask focused questions about their workflow for this phase. Adapt your questions based on the phase:

### For intake:
- What ticket system do you use? (Linear, GitHub Issues, Jira, etc.)
- How do you access tickets? (MCP tool, CLI, API)
- What fields are most important?

### For planning:
- Are there specific architectural patterns to follow?
- Are there areas of the codebase that should not be modified?
- Who reviews plans?

### For implementation:
- What testing framework do you use?
- Any specific coding standards or patterns?
- Are there code generators or scaffolding tools?

### For verification:
- What CI checks run locally?
- What commands verify the build?
- What coverage threshold is required?

### For pr-creation:
- Do you use `jj` or `git`?
- What's your branch naming convention?
- What PR template do you use?
- Are there required labels or reviewers?

### For ci-review-loop:
- What CI system runs on PRs? (GitHub Actions, CircleCI, etc.)
- What checks must pass?
- How do you view CI logs?
- Who typically reviews PRs?

### For deploy-watch:
- How does deployment happen after merge?
- What workflow/pipeline runs?
- How long does deployment typically take?
- Where can you check deployment status?

### For production-validation:
- What's the production URL?
- Are there health check endpoints?
- Do you use error tracking (Sentry, etc.)?
- How do you verify changes in production?

### For completion:
- How do you close tickets?
- Do you post summaries to the ticket?

## Step 4: Explore the Project

Based on the user's answers, explore the project to fill in details:
- Read CI config files (.github/workflows/, .circleci/, etc.)
- Read test configuration (jest.config, vitest.config, pytest.ini, etc.)
- Read deployment configs
- Check package.json scripts
- Read any existing project documentation

## Step 5: Draft Promptlet

Using the interview answers and project exploration, draft a customized promptlet following the format in `${CLAUDE_PLUGIN_ROOT}/skills/ticket-workflow/resources/promptlet-format.md`.

The promptlet should:
- Reference specific tools, commands, and URLs for this project
- Follow the project's conventions (VCS, test framework, CI system)
- Include project-specific agent instructions
- Be complete enough that no generic fallback is needed

Present the draft to the user for review.

## Step 6: Save

After the user approves (with any modifications):
1. Create `.claude/ticket-agent/promptlets/` directory if it doesn't exist
2. Write the promptlet to `.claude/ticket-agent/promptlets/<phase>.md`
3. Confirm what was saved

## Step 7: Suggest Next

After saving, suggest the next phase that doesn't have a project-local override. Or if all phases are covered, congratulate the user on a fully customized workflow.

## Rules

- **Be conversational** -- don't dump all questions at once. Ask a few, explore based on answers, then ask more.
- **Show your work** -- when exploring the project, tell the user what you're finding.
- **Draft iteratively** -- show the promptlet draft and incorporate feedback before saving.
- **Preserve the promptlet format** -- follow the standard structure (Agents, Coordination, Output Contract, Failure Handling).
- **Don't override unnecessarily** -- if the default promptlet is already good for this project, tell the user.
