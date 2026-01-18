import os
import sys
import argparse
import pandas as pd

# Add parent directory to path to import boolean_networks
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from analysis.bif_parser import parse_filename, parse_bif_edges, parse_bif_cpts
from analysis.utils import generate_ground_truth, build_learned_stg
from analysis.plotting import plot_structure_comparison, plot_stg_comparison


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
    # Output directory for plots: same dir as bif file + /plots/
    base_dir = os.path.dirname(bif_path)
    plots_dir = os.path.join(base_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    params = parse_filename(filename)
    num_vars = params.get("dim", 7)
    seed_str = params.get("id", "000")
    seed = int(seed_str)

    print(f"Visualizing File: {filename}")
    print(f"Inferred Config: Dims={num_vars}, Seed={seed}")

    print(f"Generating Ground Truth (Seed {seed})...")
    true_transitions, functions, true_edges = generate_ground_truth(seed, num_vars)

    with open(bif_path, "r") as f:
        content = f.read()

    learned_edges = parse_bif_edges(content)
    cpts, parents_map = parse_bif_cpts(content)
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
