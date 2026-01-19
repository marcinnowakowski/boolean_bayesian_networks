import os
import sys
import argparse
import pandas as pd

# Add parent directory to path to import boolean_networks
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from analysis.bif_parser import parse_bif_edges, parse_bif_cpts
from analysis.utils import parse_experiment_id, generate_ground_truth, build_learned_stg
from analysis.plotting import plot_structure_comparison, plot_stg_comparison


def main():
    parser = argparse.ArgumentParser(
        description="Visualize BNFinder results for a specific experiment."
    )
    parser.add_argument("experiment_id", help="Experiment ID (e.g., 7d_000)")
    args = parser.parse_args()

    experiment_id = args.experiment_id
    num_vars, seed = parse_experiment_id(experiment_id)

    root_dir = os.path.dirname(os.path.dirname(__file__))
    results_dir = os.path.join(root_dir, f"output/results/{experiment_id}")
    plots_dir = os.path.join(results_dir, "plots")
    csv_path = os.path.join(root_dir, f"output/analysis_report_{experiment_id}.csv")

    os.makedirs(plots_dir, exist_ok=True)

    print(f"Visualizing Experiment: {experiment_id} (Dims={num_vars}, Seed={seed})")
    print(f"Generating Ground Truth (Seed {seed})...")
    true_transitions, functions, true_edges = generate_ground_truth(seed, num_vars)

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)

        if not df.empty:
            best_idx = df["F1"].idxmax()
            best_row = df.loc[best_idx]
            best_filename = best_row["filename"]
            print(f"Best Network: {best_filename} (F1={best_row['F1']:.2f})")

            bif_path = os.path.join(results_dir, best_filename)
            if os.path.exists(bif_path):
                with open(bif_path, "r") as f:
                    content = f.read()
                learned_edges = parse_bif_edges(content)
                cpts, parents_map = parse_bif_cpts(content)
                learned_transitions = build_learned_stg(cpts, parents_map, num_vars)

                plot_structure_comparison(
                    true_edges,
                    learned_edges,
                    f"Structure Comparison (Best F1)\n{best_filename}",
                    os.path.join(plots_dir, "structure_comparison_best.png"),
                    num_vars,
                )

                plot_stg_comparison(
                    true_transitions,
                    learned_transitions,
                    f"Dynamics Comparison (Best F1)\n{best_filename}",
                    os.path.join(plots_dir, "stg_comparison_best.png"),
                )
    else:
        print(
            f"Analysis report not found at {csv_path}. Run analyze_bnf_results.py first."
        )


if __name__ == "__main__":
    main()
