#!/bin/bash
# session-start-check.sh
# Checks for active ticket-agent state files and reminds the user to resume.
# Called as a SessionStart hook; must output {"result":"continue"} to stdout.
# Reminder messages are printed to stderr so they appear in the Claude UI.

set -euo pipefail

STATE_DIR="${PWD}/.claude/ticket-agent/state"

# Always output the required SessionStart response
output_continue() {
  printf '{"result":"continue"}'
}

# If the state directory does not exist or has no JSON files, exit silently
if [ ! -d "${STATE_DIR}" ]; then
  output_continue
  exit 0
fi

# Collect all state JSON files
STATE_FILES=("${STATE_DIR}"/*.json)

# Check if glob expanded to actual files (bash leaves the pattern literal if no match)
if [ ${#STATE_FILES[@]} -eq 0 ] || [ ! -f "${STATE_FILES[0]}" ]; then
  output_continue
  exit 0
fi

TICKET_SUMMARIES=()

for state_file in "${STATE_FILES[@]}"; do
  [ -f "${state_file}" ] || continue

  # Extract ticket_id: look for "ticket_id": "VALUE"
  ticket_id=$(grep -o '"ticket_id"[[:space:]]*:[[:space:]]*"[^"]*"' "${state_file}" \
    | sed 's/.*"ticket_id"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' \
    | head -1)

  # Extract current_phase: look for "current_phase": "VALUE"
  current_phase=$(grep -o '"current_phase"[[:space:]]*:[[:space:]]*"[^"]*"' "${state_file}" \
    | sed 's/.*"current_phase"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/' \
    | head -1)

  if [ -n "${ticket_id}" ]; then
    if [ -n "${current_phase}" ]; then
      TICKET_SUMMARIES+=("${ticket_id} (phase: ${current_phase})")
    else
      TICKET_SUMMARIES+=("${ticket_id}")
    fi
  fi
done

if [ ${#TICKET_SUMMARIES[@]} -gt 0 ]; then
  # Build a comma-separated list of ticket summaries
  summary=$(printf '%s, ' "${TICKET_SUMMARIES[@]}")
  summary="${summary%, }"  # trim trailing comma and space

  echo "[ticket-agent] Active tickets found: ${summary}. Resume with /ticket <TICKET_ID>" >&2
fi

output_continue
exit 0
