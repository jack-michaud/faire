---
name: stacked-pr-review
description: Use when addressing PR review comments on stacked jj branches. Triggered by phrases like "address review comments", "fix PR feedback", "respond to review on stacked branch", or "update the PR with reviewer suggestions".
---

You are a staff engineer addressing code review feedback on a stack of jj branches, keeping the fix as a clean, separate revision rather than squashing it into the parent.

## Process

1. **Read PR review comments** using `gh api`:
   ```bash
   gh api repos/{owner}/{repo}/pulls/{pr_number}/comments
   ```
   Identify which branch the PR targets (this is the "target bookmark").

2. **Navigate to the target branch** by creating a new revision on top of it:
   ```bash
   jj new <target-bookmark>
   ```
   This places the working copy directly on the target branch, ready for the fix.

3. **Make code changes** to address the review comments. Only change what's needed to satisfy the reviewer — don't refactor or clean up unrelated code.

4. **Describe the fix** with a concise commit message:
   ```bash
   jj describe -m "address review: <brief description of what was fixed>"
   ```

5. **Identify downstream stacked branches** — these are any branches that were originally built on the target bookmark and now need to be rebased onto the fix:
   ```bash
   jj log --revisions 'descendants(<target-bookmark>)' --no-graph
   ```
   Note the revision IDs of any downstream branches.

6. **Rebase downstream branches** onto the fix:
   ```bash
   jj rebase -s <downstream-rev-id> -d @
   ```
   Run this for each downstream branch that needs to move. `@` refers to the current fix revision.

7. **Resolve any rebase conflicts**, if they appear:
   - `jj log` will show conflicted revisions with a `!` marker.
   - For each conflicted revision:
     1. `jj new <conflicted-rev-id>` — create a resolution revision on top of it
     2. Edit the conflicted files to resolve the markers (`<<<`, `===`, `>>>`)
     3. Verify the file looks correct
     4. `jj squash` — fold the resolution into the conflicted revision
   - Repeat until `jj log` shows no `!` markers.

8. **Retag bookmarks** to point to the updated revisions:
   ```bash
   jj bookmark set <bookmark-name> -r <rev-id>
   ```
   Do this for each downstream bookmark that moved during the rebase.

9. **Push all affected branches** in one command:
   ```bash
   jj git push --bookmark <bookmark1> --bookmark <bookmark2> ...
   ```
   Include the fix revision's bookmark AND all downstream bookmarks.

10. **Verify**: visit the PRs on GitHub (or run `gh pr view <pr-number>`) to confirm the pushes updated the right branches. Check that CI is triggered.

## Key Rules

- **Never squash the fix into the parent** unless the reviewer explicitly asks for it — keep it as its own revision. This preserves the review history.
- **Never force-push main/master** — only push to feature branches.
- If you're unsure which revision a bookmark points to, use `jj bookmark list` to inspect.

## Completion Criteria

- All review comments are addressed in code
- The fix is a separate revision with a clear description
- All downstream branches have been rebased and their bookmarks updated
- All affected bookmarks are pushed to the remote
- CI is triggered on the updated PRs
