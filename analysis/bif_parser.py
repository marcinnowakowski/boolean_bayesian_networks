import re
from typing import Dict, Set, Tuple, List
from sympy.logic.boolalg import SOPform
from sympy import symbols


def parse_filename(filename: str) -> Dict:
    pattern = r"(\d+)d_(\d+)_(\w+)_f(\d+)_s(\d+)_l(\d+)_at(\d+\.?\d*)_scr(\w+)\.bif"
    match = re.match(pattern, filename)
    if match:
        return {
            "dim": int(match.group(1)),
            "id": match.group(2),
            "mode": match.group(3),
            "freq": int(match.group(4)),
            "size": int(match.group(5)),
            "len": int(match.group(6)),
            "attr_ratio": float(match.group(7)),
            "score": match.group(8),
        }
    return {}


def parse_bif_edges(bif_content: str) -> Set[Tuple[str, str]]:
    """
    Parses edges from BIF content using regex.
    """
    edges = set()
    lines = bif_content.split("\n")
    for line in lines:
        line = line.strip()
        if line.startswith("probability"):
            content = (
                line.replace("probability", "")
                .replace("(", "")
                .replace(")", "")
                .replace("{", "")
                .strip()
            )
            if "|" in content:
                parts = content.split("|")
                child_part = parts[0].strip()
                parents_part = parts[1].strip()
                child = child_part.replace('"', "").strip()
                parents = [p.replace('"', "").strip() for p in parents_part.split()]
                for parent in parents:
                    edges.add((parent, child))
    return edges


def parse_bif_cpts(
    bif_content: str,
) -> Tuple[Dict[str, Dict[str, int]], Dict[str, List[str]]]:
    """
    Parses CPTs from BIF content to reconstruct Boolean functions.
    Returns:
        cpts: Dict[child_var, Dict[parent_val_string, output_int]]
        parents_map: Dict[child_var, List[parent_var_names]]
    """
    cpts = {}
    parents_map = {}

    lines = bif_content.split("\n")
    current_child = None

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if line.startswith("probability"):
            content = (
                line.replace("probability", "")
                .replace("(", "")
                .replace(")", "")
                .replace("{", "")
                .strip()
            )

            if "|" in content:
                parts = content.split("|")
                child_part = parts[0].strip()
                parents_part = parts[1].strip()
                current_child = child_part.replace('"', "").strip()
                current_parents = [
                    p.replace('"', "").strip() for p in parents_part.split()
                ]
            else:
                current_child = content.replace('"', "").strip()
                current_parents = []

            parents_map[current_child] = current_parents
            cpts[current_child] = {}

        elif line.startswith("}"):
            current_child = None

        elif current_child is not None and ("(" in line or "default" in line):
            clean_line = line.replace(";", "").strip()
            # Extract probs from end of line
            probs = clean_line.split()[-2:]  # Last two tokens

            try:
                prob_0 = float(probs[0])
                prob_1 = float(probs[1])
                output_val = 1 if prob_1 > prob_0 else 0
            except ValueError:
                i += 1
                continue

            if "default" in line:
                pass
            else:
                paren_part = clean_line.split(")")[0].replace("(", "").strip()
                parent_vals = [
                    val.replace('"', "").strip() for val in paren_part.split()
                ]
                sig = "".join(parent_vals)
                cpts[current_child][sig] = output_val

        i += 1

    return cpts, parents_map


def predict_next_state_learned(
    state_str: str, cpts: Dict, parents_map: Dict, num_vars: int
) -> str:
    next_state_list = []
    for i in range(num_vars):
        var_name = f"x{i + 1}"

        if var_name not in cpts:
            next_state_list.append(state_str[i])
            continue

        parents = parents_map.get(var_name, [])
        parent_vals_list = []
        for p in parents:
            p_idx = int(p.replace("x", "")) - 1
            parent_vals_list.append(state_str[p_idx])

        sig = "".join(parent_vals_list)

        if sig in cpts[var_name]:
            val = cpts[var_name][sig]
        else:
            val = int(state_str[i])

        next_state_list.append(str(val))

    return "".join(next_state_list)


def reconstruct_boolean_function(
    cpt_table: Dict[str, Dict[str, int]], parents: List[str]
) -> str:
    """
    Reconstructs a minimized Boolean function from the CPT using SymPy.
    """
    if not parents:
        if "" in cpt_table:
            prob_1 = cpt_table[""].get("1", 0)
            return "1" if prob_1 > 0.5 else "0"
        return "Unknown"

    sym_parents = symbols(parents)
    minterms = []

    num_parents = len(parents)
    for i in range(2**num_parents):
        bits = [(i >> j) & 1 for j in range(num_parents - 1, -1, -1)]
        key_parts = [str(b) for b in bits]
        key = "".join(key_parts)

        outcome = cpt_table.get(key, 0)
        if outcome == 1:
            minterms.append(bits)

    if not minterms:
        return "0"

    expr = SOPform(sym_parents, minterms)
    return str(expr)
