import asyncio
from pathlib import Path

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ClaudeSDKClient,
    TextBlock,
)


async def main(
    gym_project_directory: Path,
) -> None:
    options = ClaudeAgentOptions(
        model="haiku",
        cwd=gym_project_directory,
        allowed_tools=["Skill", "Read", "Glob", "Write", "Edit"],
        # max_turns=2,
    )

    client = ClaudeSDKClient(options=options)

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
