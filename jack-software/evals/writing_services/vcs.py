import subprocess


def get_git_revision() -> str:
    """Get current VCS revision (jj or git)."""
    # Try jj first
    try:
        result = subprocess.run(
            ["jj", "log", "-r", "@-", "--no-graph", "-T", "commit_id"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fall back to git
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"
