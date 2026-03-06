# Planning

## Context
Analyze the codebase, find prior art, identify system boundaries, and create a detailed implementation plan. This phase runs after intake and produces a plan that the human must review before implementation begins.

## Agents

### Agent: code-searcher
- **Parallel group**: research
- **Type**: general-purpose
- **Instructions**: |
    Search the codebase for code related to the ticket requirements.

    Based on the ticket:
    - Title: {{phases.intake.data.title}}
    - Description: {{phases.intake.data.description}}
    - Acceptance criteria: {{phases.intake.data.acceptance_criteria}}

    Find:
    1. Existing code that does something similar (prior art)
    2. Related test files and test patterns used
    3. Relevant configuration files
    4. Import patterns and dependency usage

    Use Grep and Glob tools to search thoroughly. Report file paths, line numbers, and brief descriptions of what you found.

- **Output**: List of prior art findings with file paths, descriptions, and relevance notes

### Agent: architecture-scanner
- **Parallel group**: research
- **Type**: general-purpose
- **Instructions**: |
    Analyze the project architecture to identify where changes should be made.

    Based on the ticket:
    - Title: {{phases.intake.data.title}}
    - Description: {{phases.intake.data.description}}

    Determine:
    1. Which directories/modules will be affected
    2. Existing architectural patterns (e.g., repository pattern, service layer, MVC)
    3. Dependency injection or configuration patterns
    4. API route patterns and middleware
    5. Database schema and migration patterns

    Read key files like package.json, tsconfig.json, directory READMEs, and entry points.

- **Output**: Architecture analysis with affected modules, patterns to follow, and constraints

### Agent: test-discoverer
- **Parallel group**: research
- **Type**: general-purpose
- **Instructions**: |
    Discover the testing infrastructure and patterns.

    Find:
    1. Test framework (Jest, Vitest, pytest, etc.)
    2. Test directory structure
    3. Test naming conventions
    4. Fixture and mock patterns
    5. Test configuration files
    6. Coverage requirements
    7. How to run tests (scripts in package.json, Makefile, etc.)

    Read a few representative test files to understand the patterns used.

- **Output**: Testing infrastructure summary with framework, patterns, run commands, and examples

### Agent: plan-synthesizer
- **Type**: general-purpose
- **After**: research group completes
- **Instructions**: |
    Synthesize the research from the code-searcher, architecture-scanner, and test-discoverer into an implementation plan.

    Ticket information:
    - Title: {{phases.intake.data.title}}
    - Description: {{phases.intake.data.description}}
    - Acceptance criteria: {{phases.intake.data.acceptance_criteria}}

    Research findings will be provided to you.

    Create a plan that includes:
    1. **Summary**: One-paragraph overview of the change
    2. **Components**: List of components to create or modify, with file paths
    3. **Implementation order**: Which components to build first (respecting dependencies)
    4. **Test strategy**: What tests to write for each component, following discovered patterns
    5. **Risk assessment**: Potential issues and mitigations
    6. **Acceptance verification**: How to verify each acceptance criterion is met

    The plan should be specific enough that each component can be handed to an independent agent for TDD implementation.

- **Output**: Structured implementation plan

## Coordination
Run code-searcher, architecture-scanner, and test-discoverer in parallel (research group). When all three complete, pass their combined output to the plan-synthesizer.

## Output Contract
Store in `phases.planning.data`:
- prior_art (array of {file, description, relevance})
- architecture (object with affected_modules, patterns, constraints)
- test_infrastructure (object with framework, patterns, run_commands)
- plan (object with summary, components, implementation_order, test_strategy, risks, acceptance_verification)

## Failure Handling
If any research agent fails, proceed with available data. The plan-synthesizer should note gaps. If the plan-synthesizer fails, stop and report the error. Do not proceed to implementation without a plan.

## Session Boundary
ALWAYS stop after this phase. Present the plan to the human and wait for approval. Save state and end the session. The human resumes with `/ticket {{ticket_id}}`.
