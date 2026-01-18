import os
import glob
import sys
import argparse
import pandas as pd
from typing import Dict, Set, Tuple, List

# Add parent directory to path to import boolean_networks
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from analysis.bif_parser import (
    parse_filename,
    parse_bif_edges,
    parse_bif_cpts,
    reconstruct_boolean_function,
)
from analysis.utils import (
    reconstruct_functions_from_transitions,
    extract_dependencies,
    calculate_metrics,
    evaluate_dynamics,
    parse_experiment_id,
    generate_ground_truth,
    truth_table_to_expression,
)


def main():
    parser = argparse.ArgumentParser(
        description="Analyze BNFinder results for a specific experiment."
    )
    parser.add_argument("experiment_id", help="Experiment ID (e.g., 7d_000)")
    args = parser.parse_args()

    experiment_id = args.experiment_id
    num_vars, seed = parse_experiment_id(experiment_id)

    root_dir = os.path.dirname(os.path.dirname(__file__))
    results_dir = os.path.join(root_dir, f"output/results/{experiment_id}")
    output_csv = os.path.join(root_dir, f"output/analysis_report_{experiment_id}.csv")

    if not os.path.exists(results_dir):
        print(f"Error: Results directory not found at {results_dir}")
        sys.exit(1)

    print(f"Analyzing Experiment: {experiment_id} (Dims={num_vars}, Seed={seed})")
    print(f"Generating Ground Truth Network (Seed {seed})...")
    transitions, functions, true_edges = generate_ground_truth(seed, num_vars)
    print(f"Ground Truth Edges: {len(true_edges)} edges found.")

    data = []

    bif_files = glob.glob(os.path.join(results_dir, "*.bif"))
    print(f"Found {len(bif_files)} BIF files to analyze.")

    for bif_path in bif_files:
        filename = os.path.basename(bif_path)
        params = parse_filename(filename)

        try:
            with open(bif_path, "r") as f:
                content = f.read()

            learned_edges = parse_bif_edges(content)
            cpts, parents_map = parse_bif_cpts(content)

            metrics = calculate_metrics(true_edges, learned_edges)
            dynamics_metrics = evaluate_dynamics(functions, cpts, parents_map, num_vars)

            row = params.copy()
            row.update(metrics)
            row.update(dynamics_metrics)
            row["filename"] = filename
            data.append(row)

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Reconstruct and print functions for the overall best F1 network
    if data:
        temp_df = pd.DataFrame(data)
        best_f1_idx = temp_df["F1"].idxmax()
        best_f1_row = temp_df.loc[best_f1_idx]
        best_filename = best_f1_row["filename"]
        best_path = os.path.join(results_dir, best_filename)

        print(
            f"\n=== Reconstructed Boolean Functions (Best Network: {best_filename}) ==="
        )
        if os.path.exists(best_path):
            with open(best_path, "r") as f:
                content = f.read()
            cpts, parents_map = parse_bif_cpts(content)

            # Sort variables for clean output
            import re

            variables = sorted(
                cpts.keys(),
                key=lambda x: int(re.search(r"\d+", x).group())
                if re.search(r"\d+", x)
                else x,
            )

            for var in variables:
                parents = parents_map.get(var, [])
                if not parents:
                    # Check for constant function
                    func_str = reconstruct_boolean_function(cpts[var], [])
                else:
                    func_str = reconstruct_boolean_function(cpts[var], parents)

                # Determine index for ground truth function
                var_idx = re.search(r"\d+", var)
                if var_idx:
                    idx = str(int(var_idx.group()) - 1)
                    true_func_str = truth_table_to_expression(
                        functions.get(idx, {}), num_vars
                    )
                else:
                    true_func_str = "N/A"

                print(f"{var}:")
                print(f"  True:    {true_func_str}")
                print(f"  Learned: {func_str}")

    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(f"\nAnalysis complete. Results saved to {output_csv}")

    if not df.empty:
        print("\n=== Analysis Summary ===")

        cols_to_summarize = [
            "Precision",
            "Recall",
            "F1",
            "Bitwise_Accuracy",
            "Transition_Accuracy",
            "Correct_Functions",
        ]
        summary = df.groupby(["score", "size", "len", "mode"])[cols_to_summarize].max()
        print(summary)


if __name__ == "__main__":
    main()
