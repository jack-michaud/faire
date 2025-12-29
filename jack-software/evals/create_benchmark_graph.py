#!/usr/bin/env python3
"""Generate a fancy benchmark comparison graph for model eval results."""

import argparse
import sqlite3
import json
from collections import defaultdict
from pathlib import Path
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime


def get_eval_results(db_path: str, revisions: list[tuple[str, str]]):
    """Extract and aggregate eval results from the database.

    Args:
        db_path: Path to the SQLite database
        revisions: List of (git_revision, label) tuples

    Returns:
        Dictionary mapping label -> {percentages, total_runs, most_recent, git_revision}
    """
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    results = {}

    for revision, label in revisions:
        # Match both short and full revision hashes
        cursor.execute("""
            SELECT eval_results, timestamp, model
            FROM eval_runs
            WHERE git_revision LIKE ?
            ORDER BY timestamp DESC
        """, (f"{revision}%",))
        rows = cursor.fetchall()

        if not rows:
            print(f"Warning: No results found for revision {revision}")
            continue

        # Aggregate results
        totals = defaultdict(lambda: {'passed': 0, 'total': 0})
        for row in rows:
            eval_data = json.loads(row['eval_results'])
            for check_name, passed in eval_data.items():
                totals[check_name]['total'] += 1
                if passed:
                    totals[check_name]['passed'] += 1

        # Calculate percentages
        percentages = {}
        for check_name, counts in totals.items():
            percentages[check_name] = (counts['passed'] / counts['total'] * 100) if counts['total'] > 0 else 0

        results[label] = {
            'percentages': percentages,
            'total_runs': len(rows),
            'most_recent': rows[0]['timestamp'] if rows else None,
            'git_revision': revision,
            'model': rows[0]['model'] if rows else 'unknown'
        }

    conn.close()
    return results


def create_benchmark_graph(results: dict, output_path: str = 'assets/benchmark_comparison.png', title: str = None):
    """Create a fancy bar chart comparing multiple models.

    Args:
        results: Dictionary mapping label -> eval results
        output_path: Where to save the output image
        title: Optional custom title
    """
    if not results:
        raise ValueError("No results to graph")

    # Get check names from first result (sorted for consistency)
    first_label = list(results.keys())[0]
    check_names = sorted(results[first_label]['percentages'].keys())

    # Format labels for better readability
    label_map = {
        'no_constructor_side_effects': 'No Constructor\nSide Effects',
        'used_dataclasses_for_methods': 'Used Dataclasses\nfor Methods',
        'used_none_instead_of_optional': 'Used None Instead\nof Optional',
        'used_service_skill': 'Used Service\nSkill'
    }

    check_labels = [label_map.get(name, name.replace('_', ' ').title()) for name in check_names]

    # Create figure with custom styling
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#ffffff')

    # Bar configuration
    x = range(len(check_names))
    num_models = len(results)
    width = 0.8 / num_models  # Total width of 0.8 divided among models

    # Professional color palette (works for up to 6 models)
    colors = ['#FF6B6B', '#4ECDC4', '#FFD93D', '#6C5CE7', '#00B894', '#FD79A8']

    # Create bars for each model
    all_bars = []
    legend_patches = []

    for idx, (label, data) in enumerate(results.items()):
        scores = [data['percentages'].get(name, 0) for name in check_names]
        offset = (idx - num_models/2 + 0.5) * width
        color = colors[idx % len(colors)]

        bars = ax.bar([i + offset for i in x], scores, width,
                      label=label, color=color,
                      edgecolor='white', linewidth=1.5, alpha=0.9)
        all_bars.append(bars)

        # Add value labels on bars
        for bar in bars:
            height = bar.get_height()
            if height > 0:  # Only show label if there's a value
                ax.text(bar.get_x() + bar.get_width()/2., height,
                       f'{height:.1f}%',
                       ha='center', va='bottom', fontsize=9, fontweight='bold')

        # Create legend patch with run count
        run_count = data['total_runs']
        legend_patches.append(mpatches.Patch(color=color, label=f'{label} (n={run_count})'))

    # Customize axes
    ax.set_xlabel('Evaluation Checks', fontsize=14, fontweight='bold', labelpad=15)
    ax.set_ylabel('Pass Rate (%)', fontsize=14, fontweight='bold', labelpad=15)

    if title is None:
        title = f'Python Service Writing Evaluation: {" vs ".join(results.keys())}'
    ax.set_title(title, fontsize=18, fontweight='bold', pad=20)

    ax.set_xticks(x)
    ax.set_xticklabels(check_labels, fontsize=11)
    ax.set_ylim(0, 110)

    # Add grid for better readability
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)

    # Legend with run counts
    ax.legend(handles=legend_patches, loc='lower right', fontsize=12, framealpha=0.95)

    # Add metadata footer
    footer_parts = []
    for label, data in results.items():
        if data['most_recent']:
            date = datetime.fromisoformat(data['most_recent']).strftime('%Y-%m-%d')
            footer_parts.append(f"{label}: {data['total_runs']} runs (last: {date})")

    footer_text = "  |  ".join(footer_parts)
    fig.text(0.5, 0.02, footer_text, ha='center', fontsize=9,
            style='italic', color='#666666')

    # Tight layout
    plt.tight_layout(rect=[0, 0.03, 1, 1])

    # Ensure output directory exists
    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)

    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"✓ Benchmark graph saved to: {output_path}")

    return output_path


