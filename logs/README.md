# Logs Plugin

Logging hooks and commands for tracking Claude Code tool usage.

Heavily inspired by [disler's Claude Hooks repo](https://github.com/disler/claude-code-hooks-mastery).

## Features

- **Automatic Logging**: Logs all tool calls before and after execution
- **Pre-Tool Logging**: Captures tool names and inputs before execution
- **Post-Tool Logging**: Captures tool names, inputs, and outputs after execution
- **Slash Commands**: View and manage logs directly from Claude Code

## Installation

Install via the faire marketplace:

```bash
claude plugin install logs@faire
```

## Usage

### Automatic Logging

Once installed, the plugin automatically logs all tool usage to:
- `logs/pre_tool_use.json` - Tool calls before execution
- `logs/post_tool_use.json` - Tool results after execution

### Slash Commands

#### `/logs:view-pre`
View all pre-tool-use logs, showing tool calls before execution.

#### `/logs:view-post`
View all post-tool-use logs, showing tool results after execution.

#### `/logs:stats`
Display statistics about tool usage including:
- Total tool calls
- Most frequently used tools
- Tool usage breakdown

#### `/logs:clear`
Clear all log files to start fresh.

## Log Format

Logs are stored as JSON arrays with the following structure:

### Pre-Tool Use
```json
[
  {
    "tool_name": "Bash",
    "tool_input": {
      "command": "ls -la",
      "description": "List directory contents"
    },
    "session_id": "abc123",
    "cwd": "/path/to/project"
  }
]
```

### Post-Tool Use
```json
[
  {
    "tool_name": "Bash",
    "tool_input": {
      "command": "ls -la"
    },
    "tool_response": {
      "stdout": "...",
      "stderr": "",
      "exit_code": 0
    },
    "session_id": "abc123"
  }
]
```

## Requirements

- Python 3.8+
- uv (for running hook scripts)

## License

MIT
