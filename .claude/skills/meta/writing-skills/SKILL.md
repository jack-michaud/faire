---
name: Creating Skills
description: A meta-skill for documenting and creating reusable skills for Claude Code agents. Use when you discover a technique, pattern, or workflow worth documenting for reuse across projects.
---

# Creating Skills

## Overview

Write a skill file in `.claude/skills/`. Test it with TDD.

**Core Principle**: If you did not test a skill, it is useless.

## Process: The RED-GREEN-REFACTOR Cycle for Skills

### RED: Write Failing Tests First
1. **Create failing test cases** that demonstrate edge cases or common mistakes
2. **Document assertions** for each test case (expected behavior in `expected.md`)

### GREEN: Make Tests Pass
3. **Write the skill** that addresses all test cases
4. **Test skill with subagent** using the failing test cases
5. **Analyze results**: Did the subagent catch what was expected?
6. **Iterate on skill** until all tests pass

### REFACTOR: Improve While Tests Stay Green
7. **Run code review** on the skill (token optimization, clarity)
8. **Regression test** with all examples to ensure nothing broke
9. **Document changes** and test outcomes

## Examples

### Example 1: Python Code Review Skill

This section documents the complete TDD process used to create the Python Code Review skill (`.claude/skills/collaboration/python-code-review.md`).

#### Initial Requirements

User requested: "A skill for reviewing python code. Make sure that we always use python 3.12 types. No untyped code is allowed. Make sure that we always use `list`, `type`, `dict` and not `List`, `Type`, `Dict` - this is old syntax."

#### Iteration 1: RED-GREEN (v1.0.0)

**1. RED - Created Failing Test Cases**

Write examples.

```
.claude/skills/collaboration/python-code-review/
└── examples/
    ├── example-1-mixed-syntax/         # Medium: Mixed old/new syntax
    │   ├── scenario.md                 # Metadata for humans
    │   ├── input.py                    # Code mixing List/list inconsistently
    │   └── expected.md                 # Assertions: Should catch List, Dict, Optional issues
    ├── example-2-untyped-code/         # Easy: Most common real-world case
    │   ├── input.py                    # Completely untyped Python class
    │   └── expected.md                 # Assertions: Should catch 0% type coverage
    └── example-3-complex-generics/     # Hard: Edge cases with TypeVar
        ├── input.py                    # Code with TypeVar, Generic, Protocol
        └── expected.md                 # Assertions: Should NOT flag legitimate typing imports
```
Copy the `input.py` into `ai/scratch/example-N`.

Run general subagents with this prompt pattern:
```
You are a specialized code reviewer. Apply the following skill to review the specified files.

**Files to Review**: ai/scratch/example-N/input.md

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

**2. Created the Skill**
- Focused on Python 3.12+ modern typing conventions
- Enforced strict typing: no `List`/`Dict`/`Type`, use built-in generics
- Ensured `X | None` instead of `Optional[X]`
- Included 6-step process with examples and anti-patterns

**3. GREEN - Ran the Tests (3 parallel subagents)**

Launched 3 subagents with this prompt pattern:
```
You are a specialized code reviewer. Apply the following skill to review the specified files.

**Skill to Apply**: Read and follow .claude/skills/collaboration/python-code-review.md

**Files to Review**: ai/scratch/example-N/input.md

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

**Test Results:**
- ✅ Example 1: PASS (with minor over-strictness - caught MORE than expected)
- ✅ Example 2: PASS (100% coverage gap identified correctly)
- ✅ Example 3: PASS (critical test: correctly distinguished deprecated vs legitimate typing imports)

**Failing Behavior Discovered:** When testing without explicit constraints, subagents provided extra non-typing feedback (design suggestions, code quality improvements) - scope creep!

#### Iteration 2: REFACTOR (v1.1.0)

**Problem:** Skill lacked explicit scope boundaries, causing subagents to provide general code review feedback.

**Fix:**
1. Added explicit scope statement in Overview:
   ```markdown
   **Scope**: This skill focuses exclusively on type annotations,
   not code logic, design patterns, performance, or general quality.
   ```

2. Added directive at start of Process section:
   ```markdown
   Focus only on type annotation issues.
   ```

**Regression Testing:**
- Launched same 3 tests without "typing only" constraint in prompt
- ✅ All tests pass: Subagents maintained focus on typing issues
- ✅ Zero design/quality feedback
- Refactoring successful!

#### Iteration 3: REFACTOR with Code Review Orchestrator (v1.2.0)

**Self-Review Process:**

Applied `/pr-review` command then **incorporated All Feedback:**

**Regression Testing After Refactor:**

Reran all 3 test cases with v1.2.0:
- ✅ Example 1: PASS (all issues caught, proper scope)
- ✅ Example 2: PASS (0% coverage identified, pure typing review)
- ✅ Example 3: PASS (nuanced TypeVar/Generic distinction correct)

**Zero regression** - all tests still pass after refactoring!

## Anti-patterns

- ❌ **Don't**: Skip creating test cases (RED phase)
  - ✅ **Do**: Write failing tests before finalizing the skill

- ❌ **Don't**: Only test happy-path scenarios
  - ✅ **Do**: Create test cases that cover edge cases

- ❌ **Don't**: Test once and move on
  - ✅ **Do**: Regression test after each refactor

- ❌ **Don't**: Accept vague skill behavior
  - ✅ **Do**: Iterate until all tests pass with precise behavior

- ❌ **Don't**: Skip the refactor step
  - ✅ **Do**: Improve the skill while tests keep you safe

- ❌ **Don't**: Create test cases without assertions
  - ✅ **Do**: Document expected behavior in expected.md


## Example Skill Template

```markdown
---
name: Skill Name
description: Brief one-line description
when_to_use: When [specific trigger or scenario]
version: 1.0.0
category: [meta|testing|debugging|collaboration|workflow]
---

# Skill Name

## Overview

2-3 sentence summary of what this skill does and why it matters.

## When to Use

- Trigger condition 1
- Trigger condition 2
- Trigger condition 3

## Process

1. First step with specific action
2. Second step with clear instruction
3. Third step with validation

## Examples

### Example 1: [Scenario Name]

**Context**: Describe the situation
**Application**: Show how to use the skill
**Outcome**: What success looks like

## Anti-patterns

- ❌ **Don't**: Common mistake 1
  - ✅ **Do**: Correct approach instead

- ❌ **Don't**: Common mistake 2
  - ✅ **Do**: Correct approach instead

## Testing This Skill (TDD Validation)

How to validate this skill works:
1. Create test case with failing example
2. Apply skill to test case
3. Verify assertions pass
```
