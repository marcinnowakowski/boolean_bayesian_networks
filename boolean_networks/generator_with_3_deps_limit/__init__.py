"""
Generator for Boolean networks where each variable depends on at most 3 variables.
"""

from .generator import generate_network, NetworkConfig, analyze_network

__all__ = ['generate_network', 'NetworkConfig', 'analyze_network']
