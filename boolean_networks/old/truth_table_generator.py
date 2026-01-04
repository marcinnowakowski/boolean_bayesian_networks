"""
Utility to create truth tables for asynchronous boolean network transitions using NetworkX.

This module provides functions to:
1. Convert boolean network transitions to NetworkX directed graphs
2. Generate comprehensive truth tables showing all possible state transitions
3. Analyze network properties like cycles, attractors, and reachability
4. Export truth tables in various formats
"""

import networkx as nx
import pandas as pd
import itertools
from typing import Dict, List, Set, Tuple, Optional
from collections import defaultdict

from .visualizer import BooleanNetworkVisualizer


class BooleanNetworkTruthTable:
    """
    A class to generate and analyze truth tables for asynchronous boolean networks.
    """
    
    def __init__(self, transitions: Dict[str, List[str]], num_variables: int = None):
        """
        Initialize the truth table generator.
        
        Args:
            transitions: Dictionary mapping current states to lists of possible next states
            num_variables: Number of boolean variables (auto-detected if None)
        """
        self.transitions = transitions
        self.num_variables = num_variables or len(next(iter(transitions.keys())))
        self.graph = self._create_graph()
        self.all_states = self._generate_all_states()
        self.visualizer = BooleanNetworkVisualizer(self.graph, self.transitions, self.num_variables, self.all_states)
        
    def _create_graph(self) -> nx.DiGraph:
        """Create a NetworkX directed graph from the transitions."""
        G = nx.DiGraph()
        
        # Add all transition edges
        for current_state, next_states in self.transitions.items():
            for next_state in next_states:
                G.add_edge(current_state, next_state)
                
        return G
    
    def _generate_all_states(self) -> List[str]:
        """Generate all possible boolean states for the given number of variables."""
        return [''.join(state) for state in itertools.product('01', repeat=self.num_variables)]
    
    def _state_to_tuple(self, state: str) -> Tuple[int, ...]:
        """Convert string state to tuple of integers."""
        return tuple(int(bit) for bit in state)
    
    def _tuple_to_state(self, state_tuple: Tuple[int, ...]) -> str:
        """Convert tuple of integers to string state."""
        return ''.join(str(bit) for bit in state_tuple)
    
    def generate_truth_table(self) -> pd.DataFrame:
        """
        Generate a comprehensive truth table for the boolean network.
        
        Returns:
            DataFrame with columns for current state variables, possible next states,
            transition probabilities (if multiple next states), and network properties.
        """
        rows = []
        
        for state in self.all_states:
            state_tuple = self._state_to_tuple(state)
            next_states = self.transitions.get(state, [])
            
            if not next_states:
                # Fixed point or undefined transition
                rows.append({
                    **{f'x{i}': bit for i, bit in enumerate(state_tuple)},
                    'current_state': state,
                    'next_states': '',
                    'num_transitions': 0,
                    'is_fixed_point': True,
                    'is_defined': False
                })
            else:
                # Probability of each transition (uniform for asynchronous networks)
                prob = 1.0 / len(next_states) if len(next_states) > 1 else 1.0
                
                for next_state in next_states:
                    next_tuple = self._state_to_tuple(next_state)
                    rows.append({
                        **{f'x{i}': bit for i, bit in enumerate(state_tuple)},
                        'current_state': state,
                        'next_state': next_state,
                        **{f'next_x{i}': bit for i, bit in enumerate(next_tuple)},
                        'transition_prob': prob,
                        'num_transitions': len(next_states),
                        'is_fixed_point': state == next_state,
                        'is_defined': True,
                        'hamming_distance': sum(a != b for a, b in zip(state_tuple, next_tuple))
                    })
        
        return pd.DataFrame(rows)
    
    def generate_state_transition_matrix(self) -> pd.DataFrame:
        """
        Generate a state transition matrix showing transitions between all states.
        
        Returns:
            DataFrame with states as both rows and columns, showing transition probabilities.
        """
        matrix = pd.DataFrame(0.0, index=self.all_states, columns=self.all_states)
        
        for current_state, next_states in self.transitions.items():
            if next_states:
                prob = 1.0 / len(next_states)
                for next_state in next_states:
                    matrix.loc[current_state, next_state] = prob
        
        return matrix
    
    def find_attractors(self) -> Dict[str, List[str]]:
        """
        Find all attractors in the network (fixed points and limit cycles).
        
        Returns:
            Dictionary with attractor types as keys and lists of states as values.
        """
        attractors = {'fixed_points': [], 'cycles': []}
        
        # Find strongly connected components
        sccs = list(nx.strongly_connected_components(self.graph))
        
        for scc in sccs:
            if len(scc) == 1:
                state = list(scc)[0]
                # Check if it's a true fixed point
                if state in self.transitions and state in self.transitions[state]:
                    attractors['fixed_points'].append(state)
            else:
                # Multi-state attractor (cycle)
                cycle_states = list(scc)
                # Verify it's actually a cycle by checking if there's a path through all states
                subgraph = self.graph.subgraph(scc)
                if nx.is_strongly_connected(subgraph):
                    attractors['cycles'].append(sorted(cycle_states))
        
        return attractors
    
    def analyze_reachability(self) -> Dict[str, Set[str]]:
        """
        Analyze which states are reachable from each starting state.
        
        Returns:
            Dictionary mapping each state to the set of reachable states.
        """
        reachability = {}
        
        for state in self.all_states:
            if state in self.graph:
                reachable = set(nx.descendants(self.graph, state))
                reachable.add(state)  # Include the state itself
                reachability[state] = reachable
            else:
                reachability[state] = {state}  # Only itself if no outgoing transitions
        
        return reachability
    
    def get_basins_of_attraction(self) -> Dict[str, Set[str]]:
        """
        Find basins of attraction for each attractor.
        
        Returns:
            Dictionary mapping attractor representatives to their basins.
        """
        attractors = self.find_attractors()
        basins = {}
        reachability = self.analyze_reachability()
        
        # For fixed points
        for fixed_point in attractors['fixed_points']:
            basin = set()
            for state in self.all_states:
                if fixed_point in reachability.get(state, set()):
                    basin.add(state)
            basins[fixed_point] = basin
        
        # For cycles, use the lexicographically smallest state as representative
        for cycle in attractors['cycles']:
            cycle_repr = min(cycle)
            basin = set()
            for state in self.all_states:
                if any(cycle_state in reachability.get(state, set()) for cycle_state in cycle):
                    basin.add(state)
            basins[cycle_repr] = basin
        
        return basins
    
    def export_truth_table(self, filename: str, format: str = 'csv'):
        """
        Export the truth table to a file.
        
        Args:
            filename: Output filename
            format: Export format ('csv', 'excel', 'json')
        """
        truth_table = self.generate_truth_table()
        
        if format.lower() == 'csv':
            truth_table.to_csv(filename, index=False)
        elif format.lower() == 'excel':
            truth_table.to_excel(filename, index=False)
        elif format.lower() == 'json':
            truth_table.to_json(filename, orient='records', indent=2)
        else:
            raise ValueError(f"Unsupported format: {format}")
    
    def visualize_network(self, filename: str = None, layout: str = 'spring'):
        """
        Visualize the network using NetworkX and matplotlib.
        
        Args:
            filename: Optional filename to save the plot
            layout: Layout algorithm ('spring', 'circular', 'shell', etc.)
        """
        self.visualizer.visualize_network(filename, layout)
    
    def visualize_hypercube_4d(self, filename: str = None, projection: str = 'stereographic'):
        """
        Visualize the 4D hypercube network with states positioned according to hypercube geometry.
        
        Args:
            filename: Optional filename to save the plot
            projection: Projection method ('stereographic', 'orthographic', 'grid')
        """
        self.visualizer.visualize_hypercube_4d(filename, projection)
    
    def visualize_hypercube_3d(self, filename: str = None, cube_separation: float = 2.0):
        """
        Visualize the 4D hypercube network as two connected 3D cubes in 3D space.
        The 4th dimension determines which cube (w=0 or w=1).
        
        Args:
            filename: Optional filename to save the plot
            cube_separation: Distance between the two 3D cubes along z-axis
        """
        self.visualizer.visualize_hypercube_3d(filename, cube_separation)
    
    def print_summary(self):
        """Print a summary of the network properties."""
        attractors = self.find_attractors()
        basins = self.get_basins_of_attraction()
        
        print("=== Boolean Network Summary ===")
        print(f"Number of variables: {self.num_variables}")
        print(f"Total possible states: {2**self.num_variables}")
        print(f"Defined transitions: {len(self.transitions)}")
        print(f"Total edges: {self.graph.number_of_edges()}")
        
        print(f"\nFixed points: {len(attractors['fixed_points'])}")
        for fp in attractors['fixed_points']:
            basin_size = len(basins.get(fp, set()))
            print(f"  {fp} (basin size: {basin_size})")
        
        print(f"\nLimit cycles: {len(attractors['cycles'])}")
        for i, cycle in enumerate(attractors['cycles']):
            cycle_repr = min(cycle)
            basin_size = len(basins.get(cycle_repr, set()))
            print(f"  Cycle {i+1}: {' → '.join(cycle + [cycle[0]])} (basin size: {basin_size})")