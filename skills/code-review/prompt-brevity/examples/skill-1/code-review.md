---
name: Code Review Orchestrator
description: Delegate specialized reviews to subagents and synthesize their findings
when_to_use: When reviewing skills, CLAUDE.md, slash commands, or AI prompt content
version: 1.0.0
category: collaboration
---

# Code Review Orchestrator

## Overview

This skill orchestrates specialized review subagents to analyze code and documentation. Each subagent applies a specific review skill and returns focused findings. The orchestrator collects and presents results without additional commentary.

## When to Use

- Reviewing skills in .claude/skills/
- Evaluating CLAUDE.md files
- Assessing slash command prompts in .claude/commands/
- Any AI prompt or LLM instruction content review

## Process

### 1. Identify Files to Review

Determine what needs review:
- Single file or multiple files
- File type (skill, CLAUDE.md, command, etc.)
- Relevant review dimensions

### 2. Select Review Skills

Map content type to review skills:

**For AI Prompt Content** (skills, CLAUDE.md, commands):
- `collaboration/reviews/prompt-brevity` - Token efficiency and clarity

**For Future Review Types** (extensible):
- Add new skills in `collaboration/reviews/` as needed

### 3. Launch Subagents in Parallel

For each selected review skill, launch a general-purpose subagent with this exact task structure:

```
You are a specialized code reviewer. Apply the following skill to review the specified files.

**Skill to Apply**: [Read and follow .claude/skills/collaboration/reviews/[skill-name].md]

**Files to Review**: [list of file paths]

**Output Format** (use exactly this structure):

For each issue found, output:

---
**File**: [file path]
**Lines**: [line range, e.g., "45-52" or "78"]
**Issue**: [brief description of the problem]
**Suggestion**: [exact multiline replacement for the specified line range; omit this field if no specific change is proposed]
**Reason**: [why this change improves the code]
---

IMPORTANT about **Suggestion** field:
- Provide the EXACT text that should replace the specified line range
- For multiline ranges, include the complete replacement text preserving formatting
- If suggesting removal, state "Remove these lines" instead of providing replacement text
- If providing only a diagnostic observation without a specific fix, omit the **Suggestion** field entirely

Return ONLY the issues found in the format above. Do not add commentary, summary, or additional observations.
```

### 4. Collect Subagent Results

Wait for all subagents to complete. Each returns findings in the standardized format.

### 5. Present Findings

Output subagent results directly without modification:

```markdown
## Review Results

### Prompt Brevity Review

[paste subagent output exactly as returned]

### [Future Review Type]

[paste subagent output exactly as returned]
```

**Do not add**:
- Summary commentary
- Severity rankings
- Additional suggestions
- Personal observations

## Example

### Example 1: Single Skill File Review

**Input**: Review `.claude/skills/testing/test-driven-development.md`

**Subagent Task**:
```
You are a specialized code reviewer. Apply the following skill to review the specified files.

**Skill to Apply**: Read and follow .claude/skills/collaboration/reviews/prompt-brevity.md

**Files to Review**:
- .claude/skills/testing/test-driven-development.md

**Output Format**:

For each issue found, output:

---
**File**: [file path]
**Lines**: [line range]
**Issue**: [brief description]
**Suggestion**: [exact multiline replacement; omit if no specific change]
**Reason**: [why this improves the code]
---

Return ONLY the issues found. No commentary or summary.
```

**Orchestrator Output**:
```markdown
## Review Results

### Prompt Brevity Review

---
**File**: .claude/skills/testing/test-driven-development.md
**Lines**: 12-15
**Issue**: Verbose explanation with redundant phrasing
**Suggestion**: Test-driven development: write tests before implementation code
**Reason**: 68% token reduction (23 → 7 tokens) while preserving core message
---

---
**File**: .claude/skills/testing/test-driven-development.md
**Lines**: 45
**Issue**: Fluff phrase "you should make sure to"
**Suggestion**: run the tests
**Reason**: Direct imperative is clearer and saves 5 tokens
---
```

### Example 2: Multiple File Review

