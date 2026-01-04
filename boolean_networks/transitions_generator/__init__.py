"""
Transition Generator Package

Tools for generating boolean network transitions with specific structural properties.
"""

from .generator import generate_network, NetworkConfig

__all__ = [
    "generate_network",
    "NetworkConfig",
]
