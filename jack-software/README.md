# jack-software

A collection of development skills for test-driven development, code review, debugging, and software engineering best practices.

## Commands

### `/ship-skill`

Ship a procedure, skill, or command to the faire marketplace or local project. Handles workspace isolation, validation, version bumping, commit, and push.

**Usage:**

```
/jack-software:ship-skill <description of what to add>
```

**Examples:**

```
/jack-software:ship-skill add a procedure for deploying to staging
/jack-software:ship-skill create a skill for writing GraphQL resolvers
/jack-software:ship-skill add a command to the logs plugin that shows error rate trends
/jack-software:ship-skill add a local procedure for this project's database migration
```

The command determines the content type (procedure, skill, or command), target destination (faire marketplace or local project), and target plugin from the description. For faire changes, it uses an isolated jj workspace to avoid disturbing in-progress work.

### `/add-procedure`

Add a procedure to the appropriate skill, or create a new one. Works from any project.

### `/update-skill`

Save a successful workflow into a skill's reference files.

### `/procedure-skill`

Create a procedure skill — a step-by-step process document that teaches Claude how to perform a specific workflow.

### `/plan`

Restate requirements, assess risks, and create a step-by-step implementation plan.

### `/tdd`

Enforce test-driven development workflow with 80%+ coverage.

### `/code-review`

Delegate specialized reviews to subagents and synthesize findings.

### `/e2e`

Generate and run end-to-end tests with Playwright.

### `/test-coverage`

Measure and report test coverage.
