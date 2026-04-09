# Inline Experiential Learning

A Claude Code plugin that adds retrieval priming and inline learning to the agent memory system.

## What It Does

**Retrieval priming (SessionStart hook):** At the start of every session, injects the compressed memory index from `.claude/memory/INDEX.md` along with a retrieval strategy. The agent decides depth: index only (most sessions), summary scan via `head -1`, or full file read.

**Learning detection (Stop hook):** When the agent finishes, a prompt-based Stop hook evaluates whether the session produced knowledge worth storing — corrections, new processes, or untriggered-but-relevant memory files. Most sessions fast-exit with `{ok: true}`. When learnings are detected, the main agent confirms each with the user before writing.

## Memory File Format

```
One sentence summary of the learning (~8-15 words).
Full description with context, nuance, and reasoning.
<evidence: what session/correction produced this learning>
```

Files live in `.claude/memory/<category>/<topic>.md`. Categories emerge organically from learnings. The index is rebuilt after each write.

## Installation

```bash
claude plugin install inline-experiential-learning@faire
```

## Components

| Component | Type | Purpose |
|-----------|------|---------|
| `hooks/scripts/session-start.sh` | SessionStart command hook | Reads INDEX.md, returns as additionalContext |
| `hooks/hooks.json` | Hook config | Wires up SessionStart + Stop hooks |
| `prompts/handle-learning.md` | Promptlet | Instructions for main agent after learning recommendation |
| `scripts/rebuild-memory-index.sh` | Script | Deterministic index builder from memory filesystem |

## How Learning Works

1. Stop hook agent reads the last assistant message for correction/discovery signals
2. If signals found, checks for duplicates against existing memory files
3. Greps transcript for `.claude/memory/` Read calls to find untriggered memories
4. Recommends learnings with type, suggested file path, and content
5. Main agent reads `handle-learning.md` promptlet and confirms each with user
6. On confirmation, writes the memory file and rebuilds the index

## Requirements

- `python3` (for JSON escaping in session-start hook)
- `.claude/memory/` directory in project (created on first learning)
