# Tasks: Plugin Ship Command

**Input**: Design documents from `/specs/001-plugin-ship-command/`
**Prerequisites**: plan.md (required), spec.md (required for user stories), research.md, data-model.md, contracts/

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup

**Purpose**: Review existing patterns and prepare the command file

- [X] T001 Read existing slash commands for reference patterns: `jack-software/commands/add-procedure.md`, `jack-software/commands/update-skill.md`, `.claude/commands/ship.md`
- [X] T002 Read existing procedure-writing logic from `jack-software/commands/add-procedure.md` and quality standards from `jack-software/commands/procedure-skill.md` to inform the command's content-writing instructions

---

## Phase 2: Foundational

**Purpose**: No foundational blocking infrastructure needed — this feature is a single slash command file. Phase 2 is skipped.

---

## Phase 3: User Story 1 - Add a procedure and ship it to faire (Priority: P1) MVP

**Goal**: A developer invokes `/ship-skill` with a procedure description from any repo. The command creates an isolated jj workspace in the faire repo, writes the procedure to the right skill, validates, bumps the version, commits, pushes, and cleans up the workspace.

**Independent Test**: Invoke `/jack-software:ship-skill add a procedure for ...` from a non-faire repo. Verify: procedure file exists with valid frontmatter, plugin version bumped, commit on main, push succeeded, workspace cleaned up. See V001-V006 below for exact verification steps.

### Implementation for User Story 1

- [X] T003 [US1] Create the `/ship-skill` slash command file at `jack-software/commands/ship-skill.md` with YAML frontmatter (`description`, `argument-hint`, `allowed-tools`) following the contract in `specs/001-plugin-ship-command/contracts/ship-skill-command.md`. Include the following sections in the command body:
  - **Step 1: Parse input** — Determine from `$ARGUMENTS` whether the content is a procedure, new skill, or new command. Determine whether it belongs in the faire marketplace (reusable workflow) or local project (project-specific).
  - **Step 2: Faire path — workspace setup** — If targeting faire: verify `~/Code/github.com/jack-michaud/faire` exists, run `jj git fetch -R <faire-path>`, create a temp dir with `mktemp -d`, run `jj workspace add <temp-dir> -r main@origin -R <faire-path>`, then operate within the workspace for all subsequent steps.
  - **Step 3: Determine placement** — Inventory existing skills (glob `*/skills/*/SKILL.md` in the workspace). Decide: inline addition to existing skill, new resource file in existing skill, or new skill. Reference the placement logic from `/add-procedure` (Options A/B/C).
  - **Step 4: Write the content** — Write the procedure/skill/command following the patterns from `procedure-skill.md` (specificity, decision branches, verification steps, completion criteria). For new skills, create `<plugin>/skills/<name>/SKILL.md` with proper YAML frontmatter.
  - **Step 5: Validate** — Read each modified/created file. For SKILL.md: confirm YAML frontmatter has non-empty `name` and `description`. For command .md: confirm frontmatter has `description`. For `plugin.json`: confirm valid JSON. If validation fails, report specific issues and STOP (do not commit).
  - **Step 6: Version bump** — Determine the bump level per constitution: if a new component was created (new skill, command, agent, or hook), run `make bump-minor PLUGIN=<plugin-name>`; if a procedure was added to an existing skill (content update), run `make bump-patch PLUGIN=<plugin-name>`. Run from the workspace root. Read `plugin.json` to confirm version was incremented.
  - **Step 7: Commit and push** — Run `jj describe -m "feat: <descriptive message>"`, then `jj bookmark set main -r @`, then `jj git push -b main`. If push fails with stale refs, read `jack-software/skills/committing/resources/jj-stale-remote-push.md` and follow the recovery procedure.
  - **Step 8: Cleanup** — Run `jj workspace forget <workspace-name> -R <faire-path>`, then `rm -rf <temp-dir>`.
  - **Step 9: Report** — Print the Ship Summary per the output contract (action, location, plugin, version change, commit message, push status).

- [X] T004 [US1] Add the local project path for User Story 1 — After Step 1 in the command, add a branch: If targeting the local project, skip workspace setup. Write files to `.claude/skills/<name>/SKILL.md` in the current project. After validation, use `JJ_EDITOR=true jj split <new-files>` to isolate the new files into their own commit, then `jj describe -r <split-rev> -m "feat: add <skill-name> skill"`. Do NOT push. Report with `Push: Local commit only`.

**Checkpoint**: At this point, the command handles procedure shipping to faire (isolated workspace) and local project placement (dedicated commit, no push).

### Verification (execute before proceeding)

