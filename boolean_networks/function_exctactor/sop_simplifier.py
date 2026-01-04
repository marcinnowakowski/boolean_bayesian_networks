"""
SOP Simplifier using Quine-McCluskey algorithm.

Simplifies sum-of-products boolean expressions to their minimal form.
"""

from typing import Dict, List, Set, Tuple, FrozenSet
import re


def load_sops(filepath: str) -> Dict[str, str]:
    """Load network_functions from a Python file."""
    with open(filepath, 'r') as f:
        content = f.read()
    
    namespace = {}
    exec(content, namespace)
    
    return namespace.get('network_functions', {})


def simplify_sop(expr: str, var_names: List[str] = None) -> str:
    """
    Simplify a sum-of-products expression using Quine-McCluskey.
    
    Args:
        expr: SOP expression like "(x1 & ~x2) | (x1 & x2)"
        var_names: List of variable names (auto-detected if None)
    
    Returns:
        Simplified expression
    """
    if expr in ("0", "1"):
        return expr
    
    # Parse expression to get minterms
    if var_names is None:
        var_names = _detect_variables(expr)
    
    minterms = _parse_to_minterms(expr, var_names)
    
    if not minterms:
        return "0"
    
    if len(minterms) == 2 ** len(var_names):
        return "1"
    
    # Apply Quine-McCluskey
    prime_implicants = _quine_mccluskey(minterms, len(var_names))
    
    # Select minimum cover
    essential = _select_cover(prime_implicants, minterms)
    
    # Convert back to expression
    return _implicants_to_expr(essential, var_names)


def _detect_variables(expr: str) -> List[str]:
    """Extract variable names from expression."""
    matches = re.findall(r'x\d+', expr)
    vars_set = sorted(set(matches), key=lambda x: int(x[1:]))
    return vars_set


def _parse_to_minterms(expr: str, var_names: List[str]) -> Set[int]:
    """
    Parse SOP expression to set of minterm indices.
    
    Each minterm is an integer where bit i represents variable i.
    """
    minterms = set()
    num_vars = len(var_names)
    var_to_idx = {v: i for i, v in enumerate(var_names)}
    
    # Split into terms
    terms = expr.split(" | ")
    
    for term in terms:
        term = term.strip()
        if term.startswith("(") and term.endswith(")"):
            term = term[1:-1]
        
        # Parse literals in this term
        literals = [lit.strip() for lit in term.split(" & ")]
        
        # Build constraint: which bits must be 0 or 1
        must_be_1 = set()
        must_be_0 = set()
        
        for lit in literals:
            if lit.startswith("~"):
                var = lit[1:]
                if var in var_to_idx:
                    must_be_0.add(var_to_idx[var])
            else:
                if lit in var_to_idx:
                    must_be_1.add(var_to_idx[lit])
        
        # Generate all minterms that match this term
        free_bits = set(range(num_vars)) - must_be_1 - must_be_0
        
        # Start with base value from must_be_1
        base = 0
        for idx in must_be_1:
            base |= (1 << (num_vars - 1 - idx))
        
        # Generate all combinations of free bits
        free_list = list(free_bits)
        for i in range(2 ** len(free_list)):
            val = base
            for j, bit_idx in enumerate(free_list):
                if i & (1 << j):
                    val |= (1 << (num_vars - 1 - bit_idx))
            minterms.add(val)
    
    return minterms


def _quine_mccluskey(minterms: Set[int], num_vars: int) -> Set[Tuple]:
    """
    Apply Quine-McCluskey algorithm to find prime implicants.
    
    Returns set of implicants as tuples: (value, mask)
    where mask indicates don't-care positions.
    """
    # Group minterms by number of 1s
    groups = {}
    for m in minterms:
        ones = bin(m).count('1')
        if ones not in groups:
            groups[ones] = set()
        groups[ones].add((m, 0))  # (value, mask)
    
    prime_implicants = set()
    
    while groups:
        new_groups = {}
        used = set()
        
        sorted_keys = sorted(groups.keys())
        
        for i in range(len(sorted_keys) - 1):
            g1 = groups[sorted_keys[i]]
            g2 = groups[sorted_keys[i + 1]]
            
            for (val1, mask1) in g1:
                for (val2, mask2) in g2:
                    if mask1 != mask2:
                        continue
                    
                    # Check if they differ by exactly one bit
                    diff = val1 ^ val2
                    if diff & (diff - 1) == 0 and diff != 0:  # Power of 2
                        # Can combine
                        new_mask = mask1 | diff
                        new_val = val1 & ~diff
                        
                        ones = bin(new_val).count('1')
                        if ones not in new_groups:
                            new_groups[ones] = set()
                        new_groups[ones].add((new_val, new_mask))
                        
                        used.add((val1, mask1))
                        used.add((val2, mask2))
        
        # Add unused implicants as prime
        for g in groups.values():
            for imp in g:
                if imp not in used:
                    prime_implicants.add(imp)
        
        groups = new_groups
    
    return prime_implicants


