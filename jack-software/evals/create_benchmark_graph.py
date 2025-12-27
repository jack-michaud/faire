#!/usr/bin/env python3
"""Generate a fancy benchmark comparison graph for Haiku vs Sonnet eval results."""

import sqlite3
import json
from collections import defaultdict
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from datetime import datetime

# Configuration
HAIKU_REVISION = '24dd1ad79c52e56d2118ecb877d79533b3bd6e4d'
SONNET_REVISION = '6cf39c8942c2ec317f5b52601c571b75594895bc'

def get_eval_results(db_path: str):
    """Extract and aggregate eval results from the database."""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()

    results = {}

    for revision, model_name in [
        (HAIKU_REVISION, 'claude-haiku-4-5-20251001'),
        (SONNET_REVISION, 'claude-sonnet-4-5-20250929')
    ]:
        cursor.execute("""
            SELECT eval_results, timestamp
            FROM eval_runs
            WHERE git_revision = ?
            ORDER BY timestamp DESC
        """, (revision,))
        rows = cursor.fetchall()

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

        results[model_name] = {
            'percentages': percentages,
            'total_runs': len(rows),
            'most_recent': rows[0]['timestamp'] if rows else None
        }

    conn.close()
    return results


def create_benchmark_graph(results: dict, output_path: str = 'benchmark_comparison.png'):
    """Create a fancy bar chart comparing the two models."""

    haiku_key = 'claude-haiku-4-5-20251001'
    sonnet_key = 'claude-sonnet-4-5-20250929'

    # Get check names (sorted for consistency)
    check_names = sorted(results[haiku_key]['percentages'].keys())

    # Format labels for better readability
    label_map = {
        'no_constructor_side_effects': 'No Constructor\nSide Effects',
        'used_dataclasses_for_methods': 'Used Dataclasses\nfor Methods',
        'used_none_instead_of_optional': 'Used None Instead\nof Optional',
        'used_service_skill': 'Used Service\nSkill'
    }

    labels = [label_map.get(name, name) for name in check_names]
    haiku_scores = [results[haiku_key]['percentages'][name] for name in check_names]
    sonnet_scores = [results[sonnet_key]['percentages'][name] for name in check_names]

    # Create figure with custom styling
    fig, ax = plt.subplots(figsize=(14, 8))
    fig.patch.set_facecolor('#f8f9fa')
    ax.set_facecolor('#ffffff')

    # Bar configuration
    x = range(len(check_names))
    width = 0.35

    # Colors - professional color scheme
    haiku_color = '#FF6B6B'  # Coral red
    sonnet_color = '#4ECDC4'  # Teal

    # Create bars
    bars1 = ax.bar([i - width/2 for i in x], haiku_scores, width,
                   label='Claude Haiku 4.5', color=haiku_color,
                   edgecolor='white', linewidth=1.5, alpha=0.9)
    bars2 = ax.bar([i + width/2 for i in x], sonnet_scores, width,
                   label='Claude Sonnet 4.5', color=sonnet_color,
                   edgecolor='white', linewidth=1.5, alpha=0.9)

    # Add value labels on bars
    def add_value_labels(bars):
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2., height,
                   f'{height:.1f}%',
                   ha='center', va='bottom', fontsize=10, fontweight='bold')

    add_value_labels(bars1)
    add_value_labels(bars2)

    # Customize axes
    ax.set_xlabel('Evaluation Checks', fontsize=14, fontweight='bold', labelpad=15)
    ax.set_ylabel('Pass Rate (%)', fontsize=14, fontweight='bold', labelpad=15)
    ax.set_title('Python Service Writing Evaluation: Haiku vs Sonnet',
                fontsize=18, fontweight='bold', pad=20)
    ax.set_xticks(x)
    ax.set_xticklabels(labels, fontsize=11)
    ax.set_ylim(0, 110)

    # Add grid for better readability
    ax.grid(axis='y', alpha=0.3, linestyle='--', linewidth=0.5)
    ax.set_axisbelow(True)

    # Legend with run counts
    haiku_runs = results[haiku_key]['total_runs']
    sonnet_runs = results[sonnet_key]['total_runs']

    haiku_patch = mpatches.Patch(color=haiku_color, label=f'Claude Haiku 4.5 (n={haiku_runs})')
    sonnet_patch = mpatches.Patch(color=sonnet_color, label=f'Claude Sonnet 4.5 (n={sonnet_runs})')
    ax.legend(handles=[haiku_patch, sonnet_patch],
             loc='lower right', fontsize=12, framealpha=0.95)

    # Add metadata footer
    haiku_date = datetime.fromisoformat(results[haiku_key]['most_recent']).strftime('%Y-%m-%d')
    sonnet_date = datetime.fromisoformat(results[sonnet_key]['most_recent']).strftime('%Y-%m-%d')

    footer_text = (f'Haiku: {haiku_runs} runs (last: {haiku_date})  |  '
                  f'Sonnet: {sonnet_runs} runs (last: {sonnet_date})')
    fig.text(0.5, 0.02, footer_text, ha='center', fontsize=9,
            style='italic', color='#666666')

    # Tight layout
    plt.tight_layout(rect=[0, 0.03, 1, 1])

    # Save figure
    plt.savefig(output_path, dpi=300, bbox_inches='tight', facecolor=fig.get_facecolor())
    print(f"✓ Benchmark graph saved to: {output_path}")

    return output_path


if __name__ == '__main__':
    print("Extracting eval results from database...")
    results = get_eval_results('evals.db')

    print("\nGenerating benchmark comparison graph...")
    output_file = create_benchmark_graph(results)

    print("\nSummary:")
    for model_name, data in results.items():
        short_name = "Haiku" if "haiku" in model_name else "Sonnet"
        print(f"\n{short_name} ({model_name}):")
        print(f"  Total runs: {data['total_runs']}")
        print(f"  Average score: {sum(data['percentages'].values()) / len(data['percentages']):.1f}%")
