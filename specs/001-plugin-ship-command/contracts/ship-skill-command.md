# Contract: /ship-skill Slash Command

## Interface

**Command**: `/jack-software:ship-skill`
**Arguments**: Free-text description of what to add (procedure, skill, or command)
**Invocation context**: Any Claude Code session, any working directory

## Argument Examples

```
/ship-skill add a procedure for deploying staging environments
/ship-skill create a skill for writing GraphQL resolvers in the jack-software plugin
/ship-skill add a command to logs plugin that shows error rate trends
```

## Behavior Contract

### Input Parsing

The command receives `$ARGUMENTS` as free-text. It determines:
1. **Target**: faire marketplace (default for reusable workflows) or local project (project-specific processes)
2. **Content type**: procedure (added to existing skill), new skill, or new command
3. **Target plugin**: inferred from description or defaults to `jack-software`

### Output Contract

On success, the command reports:
```
## Ship Summary

- **Action**: [Created new skill / Added procedure to existing skill / Created command]
- **Location**: [file path(s)]
- **Plugin**: [plugin name]
- **Version**: [old] → [new]
- **Commit**: [commit message]
- **Push**: [Pushed to main / Local commit only]
```

On failure:
```
## Ship Failed

- **Step**: [which step failed]
- **Issue**: [specific problem]
- **Action needed**: [what the user should do]
```

### Allowed Tools

```
Read, Write, Edit, Glob, Grep, Bash(jj:*), Bash(make:*), Bash(cd:*), Bash(rm:*), Bash(mktemp:*)
```

### Error Conditions

| Condition | Behavior |
|-----------|----------|
| Faire repo not found at known path | Error with path suggestion |
| `jj git fetch` fails | Error suggesting network check |
| Workspace creation fails | Error suggesting manual `jj git fetch` |
| Validation fails (bad frontmatter/JSON) | Abort before commit; report specific issues |
| `jj git push` fails (stale refs) | Follow stale-remote-push recovery procedure |
| `jj git push` fails (network) | Report push failure; commit preserved in workspace |
