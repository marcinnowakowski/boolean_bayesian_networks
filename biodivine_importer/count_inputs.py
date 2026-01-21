"""
Count external inputs for all networks in by_dimention directory.
"""

import os
import re
from pathlib import Path
from collections import defaultdict


SOURCE_DIR = "/Users/marcinnowakowski/mimuw/sad2/boolean_bayesian_networks/biodivine_models/by_dimention"


def count_inputs(filepath):
    """Count variables and external inputs in a .bnet file."""
    functions = {}
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    for line in lines[1:]:
        line = line.strip()
        if not line or ',' not in line:
            continue
        parts = line.split(',', 1)
        if len(parts) != 2:
            continue
        var_name = parts[0].strip()
        expression = parts[1].strip()
        functions[var_name] = expression
    
    # Find all variable references
    all_refs = set()
    for expr in functions.values():
        refs = re.findall(r'\bv_\w+\b', expr)
        all_refs.update(refs)
    
    defined_vars = set(functions.keys())
    external_inputs = all_refs - defined_vars
    return len(functions), len(external_inputs), external_inputs


def main():
    # Analyze 4d-16d
    results = []
    for dim in range(4, 17):
        dim_dir = Path(SOURCE_DIR) / f'{dim}d'
        if not dim_dir.exists():
            continue
        for bnet_file in sorted(dim_dir.glob('*.bnet')):
            num_vars, num_inputs, inputs = count_inputs(str(bnet_file))
            results.append((dim, bnet_file.name, num_vars, num_inputs))

    # Detailed output
    print('Dim | File                      | Vars | External Inputs')
    print('-' * 65)
    by_dim = defaultdict(lambda: {'total': 0, 'with_inputs': 0, 'without_inputs': 0})
    
    for dim, fname, nvars, ninputs in results:
        status = '✓ convertible' if ninputs == 0 else f'{ninputs} inputs'
        print(f'{dim:2d}d | {fname:25s} | {nvars:4d} | {status}')
        by_dim[dim]['total'] += 1
        if ninputs == 0:
            by_dim[dim]['without_inputs'] += 1
        else:
            by_dim[dim]['with_inputs'] += 1

    print()
    print('=' * 65)
    print('Summary by dimension:')
    print('Dim | Total | Convertible | With External Inputs')
    print('-' * 50)
    total_all = 0
    total_convertible = 0
    for dim in sorted(by_dim.keys()):
        d = by_dim[dim]
        total_all += d['total']
        total_convertible += d['without_inputs']
        print(f'{dim:2d}d | {d["total"]:5d} | {d["without_inputs"]:11d} | {d["with_inputs"]:20d}')
    
    print('-' * 50)
    print(f'ALL | {total_all:5d} | {total_convertible:11d} | {total_all - total_convertible:20d}')


if __name__ == "__main__":
    main()
