#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.8"
# ///

"""Generic hook logger. Appends stdin JSON to logs/<name>.json.

Usage: log_hook.py <log_name>
Example: log_hook.py stop
  -> appends to logs/stop.json
"""

import json
import sys
from pathlib import Path

def main():
    try:
        if len(sys.argv) < 2:
            sys.exit(0)

        log_name = sys.argv[1]
        input_data = json.load(sys.stdin)

        log_dir = Path.cwd() / 'logs'
        log_dir.mkdir(parents=True, exist_ok=True)
        log_path = log_dir / f'{log_name}.json'

        if log_path.exists():
            with open(log_path, 'r') as f:
                try:
                    log_data = json.load(f)
                except (json.JSONDecodeError, ValueError):
                    log_data = []
        else:
            log_data = []

        log_data.append(input_data)

        with open(log_path, 'w') as f:
            json.dump(log_data, f, indent=2)

        sys.exit(0)

    except json.JSONDecodeError:
        sys.exit(0)
    except Exception:
        sys.exit(0)

if __name__ == '__main__':
    main()
