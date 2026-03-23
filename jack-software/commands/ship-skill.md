---
description: Ship a procedure, skill, or command to the faire marketplace or local project. Handles workspace isolation, validation, version bumping, commit, and push.
argument-hint: <description of what to add, e.g. "add a procedure for deploying to staging">
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(jj:*), Bash(make:*), Bash(cd:*), Bash(rm:*), Bash(mktemp:*)
---

# Ship Skill

You are an autonomous shipping agent. You take a description of a procedure, skill, or command, write it, validate it, bump the version, commit, and push — all in an isolated workspace so you never disturb in-progress work.

## Input

The content to ship: $ARGUMENTS

## Step 1: Parse Input

If `$ARGUMENTS` is empty or contains only whitespace, report:
```
## Ship Failed

- **Step**: 1 - Parse Input
- **Issue**: No description provided
- **Action needed**: Provide a description of what to ship. Examples:
  - `/ship-skill add a procedure for deploying staging environments`
  - `/ship-skill create a skill for writing GraphQL resolvers`
  - `/ship-skill add a command to logs plugin that shows error rate trends`
```
STOP.

Analyze `$ARGUMENTS` to determine three things:

### 1a. Content type
- **Procedure**: adding a step-by-step process to an existing skill (e.g., "add a procedure for...", "add a workflow for...")
- **New skill**: creating a brand new skill (e.g., "create a skill for...", "new skill that...")
- **New command**: creating a new slash command (e.g., "add a command to...", "create a command that...")

### 1b. Target destination
- **Faire marketplace** (default): reusable workflows useful across projects. This is the default for most requests.
- **Local project**: project-specific processes. Only when the description explicitly says "local", "for this project", "project-specific", or similar.

### 1c. Target plugin
- If the description names a specific plugin (e.g., "add a command to the **logs** plugin"), use that plugin.
- Otherwise, default to `jack-software`.

## Step 2: Set up workspace

### 2a. If targeting the faire marketplace

1. Set `FAIRE_PATH` to `~/Code/github.com/jack-michaud/faire`.
2. Verify `FAIRE_PATH` exists:
   ```
   Glob: ~/Code/github.com/jack-michaud/faire/jack-software/plugin.json
   ```
   - If no match: report error — "Faire repo not found at ~/Code/github.com/jack-michaud/faire. Clone it first." and STOP.

3. Fetch latest remote state:
   ```bash
   jj git fetch -R ~/Code/github.com/jack-michaud/faire
   ```
   - If fetch fails: report error — "Failed to fetch faire remote. Check your network connection." and STOP.

4. Create a temp directory and workspace:
   ```bash
   mktemp -d
   ```
   Save the result as `TEMP_DIR`.

   ```bash
   jj workspace add <TEMP_DIR> -r main@origin -R ~/Code/github.com/jack-michaud/faire
   ```
   - If workspace creation fails: report error — "Failed to create jj workspace. Try running `jj git fetch -R ~/Code/github.com/jack-michaud/faire` manually." Clean up TEMP_DIR and STOP.

5. Save the workspace name (the basename of `TEMP_DIR`) as `WORKSPACE_NAME`.
6. All subsequent file operations (Steps 3-7) operate within `TEMP_DIR`.

### 2b. If targeting the local project

Skip workspace setup. All file operations use the current project directory. Set `WORK_DIR` to the current working directory.

## Step 3: Determine placement

### 3a. Inventory existing skills

Search for existing skills in the workspace (faire) or local project:

**Faire workspace:**
```
Glob: <TEMP_DIR>/*/skills/*/SKILL.md
```

**Local project:**
```
Glob: .claude/skills/*/SKILL.md
```

Read the frontmatter (`name` and `description`) of each matching skill.

### 3b. Choose placement

**If content type is "procedure":**

Find the skill whose domain best matches the procedure. Choose one of:

- **Option A: Inline addition** — The procedure is a natural extension of an existing skill's process. Edit the SKILL.md directly to add the new procedure section.
- **Option B: Reference file** — The procedure is a distinct sub-workflow within an existing skill's domain. Create `<skill-dir>/resources/<name>.md` with the procedure content. Add a note to the parent SKILL.md: "When <situation>, read `resources/<name>.md`."
- **Option C: New skill** — The procedure doesn't fit any existing skill. Create a new skill directory (see "new skill" flow below).

**If content type is "new skill":**

For faire: Create `<target-plugin>/skills/<kebab-case-name>/SKILL.md` in the workspace.
- If the plugin's `plugin.json` lacks a `"skills"` field, add `"skills": "./skills/"` to the manifest before creating the skill directory.

For local: Create `.claude/skills/<kebab-case-name>/SKILL.md`.

**If content type is "new command":**

Create `<target-plugin>/commands/<kebab-case-name>.md` in the workspace (faire) or `.claude/commands/<name>.md` (local).

