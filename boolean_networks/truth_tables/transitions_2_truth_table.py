"""
Convert network transitions to truth table format.

Reads transitions (state -> list of next states) and generates a truth table
where each state maps to {variable -> next_state_if_that_var_changes}.

Missing transitions are treated as self-loops.
"""

from typing import Dict, List


def load_transitions(filepath: str) -> Dict[str, List[str]]:
    """
    Load network transitions from a Python file.
    
    Args:
        filepath: Path to file containing transitions dict
    
    Returns:
        Dict mapping state to list of possible next states
    """
    with open(filepath, 'r') as f:
        content = f.read()
    
    namespace = {}
    exec(content, namespace)
    
    return namespace.get('transitions', {})


def hamming_distance(s1: str, s2: str) -> int:
    """Return number of differing bits between two states."""
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def differing_bit_index(s1: str, s2: str) -> int:
    """Return index of the single differing bit. Assumes exactly 1 bit differs."""
    for i, (c1, c2) in enumerate(zip(s1, s2)):
        if c1 != c2:
            return i
    return -1


def transitions_to_truth_table(transitions: Dict[str, List[str]], num_vars: int = None) -> Dict[str, Dict[str, str]]:
    """
    Convert transitions to truth table format.
    
    For each state:
      - Look at transitions to find which variable changes to which next state
      - If no transition for a variable, use self-loop (state stays same)
    
    Args:
        transitions: Dict mapping state -> list of next states
        num_vars: Number of variables (auto-detected if None)
    
    Returns:
        Dict mapping state -> {variable -> next_state_if_that_var_changes}
    """
    # Auto-detect num_vars from first state
    if num_vars is None:
        first_state = next(iter(transitions.keys()), None)
        if first_state:
            num_vars = len(first_state)
        else:
            num_vars = 5  # default
    
    var_names = [f"x{i+1}" for i in range(num_vars)]
    truth_table = {}
    
    # Generate all possible states
    all_states = [format(i, f'0{num_vars}b') for i in range(2 ** num_vars)]
    
    for state in all_states:
        next_states = {}
        
        # Get transitions from this state (empty list if missing = self-loop only)
        state_transitions = transitions.get(state, [])
        
        # For each variable, find what happens when it changes
        for var_idx, var in enumerate(var_names):
            # Look for a transition that changes only this variable
            found = False
            for next_state in state_transitions:
                if hamming_distance(state, next_state) == 1:
                    if differing_bit_index(state, next_state) == var_idx:
                        next_states[var] = next_state
                        found = True
                        break
            
            # If no transition for this variable, use self-loop
            if not found:
                next_states[var] = state
        
        truth_table[state] = next_states
    
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
    
    if len(sys.argv) < 2:
        print("Usage: python -m boolean_networks.truth_tables.transitions_2_truth_table <transitions_file> [-o output_file]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    output_file = None
    
    if '-o' in sys.argv:
        idx = sys.argv.index('-o')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
    
    transitions = load_transitions(filepath)
    
    # Extract docstring from original file for header
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Build output
    lines = ['"""']
    lines.append(f"Truth table generated from: {filepath}")
    lines.append("")
    lines.append("Format: state -> {{variable: next_state_if_that_var_changes}}")
    lines.append("Missing transitions are treated as self-loops.")
    lines.append('"""')
    lines.append('')
    
    truth_table = transitions_to_truth_table(transitions)
    lines.append(truth_table_to_string(truth_table))
    
    output = '\n'.join(lines)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"Truth table written to {output_file}")
    else:
        print(output)


if __name__ == "__main__":
    main()
