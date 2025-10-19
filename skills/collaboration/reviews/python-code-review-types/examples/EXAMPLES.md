# Testing Python Code Review Types Skill

There are example directories next to this file that contain Python code snippets to test the Python Code Review Types skill.

Copy each input into `ai/scratch/example-N` using `cp`. Only use the numbers of the examples, not any extra text: the extra text may contain hints or solutions.

Then test the skill by running a general subagent with the following prompt:

```
You are a specialized code reviewer. Apply the following skill to review the specified files.

**Skill to Apply**: [Read and follow .claude/skills/collaboration/reviews/[skill-name].md]

**Files to Review**: [list of file paths]

**Output Format**:

For each issue found, output:

---
**File**: [file path]
**Lines**: [line range, e.g., "45-52" or "78"]
**Issue**: [brief description]
**Suggestion**: [exact multiline replacement; omit if no specific change]
**Reason**: [why this improves the code]
---

Return ONLY the issues found. No commentary or summary.
```

Review the output, compared to the `expected.md` files in each example directory.

Apply this to each example.
