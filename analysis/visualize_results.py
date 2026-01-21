import os
import sys
import argparse
import pandas as pd

# Add parent directory to path to import boolean_networks
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from analysis.bif_parser import parse_bif_edges, parse_bif_cpts
from analysis.utils import (
    parse_experiment_id,
    reconstruct_functions_from_transitions,
    extract_dependencies,
    build_learned_stg,
    build_learned_async_stg,
)
from analysis.plotting import plot_structure_comparison, plot_stg_comparison
from trajectory_generation import config
from trajectory_generation import a01_compile_bool_nets as a01
from trajectory_generation import a02_transition_nets as a02


def main():
    parser = argparse.ArgumentParser(
        description="Visualize BNFinder results_20_01 for a specific experiment."
    )
    parser.add_argument("experiment_id", help="Experiment ID (e.g., 7d_000)")
    args = parser.parse_args()

    experiment_id = args.experiment_id
    num_vars, seed = parse_experiment_id(experiment_id)

    root_dir = os.path.dirname(os.path.dirname(__file__))
    results_dir = os.path.join(
        root_dir, f"trajectory_generation/results_20_01/{experiment_id}"
    )
    plots_dir = os.path.join(root_dir, f"analysis/plots/{experiment_id}")
    csv_path = os.path.join(
        root_dir, f"analysis/reports/analysis_report_{experiment_id}.csv"
    )

    os.makedirs(plots_dir, exist_ok=True)

    print(f"Visualizing Experiment: {experiment_id} (Dims={num_vars}, Seed={seed})")

    # Check if experiment_id exists
    if experiment_id not in config.BOOL_NETWORKS:
        print(
            f"Error: Experiment ID '{experiment_id}' not found in trajectory_generation/config.py"
        )
        sys.exit(1)

    # We delay GT generation until we find the best network to know if we want sync or async

    if os.path.exists(csv_path):
        df = pd.read_csv(csv_path)

        if not df.empty:
            # We want to visualize best network for each mode and for each metric
            metrics = ["F1", "Transition_Accuracy", "Attractors_F1"]
            modes = (
                df["mode"].unique() if "mode" in df.columns else ["async"]
            )  # default fallback

            # Pre-compile comp_net as it is constant for experiment
            net_functions = config.BOOL_NETWORKS[experiment_id]
            comp_net = a01._prepare_network(net_functions)

            for mode in modes:
                mode_df = df[df["mode"] == mode]
                if mode_df.empty:
                    continue

                for metric in metrics:
                    if metric not in mode_df.columns:
                        continue

                    best_idx = mode_df[metric].idxmax()
                    best_row = mode_df.loc[best_idx]
                    best_filename = best_row["filename"]
                    score_val = best_row[metric]

                    print(
                        f"\n--- Best {mode} Network (by {metric}): {best_filename} ({metric}={score_val:.2f}) ---"
                    )

                    # Generate GT based on mode
                    if mode == "async":
                        # print("Generating Asynchronous Ground Truth...")
                        true_transitions = a02.get_asynchronous_sts(comp_net)
                    else:
                        # print("Generating Synchronous Ground Truth...")
                        true_transitions = a02.get_synchronous_sts(comp_net)

                    # Reconstruct functions/edges from the specific dynamics we are plotting
                    functions = reconstruct_functions_from_transitions(
                        true_transitions, num_vars
                    )
                    true_edges = extract_dependencies(functions, num_vars)

                    bif_path = os.path.join(results_dir, best_filename)
                    if os.path.exists(bif_path):
                        with open(bif_path, "r") as f:
                            content = f.read()
                        learned_edges = parse_bif_edges(content)
                        cpts, parents_map = parse_bif_cpts(content)

                        if mode == "async":
                            learned_transitions = build_learned_async_stg(
                                cpts, parents_map, num_vars
                            )
                        else:
                            learned_transitions = build_learned_stg(
                                cpts, parents_map, num_vars
                            )

                        # Plot Structure
                        plot_filename_struct = f"structure_{mode}_best_{metric}.png"
                        plot_structure_comparison(
                            true_edges,
                            learned_edges,
                            f"Structure Comparison (Best {mode} {metric})\n{best_filename}",
                            os.path.join(plots_dir, plot_filename_struct),
                            num_vars,
                        )

                        # Plot Dynamics
                        plot_filename_stg = f"stg_{mode}_best_{metric}.png"
                        plot_stg_comparison(
                            true_transitions,
                            learned_transitions,
                            f"Dynamics Comparison (Best {mode} {metric})\n{best_filename}",
                            os.path.join(plots_dir, plot_filename_stg),
                        )
                    else:
                        print(f"BIF file not found: {bif_path}")
    else:
        print(
            f"Analysis report not found at {csv_path}. Run analyze_bnf_results.py first."
        )


if __name__ == "__main__":
    main()
