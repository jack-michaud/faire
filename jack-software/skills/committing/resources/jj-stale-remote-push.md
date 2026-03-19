# Fixing `jj git push` stale remote ref failures

When `jj git push` fails with:
```
Error: Failed to push some bookmarks
Hint: The following references unexpectedly moved on the remote:
  refs/heads/<branch> (reason: stale info)
```

This means the remote branch was updated (e.g. GitHub "Update branch" button, another push) since your last fetch.

## Fix procedure

1. **Fetch** to update remote tracking refs:
   ```
   jj git fetch --remote origin
   ```

2. **Inspect the graph** to see how local and remote diverged:
   ```
   jj log -r 'ancestors(@, 5) | <bookmark>@origin'
   ```
   Look for where `<bookmark>@origin` and your local commit diverge.

3. **Rebase** your local commits onto the remote tip using `::` to include all descendants:
   ```
   jj rebase -r <local-commit>:: -d <remote-tip>
   ```
   - `<local-commit>`: the first local commit that diverged (change ID from `jj log`)
   - `<remote-tip>`: the `<bookmark>@origin` revision
   - The `::` suffix recursively rebases the commit and all its descendants, including your working copy

4. **Push**:
   ```
   jj bookmark set <bookmark> -r <tip-commit>
   jj git push --bookmark <bookmark>
   ```

5. **Create a new empty working copy** after pushing:
   ```
   jj new
   ```

## Verification

After pushing, `jj log` should show your bookmark and `<bookmark>@origin` pointing to the same commit.
