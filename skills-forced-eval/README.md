# Skills Forced Eval Plugin

A UserPromptSubmit hook that forces Claude to explicitly evaluate each available skill before proceeding with implementation.

**Measured to 4x skill activation rate** - from ~20% to ~80% activation when skills are relevant. See [the original research](https://www.reddit.com/r/ClaudeCode/comments/1oywsa1/claude_code_skills_activate_20_of_the_time_heres/).

## What it does

This plugin adds a hook that intercepts every user prompt submission and injects instructions requiring Claude to:

1. **Evaluate** each skill in `<available_skills>` with YES/NO and a reason
2. **Activate** relevant skills by calling `Skill()` tool for each YES
3. **Implement** only after skill activation is complete

## Installation

Enable the plugin in your `.claude/settings.json`:

```json
{
  "enabledPlugins": {
    "skills-forced-eval@fay-plugin-marketplace": true
  },
  "extraKnownMarketplaces": {
    "fay-plugin-marketplace": {
      "source": {
        "source": "github",
        "repo": "fayhealthinc/claude-plugin-marketplace"
      }
    }
  }
}
```

## Source

Based on: https://github.com/spences10/svelte-claude-skills/blob/main/.claude/hooks/skill-forced-eval-hook.sh

