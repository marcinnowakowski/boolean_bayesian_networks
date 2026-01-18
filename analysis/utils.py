import os
import sys
from typing import Dict, Set, Tuple, List
import networkx as nx

# Add parent directory to path to import boolean_networks
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from boolean_networks.transitions_generator import generate_network, NetworkConfig
from analysis.bif_parser import predict_next_state_learned


def reconstruct_functions_from_transitions(
    transitions: Dict[str, List[str]], num_vars: int
) -> Dict[str, Dict[str, int]]:
    """
    Reconstructs the Boolean function for each variable from the transition system.
    Returns a dict where keys are variable indices (as strings '0', '1'...)
    and values are truth tables (state -> next_val).
    """
    functions = {}
    all_states = list(transitions.keys())

    for i in range(num_vars):
        truth_table = {}
        for state in all_states:
            current_val = int(state[i])
            target_val = current_val

            possible_next_states = transitions.get(state, [])
            for next_state in possible_next_states:
                if next_state[i] != state[i]:
                    target_val = int(next_state[i])
                    break

            truth_table[state] = target_val
        functions[str(i)] = truth_table

    return functions


def extract_dependencies(
    functions: Dict[str, Dict[str, int]], num_vars: int
) -> Set[Tuple[str, str]]:
    edges = set()

    for i in range(num_vars):
        target_func = functions[str(i)]
        for j in range(num_vars):
            depends = False
            for state in target_func:
                val_j = int(state[j])
                neighbor_list = list(state)
                neighbor_list[j] = "1" if val_j == 0 else "0"
                neighbor = "".join(neighbor_list)

                if neighbor in target_func:
                    if target_func[state] != target_func[neighbor]:
                        depends = True
                        break
            if depends:
                src = f"x{j + 1}"
                dst = f"x{i + 1}"
                edges.add((src, dst))

    return edges


def calculate_metrics(
    true_edges: Set[Tuple[str, str]], learned_edges: Set[Tuple[str, str]]
) -> Dict:
    tp = len(true_edges.intersection(learned_edges))
    fp = len(learned_edges - true_edges)
    fn = len(true_edges - learned_edges)

    precision = tp / (tp + fp) if (tp + fp) > 0 else 0
    recall = tp / (tp + fn) if (tp + fn) > 0 else 0
    f1 = (
        2 * (precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0
    )

    return {
        "TP": tp,
        "FP": fp,
        "FN": fn,
        "Precision": precision,
        "Recall": recall,
        "F1": f1,
    }


def evaluate_dynamics(
    true_functions: Dict[str, Dict[str, int]],
    parsed_cpts: Dict,
    parsed_parents: Dict,
    num_vars: int,
) -> Dict[str, float]:
    all_states = list(true_functions["0"].keys())

    total_states = 0
    correct_states = 0

    for state in all_states:
        true_next_list = []
        for i in range(num_vars):
            true_next_list.append(str(true_functions[str(i)][state]))
        true_next_state = "".join(true_next_list)

        learned_next_state = predict_next_state_learned(
            state, parsed_cpts, parsed_parents, num_vars
        )

        if true_next_state == learned_next_state:
            correct_states += 1

        total_states += 1

    return {
        "Transition_Accuracy": correct_states / total_states if total_states > 0 else 0,
    }


def parse_experiment_id(exp_id: str) -> Tuple[int, int]:
    """Parse experiment ID like '7d_000' into (num_vars, seed)."""
    try:
        parts = exp_id.split("_")
        dim_part = parts[0]
        seed_part = parts[1]

        num_vars = int(dim_part.replace("d", ""))
        seed = int(seed_part)
        return num_vars, seed
    except (IndexError, ValueError):
        print(
            f"Error: Invalid experiment ID format '{exp_id}'. Expected format like '7d_000' (dim_seed)."
        )
        sys.exit(1)


def build_learned_stg(cpts, parents_map, num_vars=7):
    """
    Constructs the full state transition graph for the Learned network.
    """
    transitions = {}
    for i in range(2**num_vars):
        state = f"{i:0{num_vars}b}"
        next_state = predict_next_state_learned(state, cpts, parents_map, num_vars)
        transitions[state] = [next_state]
    return transitions


def get_attractors(transitions):
    """
    Identify simple attractors (self-loops) and states part of cycles.
    """
    G = nx.DiGraph()
    for src, targets in transitions.items():
        for tgt in targets:
            G.add_edge(src, tgt)

    attractors = set()
    try:
        cycles = list(nx.simple_cycles(G))
        for cycle in cycles:
            attractors.update(cycle)
    except Exception:
        pass
    return attractors


def generate_ground_truth(seed: int, num_vars: int):
    """Generates ground truth edges and functions."""
    config = NetworkConfig(seed=seed, num_vars=num_vars)
    transitions = generate_network(config)
    functions = reconstruct_functions_from_transitions(transitions, num_vars)
    edges = extract_dependencies(functions, num_vars)
    return transitions, functions, edges


def truth_table_to_expression(truth_table: Dict[str, int], num_vars: int) -> str:
    """Converts a truth table (state -> val) to a minimized Boolean expression string."""
    from sympy import symbols
    from sympy.logic.boolalg import SOPform

    minterms = []
    # Create variables x1, x2, ..., xn
    vars_list = symbols(f"x1:{num_vars + 1}")

    for state, output in truth_table.items():
        if output == 1:
            # Convert binary string state to integer for minterm
            minterm_int = int(state, 2)
            minterms.append(minterm_int)

    if not minterms:
        return "False"
    if len(minterms) == 2**num_vars:
        return "True"

    expr = SOPform(vars_list, minterms)
    return str(expr)