def parse_revision_arg(arg: str) -> tuple[str, str]:
    """Parse a revision:label argument.

    Args:
        arg: String in format "revision:label" or just "revision"

    Returns:
        Tuple of (revision, label)
    """
    if ':' in arg:
        revision, label = arg.split(':', 1)
        return revision, label
    else:
        # If no label provided, use short revision as label
        return arg, arg[:8]


def main():
    parser = argparse.ArgumentParser(
        description='Generate benchmark comparison graphs from eval results',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Compare two models
  %(prog)s -r 24dd1ad:Haiku -r 6cf39c8:Sonnet

  # Compare three models with custom output
  %(prog)s -r 24dd1ad:Haiku -r 6cf39c8:Sonnet -r abc1234:Opus -o comparison.png

  # Use custom database path and title
  %(prog)s -r 24dd1ad:Haiku -r 6cf39c8:Sonnet --db /path/to/evals.db --title "My Comparison"
        """
    )

    parser.add_argument(
        '-r', '--revision',
        action='append',
        required=True,
        metavar='REVISION[:LABEL]',
        help='Git revision to include (with optional label). Can be specified multiple times. '
             'Format: "revision:label" or just "revision" (uses short hash as label)'
    )

    parser.add_argument(
        '-o', '--output',
        default='assets/benchmark_comparison.png',
        help='Output path for the graph (default: assets/benchmark_comparison.png)'
    )

    parser.add_argument(
        '--db',
        default='../../evals.db',
        help='Path to the SQLite database (default: ../../evals.db)'
    )

    parser.add_argument(
        '--title',
        help='Custom title for the graph (default: auto-generated)'
    )

    args = parser.parse_args()

    # Parse revision arguments
    revisions = [parse_revision_arg(r) for r in args.revision]

    print(f"Extracting eval results from database: {args.db}")
    print(f"Comparing {len(revisions)} revision(s):")
    for rev, label in revisions:
        print(f"  - {rev} (label: {label})")
    print()

    results = get_eval_results(args.db, revisions)

    if not results:
        print("Error: No results found for any of the specified revisions")
        return 1

    print("\nGenerating benchmark comparison graph...")
    output_file = create_benchmark_graph(results, args.output, args.title)

    print("\nSummary:")
    for label, data in results.items():
        print(f"\n{label}:")
        print(f"  Model: {data['model']}")
        print(f"  Revision: {data['git_revision']}")
        print(f"  Total runs: {data['total_runs']}")
        avg_score = sum(data['percentages'].values()) / len(data['percentages']) if data['percentages'] else 0
        print(f"  Average score: {avg_score:.1f}%")

    return 0


if __name__ == '__main__':
    exit(main())
