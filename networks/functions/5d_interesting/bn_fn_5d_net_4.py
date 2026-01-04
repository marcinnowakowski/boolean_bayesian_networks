"""
Simplified functions from: networks/sops/5d_interesting/bn_sop_5d_net_4.py

Dependency Structure:
  x1 depends on: x4
  x2 depends on: (constant)
  x3 depends on: x2
  x4 depends on: x1, x3
  x5 depends on: x1, x3
"""

network_functions = {
    "x1": "~x4",
    "x2": "1",
    "x3": "~x2",
    "x4": "x1 | ~x3",
    "x5": "(x1 & ~x3)",
}