#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["claude-agent-sdk"]
# ///
"""
Test the /ship-skill command end-to-end.

Usage:
    ./scripts/test-ship-skill.py

Invokes /ship-skill with a test procedure description targeting the faire
marketplace path and verifies:
- The command completes without error
- The result message indicates a successful ship
"""

import asyncio
from pathlib import Path

from claude_agent_sdk import query, ClaudeAgentOptions, ResultMessage, SdkPluginConfig

REPO_ROOT = Path(__file__).resolve().parent.parent
JACK_SOFTWARE_DIR = REPO_ROOT / "jack-software"


async def main() -> None:
    result_text = ""

    async for message in query(
        prompt="/jack-software:ship-skill add a procedure for verifying the ship-skill command works end-to-end",
        options=ClaudeAgentOptions(
            cwd=str(REPO_ROOT),
            allowed_tools=[
                "Read", "Write", "Edit", "Glob", "Grep",
                "Bash(jj:*)", "Bash(make:*)", "Bash(cd:*)",
                "Bash(rm:*)", "Bash(mktemp:*)",
            ],
            permission_mode="acceptEdits",
            max_turns=30,
            model="claude-sonnet-4-6",
            setting_sources=["project"],
            plugins=[SdkPluginConfig(type="local", path=str(JACK_SOFTWARE_DIR))],
        ),
    ):
        if isinstance(message, ResultMessage):
            result_text = message.result
            print(result_text)

    if not result_text:
        print("ERROR: No result message received")
        raise SystemExit(1)

    if "Ship Summary" in result_text:
        print("\nTEST PASSED: Ship skill command completed successfully")
    elif "Ship Failed" in result_text:
        print(f"\nTEST FAILED: Ship reported failure.\nResult: {result_text}")
        raise SystemExit(1)
    else:
        print(f"\nTEST FAILED: Result did not contain expected output format.\nResult: {result_text}")
        raise SystemExit(1)


if __name__ == "__main__":
    asyncio.run(main())
