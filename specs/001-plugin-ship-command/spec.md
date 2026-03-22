# Feature Specification: Plugin Ship Command

**Feature Branch**: `001-plugin-ship-command`
**Created**: 2026-03-22
**Status**: Draft
**Input**: User description: "I want to define a command that I can run that will update, test/verify, commit, and push new skills or plugins. It's finishing what scripts/add-procedure.py and scripts/add-component.py started. The goal is to be able to run a skill from any repo or claude code session and have it automatically make the update and push it to github."

## Clarifications

### Session 2026-03-22

- Q: Should adding a procedure to the local project also push to main? → A: No. Only modifications to the faire marketplace trigger a push to main. Local project changes are written and committed locally only.
- Q: How should faire modifications be isolated from in-progress work? → A: Use a jj workspace. The flow is: `jj git fetch`, create a new workspace from `main@origin`, make changes in that workspace, then commit and push. This keeps faire modifications isolated from any in-progress work in the main workspace.
- Q: When adding to the local project (no push), what level of automation? → A: Write the files and commit locally in their own dedicated commit (no push). The changes must be in a separate commit from any other in-progress work.
- Q: Should the jj workspace be cleaned up after a successful push? → A: Yes, auto-cleanup. Delete the workspace after a successful push.

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Add a procedure and ship it to faire (Priority: P1)

A developer is working in any Claude Code session (in any repo) and discovers a useful workflow they want to capture as a procedure in the faire marketplace. They invoke a single command with a description of the procedure. The system creates an isolated jj workspace in the faire repo (fetching latest from origin, creating a workspace from `main@origin`), determines the right skill to place the procedure in, writes it, bumps the plugin version, commits the changes, and pushes to GitHub — all without the developer leaving their current session or disturbing any in-progress work in the faire repo.

**Why this priority**: This is the core use case that the existing `add-procedure.py` script already partially handles. Completing this end-to-end flow delivers the primary value — turning a multi-step manual process into one command.

**Independent Test**: Can be tested by invoking the command with a procedure description and verifying that a new procedure appears in the faire repo via a new jj workspace, the plugin version is bumped, a commit exists, and the changes are pushed to `main`.

**Acceptance Scenarios**:

1. **Given** a developer is in a Claude Code session in any repository, **When** they invoke the command with a procedure description, **Then** the system creates an isolated jj workspace in the faire repo from `main@origin`, writes the procedure to the correct skill, bumps the plugin version, commits, and pushes to `main`.
2. **Given** the procedure naturally belongs in an existing skill, **When** the command runs, **Then** it adds the procedure to that skill (inline or as a resource file) rather than creating a new skill.
3. **Given** no existing skill matches the procedure, **When** the command runs, **Then** it creates a new skill with proper SKILL.md structure, updates `plugin.json` if needed, and ships the result.
4. **Given** the faire repo has in-progress work in its main workspace, **When** the command runs, **Then** the workspace-based flow keeps changes isolated and does not affect the existing workspace.

---

### User Story 2 - Add a new component and ship it (Priority: P2)

A developer wants to add a brand new skill or slash command to a specific plugin in the faire marketplace. They invoke the command specifying the plugin, component type, and a description. The system creates the component files following existing patterns, bumps the plugin version, commits, and pushes.

**Why this priority**: Extends the same ship workflow to cover `add-component.py`'s use case, broadening the types of marketplace contributions that can be shipped in one step.

**Independent Test**: Can be tested by invoking the command to create a new skill or command in a named plugin, then verifying the component was created with correct structure, version was bumped, and changes were pushed.

**Acceptance Scenarios**:

1. **Given** a developer specifies a plugin and component type (skill or command), **When** they invoke the command with a description, **Then** the component is created following the plugin's existing patterns, version is bumped, committed, and pushed.
2. **Given** the target plugin doesn't have a `skills` field in its `plugin.json` and a skill is being added, **When** the command runs, **Then** it adds `"skills": "./skills/"` to the plugin config before creating the skill.

---

### User Story 3 - Verify changes before pushing (Priority: P2)

Before committing and pushing, the system validates that the changes are well-formed: the SKILL.md has valid frontmatter, the `plugin.json` is valid JSON with a bumped version, and no obvious structural issues exist.

