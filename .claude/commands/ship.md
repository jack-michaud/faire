---
description: Commit changes, bump plugin version, and push to main.
allowed-tools: Bash(jj diff:*), Bash(jj log:*), Bash(jj describe:*), Bash(jj new:*), Bash(jj b:*), Bash(jj git push:*), Bash(jj split:*), Bash(make bump-patch:*), Read, Glob
---

# Ship

1. Identify which plugin(s) were modified by checking the changed files.
2. Bump the patch version for each modified plugin: `make bump-patch PLUGIN=<name>`
3. Commit using the committing skill.
4. Move main and push: `jj b s main -r @- && jj git push -b main`
