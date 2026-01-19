import os
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
    reconstruct_functions_from_transitions,
    extract_dependencies,
    calculate_metrics,
    evaluate_dynamics,
    generate_ground_truth,
)


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
    print(f"Inferred Config: Dims={num_vars}, Seed={seed}")

    print(f"Generating Ground Truth Network (Seed {seed})...")
    transitions, functions, true_edges = generate_ground_truth(seed, num_vars)
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

    from analysis.utils import truth_table_to_expression

    for var in variables:
        parents = parents_map.get(var, [])
        if not parents:
            func_str = reconstruct_boolean_function(cpts[var], [])
        else:
            func_str = reconstruct_boolean_function(cpts[var], parents)

        # Determine index for ground truth function
        # Assumes vars are x1..xn and functions keys are '0'..'(n-1)'
        var_idx = re.search(r"\d+", var)
        if var_idx:
            idx = str(int(var_idx.group()) - 1)
            true_func_str = truth_table_to_expression(functions.get(idx, {}), num_vars)
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


if __name__ == "__main__":
    main()
