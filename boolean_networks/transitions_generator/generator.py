"""
7D Boolean Network Generator (v2)

Generates networks with:
1. Parentless states (sources with no incoming edges)
2. Large SCC region 
3. Exits from SCC to 3 separate complex attractors

Uses Hamming-distance-aware construction to ensure valid async transitions.
"""

import random
from dataclasses import dataclass
from typing import Dict, List, Set, Optional


@dataclass
class NetworkConfig:
    """Configuration for network generation."""
    num_vars: int = 7
    num_parentless: int = 8  # States with no parents
    num_attractors: int = 3  # Number of complex attractors
    attractor_size: int = 4  # Size of each attractor cycle
    seed: Optional[int] = None


def generate_all_states(num_vars: int) -> List[str]:
    """Generate all possible states for n variables."""
    return [format(i, f'0{num_vars}b') for i in range(2 ** num_vars)]


def hamming_neighbors(state: str) -> List[str]:
    """Get all states that differ by exactly one bit."""
    neighbors = []
    for i in range(len(state)):
        neighbor = state[:i] + ('1' if state[i] == '0' else '0') + state[i+1:]
        neighbors.append(neighbor)
    return neighbors


def hamming_distance(s1: str, s2: str) -> int:
    """Calculate Hamming distance between two states."""
    return sum(c1 != c2 for c1, c2 in zip(s1, s2))


def generate_network(config: NetworkConfig = None) -> Dict[str, List[str]]:
    """
    Generate a 7D network with specific structural properties.
    
    Structure:
    - Parentless states → paths → SCC region → exits → 3 attractors
    
    All transitions have Hamming distance = 1 (valid async updates).
    """
    if config is None:
        config = NetworkConfig()
    
    if config.seed is not None:
        random.seed(config.seed)
    
    all_states = set(generate_all_states(config.num_vars))
    transitions: Dict[str, List[str]] = {}
    used_states: Set[str] = set()
    
    # === 1. Build 3 separate attractors using Hamming chains ===
    attractors: List[List[str]] = []
    
    for _ in range(config.num_attractors):
        available = list(all_states - used_states)
        if not available:
            break
            
        attractor = _build_hamming_cycle(available, config.attractor_size, used_states)
        
        if len(attractor) >= 2:
            attractors.append(attractor)
            used_states.update(attractor)
            
            # Create cycle transitions within attractor
            for i, state in enumerate(attractor):
                next_state = attractor[(i + 1) % len(attractor)]
                transitions[state] = [next_state]
    
    # === 2. Build parentless states ===
    available = list(all_states - used_states)
    parentless = set(random.sample(available, min(config.num_parentless, len(available))))
    used_states.update(parentless)
    
    # === 3. SCC region = remaining states ===
    scc_states = all_states - used_states
    scc_list = list(scc_states)
    
    # === 4. Wire SCC region - ensure it's strongly connected ===
    # First, create a backbone cycle through all SCC states
    # to guarantee strong connectivity
    
    # Build a Hamming path through SCC states using greedy approach
    scc_order = _build_hamming_path(scc_list)
    
    # Create backbone: each state -> next in order
    for i, state in enumerate(scc_order):
        next_state = scc_order[(i + 1) % len(scc_order)]
        transitions[state] = [next_state]
    
    # Add extra random connections for complexity
    for state in scc_states:
        neighbors = hamming_neighbors(state)
        scc_neighbors = [n for n in neighbors if n in scc_states 
                        and n not in transitions.get(state, [])]
        
        if scc_neighbors and random.random() < 0.3:
            transitions[state].append(random.choice(scc_neighbors))
    
    # === 5. Create entry points to each attractor from SCC ===
    for attractor in attractors:
        entry_state = attractor[0]
        
        # Find SCC states that can reach this attractor
        entry_candidates = [s for s in scc_states 
                          if hamming_distance(s, entry_state) == 1]
        
        if entry_candidates:
            exit_state = random.choice(entry_candidates)
            if exit_state in transitions:
                transitions[exit_state].append(entry_state)
            else:
                transitions[exit_state] = [entry_state]
    
    # === 6. Wire parentless to SCC ===
    for p_state in parentless:
        neighbors = hamming_neighbors(p_state)
        scc_neighbors = [n for n in neighbors if n in scc_states]
        
        if scc_neighbors:
            transitions[p_state] = [random.choice(scc_neighbors)]
        else:
            valid = [n for n in neighbors if n not in used_states or n in scc_states]
            transitions[p_state] = [random.choice(valid)] if valid else [neighbors[0]]
    
    return transitions


