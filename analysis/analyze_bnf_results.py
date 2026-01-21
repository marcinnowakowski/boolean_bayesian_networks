import os
import glob
import sys
import argparse
import pandas as pd

# Add parent directory to path to import boolean_networks
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from analysis.bif_parser import (
    parse_filename,
    parse_bif_edges,
    parse_bif_cpts,
    reconstruct_boolean_function,
)
from analysis.utils import (
    calculate_metrics,
    evaluate_dynamics,
    reconstruct_functions_from_transitions,
    extract_dependencies,
    parse_experiment_id,
    calculate_attractor_recovery,
    build_learned_stg,
    build_learned_async_stg,
    get_attractor_groups,
)
from trajectory_generation import config
from trajectory_generation import a01_compile_bool_nets as a01
from trajectory_generation import a02_transition_nets as a02


def main():
    parser = argparse.ArgumentParser(
        description="Analyze BNFinder results_20_01 for a specific experiment."
    )
    parser.add_argument("experiment_id", help="Experiment ID (e.g., 7d_000)")
    args = parser.parse_args()

    experiment_id = args.experiment_id
    num_vars, seed = parse_experiment_id(experiment_id)

    root_dir = os.path.dirname(os.path.dirname(__file__))
    results_dir = os.path.join(
        root_dir, f"trajectory_generation/results_20_01/{experiment_id}"
    )
    output_csv = os.path.join(
        root_dir, f"analysis/reports/analysis_report_{experiment_id}.csv"
    )

    if not os.path.exists(results_dir):
        print(f"Error: Results directory not found at {results_dir}")
        sys.exit(1)

    print(f"Analyzing Experiment: {experiment_id} (Dims={num_vars}, Seed={seed})")

    # Check if experiment_id exists in config
    if experiment_id not in config.BOOL_NETWORKS:
        print(
            f"Error: Experiment ID '{experiment_id}' not found in trajectory_generation/config.py"
        )
        print("Available IDs:", list(config.BOOL_NETWORKS.keys()))
        sys.exit(1)

    print(f"Loading Ground Truth Network from config for {experiment_id}...")

    # Load and compile network from config
    net_functions = config.BOOL_NETWORKS[experiment_id]
    comp_net = a01._prepare_network(net_functions)

    # Generate transitions (using async to match previous behavior/ground truth generation)
    # The original generate_ground_truth produced transitions used for analysis.
    # a02.get_asynchronous_sts returns dict {state: [next_states]}
    transitions = a02.get_asynchronous_sts(comp_net)

    # Reconstruct functions (truth tables) and edges for analysis
    # functions dict keys are '0', '1'... corresponding to x1, x2...
    functions = reconstruct_functions_from_transitions(transitions, num_vars)
    true_edges = extract_dependencies(functions, num_vars)

    print(f"Ground Truth Edges: {len(true_edges)} edges found.")

    # Prepare Ground Truth for Attractor Analysis
    # Generate both Sync and Async STGs once to use for comparison
    transitions_sync = a02.get_synchronous_sts(comp_net)
    transitions_async = transitions  # reusing the async transitions generated above for function reconstruction

    true_groups_sync = get_attractor_groups(transitions_sync)
    true_groups_async = get_attractor_groups(transitions_async)

    print(f"Ground Truth Attractors (Sync): {len(true_groups_sync)} groups")
    print(f"Ground Truth Attractors (Async): {len(true_groups_async)} groups")

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

            # Attractor Analysis
            mode = params.get("mode", "async")
            if mode == "sync":
                learned_stg = build_learned_stg(cpts, parents_map, num_vars)
                t_groups = true_groups_sync
            else:
                learned_stg = build_learned_async_stg(cpts, parents_map, num_vars)
                t_groups = true_groups_async

            l_groups = get_attractor_groups(learned_stg)
            attractor_metrics = calculate_attractor_recovery(t_groups, l_groups)

            row = params.copy()
            row.update(metrics)
            row.update(dynamics_metrics)
            row.update(attractor_metrics)
            row["filename"] = filename
            data.append(row)

        except Exception as e:
            print(f"Error processing {filename}: {e}")

    # Reconstruct and print functions for best networks (Sync/Async x F1/Transition Accuracy)
    if data:
        temp_df = pd.DataFrame(data)
        metrics = ["F1", "Transition_Accuracy"]
        modes = temp_df["mode"].unique() if "mode" in temp_df.columns else ["async"]

        for mode in modes:
            mode_df = temp_df[temp_df["mode"] == mode]
            if mode_df.empty:
                continue

            for metric in metrics:
                if metric not in mode_df.columns:
                    continue

                best_idx = mode_df[metric].idxmax()
                best_row = mode_df.loc[best_idx]
                best_filename = best_row["filename"]
                best_path = os.path.join(results_dir, best_filename)
                score_val = best_row[metric]

                print(
                    f"\n=== Reconstructed Boolean Functions (Best {mode} Network by {metric}: {best_filename}, {metric}={score_val:.2f}) ==="
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

                    reconstructed_dict = {}

                    for var in variables:
                        parents = parents_map.get(var, [])
                        if not parents:
                            # Check for constant function
                            func_str = reconstruct_boolean_function(cpts[var], [])
                        else:
                            func_str = reconstruct_boolean_function(cpts[var], parents)

                        reconstructed_dict[var] = func_str

                        # Determine index for ground truth function logic
                        var_idx = re.search(r"\d+", var)
                        if var_idx:
                            # idx = str(int(var_idx.group()) - 1)
                            # Use the string directly from config
                            true_func_str = net_functions.get(var, "N/A")
                        else:
                            true_func_str = "N/A"

                        print(f"{var}:")
                        print(f"  True:    {true_func_str}")
                        print(f"  Learned: {func_str}")

                    # Save to python file
                    reconstructed_dir = os.path.join(
                        root_dir, "analysis/reconstructed_functions"
                    )
                    os.makedirs(reconstructed_dir, exist_ok=True)

                    out_filename = f"{experiment_id}_{mode}_{metric}_functions.py"
                    out_path = os.path.join(reconstructed_dir, out_filename)

                    with open(out_path, "w") as f:
                        f.write(f"# Reconstructed functions for {experiment_id}\n")
                        f.write(
                            f"# Mode: {mode}, Best Metric: {metric} (Value: {score_val:.2f})\n"
                        )
                        f.write(f"# Source File: {best_filename}\n\n")
                        f.write("reconstructed_functions = {\n")
                        for var, func in reconstructed_dict.items():
                            f.write(f'    "{var}": "{func}",\n')
                        f.write("}\n")

                    print(f"  Saved reconstructed functions to {out_path}")
                else:
                    print(f"  BIF file not found: {best_path}")

    df = pd.DataFrame(data)
    df.to_csv(output_csv, index=False)
    print(f"\nAnalysis complete. Results saved to {output_csv}")

    if not df.empty:
        print("\n=== Analysis Summary ===")
        print("best results_20_01 for different sizes and lengths:")
        cols_to_summarize = [
            "Precision",
            "Recall",
            "F1",
            "Transition_Accuracy",
            "Attractors_Correct",
            "Attractors_F1",
        ]
        best_summary = df.groupby(["score", "size", "len", "mode"])[
            cols_to_summarize
        ].max()
        print(best_summary)

        cols_to_summarize = [
            "score",
            "freq",
            "attr_ratio",
            "size",
            "len",
            "mode",
            "Precision",
            "Recall",
            "F1",
            "Transition_Accuracy",
            "Attractors_Correct",
            "Attractors_F1",
        ]

        print("\n=== Top 10 Networks (best F1) ===")
        large_networks = df.nlargest(10, "F1")
        print(large_networks[cols_to_summarize])

        print("\n=== Top 10 Networks (best Transition Accuracy) ===")
        large_networks = df.nlargest(10, "Transition_Accuracy")
        print(large_networks[cols_to_summarize])

        for freq in df["freq"].unique():
            best_f1_sync = df[(df["freq"] == freq) & (df["mode"] == "sync")].nlargest(
                1, "F1"
            )
            best_ta_sync = df[(df["freq"] == freq) & (df["mode"] == "sync")].nlargest(
                1, "Transition_Accuracy"
            )
            best_f1_async = df[(df["freq"] == freq) & (df["mode"] == "async")].nlargest(
                1, "F1"
            )
            best_ta_async = df[(df["freq"] == freq) & (df["mode"] == "async")].nlargest(
                1, "Transition_Accuracy"
            )
            print(f"\n=== Best Networks for freq={freq} ===")
            print(
                pd.concat([best_f1_sync, best_ta_sync, best_f1_async, best_ta_async])[
                    cols_to_summarize
                ]
            )

        for attr_ratio in df["attr_ratio"].unique():
            best_f1_sync = df[
                (df["attr_ratio"] == attr_ratio) & (df["mode"] == "sync")
            ].nlargest(1, "F1")
            best_ta_sync = df[
                (df["attr_ratio"] == attr_ratio) & (df["mode"] == "sync")
            ].nlargest(1, "Transition_Accuracy")
            best_f1_async = df[
                (df["attr_ratio"] == attr_ratio) & (df["mode"] == "async")
            ].nlargest(1, "F1")
            best_ta_async = df[
                (df["attr_ratio"] == attr_ratio) & (df["mode"] == "async")
            ].nlargest(1, "Transition_Accuracy")
            print(f"\n=== Best Networks for attr_ratio={attr_ratio} ===")
            print(
                pd.concat([best_f1_sync, best_ta_sync, best_f1_async, best_ta_async])[
                    cols_to_summarize
                ]
            )


if __name__ == "__main__":
    main()