**Input**: Review all skills in `.claude/skills/collaboration/`

**Action**: Launch one subagent with all file paths

**Orchestrator Output**:
```markdown
## Review Results

### Prompt Brevity Review

---
**File**: .claude/skills/collaboration/writing-commit-messages.md
**Lines**: 8-10
**Issue**: Ceremonial phrase "in order to"
**Suggestion**: to write good commit messages
**Reason**: Standard brevity pattern saves 2 tokens
---

---
**File**: .claude/skills/collaboration/writing-commit-messages.md
**Lines**: 67-72
**Issue**: Redundant examples demonstrating same concept
**Reason**: Reduces redundancy by 40 tokens without information loss (no specific replacement provided - requires context-aware consolidation)
---

---
**File**: .claude/skills/collaboration/code-review.md
**Lines**: 34
**Issue**: Hedge words "you might want to consider"
**Suggestion**: consider
**Reason**: Removes unnecessary hedging, saves 4 tokens
---
```

## Anti-patterns

- ❌ **Don't**: Add your own commentary or summary
  - ✅ **Do**: Present subagent findings exactly as returned

- ❌ **Don't**: Filter or editorialize subagent results
  - ✅ **Do**: Trust subagent expertise and show all findings

- ❌ **Don't**: Combine findings from different review types
  - ✅ **Do**: Keep each review skill's findings separate

- ❌ **Don't**: Launch subagents sequentially
  - ✅ **Do**: Launch all subagents in parallel for efficiency

- ❌ **Don't**: Add severity ratings or prioritization
  - ✅ **Do**: Let findings speak for themselves

## Subagent Task Template

Use this exact template when launching subagents:

```
You are a specialized code reviewer. Apply the following skill to review the specified files.

**Skill to Apply**: Read and follow .claude/skills/collaboration/reviews/[SKILL-NAME].md

**Files to Review**:
- [file path 1]
- [file path 2]
- [file path N]

**Output Format** (use exactly this structure):

For each issue found, output:

**File**: [file path]
**Lines**: [line range, e.g., "45-52" or "78"]
**Issue**: [brief description of the problem]
**Suggestion**: [exact multiline replacement for the line range; omit if no specific change]
**Reason**: [why this change improves the code]
---

IMPORTANT about the **Suggestion** field:
- Provide EXACT replacement text that can directly replace the specified line range
- For multiline ranges, include complete replacement preserving indentation/formatting
- If suggesting removal only, state "Remove these lines"
- If no specific textual change can be provided (diagnostic only), omit the **Suggestion** field

IMPORTANT: Return ONLY the issues found in the format above. Do not add:
- Commentary or analysis
- Summary sections
- Overall observations
- Counts or statistics
- Recommendations beyond the specific findings

If no issues are found, return: "No issues found."
```

## Testing This Skill

### Test Scenario 1: Single File Review

1. Select one skill file to review
2. Launch prompt-brevity subagent with correct task format
3. Collect and present results without modification
4. Success: Only subagent findings displayed, no additional commentary

### Test Scenario 2: Parallel Multi-File Review

1. Select 3+ files for review
2. Launch subagent with all files in single task
3. Verify parallel execution (not sequential)
4. Success: All findings collected and presented cleanly

### Test Scenario 3: No Issues Found

1. Review a well-written, concise skill file
2. Launch subagent
3. Verify proper handling of "No issues found"
4. Success: Clean output without inventing issues

## Extensibility

To add new review dimensions:

1. Create new review skill in `.claude/skills/collaboration/reviews/[new-skill].md`
2. Update "Select Review Skills" section to include new skill
3. Launch additional subagent with new skill
4. Present findings in separate section

Example future skills:
- `reviews/security-practices` - Check for security anti-patterns
- `reviews/accessibility` - Verify inclusive language and examples
- `reviews/consistency` - Ensure style consistency across skills

## Related Skills

- `collaboration/reviews/prompt-brevity` - The review skill currently used
- `meta/creating-skills` - Skill creation guidelines

---

**Remember**: This is an orchestrator. Your job is to delegate to experts and present their findings, not to review yourself.
