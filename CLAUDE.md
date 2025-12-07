# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Overview

This is a Claude Code plugin marketplace repository containing multiple plugins for software engineering workflows. The repository follows a multi-plugin structure where each top-level directory represents a separate plugin.

**For detailed information about each plugin, see:**
- `jack-software/` - Development skills (see README.md in that directory)
- `browser-testing/` - Browser automation with Playwright (see `browser-testing/README.md`)
- `supabase/` - Supabase operations agent (see `supabase/README.md`)
- `logs/` - Tool usage logging (see `logs/README.md`)

**For plugin development patterns, see:**
- Creating skills: `jack-software/skills/creating-slash-commands/SKILL.md`
- Creating hooks: `jack-software/skills/creating-hooks/SKILL.md`
- Creating slash commands: `jack-software/skills/creating-slash-commands/SKILL.md`

## Repository Structure

This is a multi-plugin marketplace. Each top-level directory (jack-software, browser-testing, supabase, logs) is an independent plugin with its own `plugin.json`. The `.claude-plugin/marketplace.json` file defines all available plugins in this marketplace.

**Key files:**
- `.claude-plugin/marketplace.json` - Marketplace metadata listing all plugins
- `{plugin}/plugin.json` - Individual plugin configuration
- `{plugin}/README.md` - Plugin-specific documentation

## Development Workflow

### Testing Plugins Locally

```bash
# Add this local marketplace to Claude Code
claude plugin marketplace add /Users/Jack/Code/github.com/jack-michaud/faire

# Install a specific plugin
claude plugin install jack-software@faire
claude plugin install browser-testing@faire
claude plugin install supabase@faire
claude plugin install logs@faire

# Verify installation
claude plugin list
claude skills list
```

### Plugin Component Patterns

When working with plugin components, reference the existing implementations:

**Skills:** Look at `jack-software/skills/` for examples. Skills are markdown files with YAML frontmatter (`name` and `description` fields). Main skill content should be in `SKILL.md`.

**Hooks:** See `logs/hooks/hooks.json` for the hooks definition pattern. Hook scripts (like `logs/scripts/pre_tool_use.py`) read JSON from stdin and write JSON to stdout.

**Slash Commands:** See `logs/commands/` for examples. Commands are markdown files with YAML frontmatter that expand to prompts.

**Agents:** See `supabase/agents/supabase-expert.md` for the agent definition pattern. Agents can reference resource files from a `resources/` directory.

**MCP Servers:** See `browser-testing/plugin.json` for MCP server configuration in the `mcpServers` array.

## Architecture

This repository uses a **multi-plugin marketplace architecture**. Each plugin is independently versioned and installable. Plugins can contain any combination of:
- Skills (process documentation)
- Hooks (event-driven scripts)
- Slash Commands (quick prompts)
- Agents (specialized subagents)
- MCP Servers (external tool integrations)

The marketplace system allows users to install only the plugins they need rather than a monolithic package.
