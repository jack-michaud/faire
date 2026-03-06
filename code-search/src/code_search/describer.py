"""Haiku descriptions via Agent SDK with bounded concurrency."""

import asyncio

from claude_agent_sdk import query
from claude_agent_sdk.types import AssistantMessage, ClaudeAgentOptions, TextBlock

from code_search.chunker import CodeChunk

MAX_CONCURRENT = 3
_semaphore = asyncio.Semaphore(MAX_CONCURRENT)


async def _describe_chunk(chunk: CodeChunk, file_path: str) -> str | None:
    """Generate a brief description for a code chunk using Haiku."""
    async with _semaphore:
        try:
            prompt = (
                f"Describe what this code does in one sentence. "
                f"File: {file_path}, {chunk.chunk_type}: {chunk.chunk_name}\n\n"
                f"```\n{chunk.source_code[:2000]}\n```"
            )
            messages = query(
                prompt=prompt,
                options=ClaudeAgentOptions(
                    model="haiku",
                    max_turns=1,
                    permission_mode="bypassPermissions",
                ),
            )
            for msg in messages:
                if isinstance(msg, AssistantMessage):
                    for block in msg.content:
                        if isinstance(block, TextBlock):
                            return block.text
        except Exception:
            pass
    return None


async def describe_chunks(
    chunks: list[CodeChunk], file_path: str
) -> list[str | None]:
    """Generate descriptions for all chunks with bounded concurrency."""
    tasks = [_describe_chunk(chunk, file_path) for chunk in chunks]
    return await asyncio.gather(*tasks)