def _select_cover(implicants: Set[Tuple], minterms: Set[int]) -> Set[Tuple]:
    """Select minimum set of implicants that cover all minterms."""
    if not implicants:
        return set()
    
    # Map each implicant to minterms it covers
    coverage = {}
    for imp in implicants:
        val, mask = imp
        covered = set()
        for m in minterms:
            if (m & ~mask) == (val & ~mask):
                covered.add(m)
        coverage[imp] = covered
    
    selected = set()
    uncovered = minterms.copy()
    
    # Find essential implicants (cover minterms that no other covers)
    for m in minterms:
        covers_m = [imp for imp in implicants if m in coverage[imp]]
        if len(covers_m) == 1:
            imp = covers_m[0]
            if imp not in selected:
                selected.add(imp)
                uncovered -= coverage[imp]
    
    # Greedy cover remaining
    while uncovered:
        best_imp = None
        best_count = 0
        
        for imp in implicants:
            if imp in selected:
                continue
            count = len(coverage[imp] & uncovered)
            if count > best_count:
                best_count = count
                best_imp = imp
        
        if best_imp is None:
            break
        
        selected.add(best_imp)
        uncovered -= coverage[best_imp]
    
    return selected


def _implicants_to_expr(implicants: Set[Tuple], var_names: List[str]) -> str:
    """Convert implicants back to expression string."""
    if not implicants:
        return "0"
    
    num_vars = len(var_names)
    terms = []
    
    for val, mask in implicants:
        literals = []
        for i in range(num_vars):
            bit_pos = num_vars - 1 - i
            if mask & (1 << bit_pos):
                continue  # Don't care
            if val & (1 << bit_pos):
                literals.append(var_names[i])
            else:
                literals.append(f"~{var_names[i]}")
        
        if not literals:
            return "1"  # Empty term = tautology
        elif len(literals) == 1:
            terms.append(literals[0])
        else:
            terms.append("(" + " & ".join(literals) + ")")
    
    # Sort for consistent output
    terms.sort()
    
    if len(terms) == 1:
        return terms[0]
    
    return " | ".join(terms)


def simplify_all(functions: Dict[str, str]) -> Dict[str, str]:
    """Simplify all functions in dictionary."""
    # Detect all variables across all expressions
    all_vars = set()
    for expr in functions.values():
        all_vars.update(_detect_variables(expr))
    var_names = sorted(all_vars, key=lambda x: int(x[1:]))
    
    simplified = {}
    for var, expr in functions.items():
        simplified[var] = simplify_sop(expr, var_names)
    
    return simplified


def functions_to_string(functions: Dict[str, str], source_file: str = None) -> str:
    """Convert functions dict to output file format."""
    lines = ['"""']
    if source_file:
        lines.append(f"Simplified functions from: {source_file}")
        lines.append("")
    
    lines.append("Dependency Structure:")
    for var in sorted(functions.keys()):
        expr = functions[var]
        deps = set(re.findall(r'x\d+', expr))
        if deps:
            lines.append(f"  {var} depends on: {', '.join(sorted(deps, key=lambda x: int(x[1:])))}")
        else:
            lines.append(f"  {var} depends on: (constant)")
    
    lines.append('"""')
    lines.append("")
    lines.append("network_functions = {")
    
    for var in sorted(functions.keys()):
        lines.append(f'    "{var}": "{functions[var]}",')
    
    lines.append("}")
    
    return "\n".join(lines)


def main():
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python -m boolean_networks.function_exctactor.sop_simplifier <sop_file> [-o output_file]")
        sys.exit(1)
    
    filepath = sys.argv[1]
    output_file = None
    
    if '-o' in sys.argv:
        idx = sys.argv.index('-o')
        if idx + 1 < len(sys.argv):
            output_file = sys.argv[idx + 1]
    
    functions = load_sops(filepath)
    simplified = simplify_all(functions)
    output = functions_to_string(simplified, filepath)
    
    if output_file:
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"Simplified functions written to {output_file}")
    else:
        print(output)


if __name__ == "__main__":
    main()
