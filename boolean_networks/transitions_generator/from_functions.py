"""
Compute asynchronous transitions from Boolean network functions.

Given network_functions = {"x1": "x2 & ~x3", ...}, computes the state
transition graph for asynchronous update semantics.
"""

from typing import Dict, List, Tuple
import re


def generate_all_states(num_vars: int) -> List[str]:
    """Generate all possible states for n variables."""
    return [format(i, f'0{num_vars}b') for i in range(2 ** num_vars)]


def parse_expression(expr: str) -> str:
    """
    Convert Boolean expression to Python-evaluable format.
    
    Handles: ~ (not), & (and), | (or)
    """
    # Replace ~ with not, but handle the variable correctly
    # ~x1 -> (not x1)
    result = re.sub(r'~(\w+)', r'(not \1)', expr)
    result = result.replace('&', ' and ')
    result = result.replace('|', ' or ')
    return result


def evaluate_expression(expr: str, context: Dict[str, int]) -> int:
    """Evaluate a Boolean expression given variable bindings."""
    try:
        # Try direct evaluation first (for expressions using Python syntax)
        return int(eval(expr, {"__builtins__": {}}, context))
    except:
        # Convert to Python syntax
        py_expr = parse_expression(expr)
        return int(eval(py_expr, {"__builtins__": {}}, context))


def compute_transitions(network_functions: Dict[str, str]) -> Dict[str, List[str]]:
    """
    Compute asynchronous state transitions from Boolean update functions.
    
    For async updates: from state s, can transition to state s' (differing 
    in bit i) if f_i(s) != s_i.
    
    Args:
        network_functions: Dict mapping variable names to Boolean expressions
        
    Returns:
        transitions: Dict mapping each state to list of possible next states
    """
    num_vars = len(network_functions)
    all_states = generate_all_states(num_vars)
    
    # Sort variable names to ensure consistent ordering (x1, x2, ..., xN)
    var_names = sorted(network_functions.keys(), key=lambda x: int(x[1:]))
    
    transitions = {}
    
    for state in all_states:
        possible_next = []
        
        # Create variable bindings for this state
        context = {}
        for i, var_name in enumerate(var_names):
            context[var_name] = int(state[i])
        
        # Check each variable for possible update
        for var_idx, var_name in enumerate(var_names):
            expr = network_functions[var_name]
            
            # Evaluate the function
            f_value = evaluate_expression(expr, context)
            current_bit = int(state[var_idx])
            
            # Can flip this bit if f_value != current_bit
            # Ensure f_value is 0 or 1
            f_value = 1 if f_value else 0
            if f_value != current_bit:
                next_state = state[:var_idx] + str(f_value) + state[var_idx + 1:]
                possible_next.append(next_state)
        
        # If no transitions possible, this is a fixed point (self-loop)
        if not possible_next:
            possible_next = [state]
        
        transitions[state] = possible_next
    
    return transitions


def transitions_to_string(transitions: Dict[str, List[str]]) -> str:
    """Convert transitions dict to Python code string."""
    lines = ["# Asynchronous state transitions (derived from functions)"]
    lines.append("transitions = {")
    
    for state in sorted(transitions.keys()):
        targets = transitions[state]
        targets_str = ", ".join(f'"{t}"' for t in sorted(targets))
        lines.append(f'    "{state}": [{targets_str}],')
    
    lines.append("}")
    
    return "\n".join(lines)


def add_transitions_to_file(filepath: str, overwrite: bool = False) -> Tuple[bool, str]:
    """
    Add transitions to a network file that only has network_functions.
    
    Args:
        filepath: Path to the Python network file
        overwrite: If True, replace existing transitions
        
    Returns:
        (success, message)
    """
    import importlib.util
    
    # Load the module
    spec = importlib.util.spec_from_file_location("network", filepath)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    if not hasattr(module, 'network_functions'):
        return False, "No network_functions found"
    
    # Read existing content
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Check if transitions already exist
    if 'transitions = {' in content and not overwrite:
        return False, "Transitions already exist (use overwrite=True to replace)"
    
    # Compute transitions
    transitions = compute_transitions(module.network_functions)
    transitions_str = transitions_to_string(transitions)
    
    if 'transitions = {' in content and overwrite:
        # Remove existing transitions
        import re
        content = re.sub(r'\n# Asynchronous state transitions.*?^transitions = \{.*?^\}',
                        '', content, flags=re.MULTILINE | re.DOTALL)
    
    # Append transitions
    with open(filepath, 'w') as f:
        f.write(content.rstrip() + "\n\n" + transitions_str + "\n")
    
    return True, f"Added {len(transitions)} state transitions"


if __name__ == "__main__":
    # Example usage
    example_functions = {
        "x1": "~x2 | x3",
        "x2": "x1 & x3",
        "x3": "~x1",
    }
    
    transitions = compute_transitions(example_functions)
    print(transitions_to_string(transitions))
