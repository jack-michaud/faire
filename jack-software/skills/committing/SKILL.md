---
name: Committing
description: Any time committing changes is mentioned, use this commit flow.
---

You are staff engineer committing a commit message.

- Check for `jj` - Use that by default.
  - `jj` commits all files by default (no staging step needed).
  - If there are files in the revision you don't want committed, first add them to `.gitignore`, then run `jj file untrack <paths>` to remove them from tracking.
  - Use `jj describe -m "<message>" && jj new` if you're on a revision with changes

Commit message format:
- Under 50 lines
- Brief but descriptive

## Constraints

- Never use `--into` together with `-r` in `jj squash` — these flags conflict
- Never squash into an immutable (already-pushed) parent; make a separate commit instead

# Resources

Custom docs written on committing topics:

- `resources/jj-advanced-workflows.md`
