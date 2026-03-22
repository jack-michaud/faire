# Implementation Plan: Plugin Ship Command

**Branch**: `001-plugin-ship-command` | **Date**: 2026-03-22 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `/specs/001-plugin-ship-command/spec.md`

## Summary

Create a unified slash command (`/ship-skill`) in the `jack-software` plugin that automates the full lifecycle of adding procedures or components to the faire marketplace (or local project): write content, validate, bump version, commit, and push. For faire changes, the command uses an isolated jj workspace from `main@origin` to avoid interfering with in-progress work. For local changes, it writes and commits in a dedicated commit without pushing.

## Technical Context

**Language/Version**: Markdown (slash command), Python (Agent SDK test script)
**Primary Dependencies**: jj (VCS), make (version bumping), Claude Code plugin system
**Storage**: File system (markdown files, JSON configs)
**Testing**: Agent SDK test script (`scripts/test-ship-skill.py`) that invokes the command and asserts on file system side effects
**Target Platform**: macOS (developer workstation with Claude Code installed)
**Project Type**: CLI plugin (Claude Code slash command)
**Performance Goals**: N/A (single-user interactive tool)
**Constraints**: Must work from any directory; must not disturb in-progress faire work
**Scale/Scope**: Single developer, single marketplace repo

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Plugin Independence | PASS | Adds to jack-software only; no cross-plugin dependencies |
| II. Convention-Driven Components | PASS | Follows slash command pattern (markdown + YAML frontmatter); reuses existing procedure-writing patterns |
| III. Simplicity First | PASS | Single slash command + one validation script; reuses existing `make bump-patch`, committing skill, and `/add-procedure` patterns |
| Versioning (patch bump) | REQUIRED | Must bump jack-software patch version when shipping |
| Automate the Rote | ALIGNED | This feature IS automating the rote (the manual add → validate → bump → commit → push cycle) |

**Gate result**: PASS — no violations.

## Project Structure

### Documentation (this feature)

```text
specs/001-plugin-ship-command/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/           # Phase 1 output
└── tasks.md             # Phase 2 output (/speckit.tasks command)
```

### Source Code (repository root)

```text
jack-software/
├── commands/
│   └── ship-skill.md        # NEW: The unified ship command
├── skills/
│   └── committing/
│       └── SKILL.md          # EXISTING: Referenced for commit workflow
└── plugin.json               # EXISTING: Version bump target

scripts/
└── test-ship-skill.py        # NEW: Agent SDK test script
```

**Structure Decision**: This feature adds a single slash command file to the existing `jack-software/commands/` directory plus a test script in `scripts/`. Validation is embedded in the command's prompt instructions (checking YAML frontmatter and JSON validity inline). The test script uses `claude-agent-sdk` to invoke the command and verify side effects, following the same pattern as `scripts/add-procedure.py`.

## Complexity Tracking

No violations to justify.
