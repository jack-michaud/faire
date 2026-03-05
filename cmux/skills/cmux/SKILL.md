---
name: cmux Workspace Orchestration
description: >-
  This skill should be used when the user asks to "set up a dev environment",
  "create a workspace", "open a browser pane", "split terminal", "spin up frontend and backend",
  "use cmux", "manage cmux panes", "run commands in cmux", or mentions cmux workspaces, panes,
  surfaces, or browser automation. Provides workflow guidance for orchestrating multi-pane
  development environments with terminal and browser surfaces.
---

# cmux Workspace Orchestration

cmux is a terminal multiplexer application for macOS with a rich CLI for managing windows,
workspaces, panes, browser surfaces, and sidebar logging. It is controlled via a Unix socket
at `/tmp/cmux.sock`.

## Core Concepts

cmux organizes its hierarchy as: **Window > Workspace > Pane > Surface (Tab)**

- **Window**: Top-level OS window
- **Workspace**: A named layout within a window (like tmux sessions). Visible in the sidebar.
- **Pane**: A split region within a workspace. Each pane contains one or more surfaces as tabs.
- **Surface**: A single terminal or browser tab within a pane. Referenced as `surface:<n>`.

All commands use **ref format** by default: `workspace:1`, `pane:2`, `surface:3`.

Environment variables `CMUX_WORKSPACE_ID` and `CMUX_SURFACE_ID` are auto-set in cmux terminals
and serve as defaults for `--workspace` and `--surface` flags.

## CLI Reference

Run `cmux --help` for the full command list. Run `cmux <command> --help` for details on any
specific command. Use `--json` flag on most commands for machine-readable output.

## Tips

- Use `cmux identify --json` to discover the current workspace, pane, and surface context.
- After creating splits, use `cmux list-panes` and `cmux list-pane-surfaces` to discover new surface refs.
- Use `cmux capture-pane --lines <n>` to read terminal output and detect when processes are ready.
- Use `cmux log` with levels (`progress`, `success`, `error`) and `cmux notify` for sidebar visibility.
- Browser `snapshot --interactive` returns an accessibility tree ideal for understanding page structure.
- `cmux send` uses `\n` for Enter and `\t` for Tab in the text argument.

## Workflows

Successful workflows are documented as reference files. Check `references/` for proven patterns.
