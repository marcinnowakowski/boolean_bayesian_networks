"""
Importer for biodivine-boolean-models .bnet files.

Imports model.bnet files from subdirectories and renames them to model_<id>.bnet
"""

import os
import re
import shutil
from pathlib import Path
from typing import Optional


# Default paths
DEFAULT_SOURCE_DIR = "/Users/marcinnowakowski/mimuw/sad2/biodivine-boolean-models/models"
DEFAULT_TARGET_DIR = "/Users/marcinnowakowski/mimuw/sad2/boolean_bayesian_networks/biodivine_models/raw"


def extract_id_from_dirname(dirname: str) -> Optional[str]:
    """
    Extract the ID from directory name.
    
    Directory names are in format: [id-XXX]__[var-YYY]__[in-ZZZ]__[MODEL-NAME]
    Returns the ID part (e.g., '001', '002', etc.)
    """
    match = re.match(r'\[id-(\d+)\]', dirname)
    if match:
        return match.group(1)
    return None


def import_model(source_dir: str, target_dir: str, dirname: str) -> Optional[str]:
    """
    Import a single model.bnet file from a subdirectory.
    
    Args:
        source_dir: Path to the source models directory
        target_dir: Path to the target directory
        dirname: Name of the model subdirectory
        
    Returns:
        Path to the imported file, or None if import failed
    """
    model_id = extract_id_from_dirname(dirname)
    if model_id is None:
        print(f"Warning: Could not extract ID from directory name: {dirname}")
        return None
    
    source_path = Path(source_dir) / dirname / "model.bnet"
    if not source_path.exists():
        print(f"Warning: model.bnet not found in {dirname}")
        return None
    
    target_filename = f"model_{model_id}.bnet"
    target_path = Path(target_dir) / target_filename
    
    shutil.copy2(source_path, target_path)
    return str(target_path)


def import_all_models(
    source_dir: str = DEFAULT_SOURCE_DIR,
    target_dir: str = DEFAULT_TARGET_DIR,
    verbose: bool = True
) -> dict:
    """
    Import all model.bnet files from the biodivine-boolean-models repository.
    
    Args:
        source_dir: Path to the source models directory
        target_dir: Path to the target directory for imported models
        verbose: Whether to print progress information
        
    Returns:
        Dictionary with import statistics and results
    """
    source_path = Path(source_dir)
    target_path = Path(target_dir)
    
    if not source_path.exists():
        raise FileNotFoundError(f"Source directory not found: {source_dir}")
    
    # Create target directory if it doesn't exist
    target_path.mkdir(parents=True, exist_ok=True)
    
    # Get all subdirectories
    subdirs = [d for d in os.listdir(source_dir) if (source_path / d).is_dir()]
    subdirs.sort()  # Sort to process in order
    
    results = {
        'imported': [],
        'failed': [],
        'total': len(subdirs)
    }
    
    if verbose:
        print(f"Found {len(subdirs)} model directories")
        print(f"Importing to: {target_dir}")
        print("-" * 60)
    
    for dirname in subdirs:
        imported_path = import_model(source_dir, target_dir, dirname)
        if imported_path:
            results['imported'].append(imported_path)
            if verbose:
                model_id = extract_id_from_dirname(dirname)
                print(f"  Imported: model_{model_id}.bnet")
        else:
            results['failed'].append(dirname)
    
    if verbose:
        print("-" * 60)
        print(f"Successfully imported: {len(results['imported'])} models")
        if results['failed']:
            print(f"Failed: {len(results['failed'])} models")
    
    return results


def main():
    """Main entry point for command-line usage."""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Import .bnet models from biodivine-boolean-models repository"
    )
    parser.add_argument(
        '-s', '--source',
        default=DEFAULT_SOURCE_DIR,
        help=f"Source directory (default: {DEFAULT_SOURCE_DIR})"
    )
    parser.add_argument(
        '-t', '--target',
        default=DEFAULT_TARGET_DIR,
        help=f"Target directory (default: {DEFAULT_TARGET_DIR})"
    )
    parser.add_argument(
        '-q', '--quiet',
        action='store_true',
        help="Suppress verbose output"
    )
    
    args = parser.parse_args()
    
    results = import_all_models(
        source_dir=args.source,
        target_dir=args.target,
        verbose=not args.quiet
    )
    
    return 0 if not results['failed'] else 1


if __name__ == "__main__":
    exit(main())
