#!/bin/bash
# Tests for the find-blocking hook (block_find.sh)

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
  local code=$?

  local actual
  if [ $code -eq 2 ]; then actual="BLOCKED"; else actual="BYPASSED"; fi

  if [ "$actual" = "$expect" ]; then
    echo "  PASS  $actual  | $label"
    PASS=$((PASS + 1))
  else
    echo "  FAIL  $actual (expected $expect)  | $label"
    FAIL=$((FAIL + 1))
  fi
}

echo "=== Should BLOCK ==="
test_hook BLOCKED "direct find"              "find . -name '*.py'"
test_hook BLOCKED "leading space"            " find . -name '*.py'"
test_hook BLOCKED "full path"                "/usr/bin/find . -name '*.py'"
test_hook BLOCKED "chained with &&"          "ls && find . -delete"
test_hook BLOCKED "chained with ;"           "ls; find . -delete"
test_hook BLOCKED "piped via xargs"          "echo /tmp | xargs find"
test_hook BLOCKED "subshell"                 'echo $(find . -name secret)'
test_hook BLOCKED "backticks"                'echo `find . -name secret`'
test_hook BLOCKED "env prefix"               "env find . -name '*.py'"
test_hook BLOCKED "command prefix"           "command find . -name '*.py'"

echo ""
echo "=== Should BYPASS ==="
test_hook BYPASSED "findutils package"       "apt install findutils"
test_hook BYPASSED "grep for find in file"   "grep 'find' file.txt"
test_hook BYPASSED "\$finding variable"      'echo $finding'
test_hook BYPASSED "findByName function"     "node -e 'findByName()'"

echo ""
echo "=== Results: $PASS passed, $FAIL failed ==="
exit $FAIL
