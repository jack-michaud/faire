"""LLM-based helpers for analyzing generated Python code in evals."""

from pathlib import Path

from claude_agent_sdk import AssistantMessage, ClaudeAgentOptions, TextBlock, query


async def check_no_constructor_side_effects(file_path: Path) -> bool:
    """Check if __init__ methods avoid side effects like IO operations using an LLM.

    Uses an LLM to semantically analyze whether:
    - __init__ methods perform IO operations (file, network, database operations)
    - IO operations are properly deferred to @cached_property decorated methods

    Returns True if constructors have no side effects, False otherwise.
    """
    if not file_path.exists():
        return False

    try:
        content = file_path.read_text()
    except (UnicodeDecodeError, OSError):
        return False

    # Handle edge cases: empty files or files with no content to analyze
    if not content.strip():
        return True

    # Check if file has any classes with __init__ methods using simple heuristic
    # If no __init__ methods, no violation is possible
    if "__init__" not in content:
        return True

    prompt = f"""Analyze this Python code to check if it follows the guideline: "No side effects in constructor".

Guidelines:
- __init__ methods should NOT perform IO operations (file operations, network calls, database operations)
- IO operations should be deferred to @cached_property decorated methods and lazily evaluated
- Simple attribute assignments in __init__ are fine
- If there are no __init__ methods in the code, there can be no violation (respond YES)

Code to analyze:
```python
{content}
```

Does this code follow the guideline? Respond with ONLY "YES" or "NO" followed by a brief explanation.
- YES means the code follows the guideline (no IO in __init__, or no __init__ methods at all)
- NO means the code violates the guideline (has IO operations in __init__)
"""

    options = ClaudeAgentOptions(model="haiku")
    response_text = ""

    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    response_text += block.text

    # Parse the response - look for YES at the start
    response_text = response_text.strip().upper()
    return response_text.startswith("YES")
