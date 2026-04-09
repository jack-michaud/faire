#!/usr/bin/env bash
# rebuild-memory-index.sh
# Deterministically rebuilds the compressed memory index from the filesystem.
# Usage: ./rebuild-memory-index.sh [memory-dir] [output-file]

set -euo pipefail

MEMORY_DIR="${1:-${CLAUDE_PROJECT_DIR:-.}/.claude/memory}"
OUTPUT_FILE="${2:-$MEMORY_DIR/INDEX.md}"

# Ensure memory directory exists
if [ ! -d "$MEMORY_DIR" ]; then
  echo "Memory directory not found: $MEMORY_DIR" >&2
  exit 1
fi

index=""
for category_dir in "$MEMORY_DIR"/*/; do
  [ -d "$category_dir" ] || continue
  category=$(basename "$category_dir")

  files=""
  for f in "$category_dir"*.md; do
    [ -f "$f" ] || continue
    name=$(basename "$f" .md)
    if [ -z "$files" ]; then
      files="$name"
    else
      files="$files,$name"
    fi
  done

  [ -z "$files" ] && continue

  if [ -z "$index" ]; then
    index="|$category/{$files}.md"
  else
    index="$index|$category/{$files}.md"
  fi
done

# Strip leading pipe
index="${index#|}"

if [ -z "$index" ]; then
  cat > "$OUTPUT_FILE" << 'EOF'
# Memory Index

No memory files found. Categories will appear as learnings are stored.
EOF
else
  cat > "$OUTPUT_FILE" << EOF
# Memory Index

Knowledge in \`$MEMORY_DIR/\`:
$index

Read a topic file for detail; line 1 is the summary.
EOF
fi

echo "Index rebuilt: $OUTPUT_FILE" >&2