**Why this priority**: Prevents shipping broken skills or plugins that would fail when installed. Catches mistakes before they reach `main`.

**Independent Test**: Can be tested by intentionally creating a malformed skill (e.g., missing frontmatter) and verifying the command reports the issue and does not push.

**Acceptance Scenarios**:

1. **Given** changes include a new or modified SKILL.md, **When** the verification step runs, **Then** it confirms the file has valid YAML frontmatter with `name` and `description` fields.
2. **Given** a `plugin.json` was modified, **When** the verification step runs, **Then** it confirms the file is valid JSON and the version was incremented.
3. **Given** verification finds issues, **When** the issues are reported, **Then** the command stops before committing and reports what needs to be fixed.

---

### Edge Cases

- What happens when `jj git push` fails due to stale refs? The command should follow the existing stale-remote-push recovery procedure from the committing skill.
- What happens when the developer is offline or GitHub is unreachable? The command should commit locally in the workspace and report that the push failed, allowing the user to push later.
- What happens when the faire repo path doesn't exist on the machine? The command should fail with a clear error message.
- What happens when workspace creation fails (e.g., `main@origin` doesn't exist)? The command should report the issue and suggest running `jj git fetch` manually.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: The command MUST be invocable as a slash command from any Claude Code session, regardless of the current working directory.
- **FR-002**: The command MUST determine whether the procedure/component belongs in the faire marketplace or the local project based on the nature of the content (reusable vs. project-specific).
- **FR-003**: The command MUST write the procedure or component to the correct location following existing patterns (SKILL.md structure, command frontmatter, resource files).
- **FR-004**: The command MUST bump the version of the affected plugin using the appropriate semver level per the constitution: `make bump-minor` when adding a new component (new skill, command, agent, or hook), `make bump-patch` when adding a procedure to an existing skill or making content updates. This applies only when modifying faire marketplace plugins.
- **FR-005**: The command MUST commit changes using the project's jj-based commit workflow. For local project changes, the new files MUST be placed in their own dedicated commit, separate from any other in-progress work.
- **FR-006**: The command MUST push changes to GitHub after a successful commit, but ONLY when modifying the faire marketplace. Local project changes MUST NOT trigger a push.
- **FR-011**: When modifying the faire marketplace, the command MUST create an isolated jj workspace by: (1) running `jj git fetch`, (2) creating a new workspace from `main@origin`, (3) making all changes within that workspace, (4) committing and pushing from the workspace, and (5) deleting the workspace after a successful push. This ensures isolation from any in-progress work.
- **FR-007**: The command MUST validate that written files are well-formed before committing (valid YAML frontmatter in skills, valid JSON in plugin configs).
- **FR-008**: The command MUST report a summary of what was done: files created/modified, version bump, commit message, and push status.
- **FR-009**: The command MUST abort gracefully if validation fails, reporting specific issues without committing broken changes.
- **FR-010**: The command MUST work from outside the faire repository by operating on the faire repo at its known location.

### Key Entities

- **Procedure**: A step-by-step workflow added to a skill's SKILL.md or resources directory.
- **Component**: A skill (SKILL.md with frontmatter) or command (markdown with frontmatter) within a plugin.
- **Plugin**: A top-level directory in the faire repo with a `plugin.json` manifest.
- **Marketplace**: The collection of plugins defined in `.claude-plugin/marketplace.json`.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: A developer can go from "I want to capture this workflow" to "it's live on GitHub" in a single command invocation, without switching repositories or running multiple scripts.
- **SC-002**: 100% of shipped skills have valid YAML frontmatter with `name` and `description` fields.
- **SC-003**: 100% of shipped changes include a version bump for the affected plugin.
- **SC-004**: The command completes the full add-verify-commit-push cycle without manual intervention in the happy path.
- **SC-005**: When validation fails, the developer receives actionable feedback identifying exactly what needs to be fixed.

## Assumptions

- The faire repository is always located at `~/Code/github.com/jack-michaud/faire`.
- `jj` is the VCS tool used for all commit and push operations.
- The `make bump-patch` target and `bump-version.sh` script remain the canonical way to bump versions.
- The existing `/ship` command and committing skill patterns should be reused rather than reinvented.
- The command will be implemented as a slash command in the `jack-software` plugin (the primary development skills plugin).
- The default target plugin for general procedures is `jack-software`.
