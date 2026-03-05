---
description: Save a successful workflow into a skill's reference files
argument-hint: <skill-name>
allowed-tools: Bash(jj:*), Read, Write, Edit, Glob, Grep
---

# Update Skill

Persist a successful workflow from this conversation into a skill's knowledge base.

## Instructions

1. **Identify the target skill and content**: Use the argument as the skill name. Review the conversation for the workflow, pattern, or knowledge to capture.

2. **Spawn the skill-updater agent**: Delegate all file edits to the `skill-updater` agent. Pass it:
   - The target skill name
   - The workflow content to persist (summarize the key steps, commands, patterns, and any corrections/anti-patterns discovered)

3. **After the agent completes**: Review the summary of changes. Then run the jj commit and push:

```bash
jj describe -m "feat: update <skill-name> skill with <topic>"
jj new
jj bookmark set main -r @-
jj git push
```

Replace `<skill-name>` and `<topic>` with the actual values from the agent's summary.

## Example

```
/update-skill modal
```

This will:
1. Capture the successful workflow from the conversation
2. Create a reference file in `jack-software/skills/modal/resources/`
3. Update `jack-software/skills/modal/SKILL.md` with the new resource
4. Bump the version in `plugin.json` and `marketplace.json`
5. Commit and push via jj
