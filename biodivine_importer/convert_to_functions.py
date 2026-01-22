"""
Convert biodivine .bnet files to our Python network format.

Transforms files from biodivine_models/by_dimention to networks/functions/biodivine
"""

import os
import re
from pathlib import Path
from typing import Dict, List, Tuple
from itertools import product


SOURCE_DIR = "/Users/marcinnowakowski/mimuw/sad2/boolean_bayesian_networks/biodivine_models/by_dimention"
TARGET_DIR = "/Users/marcinnowakowski/mimuw/sad2/boolean_bayesian_networks/networks/functions/biodivine"


def parse_bnet_file(filepath: str) -> Tuple[Dict[str, str], set]:
    """
    Parse a .bnet file and return {variable_name: boolean_expression} and set of external inputs.
    
    .bnet format:
    targets,factors
    v_A, (v_B & !v_C)
    v_B, v_A | v_C
    ...
    
    Returns:
        (functions, external_inputs) - external_inputs are variables referenced but not defined
    """
    functions = {}
    
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    for line in lines[1:]:  # Skip header
        line = line.strip()
        if not line or ',' not in line:
            continue
        
        # Split on first comma only (expression may contain commas in rare cases)
        parts = line.split(',', 1)
        if len(parts) != 2:
            continue
        
        var_name = parts[0].strip()
        expression = parts[1].strip()
        
        functions[var_name] = expression
    
    # Find all variable references in expressions
    all_refs = set()
    for expr in functions.values():
        # Find all v_... patterns
        refs = re.findall(r'\bv_\w+\b', expr)
        all_refs.update(refs)
    
    # External inputs are referenced but not defined
    defined_vars = set(functions.keys())
    external_inputs = all_refs - defined_vars
    
    return functions, external_inputs


def normalize_variable_names(functions: Dict[str, str]) -> Tuple[Dict[str, str], Dict[str, str]]:
    """
    Normalize variable names to x1, x2, x3... format.
    
    Returns:
        (normalized_functions, name_mapping) where name_mapping is {original: new}
    """
    # Sort variable names for consistent ordering
    var_names = sorted(functions.keys())
    
    # Create mapping
    name_mapping = {}
    for i, var_name in enumerate(var_names, 1):
        name_mapping[var_name] = f"x{i}"
    
    # Apply mapping to both keys and expressions
    normalized = {}
    for var_name, expr in functions.items():
        new_name = name_mapping[var_name]
        new_expr = expr
        
        # Replace variable names in expression (longer names first to avoid partial replacement)
        for old_name in sorted(name_mapping.keys(), key=len, reverse=True):
            new_var = name_mapping[old_name]
            # Use word boundary-like replacement
            new_expr = re.sub(r'\b' + re.escape(old_name) + r'\b', new_var, new_expr)
        
        normalized[new_name] = new_expr
    
    return normalized, name_mapping


def convert_expression_syntax(expr: str) -> str:
    """
    Convert bnet expression syntax to our Python-like format.
    
    Converts:
    - ! to ~
    - Keeps &, |, parentheses
    """
    return expr.replace('!', '~')


def extract_dependencies(expr: str, num_vars: int) -> List[int]:
    """Extract which variables (0-indexed) appear in the expression."""
    deps = set()
    for i in range(1, num_vars + 1):
        if re.search(rf'\bx{i}\b', expr):
            deps.add(i - 1)  # 0-indexed
    return sorted(deps)


def eval_boolean_expr(expr: str, var_values: Dict[str, bool]) -> bool:
    """
    Evaluate a boolean expression with given variable values.
    
    expr: Expression like "(x1 & ~x2) | x3"
    var_values: {"x1": True, "x2": False, ...}
    """
    # Create evaluation context
    context = {}
    for var, val in var_values.items():
        context[var] = val
    
    # Convert expression to Python syntax
    py_expr = expr
    py_expr = py_expr.replace('~', ' not ')
    py_expr = py_expr.replace('&', ' and ')
    py_expr = py_expr.replace('|', ' or ')
    
    try:
        return bool(eval(py_expr, {"__builtins__": {}}, context))
    except Exception as e:
        raise ValueError(f"Failed to evaluate expression '{expr}': {e}")


