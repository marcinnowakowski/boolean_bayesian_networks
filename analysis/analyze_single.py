import os
import sys
import argparse

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
    calculate_attractor_recovery,
    build_learned_stg,
    build_learned_async_stg,
    get_attractor_groups,
)
from trajectory_generation import config
from trajectory_generation import a01_compile_bool_nets as a01
from trajectory_generation import a02_transition_nets as a02


def main():
    parser = argparse.ArgumentParser(description="Analyze a single BNFinder BIF file.")
    parser.add_argument("bif_path", help="Path to the .bif file")
    args = parser.parse_args()

    bif_path = args.bif_path

    if not os.path.exists(bif_path):
        print(f"Error: File not found at {bif_path}")
        sys.exit(1)

    filename = os.path.basename(bif_path)
    params = parse_filename(filename)

    if not params:
        # Default fallback if filename parsing fails?
        # Or require specific format?
        # For this assignment, assuming standard naming.
        # But we could try to infer from parents/cpts size?
        # Let's rely on naming for 'dim' and 'seed' (via experiment ID logic) or require args?
        # The prompt implies standard usage. But if 'params' is empty, we don't know seed.
        # Let's parse 'dim' and 'seed' from filename parts like `7d_000_...`
        print(
            f"Warning: Could not parse parameters from filename '{filename}'. Assuming defaults or failing."
        )
        # Try to parse manually for seed/dim if parse_filename failed structure but prefix exists?
        # parse_filename handles standard format.
        pass

    # Extract dim and seed from params or filename parts
    # parse_filename returns 'dim': 7, 'id': '000'
    num_vars = params.get("dim", 7)
    seed_str = params.get(
        "id", "000"
    )  # Defaulting to 000 if not found is risky but ok for now
    seed = int(seed_str)

    print(f"Analyzing File: {filename}")
    experiment_id = f"{num_vars}d_{seed:03d}"
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

    # Generate transitions (async)
    transitions = a02.get_asynchronous_sts(comp_net)

    # Reconstruct functions (truth tables) and edges for analysis
    functions = reconstruct_functions_from_transitions(transitions, num_vars)
    true_edges = extract_dependencies(functions, num_vars)

    print(f"Ground Truth Edges: {len(true_edges)} edges found.")

    with open(bif_path, "r") as f:
        content = f.read()

    learned_edges = parse_bif_edges(content)
    cpts, parents_map = parse_bif_cpts(content)

    metrics = calculate_metrics(true_edges, learned_edges)
    dynamics_metrics = evaluate_dynamics(functions, cpts, parents_map, num_vars)

    # Reconstruct boolean functions
    print("\n=== Reconstructed Boolean Functions ===")
    import re

    variables = sorted(
        cpts.keys(),
        key=lambda x: int(re.search(r"\d+", x).group()) if re.search(r"\d+", x) else x,
    )

    for var in variables:
        parents = parents_map.get(var, [])
        if not parents:
            func_str = reconstruct_boolean_function(cpts[var], [])
        else:
            func_str = reconstruct_boolean_function(cpts[var], parents)

        # Determine index for ground truth function logic
        var_idx = re.search(r"\d+", var)
        if var_idx:
            # Use the string directly from config
            true_func_str = net_functions.get(var, "N/A")
        else:
            true_func_str = "N/A"

        print(f"{var}:")
        print(f"  True:    {true_func_str}")
        print(f"  Learned: {func_str}")

    print("\n=== Metrics ===")
    for k, v in metrics.items():
        print(f"{k}: {v:.4f}")
    for k, v in dynamics_metrics.items():
        print(f"{k}: {v:.4f}")

    # Attractor Analysis
    bif_file = os.path.basename(bif_path)
    mode = "async"
    if "_sync_" in bif_file:
        mode = "sync"

    print(f"Assessing Attractors (Mode: {mode})...")
    if mode == "async":
        # true_transitions (async) was already generated as 'transitions'
        learned_transitions_stg = build_learned_async_stg(cpts, parents_map, num_vars)
        true_transitions_stg = transitions  # reuse
    else:
        true_transitions_stg = a02.get_synchronous_sts(comp_net)
        learned_transitions_stg = build_learned_stg(cpts, parents_map, num_vars)

    true_groups = get_attractor_groups(true_transitions_stg)
    learned_groups = get_attractor_groups(learned_transitions_stg)
    attractor_metrics = calculate_attractor_recovery(true_groups, learned_groups)

    print("Attractor Analysis:")
    print(f"True Attractors Count:    {attractor_metrics['Attractors_True_Count']}")
    print(f"Learned Attractors Count: {attractor_metrics['Attractors_Learned_Count']}")
    print(f"Correctly Recovered:      {attractor_metrics['Attractors_Correct']}")


if __name__ == "__main__":
    main()
