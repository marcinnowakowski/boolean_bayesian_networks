"""
Organize biodivine models by dimension (number of variables).

Copies models from raw/ to by_dimention/<dim>d/ with naming: model_<id>_<dim>d.bnet
"""

import os
import re
import shutil
from pathlib import Path
from collections import defaultdict


RAW_DIR = "/Users/marcinnowakowski/mimuw/sad2/boolean_bayesian_networks/biodivine_models/raw"
TARGET_DIR = "/Users/marcinnowakowski/mimuw/sad2/boolean_bayesian_networks/biodivine_models/by_dimention"


def count_variables(bnet_path: str) -> int:
    """
    Count the number of variables in a .bnet file.
    
    Each non-empty line after the header (targets,factors) defines one variable.
    """
    with open(bnet_path, 'r') as f:
        lines = f.readlines()
    
    # Skip header and count non-empty lines
    count = 0
    for line in lines[1:]:  # Skip "targets,factors" header
        line = line.strip()
        if line and ',' in line:  # Valid variable definition
            count += 1
    
    return count


def extract_id(filename: str) -> str:
    """Extract model ID from filename like model_001.bnet -> 001"""
    match = re.match(r'model_(\d+)\.bnet', filename)
    if match:
        return match.group(1)
    return None


def organize_by_dimension(raw_dir: str = RAW_DIR, target_dir: str = TARGET_DIR, verbose: bool = True):
    """
    Organize all models by their dimension.
    
    Args:
        raw_dir: Directory containing raw .bnet files
        target_dir: Target directory for organized files
        verbose: Whether to print progress
        
    Returns:
        Dictionary with statistics
    """
    raw_path = Path(raw_dir)
    target_path = Path(target_dir)
    
    if not raw_path.exists():
        raise FileNotFoundError(f"Raw directory not found: {raw_dir}")
    
    # Get all .bnet files
    bnet_files = sorted(raw_path.glob("model_*.bnet"))
    
    if verbose:
        print(f"Found {len(bnet_files)} models in {raw_dir}")
        print("-" * 60)
    
    stats = defaultdict(list)
    
    for bnet_file in bnet_files:
        model_id = extract_id(bnet_file.name)
        if model_id is None:
            print(f"Warning: Could not extract ID from {bnet_file.name}")
            continue
        
        # Count variables (dimension)
        dim = count_variables(str(bnet_file))
        
        # Create target directory
        dim_dir = target_path / f"{dim}d"
        dim_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy with new name
        new_filename = f"model_{model_id}_{dim}d.bnet"
        target_file = dim_dir / new_filename
        shutil.copy2(bnet_file, target_file)
        
        stats[dim].append(model_id)
        
        if verbose:
            print(f"  {bnet_file.name} -> {dim}d/{new_filename}")
    
    if verbose:
        print("-" * 60)
        print("\nSummary by dimension:")
        for dim in sorted(stats.keys()):
            print(f"  {dim}d: {len(stats[dim])} models")
        print(f"\nTotal: {sum(len(v) for v in stats.values())} models organized")
    
    return dict(stats)


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Organize biodivine models by dimension"
    )
    parser.add_argument(
        '-r', '--raw',
        default=RAW_DIR,
        help=f"Raw models directory (default: {RAW_DIR})"
    )
    parser.add_argument(
        '-t', '--target',
        default=TARGET_DIR,
        help=f"Target directory (default: {TARGET_DIR})"
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help="Suppress verbose output"
    )
    
    args = parser.parse_args()
    
    organize_by_dimension(
        raw_dir=args.raw,
        target_dir=args.target,
        verbose=not args.quiet
    )


if __name__ == "__main__":
    main()
