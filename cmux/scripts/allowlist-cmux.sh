#!/usr/bin/env bash
set -euo pipefail

INPUT=$(cat)
TOOL_NAME=$(echo "$INPUT" | jq -r '.tool_name')

if [ "$TOOL_NAME" != "Bash" ]; then
  exit 0
fi

COMMAND=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Extract the cmux subcommand (first two words if "cmux <subcommand>")
if ! echo "$COMMAND" | grep -qE '^\s*cmux\b'; then
  exit 0
fi

SUBCOMMAND=$(echo "$COMMAND" | awk '{for(i=1;i<=NF;i++){if($i=="cmux"){print $(i+1);exit}}}')

# Safe read-only and non-destructive commands
ALLOWED=(
  # System / identity
  ping
  version
  capabilities
  identify

  # Listing (read-only)
  list-windows
  current-window
  list-workspaces
  list-panes
  list-pane-surfaces
  list-log
  list-buffers
  sidebar-state
  find-window

  # Reading terminal content
  capture-pane

  # Creating (additive, non-destructive)
  new-window
  new-workspace
  new-split
  new-pane
  new-surface

  # Navigation / focus (non-destructive)
  focus-window
  focus-pane
  last-pane
  next-window
  previous-window
  last-window

  # Naming / organizing (non-destructive)
  rename-tab
  workspace-action
  tab-action
  reorder-workspace
  reorder-surface
  move-surface
  move-workspace-to-window

  # Logging / notifications (non-destructive)
  log
  clear-log
  notify

  # Clipboard (non-destructive)
  set-buffer

  # Display
  display-message

  # Browser (read + interact, no send-keys equivalent)
  browser
)

for allowed in "${ALLOWED[@]}"; do
  if [ "$SUBCOMMAND" = "$allowed" ]; then
    echo '{"hookSpecificOutput":{"permissionDecision":"allow"}}'
    exit 0
  fi
done

# Not in allowlist — falls through to normal permission flow
# This catches: send, close-window, close-surface, respawn-pane,
# swap-pane, break-pane, join-pane, pipe-pane, paste-buffer,
# drag-surface-to-split, resize-pane, clear-history, etc.
exit 0
