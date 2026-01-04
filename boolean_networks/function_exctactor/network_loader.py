"""
Network loader utilities for loading boolean networks from various sources.
"""

from typing import Dict, List
import os


def load_network_from_file(filepath: str) -> Dict[str, List[str]]:
    """
    Load a boolean network from a Python file containing a transitions dictionary.
    
    Args:
        filepath: Path to the Python file containing the transitions dictionary
        
    Returns:
        Dictionary of transitions
    """
    # Handle relative paths
    if not os.path.isabs(filepath):
        # Look in the networks directory first, then current directory
        networks_dir = os.path.join(os.path.dirname(__file__), '..', 'networks')
        networks_path = os.path.join(networks_dir, filepath)
        if os.path.exists(networks_path):
            filepath = networks_path
    
    # Read and execute the file to get the transitions
    with open(filepath, 'r') as f:
        content = f.read()
    
    # Execute the content in a local namespace
    namespace = {}
    exec(content, namespace)
    
    return namespace.get('transitions', {})


def load_network_from_dict(transitions: Dict[str, List[str]]) -> Dict[str, List[str]]:
    """
    Load a boolean network from a transitions dictionary (identity function for consistency).
    
    Args:
        transitions: Dictionary mapping current states to lists of possible next states
        
    Returns:
        Dictionary of transitions
    """
    return transitions


def validate_network(transitions: Dict[str, List[str]], num_variables: int = None) -> bool:
    """
    Validate that a boolean network is properly formatted.
    
    Args:
        transitions: Dictionary mapping current states to lists of possible next states
        num_variables: Expected number of variables (auto-detected if None)
        
    Returns:
        True if the network is valid, raises ValueError if invalid
    """
    if not transitions:
        raise ValueError("Transitions dictionary cannot be empty")
    
    # Auto-detect number of variables
    if num_variables is None:
        num_variables = len(next(iter(transitions.keys())))
    
    # Check all states have the correct number of variables
    for state in transitions.keys():
        if len(state) != num_variables:
            raise ValueError(f"State {state} has {len(state)} variables, expected {num_variables}")
        
        if not all(bit in '01' for bit in state):
            raise ValueError(f"State {state} contains non-binary characters")
    
    # Check all next states are properly formatted
    for current_state, next_states in transitions.items():
        if not isinstance(next_states, list):
            raise ValueError(f"Next states for {current_state} must be a list")
        
        for next_state in next_states:
            if len(next_state) != num_variables:
                raise ValueError(f"Next state {next_state} has {len(next_state)} variables, expected {num_variables}")
            
            if not all(bit in '01' for bit in next_state):
                raise ValueError(f"Next state {next_state} contains non-binary characters")
    
    return True