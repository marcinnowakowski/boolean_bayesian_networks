"""
Extract boolean functions from truth table format.

Reads truth tables like:
    truth_table = {
        "00000": {"x1": "00000", "x2": "01000", ...},
        ...
    }

And extracts network functions in sum-of-products form:
    network_functions = {
        "x1": "~x4 | x5",
        ...
    }
"""

from typing import Dict, List, Set, Tuple


def load_truth_table(filepath: str) -> Dict[str, Dict[str, str]]:
    """
    Load truth table from a Python file.
    
    Args:
        filepath: Path to file containing truth_table dict
    
    Returns:
        Dict mapping state -> {variable -> next_state}
    """
    with open(filepath, 'r') as f:
        content = f.read()
    
    namespace = {}
    exec(content, namespace)
    
    return namespace.get('truth_table', {})


def extract_functions(truth_table: Dict[str, Dict[str, str]], num_vars: int = None) -> Dict[str, str]:
    """
    Extract boolean functions from truth table.
    
    For each variable, determines when it becomes 1 and builds a SOP expression.
    
    Args:
        truth_table: Dict mapping state -> {variable -> next_state}
        num_vars: Number of variables (auto-detected if None)
    
    Returns:
        Dict mapping variable name to boolean expression
    """
    # Auto-detect num_vars
    if num_vars is None:
        first_state = next(iter(truth_table.keys()), None)
        if first_state:
            num_vars = len(first_state)
        else:
            num_vars = 5
    
    var_names = [f"x{i+1}" for i in range(num_vars)]
    functions = {}
    
    for var_idx, var_name in enumerate(var_names):
        # Collect minterms: states where this variable becomes 1
        minterms = []
        
        for state, next_states in truth_table.items():
            next_state = next_states.get(var_name, state)
            # Check if this variable is 1 in the next state
            next_val = int(next_state[var_idx])
            
            if next_val == 1:
                # Convert state string to tuple of ints
                state_tuple = tuple(int(b) for b in state)
                minterms.append(state_tuple)
        
        # Build expression from minterms
        functions[var_name] = _build_sop(minterms, var_names, num_vars)
    
    return functions


def _build_sop(minterms: List[Tuple], var_names: List[str], num_vars: int) -> str:
    """
    Build sum-of-products expression from minterms.
    
    Args:
        minterms: List of state tuples where output = 1
        var_names: List of variable names
        num_vars: Number of variables
    
    Returns:
        Boolean expression string
    """
    if not minterms:
        return "0"
    
    # If all states are minterms, output is always 1
    if len(minterms) == 2 ** num_vars:
        return "1"
    
    # Build product terms
    terms = []
    for minterm in minterms:
        parts = []
        for i, bit in enumerate(minterm):
            if bit == 1:
                parts.append(var_names[i])
            else:
                parts.append(f"~{var_names[i]}")
        terms.append(frozenset(parts))
    
    # Remove duplicates
    terms = list(set(terms))
    
    # Convert back to sets for simplification
    terms = [set(t) for t in terms]
    
    # Apply simplification
    terms = _simplify_terms(terms, var_names)
    
    return _terms_to_string(terms)


def _simplify_terms(terms: List[Set[str]], var_names: List[str]) -> List[Set[str]]:
    """Apply basic simplification rules."""
    # Apply absorption: A | (A & B) = A
    terms = _apply_absorption(terms)
    
    # Combine terms that differ by one variable
    changed = True
    while changed:
        terms, changed = _combine_adjacent(terms, var_names)
        if changed:
            terms = _apply_absorption(terms)
    
    return terms


def _apply_absorption(terms: List[Set[str]]) -> List[Set[str]]:
    """Apply absorption law: A | (A & B) = A"""
    result = []
    for term in terms:
        absorbed = False
        for other in terms:
            if term != other and other.issubset(term):
                absorbed = True
                break
        if not absorbed:
            result.append(term)
    return result