## Step 4: Write the content

### For procedures (Options A and B)

Write clear, specific procedure content following these quality standards:
- **Specificity over generality**: real function names, file paths, tool commands
- **Decision branches with if/else**: every non-trivial fork must be explicit
- **Verification steps**: confirm actions worked before moving on
- **Iteration loops**: "repeat steps N-M until <condition>" where refinement is needed
- **Concrete examples**: show what good input/output looks like
- **Completion criteria**: define what "done" looks like

### For new skills (Option C)

Create `SKILL.md` with this structure:

```markdown
---
name: <kebab-case-name>
description: <Trigger condition — be specific. Include example phrases like "Use when..." or "Triggered by...".>
---

<Role statement — who is Claude acting as?>

## Process

1. <Step with specific, actionable instruction>
2. <Decision point>
   - If <condition A>: <action>
   - If <condition B>: <action>
3. <Verification step>
4. <Completion step>
```

### For new commands

Create the command `.md` with YAML frontmatter:

```markdown
---
description: <What this command does>
argument-hint: <expected arguments>
allowed-tools: <comma-separated tool list>
---

<Command instructions>
```

## Step 5: Validate

Read each modified or created file and check:

1. **SKILL.md files**: Must have YAML frontmatter with non-empty `name` and `description` fields.
2. **Command .md files**: Must have YAML frontmatter with non-empty `description` field.
3. **plugin.json**: Must be valid JSON (read it and confirm it parses).
4. **marketplace.json** (faire only): Must be valid JSON.

If any validation check fails:
- Report the specific file path and issue.
- Do NOT proceed to commit.
- STOP and report the failure.

## Step 6: Bump version

Determine the bump level:
- **New component** (new skill, command, agent, or hook) → `make bump-minor PLUGIN=<plugin-name>`
- **Procedure added to existing skill** (content update) → `make bump-patch PLUGIN=<plugin-name>`

Note: `<plugin-name>` is the **directory name** of the plugin (e.g., `jack-software`, `logs`), not the `name` field from `plugin.json`.

Run from the workspace root (TEMP_DIR for faire, repo root for local):
```bash
make bump-minor PLUGIN=<plugin-name>
```
or
```bash
make bump-patch PLUGIN=<plugin-name>
```

Read `<plugin>/plugin.json` after the bump to confirm the version was incremented.

**For faire only**: Also read `.claude-plugin/marketplace.json` and confirm the plugin entry version matches `plugin.json`. If they don't match, report the mismatch and STOP.

## Step 7: Commit and push

### 7a. Faire path

1. Describe the working copy commit:
   ```bash
   jj describe -m "feat: <descriptive message>" -R ~/Code/github.com/jack-michaud/faire
   ```

2. Move the main bookmark:
   ```bash
   jj bookmark set main -r @ -R ~/Code/github.com/jack-michaud/faire
   ```

3. Push to remote:
   ```bash
   jj git push -b main -R ~/Code/github.com/jack-michaud/faire
   ```

   If push fails with "stale info" or "references unexpectedly moved":
   - Read `jack-software/skills/committing/resources/jj-stale-remote-push.md` in the workspace
   - Follow the recovery procedure (fetch, inspect, rebase, push)

   If push fails for other reasons (network, permissions):
   - Report the error: "Push failed: <error>. Your commit is preserved in the workspace at <TEMP_DIR>. Resolve the issue and push manually."
   - Do NOT clean up the workspace (skip Step 8) so the user can recover.
   - STOP.

### 7b. Local project path

1. Use `jj split` to isolate the new files into their own commit:
   ```bash
   JJ_EDITOR=true jj split -- <new-file-paths>
   ```
   This puts the new files in the first (parent) revision, everything else stays in the working copy.
   Note the change ID of the parent revision from the output (it will say "First part: <change-id>").

2. Describe the split commit using the change ID from step 1:
   ```bash
   jj describe -r <change-id-from-step-1> -m "feat: add <name> skill"
   ```

Do NOT push for local project changes.

## Step 8: Cleanup (faire only)

1. Forget the workspace:
   ```bash
   jj workspace forget <WORKSPACE_NAME> -R ~/Code/github.com/jack-michaud/faire
   ```

2. Remove the temp directory:
   ```bash
   rm -rf <TEMP_DIR>
   ```

## Step 9: Report

Print the ship summary:

```
## Ship Summary

- **Action**: [Created new skill / Added procedure to existing skill / Created command]
- **Location**: [file path(s)]
- **Plugin**: [plugin name]
- **Version**: [old version] → [new version]
- **Commit**: [commit message]
- **Push**: [Pushed to main / Local commit only]
```

If any step failed:

```
## Ship Failed

- **Step**: [which step failed]
- **Issue**: [specific problem]
- **Action needed**: [what the user should do]
```
