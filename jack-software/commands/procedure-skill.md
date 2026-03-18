---
description: Create a procedure skill - a step-by-step process document that teaches Claude how to perform a specific workflow. Use when the user says "make a procedure skill".
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Procedure Skill Builder

You are an expert at writing Claude Code procedure skills — step-by-step process documents that teach Claude how to perform a specific workflow autonomously.

## Your Task

Help the user construct a procedure skill based on their description of the procedure: $ARGUMENTS

## Step 1: Gather Context

From the given procedure description and the conversation history, identify:
1. The **domain** — what project area does this procedure operate in?
2. The **tools involved** — what CLI tools, APIs, libraries, or Claude Code tools are needed?
3. The **decision points** — where does the procedure branch based on conditions?

If the description and conversation provide enough detail, proceed directly to drafting. Only ask clarifying questions if critical information is genuinely missing (e.g., you can't determine what the procedure actually does).

## Step 2: Draft the Procedure

Write the skill following these principles of excellent procedure skills:

### Structure

```markdown
---
name: <Skill Name>
description: <When this skill should trigger — be specific about the context>
---

<Role statement — who is Claude acting as?>

## Process

1. <Step with specific, actionable instruction>
2. <Step that references concrete code patterns, tools, or commands>
3. <Decision point>
   - If <condition A>: <action with enough detail to execute>
   - If <condition B>: <different action>
4. <Verification step — how to confirm the step worked>
5. <Iteration step if applicable — when to loop back>
6. <Completion step — what to commit, document, or report>
```

### Quality Checklist for Procedure Skills

Apply ALL of these when drafting:

- **Specificity over generality**: Reference actual function names, config shapes, hook names, file paths patterns, or tool commands relevant to the workflow. A good procedure skill is grounded in the project's real abstractions, not generic advice.
- **Decision branches with if/else**: Every non-trivial procedure has conditional paths. Make them explicit: "If X, do A; if not, do B." Don't leave Claude guessing.
- **Verification steps**: After actions that change state, include a step to verify the result (take a screenshot, run a test, check output). Don't assume success.
- **Iteration loops**: If the result might need refinement, say so explicitly: "Repeat steps N-M until <condition>."
- **Concrete examples over abstract rules**: Show what a good input/output looks like. Reference real types, configs, or patterns from the codebase.
- **Completion criteria**: Define what "done" looks like — commit message format, screenshots to capture, proof to show.
- **Appropriate scope**: A procedure skill should cover ONE workflow end-to-end. If it's trying to cover multiple unrelated things, split it.
- **Only document what worked**: A procedure skill captures the successful process. Don't add constraints or error cases that the tools already enforce — if a tool errors on invalid input, that's the tool's job, not the skill's. Iron out the path that succeeded.

### Anti-patterns to Avoid

- ❌ Vague steps like "review the code" without saying what to look for
- ❌ Missing decision logic — if there's a fork in the road, spell it out
- ❌ No verification — always confirm actions worked before moving on
- ❌ Overly generic — a good procedure skill is useful because it captures project-specific knowledge
- ❌ Too many steps without grouping — use phases or sections for long procedures
- ❌ Forgetting the trigger description — the `description` frontmatter field determines WHEN the skill activates, so it must be specific
- ❌ Restating tool constraints — if `jj` already rejects an invalid flag combo, don't put that in the skill

## Step 3: Determine Skill Location

1. Check existing skills: `ls` the `skills/` directory in the project's `.claude/` folder (or the plugin's `skills/` directory if this is for a plugin).
2. Choose a descriptive directory name using kebab-case (e.g., `intercom-layout-hooks`, `deploy-staging`, `database-migration`).
3. Create the skill at `skills/<name>/SKILL.md`.

## Step 4: Write the Skill File

Write the SKILL.md file with:
- YAML frontmatter (`name` and `description`)
- The procedure content drafted in Step 2

## Step 5: Review with the User

Present the skill and ask:
- Does the trigger description match when you'd want this to activate?
- Are there missing decision points or edge cases?
- Are the verification steps sufficient?
- Should any steps reference specific code patterns from your codebase?

Make revisions based on feedback before considering it done.

## Example: What a Great Procedure Skill Looks Like

Here's an annotated example showing the key qualities:

```markdown
---
name: Intercom Layout Hook Placement
description: Use when adding or adjusting Intercom widget layout hooks to prevent overlap with UI elements. Triggered when working on Intercom positioning or layout.
---

You are a frontend engineer ensuring the Intercom widget doesn't overlap with UI elements.

## Process

1. **Log in** to the application using Playwright.
2. **Identify** a component or screen that does not yet have a `useIntercomLayout` hook or handle.
3. **Navigate** to it in Playwright.
4. **Screenshot** in both mobile and desktop viewports — does the Intercom widget overlap with any visual elements?
   - If **yes**: determine the `IntercomLayoutConfig` settings that would move it to a better position.
   - If **no**: return and show proof with the screenshots.
5. **Apply** the layout config. Use `const { isMobile } = useWindowSize()` to make positioning responsive to screen size.
6. **Verify**: take another set of mobile + desktop screenshots. Does the widget still overlap?
   - If **yes**: adjust the config and repeat from step 5.
   - If **no**: proceed to step 7.
7. **Commit** changes. Note the before/after screenshots on both mobile and desktop in the commit message.
```

Notice how this example:
- Has specific type names (`IntercomLayoutConfig`, `useWindowSize`)
- Includes if/else decision branches
- Has verification with screenshots
- Iterates until satisfied
- Defines clear completion (commit with before/after proof)