def _combine_adjacent(terms: List[Set[str]], var_names: List[str]) -> Tuple[List[Set[str]], bool]:
    """Combine terms that differ only by one complemented variable."""
    changed = False
    new_terms = []
    used = set()
    
    terms_list = list(terms)
    
    for i, term1 in enumerate(terms_list):
        if i in used:
            continue
        
        combined = False
        for j, term2 in enumerate(terms_list):
            if i >= j or j in used:
                continue
            
            # Check if terms differ by exactly one variable
            diff_var = _find_single_diff(term1, term2, var_names)
            if diff_var:
                # Combine: (A & B) | (A & ~B) = A
                new_term = term1 - {diff_var, f"~{diff_var}"}
                new_term = new_term - {f"~{diff_var}", diff_var}
                
                # Remove both positive and negative forms of the variable
                new_term = {lit for lit in term1 if lit != diff_var and lit != f"~{diff_var}"}
                
                if new_term:  # Don't add empty term
                    new_terms.append(new_term)
                else:
                    # Empty term means always true for this combination
                    return [set()], True
                
                used.add(i)
                used.add(j)
                combined = True
                changed = True
                break
        
        if not combined:
            new_terms.append(term1)
    
    return new_terms, changed


def _find_single_diff(term1: Set[str], term2: Set[str], var_names: List[str]) -> str:
    """Find if terms differ by exactly one complemented variable."""
    # Both terms must have same size
    if len(term1) != len(term2):
        return None
    
    diff_var = None
    
    for var in var_names:
        pos = var
        neg = f"~{var}"
        
        has1_pos = pos in term1
        has1_neg = neg in term1
        has2_pos = pos in term2
        has2_neg = neg in term2
        
        # One term has positive, other has negative
        if (has1_pos and has2_neg) or (has1_neg and has2_pos):
            if diff_var is not None:
                return None  # More than one difference
            diff_var = var
        # Both have same literal - OK
        elif has1_pos == has2_pos and has1_neg == has2_neg:
            continue
        else:
            return None  # Different in a way that can't be combined
    
    return diff_var


def _terms_to_string(terms: List[Set[str]]) -> str:
    """Convert terms to expression string."""
    if not terms:
        return "0"
    
    # Check for tautology (empty term means always true)
    if any(len(t) == 0 for t in terms):
        return "1"
    
    # Sort literals within each term for consistency
    def sort_key(lit):
        var = lit.lstrip("~")
        return (int(var[1:]) if var[1:].isdigit() else 0, lit.startswith("~"))
    
    result_terms = []
    for term in terms:
        sorted_lits = sorted(term, key=sort_key)
        if len(sorted_lits) == 1:
            result_terms.append(sorted_lits[0])
        else:
            result_terms.append("(" + " & ".join(sorted_lits) + ")")
    
    # Sort terms for consistent output
    result_terms.sort()
    
    if len(result_terms) == 1:
        return result_terms[0]
    
    return " | ".join(result_terms)


def functions_to_string(functions: Dict[str, str], source_file: str = None) -> str:
    """
    Convert functions dict to output file format.
    
    Args:
        functions: Dict mapping variable name to expression
        source_file: Optional source file path for docstring
    
    Returns:
        Formatted Python file content
    """
    lines = ['"""']
    if source_file:
        lines.append(f"Functions extracted from: {source_file}")
        lines.append("")
    
    lines.append("Dependency Structure:")
    for var in sorted(functions.keys()):
        expr = functions[var]
        deps = _extract_dependencies(expr)
        if deps:
            lines.append(f"  {var} depends on: {', '.join(sorted(deps))}")
        else:
            lines.append(f"  {var} depends on: (constant)")
    
    lines.append('"""')
    lines.append("")
    lines.append("network_functions = {")
    
    for var in sorted(functions.keys()):
        lines.append(f'    "{var}": "{functions[var]}",')
    
    lines.append("}")
    
    return "\n".join(lines)


def _extract_dependencies(expr: str) -> Set[str]:
    """Extract variable names from expression."""
    import re
    matches = re.findall(r'x\d+', expr)
    return set(matches)


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m boolean_networks.function_exctactor.truth_table_2_functions <truth_table_file> [-o output_file]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    output_file = None
    
    if '-o' in sys.argv:
        idx = sys.argv.index('-o')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
    
    truth_table = load_truth_table(filepath)
    functions = extract_functions(truth_table)
    output = functions_to_string(functions, filepath)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"Functions written to {output_file}")
    else:
        print(output)


if __name__ == "__main__":
    main()
