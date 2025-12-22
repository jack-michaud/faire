import asyncio
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookContext,
    HookInput,
    HookJSONOutput,
    HookMatcher,
    SystemMessage,
    TextBlock,
)


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

    if "writing_services.py" in file_path:
        return {
            "decision": "block",
            "reason": "This is the eval we're running now: this would be like reading the answers to the test! No peeking!",
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


class Check:
    _passed: bool
    _value: bool

    def __init__(self, default: bool, passed: bool) -> None:
        self._passed = passed
        self._value = default

    def mark(self, value: bool) -> None:
        self._value = value

    def did_pass(self) -> bool:
        return self._value == self._passed


class EvalResult:
    used_service_skill = Check(default=False, passed=True)


async def main(
    gym_project_directory: Path,
) -> None:
    options = ClaudeAgentOptions(
        model="haiku",
        cwd=gym_project_directory,
        allowed_tools=["Skill", "Read", "Glob", "Write", "Edit"],
        plugins=[
            # TODO: Local plugins' hooks are completely busted. I will make a manual hook instead.
            # https://github.com/anthropics/claude-code/issues/12151
            # {
            #    "type": "local",
            #    "path": str(Path(__file__).parent.parent.parent / "skills-forced-eval"),
            # }
            {
                "type": "local",
                "path": str(Path(__file__).parent.parent.parent / "jack-software"),
            }
        ],
        hooks={
            "PreToolUse": [
                HookMatcher(matcher="Read", hooks=[block_reading_eval_scripts_hook])
            ],
            "UserPromptSubmit": [
                HookMatcher(matcher="*", hooks=[skills_forced_eval_hook])
            ],
        },
        # max_turns=2,
    )

    client = ClaudeSDKClient(options=options)
    await client.connect()

    await client.query("""Write a logging service in jack-software/evals/logger.py that stores eval run results.
    We should be able to store:
    - the wall clock time the eval took, 
    - number of input and output tokens the agent took, 
    - a dictionary of eval results,
    - the git commit revision or jj hash,
    - the working directory of the run,
    - the timestamp

    All in a sqlite database.""")

    async for message in client.receive_response():
        print(message)
        if isinstance(message, SystemMessage):
            if message.subtype == "init":
                print(f"Plugins: {message.data.get('plugins')}")
                continue
            print(message)

        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    print(f"Claude: {block.text}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("gym_project_directory", type=Path)

    args = parser.parse_args()

    asyncio.run(main(args.gym_project_directory))
