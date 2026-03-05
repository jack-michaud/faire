#!/bin/bash
# Block find commands - redirect to Glob or Read tools instead.
# Reads PreToolUse JSON from stdin.

PATTERN='(^|[;&| \t($`])find[[:space:]]|/find[[:space:]]|[;&| \t($`]find$|^find$'

jq -r '.tool_input.command // ""' | grep -qE "$PATTERN" && {
  echo 'Blocked: use Glob or Read tools instead of find.'
  exit 2
} || exit 0