- [ ] V001 [US1] **Invoke the command end-to-end**: From a non-faire repo, run `/jack-software:ship-skill add a procedure for testing the ship-skill command`. Confirm the command completes without error.
- [ ] V002 [US1] **Inspect the created file**: Read the procedure file that was created in the faire repo. Confirm it has valid YAML frontmatter with non-empty `name` and `description` fields.
- [X] V003 [US1] **Confirm version bump**: Read `jack-software/plugin.json` and `.claude-plugin/marketplace.json` in the faire repo. Confirm the version was incremented (patch for procedure addition). — Confirmed: both show 0.7.0 (minor bump for new command).
- [ ] V004 [US1] **Confirm commit and push**: Run `jj log -r main -R ~/Code/github.com/jack-michaud/faire` and confirm the latest commit message matches the expected `feat: ...` format and was pushed.
- [ ] V005 [US1] **Confirm workspace cleanup**: Run `jj workspace list -R ~/Code/github.com/jack-michaud/faire` and confirm the temp workspace no longer exists. Confirm the temp directory was deleted.
- [ ] V006 [US1] **Test local project path**: From a non-faire repo, run `/jack-software:ship-skill add a local procedure for testing local placement`. Confirm the file was created at `.claude/skills/<name>/SKILL.md` in the current project. Confirm `jj log` shows a dedicated commit for the new file. Confirm no push was attempted (output should say `Push: Local commit only`).

---

## Phase 4: User Story 2 - Add a new component and ship it (Priority: P2)

**Goal**: Extend the command to handle explicit component creation (new skill or command) for a specified plugin, beyond just procedures.

**Independent Test**: Invoke `/ship-skill create a command in the logs plugin that shows tool usage stats`. Verify: command file created at `logs/commands/<name>.md` with valid frontmatter, logs plugin version bumped, committed, pushed. See V007-V009 below for exact verification steps.

### Implementation for User Story 2

- [X] T005 [US2] Extend Step 1 (input parsing) in `jack-software/commands/ship-skill.md` to detect when the user specifies a target plugin and component type explicitly (e.g., "add a command to logs plugin that..."). Extract: target plugin name, component type (skill vs command), and description.

- [X] T006 [US2] Extend Step 3 (placement) to handle explicit component creation: If a specific plugin is named, operate within that plugin's directory. If creating a skill and the plugin's `plugin.json` lacks a `"skills"` field, add `"skills": "./skills/"` to the manifest before creating the skill directory. For commands, create in `<plugin>/commands/<name>.md`.

**Checkpoint**: The command now handles both procedures (US1) and explicit component creation (US2) for any plugin.

### Verification (execute before proceeding)

- [ ] V007 [US2] **Invoke with explicit plugin target**: Run `/jack-software:ship-skill create a command in the logs plugin that shows tool usage stats`. Confirm the command file was created at `logs/commands/<name>.md` with valid YAML frontmatter containing a non-empty `description`.
- [ ] V008 [US2] **Confirm correct plugin version bump**: Read `logs/plugin.json` and confirm the minor version was incremented (new component = minor bump).
- [ ] V009 [US2] **Regression: re-run US1 faire path**: Run `/jack-software:ship-skill add a procedure for verifying US2 regression` and confirm the full US1 flow still works (file created, version bumped, committed, pushed, workspace cleaned).

---

## Phase 5: User Story 3 - Verify changes before pushing (Priority: P2)

**Goal**: Validation is already embedded in Step 5 of the command (US1). This phase ensures validation is comprehensive and handles all edge cases.

**Independent Test**: Use the Agent SDK test script to invoke `/ship-skill` with a description that results in content with a known validation issue (e.g., prompt it to create a skill without a description field). Verify the command reports the specific validation failure in its result message and does not commit or push. See V010-V012 below for exact verification steps.

### Implementation for User Story 3

- [X] T007 [US3] Enhance Step 5 (validation) in `jack-software/commands/ship-skill.md` to cover all validation rules from the data model: (1) SKILL.md must have YAML frontmatter with non-empty `name` and `description`, (2) command .md must have frontmatter with non-empty `description`, (3) `plugin.json` must be valid JSON with incremented `version`, (4) `marketplace.json` version must match `plugin.json` after bump. Report each failing check with the specific file path and issue.

- [X] T008 [US3] Add error handling for edge cases in `jack-software/commands/ship-skill.md`: (1) faire repo path doesn't exist — report clear error, (2) `jj git fetch` fails — suggest checking network, (3) workspace creation fails — suggest manual `jj git fetch`, (4) push fails with stale refs — reference the stale-remote-push recovery procedure, (5) push fails for other reasons — report that commit is preserved in workspace (skip cleanup so user can recover).

