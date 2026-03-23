# End-to-End Verification of /ship-skill

Use this procedure when you want to confirm that the `/ship-skill` command works correctly — including workspace creation, content writing, version bumping, committing, and pushing.

## Prerequisites

- The faire repo is available at `~/Code/github.com/jack-michaud/faire`
- `uv` is installed and on PATH (for running the test script)
- The `jack-software` plugin is installed locally

## Step 1: Locate the test script

```bash
ls ~/Code/github.com/jack-michaud/faire/scripts/test-ship-skill.py
```

- If the file exists: proceed to Step 2.
- If missing: the test script has not yet been created. Create it per the pattern in `scripts/test-ship-skill.py` in the faire repo, then proceed.

## Step 2: Run the test

From the faire repo root:

```bash
cd ~/Code/github.com/jack-michaud/faire && ./scripts/test-ship-skill.py
```

Expected output (success):

```
## Ship Summary

- **Action**: Added procedure to existing skill
- **Location**: jack-software/commands/resources/ship-skill-e2e-verification.md
- **Plugin**: jack-software
- **Version**: X.Y.Z → X.Y.(Z+1)
- **Commit**: feat: add ship-skill e2e verification procedure
- **Push**: Pushed to main

TEST PASSED: Ship skill command completed successfully
```

## Step 3: Interpret results

| Output contains | Meaning | Action |
|---|---|---|
| `Ship Summary` + `TEST PASSED` | ✅ Command works end-to-end | Done |
| `Ship Failed` + `TEST FAILED` | ❌ Command reported a failure | Read the failure reason and debug (see Step 4) |
| `TEST FAILED: Result did not contain expected output format` | ❌ Output format changed | The `ship-skill.md` Step 9 report format may have changed; update the test assertion |

## Step 4: Debug failures

### "Failed to fetch faire remote"

```bash
jj git fetch -R ~/Code/github.com/jack-michaud/faire
```

Check network connectivity and remote URL:

```bash
jj git remote list -R ~/Code/github.com/jack-michaud/faire
```

### "Failed to create jj workspace"

Check for stale workspaces:

```bash
jj workspace list -R ~/Code/github.com/jack-michaud/faire
```

If there are temp workspaces left over from a previous failed run, forget them:

```bash
jj workspace forget <WORKSPACE_NAME> -R ~/Code/github.com/jack-michaud/faire
```

Then re-run the test.

### Push fails with "stale info" or "references unexpectedly moved"

Another push landed between fetch and push. Read the recovery procedure:

```
jack-software/skills/committing/resources/jj-stale-remote-push.md
```

Follow the fetch → inspect → rebase → push steps described there.

### Version mismatch between plugin.json and marketplace.json

```bash
cat ~/Code/github.com/jack-michaud/faire/jack-software/plugin.json | python3 -c "import sys,json; d=json.load(sys.stdin); print(d['version'])"
cat ~/Code/github.com/jack-michaud/faire/.claude-plugin/marketplace.json | python3 -c "import sys,json; d=json.load(sys.stdin); [print(p['version']) for p in d['plugins'] if p['name']=='jack-software']"
```

If mismatched, run:

```bash
make bump-patch PLUGIN=jack-software -C ~/Code/github.com/jack-michaud/faire
```

Then verify both files show the same version.

## Completion criteria

The verification is **done** when:

1. `./scripts/test-ship-skill.py` exits with code 0
2. Output contains `Ship Summary` and `TEST PASSED`
3. A new commit appears in the faire repo with the shipped content
4. `jack-software/plugin.json` version was incremented
