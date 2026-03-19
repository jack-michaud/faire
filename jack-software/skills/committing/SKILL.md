---
name: Committing
description: Any time committing changes is mentioned, use this commit flow.
---

You are staff engineer committing a commit message.

- Check for `jj` - Use that by default.
  - `jj` commits all files by default (no staging step needed).
  - Use `jj describe -m "<message>" && jj new` if you're on a revision with changes

- If the working copy has changes that belong to different commits, use `jj split`:
  1. `JJ_EDITOR=true jj split <filesets>` — files matching the filesets go in the first revision, the rest in the second.
  2. `jj describe -r <rev-id> -m "message"` for each resulting revision.

Commit message format:
- Under 50 lines
- Brief but descriptive

- When `jj git push` fails with "stale info" or "references unexpectedly moved on the remote", read `resources/jj-stale-remote-push.md` for the fix procedure.
