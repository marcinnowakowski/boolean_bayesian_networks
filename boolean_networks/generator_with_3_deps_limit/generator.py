"""
7D Boolean Network Generator with 3-Variable Dependency Limit

Each variable x_i has an update function f_i that depends on at most 3 variables.

Key insight: In async Boolean networks, from state s we can transition to 
state s' (differing in bit i) if f_i(s) ≠ s_i.

To enforce 3-variable limit:
1. For each variable x_i, choose 3 dependency variables (deps_i)
2. Define f_i as a Boolean function of those 3 variables
3. Transitions are determined by: can flip x_i iff f_i(s) ≠ s_i

This guarantees that the resulting truth table will have functions 
depending on at most 3 variables.
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Set, Optional, Tuple


@dataclass
class NetworkConfig:
    """Configuration for network generation."""
    num_vars: int = 7
    num_deps: int = 3  # Each variable depends on at most this many variables
    seed: Optional[int] = None
    # Control function complexity
    min_true_outputs: int = 2  # Minimum number of input combinations where f=1
    max_true_outputs: int = 6  # Maximum (out of 8 for 3 deps)


def generate_all_states(num_vars: int) -> List[str]:
    """Generate all possible states for n variables."""
    return [format(i, f'0{num_vars}b') for i in range(2 ** num_vars)]


def generate_network(config: NetworkConfig = None) -> Tuple[Dict[str, List[str]], Dict[str, Tuple[List[int], Dict[str, int]]]]:
    """
    Generate a network where each variable depends on at most 3 others.
    
    Returns:
        transitions: Dict[state -> list of possible next states]
        functions: Dict[var_name -> (dependency_indices, truth_table)]
            where truth_table maps 3-bit string to 0 or 1
    """
    if config is None:
        config = NetworkConfig()
    
    if config.seed is not None:
        random.seed(config.seed)
    
    num_vars = config.num_vars
    all_states = generate_all_states(num_vars)
    
    # Step 1: Define dependencies and functions for each variable
    functions = {}
    for var_idx in range(num_vars):
        var_name = f"x{var_idx + 1}"
        
        # Choose dependency variables (indices)
        # Can include self or not - random choice
        all_indices = list(range(num_vars))
        deps = random.sample(all_indices, min(config.num_deps, num_vars))
        deps.sort()
        
        # Define truth table for this function
        # Maps 3-bit input (from deps) to output (0 or 1)
        num_inputs = 2 ** len(deps)
        
        # Random function with controlled number of 1s
        num_ones = random.randint(config.min_true_outputs, 
                                  min(config.max_true_outputs, num_inputs - 1))
        ones_positions = random.sample(range(num_inputs), num_ones)
        
        truth_table = {}
        for i in range(num_inputs):
            input_bits = format(i, f'0{len(deps)}b')
            truth_table[input_bits] = 1 if i in ones_positions else 0
        
        functions[var_name] = (deps, truth_table)
    
    # Step 2: Compute transitions based on functions
    transitions = {}
    
    for state in all_states:
        possible_next = []
        
        for var_idx in range(num_vars):
            var_name = f"x{var_idx + 1}"
            deps, truth_table = functions[var_name]
            
            # Extract dependency bits from current state
            dep_bits = ''.join(state[d] for d in deps)
            
            # Evaluate function
            f_value = truth_table[dep_bits]
            current_bit = int(state[var_idx])
            
            # Can flip this bit if f_value != current_bit
            if f_value != current_bit:
                # Create next state by flipping bit var_idx
                next_state = state[:var_idx] + str(f_value) + state[var_idx + 1:]
                possible_next.append(next_state)
        
        # If no transitions possible, this is a fixed point (self-loop)
        if not possible_next:
            possible_next = [state]
        
        transitions[state] = possible_next
    
    return transitions, functions


def functions_to_expressions(functions: Dict[str, Tuple[List[int], Dict[str, int]]]) -> Dict[str, str]:
    """Convert function truth tables to Boolean expressions."""
    expressions = {}
    
    for var_name, (deps, truth_table) in functions.items():
        dep_names = [f"x{d + 1}" for d in deps]
        
        # Build SOP from truth table
        terms = []
        for input_bits, output in truth_table.items():
            if output == 1:
                term_parts = []
                for i, bit in enumerate(input_bits):
                    if bit == '1':
                        term_parts.append(dep_names[i])
                    else:
                        term_parts.append(f"~{dep_names[i]}")
                terms.append("(" + " & ".join(term_parts) + ")")
        
        if terms:
            expressions[var_name] = " | ".join(terms)
        else:
            expressions[var_name] = "0"  # Always false
    
    return expressions


def network_to_string(transitions: Dict[str, List[str]], 
                      functions: Dict[str, Tuple[List[int], Dict[str, int]]],
                      name: str = "generated_network") -> str:
    """Convert network to Python file format."""
    expressions = functions_to_expressions(functions)
    
    lines = ['"""']
    lines.append(f"7D Boolean Network: {name}")
    lines.append("")
    lines.append("Each variable depends on at most 3 variables.")
    lines.append("")
    lines.append("Dependencies:")
    for var_name, (deps, _) in sorted(functions.items()):
        dep_names = [f"x{d + 1}" for d in deps]
        lines.append(f"  {var_name} depends on: {', '.join(dep_names)}")
    lines.append('"""')
    lines.append("")
    
    # Output the functions
    lines.append("# Boolean update functions (each depends on at most 3 variables)")
    lines.append("network_functions = {")
    for var_name in sorted(expressions.keys()):
        expr = expressions[var_name]
        lines.append(f'    "{var_name}": "{expr}",')
    lines.append("}")
    lines.append("")
    
    # Also output transitions for reference
    lines.append("# Asynchronous state transitions (derived from functions)")
    lines.append("transitions = {")
    for state in sorted(transitions.keys()):
        targets = transitions[state]
        targets_str = ", ".join(f'"{t}"' for t in sorted(targets))
        lines.append(f'    "{state}": [{targets_str}],')
    lines.append("}")
    
    return "\n".join(lines)


