"""
Simplified functions from: networks/sops/5d_interesting/bn_sop_5d_net_3.py

Dependency Structure:
  x1 depends on: x2, x4, x5
  x2 depends on: x3, x4, x5
  x3 depends on: x4
  x4 depends on: x3, x5
  x5 depends on: x4
"""

network_functions = {
    "x1": "(x2 & x4 & x5)",
    "x2": "(x3 & x4 & x5)",
    "x3": "x4",
    "x4": "(~x3 & ~x5)",
    "x5": "~x4",
}