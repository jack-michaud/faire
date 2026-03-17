#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk"]
# ///
"""
Add a command or skill to a plugin in the faire marketplace.

Usage:
    ./scripts/add-component.py <plugin> <command|skill> "<description of what to create>"

Examples:
    ./scripts/add-component.py logs command "A command that shows the last N tool calls with timestamps"
    ./scripts/add-component.py jack-software skill "A skill for writing GraphQL resolvers following best practices"
"""

import argparse
import asyncio
import sys
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage


REPO_ROOT = Path(__file__).resolve().parent.parent


def build_system_prompt(plugin: str, component_type: str) -> str:
    return f"""\
You are a plugin component creator for a Claude Code plugin marketplace repository.

## Repository layout

The repo root is: {REPO_ROOT}

Each top-level directory is a plugin (e.g. jack-software/, logs/, browser-testing/).
Each plugin has a `plugin.json` with name, version, description, author, and optional
`skills` and `hooks` fields.

## How skills work

- Located under `<plugin>/skills/<skill-name>/SKILL.md`
- SKILL.md has YAML frontmatter with `name` and `description`, then markdown body:
  ```
  ---
  name: My Skill Name
  description: One-line description of when this skill triggers.
  ---

  <skill instructions in markdown>
  ```
- Skills can have `resources/` subdirectories with supporting markdown files.
- The `description` field is critical — it determines when the skill is activated.
  Write it as a trigger condition, e.g. "Use when writing Python services that interface with external systems."

## How commands work

- Located under `<plugin>/commands/<command-name>.md`
- Commands have YAML frontmatter with at minimum `description`, optionally `allowed-tools`:
  ```
  ---
  description: One-line description of the command
  allowed-tools: Read,Edit,Bash(git:*)
  ---

  <command prompt body in markdown>
  ```
- Use `$ARGUMENTS` in the body to reference user-provided arguments.
- Commands expand into prompts that Claude executes.

## Your task

You are adding a **{component_type}** to the **{plugin}** plugin.

## Instructions

1. First, read `{plugin}/plugin.json` to understand the plugin.
2. If adding a skill, check if the plugin.json has a `"skills"` field. If not, you'll need to add one pointing to `"./skills/"`.
3. Look at existing {component_type}s in the plugin (or in other plugins) for style reference.
4. Create the new {component_type} file(s) following the patterns above.
5. Print a summary of what you created.

Keep the content focused and concise. Don't over-engineer.
"""


def build_prompt(component_type: str, description: str) -> str:
    return f"Create a new {component_type} based on this description: {description}"


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add a command or skill to a faire plugin"
    )
    parser.add_argument("plugin", help="Plugin name (e.g. jack-software, logs)")
    parser.add_argument(
        "type",
        choices=["command", "skill"],
        help="Component type to create",
    )
    parser.add_argument("description", help="Description of what to create")
    args = parser.parse_args()

    plugin_dir = REPO_ROOT / args.plugin
    if not (plugin_dir / "plugin.json").exists():
        print(f"Error: {args.plugin}/plugin.json not found", file=sys.stderr)
        print("Available plugins:", file=sys.stderr)
        for p in sorted(REPO_ROOT.glob("*/plugin.json")):
            print(f"  - {p.parent.name}", file=sys.stderr)
        sys.exit(1)

    system_prompt = build_system_prompt(args.plugin, args.type)
    prompt = build_prompt(args.type, args.description)

    async for message in query(
        prompt=prompt,
        options=ClaudeAgentOptions(
            cwd=str(REPO_ROOT),
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep"],
            system_prompt=system_prompt,
            permission_mode="acceptEdits",
            max_turns=15,
            model="claude-haiku-4-5",
        ),
    ):
        if isinstance(message, ResultMessage):
            print(message.result)


if __name__ == "__main__":
    asyncio.run(main())
