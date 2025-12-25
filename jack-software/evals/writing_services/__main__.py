import argparse
import asyncio
import time
from datetime import datetime
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    HookMatcher,
    ResultMessage,
    SystemMessage,
    TextBlock,
    ToolUseBlock,
)

from ..hidden_logger import EvalRunResult, Logger
from .checks import EvalResult
from .skills import block_reading_eval_scripts_hook, skills_forced_eval_hook
from .vcs import get_git_revision

BLOCKED_FILES = [
    "writing_services.py",
    "hidden_logger.py",
]


async def main(
    gym_project_directory: Path,
) -> None:
    logger = Logger()
    eval_result = EvalResult()

    # Track timing and tokens
    start_time = time.time()
    total_input_tokens = 0
    total_output_tokens = 0

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

                if isinstance(block, ToolUseBlock):
                    if (
                        block.name == "Skill"
                        and "writing-python-services" in block.input.get("skill")
                    ):
                        eval_result.used_service_skill.mark(True)

        if isinstance(message, ResultMessage):
            # Track token usage
            if message.usage:
                # > The input_tokens field represents only the tokens that come after the last cache breakpoint in your request - not all the input tokens you sent.
                # > To calculate total input tokens:
                # > ```
                # > total_input_tokens = cache_read_input_tokens + cache_creation_input_tokens + input_tokens
                # > ```
                # https://platform.claude.com/docs/en/build-with-claude/prompt-caching#tracking-cache-performance
                total_input_tokens = (
                    message.usage.get("input_tokens")
                    + message.usage.get("cache_read_input_tokens")
                    + message.usage.get("cache_creation_input_tokens")
                )
                total_output_tokens = message.usage.get("output_tokens")

    # Calculate wall clock time
    wall_clock_time = time.time() - start_time

    # Log the eval run
    run_result = EvalRunResult(
        wall_clock_time=wall_clock_time,
        input_tokens=total_input_tokens,
        output_tokens=total_output_tokens,
        eval_results=eval_result.to_dict(),
        git_revision=get_git_revision(),
        working_directory=str(gym_project_directory.absolute()),
        timestamp=datetime.now(),
    )

    run_id = logger.log_eval_run(run_result)
    print(f"\nLogged eval run with ID: {run_id}")
    print(f"Wall clock time: {wall_clock_time:.2f}s")
    print(f"Tokens - Input: {total_input_tokens}, Output: {total_output_tokens}")
    print(f"Results: {eval_result.to_dict()}")

    # Clean up
    logger.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("gym_project_directory", type=Path)

    args = parser.parse_args()

    asyncio.run(main(args.gym_project_directory))
