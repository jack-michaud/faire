# Testing PreToolUse Blocking Hooks

## Context

When building PreToolUse hooks that block specific Bash commands (e.g., blocking `find`, `curl`, or other tools), the regex matching logic is complex enough to warrant a dedicated test harness. This pattern applies whenever you need to be confident that:

- The block fires for all real invocations of the target command
- The block does NOT fire for false positives (variable names, strings, similar words)

## Process

### 1. Extract hook logic into a standalone script

Never inline complex regex in `hooks.json`. Instead, create a dedicated shell script (e.g., `hooks/block_find.sh`) and delegate to it from `hooks.json`.

**hooks.json entry:**
```json
{
  "type": "command",
  "command": "bash \"${CLAUDE_PLUGIN_ROOT}/hooks/block_find.sh\"",
  "timeout": 5
}
```

The `${CLAUDE_PLUGIN_ROOT}` variable is set by Claude Code to the plugin's root directory, ensuring the path resolves correctly regardless of the current working directory.

**Why delegate to a script:**
- Avoids double-escaping issues when regex lives inside a JSON string inside a `bash -c` string
- Creates a single source of truth that both the hook and test harness invoke
- Makes the regex readable and maintainable (use single-quoted `PATTERN='...'` in bash)

### 2. Write the hook script

```bash
#!/bin/bash
# hooks/block_find.sh

INPUT=$(cat)
CMD=$(echo "$INPUT" | jq -r '.tool_input.command // ""')

# Use a variable to avoid quoting hell between JSON, bash, and regex layers
PATTERN='(^|[;&|`$([:space:]])(sudo[[:space:]]+)?(/[^ ]*/)?(env[[:space:]]+|command[[:space:]]+)?find([[:space:]]|$)'

if echo "$CMD" | grep -qE "$PATTERN"; then
  echo "Blocked: find command detected" >&2
  exit 2
fi

exit 0
```

Key details:
- `exit 2` blocks the tool call; `exit 0` allows it
- Parse stdin with `jq` — never use string manipulation on JSON
- Use `// ""` in jq to provide a default for missing fields
- Define the regex as a `PATTERN` variable to avoid escaping layers

### 3. Create a test harness script

Place it alongside the hook: `hooks/test_block_find.sh`

```bash
#!/bin/bash
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
HOOK_SCRIPT="$SCRIPT_DIR/block_find.sh"
PASS=0
FAIL=0

test_hook() {
  local expect="$1"
  local label="$2"
  local cmd="$3"
  local json
  json=$(jq -n --arg c "$cmd" '{"tool_name":"Bash","tool_input":{"command":$c}}')
  echo "$json" | bash "$HOOK_SCRIPT" 2>/dev/null
  local actual
  if [ $? -eq 2 ]; then actual="BLOCKED"; else actual="BYPASSED"; fi
  if [ "$actual" = "$expect" ]; then
    echo "  PASS  $actual  | $label"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  $actual (expected $expect)  | $label"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Bypass vectors (should be BLOCKED) ==="
test_hook "BLOCKED" "bare command"            "find . -name '*.txt'"
test_hook "BLOCKED" "leading space"           " find . -name '*.txt'"
test_hook "BLOCKED" "full path"               "/usr/bin/find . -name '*.txt'"
test_hook "BLOCKED" "chained with &&"         "ls && find . -name '*.txt'"
test_hook "BLOCKED" "chained with ;"          "ls; find . -name '*.txt'"
test_hook "BLOCKED" "piped into"              "xargs find"
test_hook "BLOCKED" "subshell \$()"          "echo \$(find . -name '*.txt')"
test_hook "BLOCKED" "backticks"               "echo \`find . -name '*.txt'\`"
test_hook "BLOCKED" "prefixed with env"       "env find . -name '*.txt'"
test_hook "BLOCKED" "prefixed with command"   "command find . -name '*.txt'"
test_hook "BLOCKED" "sudo"                    "sudo find /etc -name '*.conf'"

echo ""
echo "=== False positives (should be BYPASSED) ==="
test_hook "BYPASSED" "similar word findutils"  "findutils --version"
test_hook "BYPASSED" "grep for find string"    "grep 'find' file.txt"
test_hook "BYPASSED" "variable name \$finding" "echo \$finding"
test_hook "BYPASSED" "word in a path arg"      "ls /usr/share/doc/findutils"

echo ""
echo "Results: $PASS passed, $FAIL failed"
[ $FAIL -eq 0 ] && exit 0 || exit 1
```

### 4. Run and iterate

Run the test script directly:
```bash
bash hooks/test_block_find.sh
```

Fix the `PATTERN` in `block_find.sh` until all cases pass. Because both the test and the live hook use the same script, there is no drift between what is tested and what runs in production.

## Commands

```bash
# Run the test harness
bash hooks/test_block_find.sh

# Manually test a single case
echo '{"tool_name":"Bash","tool_input":{"command":"find . -name *.txt"}}' | bash hooks/block_find.sh

# Check exit code of last invocation
echo $?
```

## Sources

- Claude Code hooks documentation: https://docs.claude.com/en/docs/claude-code/hooks
