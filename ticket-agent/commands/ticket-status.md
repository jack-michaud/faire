---
description: "Show status of active ticket workflows"
---

# Ticket Status

Check for active ticket workflows in this project.

## Step 1: Find State Files

Look for state files at `.claude/ticket-agent/state/*.json`.

If the directory doesn't exist or is empty, report:
```
No active ticket workflows in this project.

Start one with: /ticket <ticket-id>
Customize workflows with: /ticket-learn [phase]
```

## Step 2: Display Status

For each state file found, read it and display:

```
Ticket: <ticket_id>
Phase:  <current_phase>
Branch: <branch_name or "not created yet">
PR:     <pr_url or "not created yet">

Phase Progress:
  [x] intake
  [x] planning
  [ ] implementation    <-- current
  [ ] verification
  [ ] pr-creation
  [ ] ci-review-loop
  [ ] human-merge-gate
  [ ] deploy-watch
  [ ] production-validation
  [ ] completion
```

Mark completed phases with `[x]`, the current phase with `<-- current`, and pending phases with `[ ]`.

## Step 3: Promptlet Coverage

Also check which phases have project-local promptlets at `.claude/ticket-agent/promptlets/`:

```
Promptlet Coverage:
  intake:                default
  planning:              default
  implementation:        custom (project-local)
  verification:          default
  pr-creation:           custom (project-local)
  ci-review-loop:        custom (project-local)
  deploy-watch:          default
  production-validation: default
  completion:            default

Customize more phases with: /ticket-learn [phase]
```

## Step 4: Resume Hint

If any tickets are in progress, suggest how to resume:
```
Resume with: /ticket <ticket-id>
```
