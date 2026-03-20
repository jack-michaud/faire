---
name: merging-pr-stack
description: Use when merging a stack of stacked PRs with jj. Triggered by phrases like "merge the PR stack", "merge the stacked PRs", "land these PRs", or "merge the stack into main".
---

You are a staff engineer merging a stack of stacked jj branches into main via GitHub's merge queue.

## Process

### Phase 1: Pre-merge checks

1. **List the PR stack** from base to tip. If not provided, infer from `jj log` and `gh pr list`:
   ```bash
   jj log --revisions 'ancestors(@, 10) & bookmarks()' --no-graph
   gh pr list --state open
   ```
   Order them base-first (the PR closest to `main` merges first).

2. **Check CI on the base PR**:
   ```bash
   gh pr checks <base-pr-number>
   ```
   - If all checks pass: proceed to Phase 2.
   - If checks are failing: stop and report which checks failed. Do not proceed until CI is green.

### Phase 2: Merge the base PR

3. **Add the base PR to the merge queue** (preferred) or merge directly:
   ```bash
   gh pr merge <base-pr-number> --merge --auto
   ```
   - If the repo uses a merge queue, `--auto` will queue it automatically.
   - If merge queue is not configured, this merges immediately.

4. **Poll merge queue status** via GraphQL until the entry is merged or errored:
   ```bash
   gh api graphql -f query='
     query($owner: String!, $repo: String!, $number: Int!) {
       repository(owner: $owner, name: $repo) {
         pullRequest(number: $number) {
           mergeQueueEntry {
             state
             position
             estimatedTimeToMerge
           }
         }
       }
     }
   ' -f owner=<owner> -f repo=<repo> -F number=<base-pr-number>
   ```
   - `state` values: `QUEUED`, `AWAITING_CHECKS`, `MERGEABLE`, `MERGED`, `FAILED`, `LOCKED`
   - If `state` is `MERGED`: proceed to Phase 3.
   - If `state` is `FAILED` or `LOCKED`: stop and report the failure. Do not proceed with the rest of the stack.
   - If `state` is `QUEUED` or `AWAITING_CHECKS`: wait ~30s and poll again. Repeat until terminal state.
   - If no `mergeQueueEntry` (not using merge queue): check `gh pr view <number> --json state` — if `state` is `MERGED`, proceed.

### Phase 3: Rebase remaining stack onto main

5. **Fetch the updated remote**:
   ```bash
   jj git fetch
   ```

6. **Rebase remaining stack branches onto `main@origin`**:
   ```bash
   jj rebase -s <next-branch-bookmark> -d main@origin
   ```
   - Repeat for each remaining branch in the stack, base-first.
   - Alternatively, if the entire remaining stack is contiguous:
     ```bash
     jj rebase -s <next-branch-bookmark> -d main@origin
     ```
     jj will automatically carry descendants along.

7. **Resolve conflicts** if any appear (`jj log` shows `!` markers):
   - For each conflicted revision:
     1. `jj new <conflicted-rev-id>` — create resolution on top
     2. Edit conflicted files to resolve `<<<`/`===`/`>>>` markers
     3. `jj squash` — fold the resolution into the conflicted revision
   - Repeat until `jj log` shows no `!` markers.

8. **Verify base retargeting** — the next PR's base should now target `main`:
   ```bash
   gh pr view <next-pr-number> --json baseRefName
   ```
   - If `baseRefName` is still the old merged branch: update it:
     ```bash
     gh pr edit <next-pr-number> --base main
     ```

9. **Push the rebased branches**:
   ```bash
   jj git push --bookmark <next-branch> --bookmark <branch-after-that> ...
   ```
   Push all remaining stack branches in one command.

### Phase 4: Repeat for each remaining PR

10. **Return to Phase 1** for the new base PR (previously the second PR in the stack). Repeat Phases 1–3 until all PRs in the stack are merged.

## Completion Criteria

- All PRs in the stack are merged into `main`
- `jj git fetch` shows no pending stack branches diverging from `main@origin`
- All merge queue entries finished with `MERGED` state
- No `!` conflict markers remain in `jj log`