def generate_transitions(functions: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Generate asynchronous transitions from boolean functions.
    
    For each state, compute which bits would flip if that variable's function
    is applied, creating transitions for asynchronous updates.
    """
    # Get sorted variable names
    var_names = sorted(functions.keys(), key=lambda x: int(x[1:]))
    num_vars = len(var_names)
    
    transitions = {}
    
    # Iterate over all possible states
    for state_tuple in product([0, 1], repeat=num_vars):
        state_str = ''.join(str(b) for b in state_tuple)
        
        # Create variable value mapping for this state
        var_values = {var_names[i]: bool(state_tuple[i]) for i in range(num_vars)}
        
        next_states = []
        
        # For each variable, check if applying its function would change its value
        for i, var in enumerate(var_names):
            expr = functions[var]
            new_val = eval_boolean_expr(expr, var_values)
            current_val = bool(state_tuple[i])
            
            if new_val != current_val:
                # This variable would change - create a transition
                new_state_list = list(state_tuple)
                new_state_list[i] = 1 if new_val else 0
                new_state_str = ''.join(str(b) for b in new_state_list)
                next_states.append(new_state_str)
        
        # If no transitions (fixed point), state transitions to itself
        if not next_states:
            next_states = [state_str]
        
        transitions[state_str] = sorted(set(next_states))
    
    return transitions


def format_output(
    original_name: str,
    dim: int,
    functions: Dict[str, str],
    transitions: Dict[str, List[str]],
    name_mapping: Dict[str, str],
    input_substitutions: Dict[str, str] = None
) -> str:
    """Format the output Python file."""
    lines = []
    
    # Header
    lines.append('"""')
    lines.append(f'{dim}D Boolean Network: {original_name}')
    lines.append('')
    lines.append('Converted from biodivine-boolean-models repository.')
    
    if input_substitutions:
        lines.append('')
        lines.append('External inputs substituted with constants:')
        for inp, val in sorted(input_substitutions.items()):
            lines.append(f'  {inp} = {val}')
    
    lines.append('')
    lines.append('Original variable mapping:')
    for orig, new in sorted(name_mapping.items(), key=lambda x: int(x[1][1:])):
        lines.append(f'  {new} = {orig}')
    lines.append('"""')
    lines.append('')
    
    # Functions
    lines.append('# Boolean update functions')
    lines.append('network_functions = {')
    for var in sorted(functions.keys(), key=lambda x: int(x[1:])):
        lines.append(f'    "{var}": "{functions[var]}",')
    lines.append('}')
    lines.append('')
    
    # Transitions
    lines.append('# Asynchronous state transitions (derived from functions)')
    lines.append('transitions = {')
    for state in sorted(transitions.keys()):
        next_states = transitions[state]
        next_str = ', '.join(f'"{s}"' for s in next_states)
        lines.append(f'    "{state}": [{next_str}],')
    lines.append('}')
    
    return '\n'.join(lines)


def convert_bnet_file(source_path: str, target_path: str, verbose: bool = True) -> bool:
    """Convert a single .bnet file to our format."""
    try:
        # Parse
        raw_functions, external_inputs = parse_bnet_file(source_path)
        if not raw_functions:
            print(f"  Warning: No functions found in {source_path}")
            return False
        
        # Skip files with external inputs (they have undefined constants)
        if external_inputs:
            if verbose:
                print(f"  Skipping {Path(source_path).name}: has {len(external_inputs)} external inputs ({', '.join(sorted(external_inputs)[:3])}{'...' if len(external_inputs) > 3 else ''})")
            return False
        
        # Normalize variable names
        normalized, name_mapping = normalize_variable_names(raw_functions)
        
        # Convert syntax
        functions = {k: convert_expression_syntax(v) for k, v in normalized.items()}
        
        # Generate transitions
        transitions = generate_transitions(functions)
        
        # Format output
        dim = len(functions)
        original_name = Path(source_path).stem
        output = format_output(original_name, dim, functions, transitions, name_mapping)
        
        # Write
        os.makedirs(os.path.dirname(target_path), exist_ok=True)
        with open(target_path, 'w') as f:
            f.write(output)
        
        if verbose:
            print(f"  Converted: {Path(source_path).name} -> {Path(target_path).name}")
        
        return True
        
    except Exception as e:
        print(f"  Error converting {source_path}: {e}")
        return False


def substitute_inputs(functions: Dict[str, str], external_inputs: set, input_values: Dict[str, str]) -> Dict[str, str]:
    """
    Substitute external inputs with constant values (0 or 1).
    
    Args:
        functions: Dict of variable -> expression
        external_inputs: Set of external input variable names
        input_values: Dict mapping input name -> "0" or "1"
    
    Returns:
        New functions dict with inputs replaced by constants
    """
    result = {}
    for var, expr in functions.items():
        new_expr = expr
        for inp, val in input_values.items():
            # Replace input with True/False for proper boolean evaluation
            replacement = "1" if val == "1" else "0"
            new_expr = re.sub(r'\b' + re.escape(inp) + r'\b', replacement, new_expr)
        result[var] = new_expr
    return result


def simplify_expression(expr: str) -> str:
    """
    Simplify boolean expression after substituting constants.
    
    Replaces patterns like:
    - (1 & X) -> X
    - (0 & X) -> 0
    - (1 | X) -> 1
    - (0 | X) -> X
    - !0 -> 1, !1 -> 0
    - ~0 -> 1, ~1 -> 0
    """
    # Convert to Python-evaluable form
    py_expr = expr
    py_expr = py_expr.replace('~', ' not ')
    py_expr = py_expr.replace('!', ' not ')
    py_expr = py_expr.replace('&', ' and ')
    py_expr = py_expr.replace('|', ' or ')
    
    # Replace 0/1 with False/True for evaluation
    py_expr = re.sub(r'\b0\b', 'False', py_expr)
    py_expr = re.sub(r'\b1\b', 'True', py_expr)
    
    # Try to evaluate if it's a constant expression
    try:
        # Check if it contains any variables (x followed by digit)
        if not re.search(r'\bx\d+\b', py_expr):
            result = eval(py_expr, {"__builtins__": {}}, {})
            return "1" if result else "0"
    except:
        pass
    
    # Return original expression with syntax converted
    return expr


def convert_bnet_file_with_inputs(source_path: str, target_dir: str, verbose: bool = True, max_inputs: int = 3) -> int:
    """
    Convert a .bnet file with external inputs by creating variations.
    
    Creates 2^n output files for n external inputs (up to max_inputs).
    
    Args:
        source_path: Path to source .bnet file
        target_dir: Target directory for output files
        verbose: Print progress
        max_inputs: Maximum number of inputs to handle (default: 3)
    
    Returns:
        Number of files created
    """
    try:
        # Parse
        raw_functions, external_inputs = parse_bnet_file(source_path)
        if not raw_functions:
            if verbose:
                print(f"  Warning: No functions found in {source_path}")
            return 0
        
        # If no external inputs, use regular conversion
        if not external_inputs:
            return 0  # Will be handled by regular converter
        
        # Sort inputs for consistent ordering
        input_list = sorted(external_inputs)
        num_inputs = len(input_list)
        
        # Skip if too many inputs
        if num_inputs > max_inputs:
            if verbose:
                print(f"  Skipping {Path(source_path).name}: too many inputs ({num_inputs} > {max_inputs})")
            return 0
        
        # Extract model info from filename
        filename = Path(source_path).stem  # e.g., model_165_4d
        match = re.match(r'model_(\d+)_(\d+)d', filename)
        if not match:
            if verbose:
                print(f"  Warning: Could not parse filename {filename}")
            return 0
        
        model_id = match.group(1)
        dim = int(match.group(2))
        
        created = 0
        
        # Generate all combinations of input values
        for values in product(['0', '1'], repeat=num_inputs):
            variation = ''.join(values)
            input_values = {input_list[i]: values[i] for i in range(num_inputs)}
            
            # Substitute inputs
            substituted = substitute_inputs(raw_functions, external_inputs, input_values)
            
            # Normalize variable names
            normalized, name_mapping = normalize_variable_names(substituted)
            
            # Convert syntax
            functions = {k: convert_expression_syntax(v) for k, v in normalized.items()}
            
            # Generate transitions
            transitions = generate_transitions(functions)
            
            # Format output
            original_name = f"{filename}_{variation}"
            output = format_output(original_name, dim, functions, transitions, name_mapping, input_values)
            
            # Write file
            output_filename = f"bn_{model_id}_{dim}d_{variation}.py"
            output_path = Path(target_dir) / f"{dim}d" / output_filename
            os.makedirs(output_path.parent, exist_ok=True)
            
            with open(output_path, 'w') as f:
                f.write(output)
            
            if verbose:
                print(f"  Created: {output_filename}")
            
            created += 1
        
        return created
        
    except Exception as e:
        print(f"  Error converting {source_path} with inputs: {e}")
        import traceback
        traceback.print_exc()
        return 0


def convert_dimension(dim: int, source_dir: str = SOURCE_DIR, target_dir: str = TARGET_DIR, verbose: bool = True, max_inputs: int = 3):
    """Convert all files for a specific dimension."""
    dim_source = Path(source_dir) / f"{dim}d"
    dim_target = Path(target_dir) / f"{dim}d"
    
    if not dim_source.exists():
        print(f"Source directory not found: {dim_source}")
        return 0
    
    bnet_files = list(dim_source.glob("*.bnet"))
    if verbose:
        print(f"\n{dim}d: Found {len(bnet_files)} files")
    
    converted = 0
    for bnet_file in sorted(bnet_files):
        # First try regular conversion (no external inputs)
        new_name = bnet_file.stem.replace('model_', 'bn_') + '.py'
        target_path = dim_target / new_name
        
        if convert_bnet_file(str(bnet_file), str(target_path), verbose):
            converted += 1
        else:
            # Try conversion with input substitution
            num_created = convert_bnet_file_with_inputs(str(bnet_file), target_dir, verbose, max_inputs)
            converted += num_created
    
    return converted


def convert_all(min_dim: int = 4, max_dim: int = 16, source_dir: str = SOURCE_DIR, target_dir: str = TARGET_DIR, verbose: bool = True, max_inputs: int = 3):
    """Convert all dimensions from min_dim to max_dim."""
    total = 0
    
    if verbose:
        print(f"Converting biodivine models from {min_dim}d to {max_dim}d")
        print(f"Source: {source_dir}")
        print(f"Target: {target_dir}")
        print(f"Max inputs to substitute: {max_inputs}")
        print("-" * 60)
    
    for dim in range(min_dim, max_dim + 1):
        converted = convert_dimension(dim, source_dir, target_dir, verbose, max_inputs)
        total += converted
    
    if verbose:
        print("-" * 60)
        print(f"Total converted: {total} files")
    
    return total


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="Convert biodivine .bnet files to Python format")
    parser.add_argument('--min-dim', type=int, default=4, help="Minimum dimension (default: 4)")
    parser.add_argument('--max-dim', type=int, default=16, help="Maximum dimension (default: 16)")
    parser.add_argument('-s', '--source', default=SOURCE_DIR, help="Source directory")
    parser.add_argument('-t', '--target', default=TARGET_DIR, help="Target directory")
    parser.add_argument('-q', '--quiet', action='store_true', help="Suppress verbose output")
    parser.add_argument('--max-inputs', type=int, default=3, help="Max external inputs to substitute (default: 3)")
    
    args = parser.parse_args()
    
    convert_all(
        min_dim=args.min_dim,
        max_dim=args.max_dim,
        source_dir=args.source,
        target_dir=args.target,
        verbose=not args.quiet,
        max_inputs=args.max_inputs
    )


if __name__ == "__main__":
    main()
