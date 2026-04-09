#!/usr/bin/env bash
# session-start.sh
# SessionStart hook: reads the memory index and injects it as additionalContext.
# If no memory directory or index exists, exits cleanly with no context.

set -euo pipefail

MEMORY_DIR="${CLAUDE_PROJECT_DIR:-.}/.claude/memory"
INDEX_FILE="${MEMORY_DIR}/INDEX.md"

# Fast exit if no memory directory or index
if [ ! -f "$INDEX_FILE" ]; then
  echo '{}'
  exit 0
fi

INDEX_CONTENT=$(cat "$INDEX_FILE")

RETRIEVAL_INSTRUCTION='Retrieval strategy:
1. **Keyword match**: Compare your task terms against topic slugs in the index. If a slug overlaps with what you are about to do, read that file.
2. **Category match**: Match the type of work to a category. Debugging -> check error/troubleshooting categories. Building a new feature -> check patterns/process categories. Configuring tooling -> check setup/config categories.
3. **Uncertainty trigger**: If unsure how to proceed, run `head -1` on candidate files in the relevant category to scan summaries. Let the summaries decide if a full read is worth it.

Read full files only when the summary confirms relevance. Do not read everything — targeted retrieval keeps context focused.'

CONTEXT="## Agent Memory

${INDEX_CONTENT}

${RETRIEVAL_INSTRUCTION}"

# Escape the context for JSON embedding
ESCAPED_CONTEXT=$(printf '%s' "$CONTEXT" | python3 -c 'import sys,json; print(json.dumps(sys.stdin.read()))')

cat <<EOF
{
  "hookSpecificOutput": {
    "hookEventName": "SessionStart",
    "additionalContext": ${ESCAPED_CONTEXT}
  }
}
EOF
