# Research: Plugin Ship Command

**Date**: 2026-03-22

## R1: jj Workspace Isolation Flow

**Decision**: Use `jj workspace add` to create an ephemeral workspace from `main@origin` for faire modifications.

**Rationale**: jj workspaces create a second working copy attached to the same repo. This lets the command make changes in isolation without affecting the developer's in-progress work in the main workspace. The workspace is created, used for the atomic change, and then forgotten.

**Concrete flow**:
```bash
# From faire repo root (~/Code/github.com/jack-michaud/faire)
jj git fetch                                          # Update remote tracking refs
jj workspace add /tmp/faire-ship-XXXX -r main@origin  # Create workspace at temp dir
cd /tmp/faire-ship-XXXX                                # Work in the workspace

# ... make changes, validate, bump version ...

jj describe -m "feat: <commit message>"               # Describe the working copy commit
jj bookmark set main -r @                             # Move main bookmark to this commit
jj git push -b main                                   # Push to remote

# Cleanup
cd -                                                  # Return to original dir
jj workspace forget faire-ship-XXXX                   # Remove workspace (from main repo)
rm -rf /tmp/faire-ship-XXXX                           # Clean up working copy dir
```

**Alternatives considered**:
- Git worktrees: Not applicable — project uses jj, not raw git.
- Working in main workspace with stash: Would risk conflicts with in-progress work; jj doesn't have a traditional stash. The workspace approach is cleaner.
- Creating a branch instead: Adds unnecessary branch management overhead. The workspace approach pushes directly to main, matching the existing `/ship` workflow.

## R2: Command Design — Single vs. Multiple Commands

**Decision**: Single slash command (`/ship-skill`) that handles both procedures and components through its argument format.

**Rationale**: The existing `/add-procedure` command already determines placement and type from the description. Adding a separate `/ship-component` would fragment the workflow. A single command keeps the UX simple — "I want to ship this to the marketplace" — and uses argument patterns to disambiguate:
- `/ship-skill add a procedure for deploying to staging` → procedure mode
- `/ship-skill add a command to jack-software that formats markdown` → component mode (explicit plugin + type)

**Alternatives considered**:
- Two separate commands (`/ship-procedure`, `/ship-component`): More explicit but fragments the "ship" concept. Rejected per Simplicity First.
- Extending existing `/ship` command: The current `/ship` is a projet-specific command for the faire repo (in `.claude/commands/`), not a plugin command. It only works when you're already in the faire repo. The new command must be a plugin command available everywhere.

## R3: Validation Approach

**Decision**: Inline validation in the slash command prompt (no separate script).

**Rationale**: The validation checks are simple enough to express as prompt instructions:
1. Read the modified SKILL.md and check for `name` and `description` in YAML frontmatter
2. Read the modified `plugin.json` and check it's valid JSON with an incremented version
3. If validation fails, report and stop

A separate validation script would be over-engineering for 2-3 simple checks that Claude can perform directly via Read tool.

**Alternatives considered**:
- Bash validation script: Would add a script file, Makefile target, and complexity. The checks are too simple to warrant this.
- Python validation script: Even more overhead. Rejected.

## R4: Local Project Commit Isolation

**Decision**: Use `jj split` to isolate new skill/procedure files into their own commit when adding to a local project.

**Rationale**: When the developer is working on a local project, their working copy likely has other in-progress changes. The new skill files need to go in their own commit. `jj split` with filesets targeting the new files achieves this: `JJ_EDITOR=true jj split <new-files>` puts the new files in one commit and everything else stays in the working copy.

**Alternatives considered**:
- `jj new` first then make changes: Would lose the developer's current working copy context. Bad UX.
- Just commit everything together: Violates the spec requirement for a dedicated commit.

## R5: Reuse of Existing Add-Procedure Logic

**Decision**: Embed the add-procedure workflow directly in the `/ship-skill` command prompt, referencing but not literally including the `/add-procedure` command.

**Rationale**: The `/ship-skill` command needs to orchestrate a multi-step workflow where procedure writing is one step. The existing `/add-procedure` logic (determine placement, inventory skills, find best home, write the procedure) can be referenced as instructions in the new command. This avoids creating a dependency on another command while reusing the proven patterns.

**Alternatives considered**:
- Calling `/add-procedure` as a sub-step: Slash commands can't invoke other slash commands. Would need to restructure as a script.
- Extracting shared logic to a skill: Would add indirection. The procedure-writing instructions are simple enough to inline.

## R6: Testing Strategy

**Decision**: Agent SDK test script that invokes the command and asserts on side effects.

**Rationale**: The command is a slash command (prompt-based), so testing it means verifying Claude follows the instructions correctly end-to-end. A Python script using `claude-agent-sdk` can invoke `/ship-skill` with a test description, then assert on the expected file system state:
- Was the SKILL.md created with valid frontmatter?
- Was the plugin version bumped?
- Does a commit exist with the expected message?
- Was the push successful (or, in dry-run mode, would it have been)?

This is the same pattern as the existing `scripts/add-procedure.py` — proven and automatable.

**Concrete approach**:
1. Create `scripts/test-ship-skill.py` using `claude-agent-sdk`
2. Invoke `/jack-software:ship-skill <test description>` against a test workspace
3. After completion, verify:
   - File exists at expected path with valid YAML frontmatter
   - `plugin.json` version is incremented
   - `jj log` shows a commit with the expected message
   - Workspace was cleaned up
4. Clean up test artifacts

**Alternatives considered**:
- Manual testing only: Not reproducible, requires human involvement. Rejected.
- Unit tests on a validation script: Would only test validation, not the full workflow. The Agent SDK approach tests the whole thing.
- Dry-run flag: Could be added later as a convenience, but the Agent SDK test with a real (but disposable) workspace is the more thorough test.
