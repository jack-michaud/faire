#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk"]
# ///
"""
Autonomously add a procedure to the appropriate skill.

Usage:
    ./scripts/add-procedure.py "<procedure description>"

Delegates to the /add-procedure slash command from the jack-software plugin.
When run from the faire repo, procedures go into plugin skills/ directories.
When run from any other project, procedures go into .claude/skills/.
"""

import argparse
import asyncio
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, SdkPluginConfig

REPO_ROOT = Path(__file__).resolve().parent.parent
JACK_SOFTWARE_DIR = REPO_ROOT / "jack-software"


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="Add a procedure to the appropriate skill"
    )
    parser.add_argument("procedure", help="Description of the procedure to add")
    args = parser.parse_args()

    async for message in query(
        prompt=f"/jack-software:add-procedure {args.procedure}",
        options=ClaudeAgentOptions(
            cwd=str(REPO_ROOT),
            allowed_tools=["Read", "Write", "Edit", "Glob", "Grep", "Bash(make:*)", "Bash(jj:*)"],
            permission_mode="acceptEdits",
            max_turns=20,
            model="claude-sonnet-4-6",
            setting_sources=["project"],
            plugins=[SdkPluginConfig(type="local", path=str(JACK_SOFTWARE_DIR))],
        ),
    ):
        if isinstance(message, ResultMessage):
            print(message.result)


if __name__ == "__main__":
    asyncio.run(main())