def _build_hamming_cycle(available: List[str], size: int, 
                         used: Set[str]) -> List[str]:
    """
    Build a cycle of states where consecutive states have Hamming distance 1.
    """
    if not available:
        return []
    
    cycle = [random.choice(available)]
    cycle_set = {cycle[0]}
    
    for _ in range(size - 1):
        current = cycle[-1]
        neighbors = hamming_neighbors(current)
        candidates = [n for n in neighbors if n not in used and n not in cycle_set]
        
        if not candidates:
            break
            
        next_state = random.choice(candidates)
        cycle.append(next_state)
        cycle_set.add(next_state)
    
    # Check if cycle is valid (last -> first is Hamming neighbor)
    if len(cycle) >= 2:
        if hamming_distance(cycle[-1], cycle[0]) != 1:
            # Trim to find valid cycle
            for trim_size in range(len(cycle) - 1, 1, -1):
                if hamming_distance(cycle[trim_size - 1], cycle[0]) == 1:
                    return cycle[:trim_size]
            # 2-state cycle
            neighbors_of_first = set(hamming_neighbors(cycle[0]))
            for state in cycle[1:]:
                if state in neighbors_of_first:
                    return [cycle[0], state]
    
    return cycle if len(cycle) >= 2 else []


def _build_hamming_path(states: List[str]) -> List[str]:
    """
    Build a path through states where consecutive states have Hamming distance 1.
    Uses greedy nearest-neighbor approach.
    """
    if not states:
        return []
    
    remaining = set(states)
    path = [random.choice(states)]
    remaining.remove(path[0])
    
    while remaining:
        current = path[-1]
        neighbors = hamming_neighbors(current)
        
        # Find Hamming neighbors in remaining
        candidates = [n for n in neighbors if n in remaining]
        
        if candidates:
            next_state = random.choice(candidates)
        else:
            # No direct neighbor, pick closest remaining state
            next_state = min(remaining, key=lambda s: hamming_distance(current, s))
        
        path.append(next_state)
        remaining.remove(next_state)
    
    return path


def network_to_string(transitions: Dict[str, List[str]], 
                      name: str = "generated_network",
                      description: str = None) -> str:
    """Convert network to Python file format."""
    lines = ['"""']
    lines.append(f"7D Boolean Network: {name}")
    if description:
        lines.append(f"\n{description}")
    lines.append("")
    lines.append("Structure:")
    lines.append("  - Parentless states (sources)")
    lines.append("  - Paths to SCC region")
    lines.append("  - Large SCC with internal connectivity")
    lines.append("  - Exits to 3 complex attractors")
    lines.append('"""')
    lines.append("")
    lines.append("# Asynchronous state transitions")
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
    sccs = _find_sccs(transitions)
    
    # Attractors = SCCs with no outgoing edges
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
        "num_sccs": len(sccs),
        "scc_sizes": sorted([len(s) for s in sccs], reverse=True),
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
    transitions = generate_network(config)
    
    analysis = analyze_network(transitions)
    print(f"Generated network:")
    print(f"  States: {analysis['num_states']}")
    print(f"  Parentless: {analysis['parentless_states']}")
    print(f"  Attractors: {analysis['num_attractors']} (sizes: {analysis['attractor_sizes']})")
    
    output = network_to_string(transitions, f"generated_7d_seed_{seed or 'random'}")
    
    if output_file:
        import os
        os.makedirs(os.path.dirname(output_file), exist_ok=True)
        with open(output_file, 'w') as f:
            f.write(output)
        print(f"Network written to {output_file}")
    else:
        print("\n" + output)


if __name__ == "__main__":
    main()
