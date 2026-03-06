# Verification

## Context
Run the full test suite, linting, and type checking across the entire project. This catches integration issues that per-component testing might miss.

## Agents

### Agent: full-verifier
- **Type**: general-purpose
- **Instructions**: |
    Run comprehensive verification on the project:

    1. **Full test suite**: Run all tests (not just the ones for changed components)
       - Look for test run commands in package.json scripts, Makefile, or CI config
       - Common commands: `npm test`, `pnpm test`, `pytest`, `cargo test`

    2. **Linting**: Run the project's linter
       - Common commands: `npm run lint`, `pnpm lint`, `eslint .`, `ruff check .`

    3. **Type checking**: Run type checker if applicable
       - Common commands: `tsc --noEmit`, `mypy .`, `pyright`

    4. **Coverage**: Check test coverage if configured
       - Report coverage percentage
       - Flag if below 80% threshold

    Report results for each check:
    - PASS/FAIL status
    - Error details if failed
    - Coverage percentage if available

    Do NOT fix any issues -- just report them.

- **Output**: Verification results for each check (test, lint, typecheck, coverage)

## Coordination
Single agent. No coordination needed.

## Output Contract
Store in `phases.verification.data`:
- tests (object: {status, details, coverage_percent})
- lint (object: {status, details})
- typecheck (object: {status, details})
- all_passed (boolean)

## Failure Handling
If any verification check fails:
1. Report all failures
2. Transition back to implementation phase with failure details
3. The implementation phase will spawn fix agents for each failure
4. After fixes, verification runs again
5. Max 3 verification-implementation cycles before stopping
