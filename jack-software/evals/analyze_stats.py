#!/usr/bin/env python3
"""Analyze eval statistics by git commit/revision."""

from collections import defaultdict
from hidden_logger import Logger
from writing_services.constants import REPO_ROOT


def analyze_eval_stats(logger: Logger) -> None:
    """Analyze and display eval statistics grouped by git revision."""
    all_runs = logger.get_all_eval_runs()

    if not all_runs:
        print("No eval runs found in the database.")
        return

    # Filter out runs with empty git diffs
    runs_with_diffs = [run for run in all_runs if run.git_diff.strip()]

    if not runs_with_diffs:
        print("No eval runs with git diffs found in the database.")
        return

    filtered_count = len(all_runs) - len(runs_with_diffs)
    if filtered_count > 0:
        print(f"Filtered out {filtered_count} eval run(s) with empty git diffs\n")

    # Group runs by git revision
    runs_by_revision = defaultdict(list)
    for run in runs_with_diffs:
        runs_by_revision[run.git_revision].append(run)

    print(f"Found {len(runs_with_diffs)} eval runs (with git diffs) across {len(runs_by_revision)} revisions\n")
    print("=" * 80)

    # Analyze each revision
    for revision, runs in sorted(runs_by_revision.items(), key=lambda x: x[1][0].timestamp, reverse=True):
        print(f"\nRevision: {revision[:12]}")
        print(f"Total runs: {len(runs)}")
        print(f"Most recent: {runs[0].timestamp}")

        # Aggregate eval results across all runs for this revision
        eval_results_aggregated = defaultdict(lambda: {"passed": 0, "total": 0})

        for run in runs:
            for eval_name, result in run.eval_results.items():
                eval_results_aggregated[eval_name]["total"] += 1
                # Handle both boolean and dict-style results
                if isinstance(result, bool):
                    if result:
                        eval_results_aggregated[eval_name]["passed"] += 1
                elif isinstance(result, dict):
                    # Assume dict has a "passed" or "success" key
                    if result.get("passed") or result.get("success"):
                        eval_results_aggregated[eval_name]["passed"] += 1
                else:
                    # Treat truthy values as passed
                    if result:
                        eval_results_aggregated[eval_name]["passed"] += 1

        # Display pass rates
        print("\nEval Results:")
        for eval_name, stats in sorted(eval_results_aggregated.items()):
            pass_rate = (stats["passed"] / stats["total"]) * 100
            print(f"  {eval_name:40} {stats['passed']:3}/{stats['total']:3} ({pass_rate:5.1f}%)")

        print("-" * 80)


if __name__ == "__main__":
    db_path = str(REPO_ROOT / "evals.db")
    logger = Logger(db_path)
    try:
        analyze_eval_stats(logger)
    finally:
        logger.close()
