# Inline Experiential Learning

A Claude Code plugin that detects non-trivial workflows and suggests saving them as project skills.

## What It Does

**Skill suggestion (Stop hook):** When the agent finishes, a prompt-based Stop hook evaluates whether the session involved trial and error, course corrections, or non-obvious multi-step processes. If so, it checks `.claude/skills/` for existing coverage and suggests creating or updating a skill. Most sessions fast-exit with `{ok: true}`.

## Installation

```bash
claude plugin install inline-experiential-learning@faire
```

## How It Works

1. Stop hook agent reviews the conversation for experiential learning signals
2. If signals found, globs `.claude/skills/*/SKILL.md` to check for existing skills
3. If no existing skill covers the process, suggests a new skill with name, description, and key steps
4. Main agent creates the skill at `.claude/skills/<name>/SKILL.md`

## Skill Format

Skills are markdown files with YAML frontmatter:

```markdown
---
name: Skill Name
description: When to use this skill
---

Skill content with steps, context, and instructions.
```

Files live in `.claude/skills/<name>/SKILL.md` in the project directory.
