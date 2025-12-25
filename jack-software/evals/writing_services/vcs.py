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


def get_vcs_diff() -> str:
    """Get diff for current VCS revision (jj or git).

    Returns:
        The diff output as a string, or empty string if unavailable
    """
    # Try jj first
    try:
        result = subprocess.run(
            ["jj", "diff", "-r", "@"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        pass

    # Fall back to git
    try:
        result = subprocess.run(
            ["git", "diff", "HEAD"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout
    except (subprocess.CalledProcessError, FileNotFoundError):
        return ""
