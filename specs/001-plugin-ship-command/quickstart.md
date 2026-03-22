# Quickstart: Plugin Ship Command

## Prerequisites

- Claude Code with `jack-software` plugin installed
- `jj` installed and configured
- Faire repo cloned at `~/Code/github.com/jack-michaud/faire`

## Usage

From any Claude Code session:

```
/ship-skill add a procedure for recovering from failed deployments
```

The command will:
1. Determine this belongs in the faire marketplace
2. Create an isolated jj workspace in the faire repo
3. Find the right skill to place the procedure
4. Write the procedure
5. Validate the changes
6. Bump the plugin version
7. Commit and push to main
8. Clean up the workspace

## Examples

### Add a procedure to an existing faire skill
```
/ship-skill add a procedure to the committing skill for squashing revisions
```

### Add a project-specific skill (local, no push)
```
/ship-skill create a skill for this project's database migration process
```

### Add a new command to a faire plugin
```
/ship-skill add a command to the logs plugin that shows error frequency
```

## Verification

After running, check:
- The ship summary shows the correct file path and version bump
- For faire changes: `jj log` in the faire repo shows the new commit on `main`
- For local changes: `jj log` in the current repo shows the dedicated commit
