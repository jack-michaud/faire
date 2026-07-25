#!/usr/bin/env python3
"""Evaluate the STE linter end to end.

1. Ask Claude (via the Claude Agent SDK) to write a tech spec for a GitHub
   clone, with no STE instructions.
2. Lint the baseline with ste_lint.py and save the feedback.
3. Ask Claude to revise the spec by applying the linter feedback.
4. Lint the revised spec.

Run with: uv run --no-project --with claude-agent-sdk python run_eval.py
"""

import asyncio
import pathlib
import subprocess
import sys

from claude_agent_sdk import (
    AssistantMessage,
    ClaudeAgentOptions,
    ResultMessage,
    TextBlock,
    query,
)

HERE = pathlib.Path(__file__).resolve().parent
LINTER = HERE.parents[1] / "scripts" / "ste_lint.py"

BASELINE_PROMPT = """\
Write a technical specification for "GitForge", a self-hosted web-based GitHub
clone (a git hosting service with a web UI).

Requirements for the document:
- Markdown, roughly 600-900 words.
- Sections: Overview, Goals, Architecture, Core Features (repository hosting,
  authentication and permissions, pull requests, issues), API Design,
  Data Model, Non-Functional Requirements.
- Write it the way a software engineer would normally write an internal tech
  spec for their team.

Output ONLY the markdown document, with no preamble or commentary.
"""

REVISION_PROMPT_TEMPLATE = """\
Below is a technical specification, followed by review feedback from a
Simplified Technical English (ASD-STE100) linter.

Revise the specification so that it satisfies the linter feedback:
- Keep the document structure, section headings, and technical content the
  same. Change the wording, not the meaning.
- Fix every finding: split long sentences, use the active voice and the simple
  present tense, replace unapproved words with the suggested alternatives,
  remove contractions and "and/or", and break up noun clusters.
- Technical names (for example "GitForge", "PostgreSQL", "REST") are allowed
  by STE. If a finding is a false positive on a technical name, you can leave
  that term as it is.

Output ONLY the revised markdown document, with no preamble or commentary.

--- SPECIFICATION ---

{spec}

--- LINTER FEEDBACK ---

{feedback}
"""


async def generate(prompt: str) -> str:
    parts = []
    options = ClaudeAgentOptions(max_turns=1, allowed_tools=[])
    async for message in query(prompt=prompt, options=options):
        if isinstance(message, AssistantMessage):
            for block in message.content:
                if isinstance(block, TextBlock):
                    parts.append(block.text)
        elif isinstance(message, ResultMessage) and message.is_error:
            raise RuntimeError(f"agent error: {message.result}")
    text = "".join(parts).strip()
    if not text:
        raise RuntimeError("agent returned no text")
    return text + "\n"


def lint(path: pathlib.Path, fmt: str) -> str:
    proc = subprocess.run(
        [sys.executable, str(LINTER), "--format", fmt, str(path)],
        capture_output=True,
        text=True,
    )
    return proc.stdout


async def main() -> None:
    print("1/4 generating baseline spec...", flush=True)
    baseline = await generate(BASELINE_PROMPT)
    (HERE / "baseline.md").write_text(baseline)

    print("2/4 linting baseline...", flush=True)
    feedback = lint(HERE / "baseline.md", "feedback")
    (HERE / "feedback.md").write_text(feedback)
    (HERE / "baseline.findings.json").write_text(lint(HERE / "baseline.md", "json"))

    print("3/4 generating revision from linter feedback...", flush=True)
    revised = await generate(
        REVISION_PROMPT_TEMPLATE.format(spec=baseline, feedback=feedback)
    )
    (HERE / "revised.md").write_text(revised)

    print("4/4 linting revised spec...", flush=True)
    (HERE / "revised.findings.json").write_text(lint(HERE / "revised.md", "json"))
    print("done")


if __name__ == "__main__":
    asyncio.run(main())
