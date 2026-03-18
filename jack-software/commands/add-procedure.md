---
description: Add a procedure to the appropriate skill, or create a new one. Works from any project.
argument-hint: <procedure description>
allowed-tools: Read, Write, Edit, Glob, Grep, Bash(make:*)
---

# Add Procedure

You are a procedure placement agent. You help place new procedures into the right skill, whether that's in the current project or in the faire plugin marketplace.

## Input

The procedure to add: $ARGUMENTS

## Step 1: Determine where the procedure belongs

This is about the **nature of the procedure**, not where you're running from:

- **Personal workflow / reusable across projects** → goes in the **faire marketplace** (e.g. `jack-software/skills/<name>/SKILL.md`). Examples: committing workflows, code review patterns, deployment processes, general development habits.
- **Project-specific process** → goes in the **current project's `.claude/skills/`**. Examples: this project's test setup, this repo's migration process, domain-specific business logic workflows.

Ask yourself: "Would this procedure be useful in a different repo?" If yes → faire. If no → local project.

To write to faire, check if `$CLAUDE_PLUGIN_ROOT` points to a faire plugin directory (it will have a `../../.claude-plugin/marketplace.json`). If so, you can write directly. Otherwise, use the faire script to add the procedure:

```bash
~/Code/github.com/jack-michaud/faire/scripts/add-procedure.py "<procedure description>"
```

Do NOT write directly to `~/.claude/plugins/cache/faire/` — that's a read-only cache regenerated from the faire repo.

## Step 2: Inventory existing skills

Search **both** locations to understand what's already covered:

**Faire marketplace** (via plugin root):
```
Glob: $CLAUDE_PLUGIN_ROOT/../../*/skills/*/SKILL.md
```

**Current project:**
```
Glob: .claude/skills/*/SKILL.md
```

Read the frontmatter (name + description) of each.

## Step 3: Load procedure-skill quality guidance

Read `$CLAUDE_PLUGIN_ROOT/commands/procedure-skill.md` — this defines what makes a good procedure skill. Apply its quality checklist to everything you write.

Key standards:
- **Specificity over generality** — real function names, file paths, tool commands
- **Decision branches with if/else** — every non-trivial fork must be explicit
- **Verification steps** — confirm actions worked before moving on
- **Iteration loops** — "repeat steps N-M until <condition>" where refinement is needed
- **Concrete examples** — show what good input/output looks like
- **Completion criteria** — define what "done" looks like
- **Only document what worked** — don't restate tool constraints

## Step 4: Find the best home

Search the existing skills for the best fit. Decide one of:

### Option A: Inline addition
If the procedure is a **natural extension** of an existing skill's process — e.g. adding a new step or branch to an existing workflow — edit the SKILL.md directly.

### Option B: Reference file
If the procedure is a **distinct sub-workflow** within an existing skill's domain — e.g. a specialized variant that only applies in certain situations:
1. Create `<skill-dir>/resources/<name>.md` with the procedure content
2. Add a note to the parent SKILL.md: "When you are in <situation>, read this reference file: `resources/<name>.md`"

### Option C: New skill
If the procedure **doesn't fit** any existing skill, or is different enough to deserve its own trigger:

**Personal/reusable → faire:** Choose the plugin that best matches the domain. Default to `jack-software`.
- Create `<plugin>/skills/<kebab-case-name>/SKILL.md` (relative to faire repo root via `$CLAUDE_PLUGIN_ROOT/../../`)
- If the plugin doesn't have `"skills"` in its `plugin.json`, add `"skills": "./skills/"`

**Project-specific → local:**
- Create `.claude/skills/<kebab-case-name>/SKILL.md`

## Step 5: Write the procedure

### For new skills (Option C)

Create the SKILL.md with this structure:

```markdown
---
name: <kebab-case-name>
description: <Trigger condition — be specific. Include example phrases like "Use when..." or "Triggered by...". Include the example from the input.>
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

### For additions (Options A and B)

Make minimal, focused edits. Don't restructure existing content unless necessary.

## Step 6: Report

Print a summary:
- **What you did**: created new skill / added to existing / created reference file
- **Where**: the file path(s) modified or created
- **Why this placement**: brief rationale for the choice
- **Trigger**: the description field value (for new skills)
