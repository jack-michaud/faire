#!/usr/bin/env python3
"""Validate a plugin.json's mcpServers field.

Usage:
    python scripts/validate_plugin.py path/to/plugin.json
"""

import json
import sys
from pathlib import Path


def validate_mcp_file(mcp_path: Path) -> list[str]:
    """Validate an .mcp.json file has the correct structure."""
    errors = []
    if not mcp_path.exists():
        errors.append(f"Referenced MCP file does not exist: {mcp_path}")
        return errors

    try:
        data = json.loads(mcp_path.read_text())
    except json.JSONDecodeError as e:
        errors.append(f"Invalid JSON in {mcp_path}: {e}")
        return errors

    if not isinstance(data, dict):
        errors.append(f"{mcp_path}: root must be an object")
        return errors

    servers = data.get("mcpServers")
    if servers is None:
        errors.append(f"{mcp_path}: missing 'mcpServers' key")
        return errors

    if not isinstance(servers, dict):
        errors.append(f"{mcp_path}: 'mcpServers' must be an object")
        return errors

    for name, config in servers.items():
        if not isinstance(config, dict):
            errors.append(f"{mcp_path}: server '{name}' config must be an object")
        elif "command" not in config:
            errors.append(f"{mcp_path}: server '{name}' missing required 'command' field")

    return errors


def validate_mcp_servers(plugin_path: Path, mcp_servers) -> list[str]:
    """Validate the mcpServers field of a plugin.json."""
    errors = []

    if isinstance(mcp_servers, str):
        mcp_path = plugin_path.parent / mcp_servers
        errors.extend(validate_mcp_file(mcp_path))

    elif isinstance(mcp_servers, dict):
        for name, config in mcp_servers.items():
            if not isinstance(config, dict):
                errors.append(f"mcpServers.{name}: config must be an object")
            elif "command" not in config:
                errors.append(f"mcpServers.{name}: missing required 'command' field")

    elif isinstance(mcp_servers, list):
        if all(isinstance(item, str) for item in mcp_servers):
            for item in mcp_servers:
                mcp_path = plugin_path.parent / item
                errors.extend(validate_mcp_file(mcp_path))
        else:
            errors.append(
                "mcpServers: array-of-objects format is not supported. "
                "Use a string path to .mcp.json, an object with server configs, "
                "or an array of string paths."
            )

    else:
        errors.append(
            f"mcpServers: invalid type '{type(mcp_servers).__name__}'. "
            "Expected string, object, or array of strings."
        )

    return errors


def validate_plugin(plugin_path: Path) -> list[str]:
    """Validate a plugin.json file."""
    errors = []

    if not plugin_path.exists():
        return [f"File not found: {plugin_path}"]

    try:
        data = json.loads(plugin_path.read_text())
    except json.JSONDecodeError as e:
        return [f"Invalid JSON: {e}"]

    if not isinstance(data, dict):
        return ["plugin.json root must be an object"]

    for field in ("name", "version", "description"):
        if field not in data:
            errors.append(f"Missing required field: {field}")

    mcp_servers = data.get("mcpServers")
    if mcp_servers is not None:
        errors.extend(validate_mcp_servers(plugin_path, mcp_servers))

    return errors


def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <plugin.json> [plugin.json ...]", file=sys.stderr)
        sys.exit(1)

    exit_code = 0
    for arg in sys.argv[1:]:
        plugin_path = Path(arg).resolve()
        print(f"Validating {arg}...")
        errors = validate_plugin(plugin_path)

        if errors:
            for error in errors:
                print(f"  ERROR: {error}")
            exit_code = 1
        else:
            print("  OK")

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
