# jj Advanced Commit Workflows

## Context
Covers advanced `jj` patterns for splitting changes across multiple commits, squashing revisions, and version bumping reminders when updating plugins.

## Process

### Splitting a revision into multiple commits

When the working copy contains changes that belong to different logical commits:

1. Use `jj split <filesets>` to split the current revision into two. Files matching the filesets go into the first commit; all remaining files go into the second.
2. To skip the interactive diff editor and accept defaults, prefix with `JJ_EDITOR=true`:
   ```
   JJ_EDITOR=true jj split <filesets>
   ```
3. After splitting, describe each resulting revision:
   ```
   jj describe -r <rev-id> -m "message for first commit"
   jj describe -r <rev-id> -m "message for second commit"
   ```

### Squashing a revision into its parent

Use `jj squash -r <rev>` to fold a revision into its parent.

Important constraints:
- Do NOT use `--into` together with `-r` — these flags conflict.
- If the parent revision is immutable (already pushed to main), squash will fail. In that case, make a separate commit instead.

### Version bumping when updating plugins

When adding new commands, skills, or other components to a plugin, always bump the patch version immediately after:

```
make bump-patch PLUGIN=<plugin-name>
```

The bump script updates both `plugin.json` and `.claude-plugin/marketplace.json` in one step.

## Commands

```bash
# Split working copy — interactive editor
jj split <filesets>

# Split working copy — skip interactive editor
JJ_EDITOR=true jj split <filesets>

# Describe a specific revision after splitting
jj describe -r <rev-id> -m "<message>"

# Squash a revision into its parent
jj squash -r <rev>

# Bump plugin patch version
make bump-patch PLUGIN=<plugin-name>
```
