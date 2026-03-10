#!/usr/bin/env bash
set -euo pipefail

usage() {
  echo "Usage: $0 <plugin-name> <patch|minor|major>"
  echo ""
  echo "Plugins:"
  for dir in */plugin.json; do
    dirname "${dir}"
  done
  exit 1
}

if [ $# -ne 2 ]; then
  usage
fi

PLUGIN="$1"
BUMP="$2"
PLUGIN_JSON="${PLUGIN}/plugin.json"
MARKETPLACE_JSON=".claude-plugin/marketplace.json"

if [ ! -f "$PLUGIN_JSON" ]; then
  echo "Error: ${PLUGIN_JSON} not found"
  exit 1
fi

if [[ "$BUMP" != "patch" && "$BUMP" != "minor" && "$BUMP" != "major" ]]; then
  echo "Error: bump type must be patch, minor, or major"
  exit 1
fi

CURRENT=$(python3 -c "import json; print(json.load(open('${PLUGIN_JSON}'))['version'])")
IFS='.' read -r MAJOR MINOR PATCH <<< "$CURRENT"

case "$BUMP" in
  major) MAJOR=$((MAJOR + 1)); MINOR=0; PATCH=0 ;;
  minor) MINOR=$((MINOR + 1)); PATCH=0 ;;
  patch) PATCH=$((PATCH + 1)) ;;
esac

NEW_VERSION="${MAJOR}.${MINOR}.${PATCH}"

# Update plugin.json
python3 -c "
import json
with open('${PLUGIN_JSON}', 'r') as f:
    data = json.load(f)
data['version'] = '${NEW_VERSION}'
with open('${PLUGIN_JSON}', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"

# Update marketplace.json
python3 -c "
import json
with open('${MARKETPLACE_JSON}', 'r') as f:
    data = json.load(f)
for plugin in data.get('plugins', []):
    if plugin.get('name') == '${PLUGIN}' or plugin.get('source') == './${PLUGIN}':
        plugin['version'] = '${NEW_VERSION}'
        break
else:
    print('Warning: plugin ${PLUGIN} not found in marketplace.json')
with open('${MARKETPLACE_JSON}', 'w') as f:
    json.dump(data, f, indent=2)
    f.write('\n')
"

echo "${PLUGIN}: ${CURRENT} -> ${NEW_VERSION}"
