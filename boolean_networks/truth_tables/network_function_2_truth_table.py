"""
Truth table generator from boolean functions.

Reads function definitions and generates a full truth table showing
the next state for each variable from each state.
"""

import os
from typing import Dict


def load_functions(filepath: str) -> Dict[str, str]:
    """
    Load network functions from a Python file.
    
    Args:
        filepath: Path to file containing network_functions dict
    
    Returns:
        Dict mapping variable name to its boolean expression
    """
    with open(filepath, 'r') as f:
        content = f.read()
    
    namespace = {}
    exec(content, namespace)
    
    return namespace.get('network_functions', {})


def evaluate_expression(expr: str, state: Dict[str, int]) -> int:
    """
    Evaluate a boolean expression given variable values.
    
    Args:
        expr: Boolean expression (e.g., "~x4", "(x1 & x3) | ~x5")
        state: Dict mapping variable names to values (0 or 1)
    
    Returns:
        0 or 1
    """
    if expr == "0":
        return 0
    if expr == "1":
        return 1
    
    # Replace variable names with their values
    result = expr
    
    # Handle negations first: ~x1 -> (not x1)
    for var, val in state.items():
        result = result.replace(f"~{var}", f"(not {val})")
    
    # Replace remaining variables
    for var, val in state.items():
        result = result.replace(var, str(val))
    
    # Replace boolean operators
    result = result.replace("&", " and ")
    result = result.replace("|", " or ")
    
    # Evaluate
    return 1 if eval(result) else 0


def generate_truth_table(functions: Dict[str, str], num_vars: int = 5) -> Dict[str, Dict[str, str]]:
    """
    Generate truth table from boolean functions.
    
    For each state, compute what each variable becomes.
    
    Args:
        functions: Dict mapping "x1", "x2", ... to boolean expressions
        num_vars: Number of variables
    
    Returns:
        Dict mapping state -> {variable -> next_state_if_that_var_changes}
    """
    var_names = [f"x{i+1}" for i in range(num_vars)]
    truth_table = {}
    
    # Generate all states
    for i in range(2 ** num_vars):
        state_str = format(i, f'0{num_vars}b')
        state_bits = [int(b) for b in state_str]
        state_dict = {var_names[j]: state_bits[j] for j in range(num_vars)}
        
        # For each variable, compute next state
        next_states = {}
        for var_idx, var in enumerate(var_names):
            expr = functions.get(var, var)  # default: stay same
            next_val = evaluate_expression(expr, state_dict)
            
            # Build next state string (only this variable changes)
            next_bits = state_bits.copy()
            next_bits[var_idx] = next_val
            next_state_str = ''.join(str(b) for b in next_bits)
            
            next_states[var] = next_state_str
        
        truth_table[state_str] = next_states
    
    return truth_table


def truth_table_to_string(truth_table: Dict[str, Dict[str, str]]) -> str:
    """Convert truth table to formatted string."""
    lines = ["truth_table = {"]
    
    for state in sorted(truth_table.keys()):
        next_states = truth_table[state]
        parts = [f'"{var}": "{next_states[var]}"' for var in sorted(next_states.keys())]
        lines.append(f'    "{state}": {{{", ".join(parts)}}},')
    
    lines.append("}")
    return "\n".join(lines)


def main():
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python -m boolean_networks.truth_table <functions_file>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    
    functions = load_functions(filepath)
    
    # Output as Python file with comment header
    print('"""')
    print("Functions:")
    for var in sorted(functions.keys()):
        print(f"  {var}' = {functions[var]}")
    print('"""')
    
    truth_table = generate_truth_table(functions)
    print()
    print(truth_table_to_string(truth_table))


if __name__ == "__main__":
    main()
