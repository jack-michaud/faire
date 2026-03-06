# Phase Reference

## Phase Definitions

### Phase 1: Intake
- **Key**: `intake`
- **Purpose**: Read the ticket and extract structured information
- **Inputs**: Ticket ID (from user)
- **Outputs**: Title, description, acceptance criteria, labels, priority
- **Agent topology**: Single general-purpose agent that reads the ticket via MCP tools or CLI
- **Transition**: Automatic to phase 2
- **Session boundary**: No

### Phase 2: Planning
- **Key**: `planning`
- **Purpose**: Analyze the codebase, find prior art, identify system boundaries, and create an implementation plan
- **Inputs**: Intake data from phase 1
- **Outputs**: Prior art references, system boundary analysis, step-by-step implementation plan
- **Agent topology**: Parallel general-purpose agents (code searcher, architecture scanner, test discoverer), then a synthesizer agent that combines findings into a plan
- **Transition**: Human reviews and approves plan
- **Session boundary**: YES - always stops here for human review

### Phase 3: Implementation
- **Key**: `implementation`
- **Purpose**: Implement the plan using TDD
- **Inputs**: Approved plan from phase 2
- **Outputs**: Code changes with passing tests
- **Agent topology**: General-purpose agents per component (parallel TDD), then review agent per component, then verification agent for full test suite
- **Transition**: Automatic to phase 4
- **Session boundary**: No

### Phase 4: Verification
- **Key**: `verification`
- **Purpose**: Run full test suite, linting, and type checking
- **Inputs**: Implementation from phase 3
- **Outputs**: All checks passing, coverage report
- **Agent topology**: Single general-purpose agent that runs all verification commands
- **Transition**: Automatic to phase 5 if all pass; back to phase 3 if failures
- **Session boundary**: No

### Phase 5: PR Creation
- **Key**: `pr-creation`
- **Purpose**: Create branch, push, and open PR
- **Inputs**: Verified implementation, ticket metadata
- **Outputs**: PR URL, branch name
- **Agent topology**: Single general-purpose agent
- **Transition**: Automatic to phase 6
- **Session boundary**: No

### Phase 6: CI + Review Loop
- **Key**: `ci-review-loop`
- **Purpose**: Monitor CI and PR reviews, fix issues autonomously
- **Inputs**: PR URL from phase 5
- **Outputs**: CI green, reviews addressed
- **Agent topology**: Parallel general-purpose agents (CI poller + review poller), fix agents spawned as needed
- **Transition**: Automatic to phase 7 when CI green and no outstanding reviews
- **Session boundary**: YES - only if 3 CI fix attempts fail
- **Max CI fix attempts**: 3

### Phase 7: Human Merge Gate
- **Key**: `human-merge-gate`
- **Purpose**: Wait for human to merge the PR
- **Inputs**: Approved PR from phase 6
- **Outputs**: PR merged
- **Agent topology**: None (main session reports status and stops)
- **Transition**: Human merges, then runs `/ticket <id>` to continue
- **Session boundary**: YES - always

### Phase 8: Deploy Watch
- **Key**: `deploy-watch`
- **Purpose**: Monitor deployment pipeline
- **Inputs**: Merged PR
- **Outputs**: Deployment status (success/failure)
- **Agent topology**: Single general-purpose agent that monitors deploy pipeline
- **Transition**: Automatic to phase 9 if deploy succeeds
- **Session boundary**: YES - if deployment takes too long or fails

### Phase 9: Production Validation
- **Key**: `production-validation`
- **Purpose**: Verify the change works in production
- **Inputs**: Deployment success from phase 8
- **Outputs**: Validation results
- **Agent topology**: Single general-purpose agent that runs production checks
- **Transition**: Automatic to phase 10
- **Session boundary**: No

### Phase 10: Completion
- **Key**: `completion`
- **Purpose**: Close the ticket and clean up
- **Inputs**: Validated production deployment
- **Outputs**: Ticket closed, summary posted
- **Agent topology**: Single general-purpose agent
- **Transition**: Terminal
- **Session boundary**: No

## Transition Rules

1. Phases execute in order 1 -> 10
2. A phase cannot start until the previous phase completes (status: "completed")
3. Phase 4 (verification) can loop back to phase 3 (implementation) if checks fail
4. Phase 6 (ci-review-loop) loops internally until CI green + reviews addressed
5. Session boundaries cause state save and session end
6. `/ticket <id>` resumes from `current_phase`

## State Transitions

```
intake -> planning -> [HUMAN REVIEW] -> implementation -> verification
    ^                                                        |
    |                                                        v (if fails)
    |                                               implementation (retry)
    v
pr-creation -> ci-review-loop -> [HUMAN MERGE] -> deploy-watch
                    ^    |
                    |    v (fix + push)
                    +----+
                         |
                         v (3 failures)
                    [SESSION END]

deploy-watch -> production-validation -> completion -> [DONE]
```
