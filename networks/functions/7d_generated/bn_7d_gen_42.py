"""
Simplified functions from: networks/sops/7d_generated/bn_7d_gen_42.py

Dependency Structure:
  x1 depends on: x1, x2, x3, x4, x5, x6, x7
  x2 depends on: x1, x2, x3, x4, x5, x6, x7
  x3 depends on: x1, x2, x3, x4, x5, x6, x7
  x4 depends on: x1, x2, x3, x4, x5, x6, x7
  x5 depends on: x1, x2, x3, x4, x5, x6, x7
  x6 depends on: x1, x2, x3, x4, x5, x6, x7
  x7 depends on: x1, x2, x3, x4, x5, x6, x7
"""

network_functions = {
    "x1": "(x1 & x2 & x4 & ~x6 & ~x7) | (x1 & x2 & ~x3 & x4) | (x1 & x3 & ~x4 & x5 & x6) | (x1 & x3 & ~x4 & ~x5 & ~x6) | (x1 & x4 & ~x5 & x6 & ~x7) | (x1 & x5 & x7) | (x1 & ~x2 & x3 & x4 & x5) | (x1 & ~x2 & ~x4 & x7) | (x1 & ~x2 & ~x6 & x7) | (x1 & ~x3 & x4 & ~x5) | (x1 & ~x3 & x7) | (x1 & ~x3 & ~x4 & x5 & ~x6) | (x1 & ~x3 & ~x5 & x6) | (x2 & ~x3 & x4 & x5 & x6 & x7) | (x2 & ~x3 & ~x4 & ~x5 & ~x6 & ~x7) | (~x1 & x3 & x4 & ~x5 & ~x6 & ~x7) | (~x1 & ~x2 & x3 & x5 & ~x6) | (~x1 & ~x2 & x3 & ~x4 & ~x5 & x6 & ~x7) | (~x2 & x4 & x5 & x6 & ~x7)",
    "x2": "(x1 & x2 & x3 & ~x4 & ~x6) | (x1 & x2 & x3 & ~x5) | (x1 & x2 & x7) | (x1 & x3 & x4 & x5 & x6) | (x1 & x4 & x5 & x6 & x7) | (x1 & ~x3 & ~x4 & ~x5 & x7) | (x2 & x3 & x4 & ~x5 & x7) | (x2 & x3 & x4 & ~x5 & ~x6) | (x2 & x4 & x5 & x6 & ~x7) | (x2 & ~x3 & x5 & x6) | (x2 & ~x4 & ~x5 & ~x7) | (~x1 & x2 & ~x3 & ~x6) | (~x1 & x2 & ~x3 & ~x7) | (~x1 & x2 & ~x4 & x5) | (~x1 & x3 & x4 & ~x5 & ~x6 & x7) | (~x1 & ~x2 & x4 & x5 & ~x6 & ~x7) | (~x1 & ~x3 & ~x4 & ~x6 & ~x7) | (~x2 & x3 & x4 & x5 & ~x6 & ~x7) | (~x2 & x3 & ~x4 & x5 & x6 & ~x7) | (~x3 & x4 & x5 & ~x6 & x7)",
    "x3": "(x1 & x2 & ~x4 & x5 & ~x6 & x7) | (x1 & x4 & ~x5 & ~x6 & x7) | (x1 & ~x2 & x4 & x5 & x6) | (x1 & ~x2 & x4 & x6 & x7) | (x2 & x3 & x4 & x5) | (x2 & x3 & x6) | (x2 & x3 & ~x4 & ~x5) | (x3 & x5 & ~x7) | (x3 & ~x4 & ~x5 & x6) | (x3 & ~x5 & x6 & x7) | (~x1 & x2 & ~x4 & ~x5 & ~x6 & x7) | (~x1 & x4 & ~x5 & ~x6 & ~x7) | (~x1 & ~x2 & x3 & x5) | (~x1 & ~x2 & x4 & ~x5 & ~x7) | (~x1 & ~x2 & ~x4 & x5 & ~x6 & x7) | (~x2 & x3 & x4 & ~x5 & ~x6) | (~x2 & x4 & x5 & x6 & x7)",
    "x4": "(x1 & x2 & x3 & x5 & ~x6 & x7) | (x1 & x2 & ~x3 & x4) | (x1 & x2 & ~x3 & ~x5 & ~x6 & x7) | (x1 & x4 & x5 & ~x6) | (x1 & ~x2 & x3 & x4 & x5) | (x1 & ~x2 & x3 & ~x4 & ~x5 & x6 & ~x7) | (x1 & ~x2 & ~x3 & x5 & x6 & x7) | (x2 & x4 & ~x6 & ~x7) | (x2 & ~x3 & ~x5 & x6 & ~x7) | (x3 & x4 & x5 & x6 & ~x7) | (x4 & x5 & ~x6 & x7) | (x4 & ~x5 & x6 & x7) | (~x1 & x2 & x3 & x4) | (~x1 & x2 & x3 & x5 & ~x7) | (~x1 & x3 & x4 & ~x5) | (~x1 & ~x2 & x3 & x5 & x6 & x7) | (~x1 & ~x2 & ~x3 & x5 & x6 & ~x7) | (~x1 & ~x2 & ~x3 & ~x5 & ~x6 & x7) | (~x2 & ~x3 & x4 & ~x5) | (~x3 & x4 & x6 & x7)",
    "x5": "(x1 & x2 & x3 & ~x4 & ~x5 & ~x7) | (x1 & x2 & ~x3 & ~x4 & x5) | (x1 & x2 & ~x3 & ~x6 & ~x7) | (x1 & x2 & ~x4 & ~x5 & x6 & x7) | (x1 & x3 & x5 & ~x6 & x7) | (x1 & x4 & x5 & ~x6) | (x2 & ~x3 & x4 & x6 & ~x7) | (x2 & ~x4 & x5 & ~x6 & x7) | (x3 & x4 & x5 & x6 & x7) | (x3 & ~x4 & x5 & x6 & ~x7) | (~x1 & x3 & x5 & ~x6 & ~x7) | (~x1 & ~x2 & x3 & x4 & ~x6 & x7) | (~x1 & ~x2 & x3 & ~x4 & x6 & ~x7) | (~x1 & ~x2 & x5) | (~x1 & ~x2 & ~x3 & x6 & x7) | (~x1 & ~x3 & x5 & ~x6 & x7) | (~x2 & x5 & ~x7) | (~x2 & ~x3 & x5 & x6)",
    "x6": "(x1 & x2 & ~x3 & x4 & x5 & x7) | (x1 & ~x2 & x5 & x6) | (x1 & ~x2 & x6 & x7) | (x1 & ~x2 & ~x3 & ~x4 & ~x5) | (x1 & ~x4 & x6 & ~x7) | (x2 & x3 & x4 & x5 & x6) | (x2 & x3 & x6 & x7) | (x2 & ~x3 & ~x5 & x6) | (x4 & x5 & x6 & x7) | (~x1 & x2 & x3 & ~x4 & ~x5 & ~x6 & ~x7) | (~x1 & x2 & ~x3 & x6) | (~x1 & x2 & ~x3 & ~x4 & x5 & x7) | (~x1 & x4 & ~x5 & x6 & ~x7) | (~x1 & ~x3 & x4 & x6) | (~x2 & x3 & ~x4 & x6) | (~x2 & x3 & ~x5 & x6 & ~x7) | (~x2 & ~x3 & ~x4 & x5 & ~x6 & x7) | (~x3 & ~x5 & x6 & x7)",
    "x7": "(x1 & x4 & x5 & x7) | (x1 & x5 & ~x6 & x7) | (x1 & ~x2 & x7) | (x1 & ~x2 & ~x3 & x4 & ~x5) | (x1 & ~x2 & ~x3 & ~x4 & x6) | (x1 & ~x2 & ~x4 & x5 & x6) | (x1 & ~x3 & ~x4 & x5 & x6 & ~x7) | (x2 & x3 & x6 & x7) | (x2 & ~x4 & ~x5 & x6 & x7) | (x3 & x4 & ~x5 & x7) | (x3 & ~x4 & x5 & x7) | (~x1 & x2 & x3 & x4 & ~x6) | (~x1 & x2 & x4 & x7) | (~x1 & x2 & ~x3 & x4 & x5) | (~x1 & x2 & ~x3 & x5 & ~x6 & ~x7) | (~x1 & x3 & ~x6 & x7) | (~x1 & ~x3 & x6 & x7) | (~x2 & ~x3 & x5 & x7) | (~x2 & ~x3 & ~x4 & x7)",
}