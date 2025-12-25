import asyncio
from pathlib import Path

from claude_agent_sdk import HookContext, HookInput, HookJSONOutput

BLOCKED_FILES = [
    "writing_services.py",
    "hidden_logger.py",
]


async def block_reading_eval_scripts_hook(
    input: HookInput, tool_use_id: str | None, context: HookContext
) -> HookJSONOutput:
    if input["hook_event_name"] != "PreToolUse":
        # Not applicable
        return {}
    if input["tool_name"] != "Read":
        # Not applicable
        return {}

    file_path = input["tool_input"]["file_path"]

    if any(file in file_path for file in BLOCKED_FILES):
        return {
            "decision": "block",
            "reason": "This file is related to the eval we're running now: this would be like reading the answers to the test! No peeking!",
        }

    return {}


async def skills_forced_eval_hook(
    input: HookInput, tool_use_id: str | None, context: HookContext
) -> HookJSONOutput:
    if input["hook_event_name"] != "UserPromptSubmit":
        return {}

    cmd = str(
        Path(__file__).parent.parent.parent
        / "skills-forced-eval"
        / "hooks"
        / "skills-forced-eval.sh"
    )
    process = await asyncio.subprocess.create_subprocess_shell(cmd)
    assert process.stdout
    stdout_bytes = await process.stdout.read()
    stdout_str = stdout_bytes.decode("utf-8")

    return {"reason": stdout_str}