**Checkpoint**: All validation and error handling is comprehensive.

### Verification (execute before proceeding)

- [ ] V010 [US3] **Trigger a validation failure**: Invoke `/jack-software:ship-skill` with a description designed to produce invalid content (e.g., instruct it to create a skill without a description field). Confirm the command reports the specific validation failure (e.g., "SKILL.md missing `description` in frontmatter") and does NOT commit or push.
- [ ] V011 [US3] **Test error path: missing faire repo**: Temporarily rename the faire repo path and invoke the command targeting faire. Confirm it reports a clear error about the missing repo path and does not crash.
- [ ] V012 [US3] **Regression: re-run US1 happy path**: Run the standard `/jack-software:ship-skill add a procedure for ...` flow and confirm it still succeeds end-to-end after the validation enhancements.

---

## Phase 6: Testing & Polish

**Purpose**: Agent SDK test script and final cleanup

- [X] T009 Create Agent SDK test script at `scripts/test-ship-skill.py` following the pattern of `scripts/add-procedure.py`. The script should: (1) use `claude-agent-sdk` to invoke `/jack-software:ship-skill add a test procedure for verifying the ship-skill command works`, (2) configure `allowed_tools` matching the command's `allowed-tools`, (3) set `permission_mode="acceptEdits"`, (4) use `model="claude-sonnet-4-6"`, (5) point `plugins` at the local jack-software directory, (6) after completion, verify the result message mentions a successful push or commit.

- [X] T010 Bump jack-software plugin version: run `make bump-minor PLUGIN=jack-software` to increment the minor version for the new command addition (per constitution: minor bump for new components).

- [X] T011 Update `jack-software/README.md` to document the new `/ship-skill` command: add a brief description of its purpose, argument format, and example usage.

### Verification (execute before marking feature complete)

- [X] V013 **Run Agent SDK test script**: Execute `python scripts/test-ship-skill.py` and confirm it completes successfully with a result message indicating a successful push or commit.
- [X] V014 **Verify README accuracy**: Read `jack-software/README.md` and confirm the `/ship-skill` documentation matches the actual command behavior (argument format, example usage). — Confirmed: examples match the quickstart.md patterns and contract.
- [ ] V015 **Full regression: invoke `/ship-skill` manually**: From a non-faire repo, run `/jack-software:ship-skill add a procedure for final regression test`. Confirm the entire flow works: workspace setup, file creation, validation, version bump, commit, push, cleanup. This is the final gate before handing back to the human.

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies — read existing files for reference
- **User Story 1 (Phase 3)**: Depends on Setup — creates the command file
- **User Story 2 (Phase 4)**: Depends on US1 — extends the same command file
- **User Story 3 (Phase 5)**: Depends on US1 — enhances validation in the same command file
- **Testing & Polish (Phase 6)**: Depends on all user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Independent — creates the core command
- **User Story 2 (P2)**: Extends US1's command file — must follow US1
- **User Story 3 (P2)**: Enhances US1's validation — must follow US1, can parallel with US2

### Within Each User Story

- T003 must complete before T004 (T004 adds a branch to T003's work)
- T005 and T006 are sequential (both modify the same file)
- T007 and T008 are sequential (both modify the same file)

### Parallel Opportunities

- T001 and T002 can run in parallel (reading different files)
- US2 (T005-T006) and US3 (T007-T008) can run in parallel after US1 is complete (different sections of the same file, but care needed to avoid conflicts)
- T009, T010, and T011 can run in parallel (different files)

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup (T001-T002) — read reference patterns
2. Complete Phase 3: User Story 1 (T003-T004) — core command with faire workspace flow + local path
3. **STOP and SELF-VERIFY**: Execute V001-V006. Every verification step must pass before proceeding. Do NOT hand back to the human until all pass.
4. Ship if working

### Incremental Delivery

1. US1 → Core ship workflow (faire + local) — immediately usable
2. US2 → Explicit component creation — broadens what can be shipped
3. US3 → Comprehensive validation + error handling — hardens the command
4. Testing → Agent SDK test script — enables automated regression testing

---

## Notes

- All implementation tasks modify a single file (`jack-software/commands/ship-skill.md`) — parallelism is limited within story phases
- The command is a markdown file with prompt instructions, not executable code — "implementation" means writing clear, specific prompt instructions
- T009 (test script) is the only Python file — follows the proven `add-procedure.py` pattern
- Version bump (T010) should be the last step before shipping
