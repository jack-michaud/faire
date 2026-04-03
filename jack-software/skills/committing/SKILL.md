---
name: committing
description: "Commit workflow using jj (Jujutsu) version control. Use when committing changes, describing revisions, splitting commits, or pushing to remote — covers jj describe, jj split, jj new, and jj git push with troubleshooting for stale remote errors."
---

# Committing

Commit flow for projects using `jj` (Jujutsu) as the version control system.

## Standard Commit Flow

1. **Check for `jj`** — use it by default over git
2. `jj` commits all files automatically (no staging step needed)
3. Use `jj describe -m "<message>" && jj new` when the current revision has changes

## Splitting Commits

When the working copy has changes that belong to different commits:

1. `JJ_EDITOR=true jj split <filesets>` — files matching the filesets go in the first revision, the rest in the second
2. `jj describe -r <rev-id> -m "message"` for each resulting revision

## Commit Message Format

- Under 50 characters for the subject line
- Brief but descriptive
- Use imperative mood ("Add feature" not "Added feature")

## Troubleshooting

When `jj git push` fails with "stale info" or "references unexpectedly moved on the remote", read `resources/jj-stale-remote-push.md` for the fix procedure.

# Resources

- `resources/jj-stale-remote-push.md` — Fix procedure for stale remote push errors
