# ticket-agent

Autonomous ticket-to-production agent for Claude Code. Drives a ticket through 10 phases -- from intake to production validation -- using customizable **promptlets** that define what agents to spawn at each step.

## Install

```bash
claude plugin marketplace add /path/to/faire
claude plugin install ticket-agent@faire
```

## Commands

| Command | Description |
|---------|-------------|
| `/ticket <ticket-id>` | Start or resume a ticket workflow |
| `/ticket-learn [phase]` | Teach the agent your project-specific workflows |
| `/ticket-status` | Show active tickets and promptlet coverage |

## How It Works

### Phases

Each ticket moves through 10 sequential phases:

1. **Intake** -- Read the ticket, extract structured data
2. **Planning** -- Search codebase, analyze architecture, create plan *(session boundary: human reviews plan)*
3. **Implementation** -- TDD per component with self-review
4. **Verification** -- Full test suite, lint, type check
5. **PR Creation** -- Branch, push, open PR via `jj` + `gh`
6. **CI + Review Loop** -- Monitor CI and reviews, fix autonomously *(session boundary: after 3 CI fix failures)*
7. **Human Merge Gate** -- Human merges the PR *(session boundary: always)*
8. **Deploy Watch** -- Monitor deployment pipeline *(session boundary: on timeout/failure)*
9. **Production Validation** -- Smoke test, verify acceptance criteria
10. **Completion** -- Close ticket, post summary

### Promptlets

Each phase is driven by a **promptlet** -- a markdown template that defines:
- Which agents to spawn and their instructions
- Parallel vs sequential coordination
- Output contracts (what data the phase produces)
- Failure handling

Promptlets resolve in two tiers:
1. **Project-local**: `.claude/ticket-agent/promptlets/<phase>.md` (created by `/ticket-learn`)
2. **Plugin default**: shipped with this plugin (generic, works anywhere)

### State

Per-ticket state is stored at `.claude/ticket-agent/state/<ticket-id>.json` in your project. This enables resuming across sessions -- just run `/ticket <id>` again.

## Customization with `/ticket-learn`

The learning mode interviews you about your project's workflows and creates project-local promptlets:

```
/ticket-learn ci-review-loop
```

This will:
1. Show the current default promptlet for that phase
2. Ask about your CI system, review process, etc.
3. Explore your project (CI configs, test setup, deploy pipelines)
4. Draft a customized promptlet with project-specific commands and tools
5. Save to `.claude/ticket-agent/promptlets/ci-review-loop.md`

Phases with project-local promptlets use them instead of the defaults. No config files needed -- the promptlets ARE the configuration.

## Project Structure

```
ticket-agent/
  plugin.json                              # Plugin manifest
  commands/
    ticket.md                              # /ticket -- main orchestrator
    ticket-learn.md                        # /ticket-learn -- teaching mode
    ticket-status.md                       # /ticket-status -- dashboard
  skills/
    ticket-workflow/
      SKILL.md                             # Workflow rules and phase definitions
      resources/
        phase-reference.md                 # Detailed phase specs and transitions
        promptlet-format.md                # How to write promptlets
        promptlets/                        # Default promptlets (9 files)
          intake.md
          planning.md
          implementation.md
          verification.md
          pr-creation.md
          ci-review-loop.md
          deploy-watch.md
          production-validation.md
          completion.md
  hooks/
    hooks.json                             # SessionStart hook
  scripts/
    session-start-check.sh                 # Reminds about active tickets
```

Per-project state (created at runtime in your target project):
```
<your-project>/.claude/ticket-agent/
  promptlets/          # Learned/customized promptlets
  state/               # Per-ticket state files
```

## Session Boundaries

The agent saves state and stops at natural breakpoints where human input is needed:

- **After planning**: Review the implementation plan before coding starts
- **After 3 CI failures**: Manual debugging needed
- **At merge gate**: Human must merge the PR (never auto-merged)
- **Deploy timeout/failure**: Check deployment manually

Resume any time with `/ticket <ticket-id>`.

## VCS

Defaults to `jj`. Override per-project via `/ticket-learn pr-creation`.
