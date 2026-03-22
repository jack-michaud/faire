# Workspace Survey

## Context

Before taking any action in a cmux session, survey the current workspace state. This gives you full context on what's running, where you are, and what surfaces are available — preventing mistakes like sending commands to the wrong pane or missing background processes.

Run this procedure at the start of any cmux session before creating splits, sending commands, or interacting with surfaces.

## Process

1. **Identify context and list workspaces** (run in parallel):

   ```bash
   cmux identify --json
   cmux list-workspaces --json
   ```

   - `identify` tells you the current workspace, pane, surface, and whether you're in a terminal or browser surface. The `caller` field is YOUR surface ref. The `focused` field is what the user is currently looking at (they may differ).
   - `list-workspaces` shows all workspaces across all windows.

2. **List panes in the current workspace**:

   ```bash
   cmux list-panes --workspace workspace:<id> --json
   ```

   Shows all panes and how many surfaces each has.

3. **List surfaces in each pane**:

   ```bash
   for pane in pane:<id1> pane:<id2> ...; do
     echo "=== $pane ==="
     cmux list-pane-surfaces --pane "$pane"
     echo
   done
   ```

   Shows what's running in each surface (terminal processes, browser tabs, Claude Code sessions).

4. **Summarize** the workspace state in a table for the user:
   - Pane refs
   - Surface refs and what's running in each
   - Which surface is the current session (your `caller` ref)
   - Any background processes worth noting

## Commands

```bash
# Step 1 — run both in parallel
cmux identify --json
cmux list-workspaces --json

# Step 2 — list panes in current workspace
cmux list-panes --workspace workspace:<id> --json

# Step 3 — list surfaces in each pane
cmux list-pane-surfaces --pane pane:<id>
```

## Tips

- Always run `identify` first so you know your own surface ref and don't accidentally send commands to yourself.
- Use `--json` for machine-readable output when you need to parse results programmatically.
- The `caller` field in `identify` output is YOUR surface; the `focused` field is what the user is looking at — these can differ if the user has switched focus since starting the session.
