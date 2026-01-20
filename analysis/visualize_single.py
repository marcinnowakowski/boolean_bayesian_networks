import os
import sys
import argparse
import pandas as pd

# Add parent directory to path to import boolean_networks
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from analysis.bif_parser import parse_filename, parse_bif_edges, parse_bif_cpts
from analysis.utils import (
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
        description="Visualize a single BNFinder BIF file."
    )
    parser.add_argument("bif_path", help="Path to the .bif file")
    args = parser.parse_args()

    bif_path = args.bif_path

    if not os.path.exists(bif_path):
        print(f"Error: File not found at {bif_path}")
        sys.exit(1)

    filename = os.path.basename(bif_path)
    params = parse_filename(filename)
    num_vars = params.get("dim", None)
    seed_str = params.get("id", None)
    seed = int(seed_str)
    # Output directory for plots: same dir as bif file + /plots/
    root_dir = os.path.dirname(os.path.dirname(__file__))
    plots_dir = os.path.join(root_dir, f"analysis/plots/{num_vars}d_{seed_str}")
    os.makedirs(plots_dir, exist_ok=True)

    # Infer experiment ID from dims and seed
    # Filename format often contains something like '5d_005'
    # We construct it:
    experiment_id = f"{num_vars}d_{seed:03d}"

    print(f"Visualizing File: {filename}")
    print(f"Inferred Config: Experiment ID={experiment_id}")

    # Check if experiment_id exists in config
    if experiment_id not in config.BOOL_NETWORKS:
        print(
            f"Error: Experiment ID '{experiment_id}' not found in trajectory_generation/config.py"
        )
        sys.exit(1)

    print(f"Loading Ground Truth Network from config for {experiment_id}...")

    # Load and compile network from config
    net_functions = config.BOOL_NETWORKS[experiment_id]
    comp_net = a01._prepare_network(net_functions)

    # Determine mode from params (default to async if not found, or check filename)
    mode = params.get("mode", "async")

    if mode == "async":
        print("Mode: Asynchronous")
        true_transitions = a02.get_asynchronous_sts(comp_net)
    else:
        print("Mode: Synchronous")
        true_transitions = a02.get_synchronous_sts(comp_net)

    # Reconstruct functions/edges for structure comparison
    functions = reconstruct_functions_from_transitions(true_transitions, num_vars)
    true_edges = extract_dependencies(functions, num_vars)

    with open(bif_path, "r") as f:
        content = f.read()

    learned_edges = parse_bif_edges(content)
    cpts, parents_map = parse_bif_cpts(content)

    if mode == "async":
        learned_transitions = build_learned_async_stg(cpts, parents_map, num_vars)
    else:
        learned_transitions = build_learned_stg(cpts, parents_map, num_vars)

    plot_structure_comparison(
        true_edges,
        learned_edges,
        f"Structure Comparison\n{filename}",
        os.path.join(plots_dir, f"{filename}_structure.png"),
        num_vars,
    )

    plot_stg_comparison(
        true_transitions,
        learned_transitions,
        f"Dynamics Comparison\n{filename}",
        os.path.join(plots_dir, f"{filename}_stg.png"),
    )


if __name__ == "__main__":
    main()
