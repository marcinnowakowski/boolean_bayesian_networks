"""
Simplified functions from: networks/sops/5d_interesting/bn_sop_5d_net_5.py

Dependency Structure:
  x1 depends on: x5
  x2 depends on: x3
  x3 depends on: x1, x2, x4
  x4 depends on: x1
  x5 depends on: x1, x4
"""

network_functions = {
    "x1": "~x5",
    "x2": "x3",
    "x3": "(x1 & x2 & x4)",
    "x4": "~x1",
    "x5": "(x1 & x4)",
}