def analyze_network(transitions: Dict[str, List[str]]) -> Dict:
    """Analyze network structure."""
    all_states = set(transitions.keys())
    
    all_targets = set()
    for targets in transitions.values():
        all_targets.update(targets)
    
    parentless = all_states - all_targets
    
    # Find fixed points (self-loops)
    fixed_points = [s for s, targets in transitions.items() 
                    if targets == [s]]
    
    # Find SCCs
    sccs = _find_sccs(transitions)
    
    # Attractors = SCCs with no exit
    attractors = []
    for scc in sccs:
        has_exit = False
        for state in scc:
            for target in transitions.get(state, []):
                if target not in scc:
                    has_exit = True
                    break
            if has_exit:
                break
        if not has_exit:
            attractors.append(scc)
    
    return {
        "num_states": len(all_states),
        "num_transitions": sum(len(t) for t in transitions.values()),
        "parentless_states": len(parentless),
        "fixed_points": len(fixed_points),
        "num_sccs": len(sccs),
        "num_attractors": len(attractors),
        "attractor_sizes": sorted([len(a) for a in attractors], reverse=True),
    }


def _find_sccs(transitions: Dict[str, List[str]]) -> List[Set[str]]:
    """Find strongly connected components using Tarjan's algorithm."""
    index_counter = [0]
    stack = []
    lowlinks = {}
    index = {}
    on_stack = {}
    sccs = []
    
    def strongconnect(node):
        index[node] = index_counter[0]
        lowlinks[node] = index_counter[0]
        index_counter[0] += 1
        stack.append(node)
        on_stack[node] = True
        
        for successor in transitions.get(node, []):
            if successor not in index:
                strongconnect(successor)
                lowlinks[node] = min(lowlinks[node], lowlinks[successor])
            elif on_stack.get(successor, False):
                lowlinks[node] = min(lowlinks[node], index[successor])
        
        if lowlinks[node] == index[node]:
            scc = set()
            while True:
                successor = stack.pop()
                on_stack[successor] = False
                scc.add(successor)
                if successor == node:
                    break
            sccs.append(scc)
    
    for node in transitions:
        if node not in index:
            strongconnect(node)
    
    return sccs


def main():
    import sys
    
    output_file = None
    seed = None
    
    if '-o' in sys.argv:
        idx = sys.argv.index('-o')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
    
    if '-s' in sys.argv:
        idx = sys.argv.index('-s')
        if idx + 1 < len(sys.argv):
            seed = int(sys.argv[idx + 1])
    
    config = NetworkConfig(seed=seed)
    transitions, functions = generate_network(config)
    
    analysis = analyze_network(transitions)
    print(f"Generated network (3-var limit):")
    print(f"  States: {analysis['num_states']}")
    print(f"  Parentless: {analysis['parentless_states']}")
    print(f"  Fixed points: {analysis['fixed_points']}")
    print(f"  Attractors: {analysis['num_attractors']} (sizes: {analysis['attractor_sizes']})")
    
    # Show dependencies
    print(f"\nDependencies:")
    for var_name, (deps, _) in sorted(functions.items()):
        dep_names = [f"x{d + 1}" for d in deps]
        print(f"  {var_name} <- {', '.join(dep_names)}")
    
    output = network_to_string(transitions, functions, f"generated_7d_3dep_seed_{seed or 'random'}")
    
    if output_file:
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"\nNetwork written to {output_file}")
    else:
        print("\n" + output)


if __name__ == "__main__":
    main()
