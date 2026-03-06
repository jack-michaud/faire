# Promptlet Format

## What is a Promptlet?

A promptlet is a markdown template that teaches the ticket agent how to execute a specific phase of the ticket workflow. Promptlets define:
- What agents to spawn
- What instructions each agent receives
- How agents coordinate (parallel, sequential, team)
- What each agent reports back
- How failures are handled

## Structure

```markdown
# <Phase Name>

## Context
What this phase does and when it runs.

## Agents

### Agent: <name>
- **Type**: general-purpose
- **Parallel group**: <group-name> (agents in the same group run in parallel)
- **Instructions**: |
    <multi-line instructions for the agent>
- **Output**: What the agent should return
- **On failure**: What to do if the agent fails

### Agent: <name>
...

## Coordination
How agents relate to each other. Which run in parallel, which are sequential.
Describe the flow: "Run agents A and B in parallel. When both complete, run agent C with their combined results."

## Output Contract
What this phase produces and stores in the state file.

## Failure Handling
What happens when things go wrong. Max retries, fallback behavior, session boundary conditions.
```

## Key Rules

1. **All agents are general-purpose type** - the promptlet provides specialization via instructions
2. **Agents cannot spawn sub-agents** - only the orchestrator (main session) spawns agents
3. **Instructions should be self-contained** - include all context the agent needs
4. **Output contracts are strict** - agents must return structured data the orchestrator can parse
5. **Promptlets ARE the configuration** - no separate config files needed

## Resolution Order

1. Project-local: `.claude/ticket-agent/promptlets/<phase>.md`
2. Plugin default: `${CLAUDE_PLUGIN_ROOT}/skills/ticket-workflow/resources/promptlets/<phase>.md`

Project-local promptlets override defaults entirely (no merging).

## Creating Custom Promptlets

Use `/ticket-learn <phase>` to create project-specific promptlets through a guided conversation. The learning mode will:
1. Show the current default promptlet
2. Interview you about your project's specific workflow
3. Explore your project's CI, test, and deploy infrastructure
4. Draft a customized promptlet
5. Save it to `.claude/ticket-agent/promptlets/<phase>.md`

## Variable Interpolation

Promptlets can reference state from previous phases using template variables:

- `{{ticket_id}}` - The ticket identifier
- `{{branch_name}}` - The VCS branch name
- `{{pr_url}}` - The PR URL
- `{{pr_number}}` - The PR number
- `{{phases.<phase>.data.<key>}}` - Data from a completed phase

The orchestrator resolves these before passing instructions to agents.

## Per-Item Agent Spawning

Some phases need to spawn one agent per item in an array (e.g., one implementer per component). These promptlets use **agent templates** instead of direct agent definitions:

- The promptlet provides a literal prompt template with `[placeholder]` markers
- The orchestrator reads the array from state (e.g., `phases.planning.data.plan.components`)
- For each item, the orchestrator fills in the placeholders and spawns an Agent tool call
- All per-item agents in the same parallel group should be spawned in a single response (parallel Agent calls)

This is different from `{{variable}}` interpolation — template variables reference state paths, while `[placeholder]` markers indicate values the orchestrator must fill from an iterated array item.

## Example: Minimal Promptlet

```markdown
# Intake

## Context
Read the ticket and extract structured information for downstream phases.

## Agents

### Agent: ticket-reader
- **Type**: general-purpose
- **Instructions**: |
    Read ticket {{ticket_id}} using available MCP tools or CLI commands.
    Extract: title, description, acceptance criteria, labels, priority, assignee.
    If the ticket cannot be found, report the error clearly.
- **Output**: JSON with fields: title, description, acceptance_criteria (array), labels (array), priority, assignee

## Coordination
Single agent, no coordination needed.

## Output Contract
Store in state as `phases.intake.data`:
- title (string)
- description (string)
- acceptance_criteria (array of strings)
- labels (array of strings)
- priority (string)

## Failure Handling
If ticket cannot be read, report error and stop. Do not proceed to planning without intake data.
```
