"""
Functions extracted from: networks/truth_tables/bn_tt_5d_net_2.py

Dependency Structure:
  x1 depends on: x1, x2, x3, x4, x5
  x2 depends on: x1, x2, x3, x4, x5
  x3 depends on: x1, x2, x3, x4, x5
  x4 depends on: x1, x2, x3, x4, x5
  x5 depends on: x1, x3
"""

network_functions = {
    "x1": "(x1 & x2 & x3 & x4 & x5) | (x1 & x2 & x3 & ~x4) | (x1 & x2 & ~x3 & ~x4 & ~x5) | (x2 & x3 & x4 & ~x5) | (x2 & ~x3 & x4) | (x2 & ~x3 & ~x4 & x5) | (~x1 & x2 & x3 & x5) | (~x1 & x2 & ~x4 & ~x5)",
    "x2": "(x1 & x2 & x3 & x4 & x5) | (x1 & x2 & x4 & ~x5) | (x1 & ~x2 & x3 & x4) | (x1 & ~x2 & ~x3 & x4 & ~x5) | (~x1 & x2 & x3 & ~x4) | (~x1 & x2 & ~x3 & ~x4 & x5) | (~x1 & x3 & x4 & x5) | (~x1 & ~x2 & x3 & ~x4 & ~x5) | (~x1 & ~x2 & ~x4 & x5) | (~x1 & ~x3 & ~x4 & ~x5) | (~x3 & x4 & x5)",
    "x3": "(x1 & x2 & ~x3 & ~x4 & ~x5) | (x1 & ~x2 & ~x4 & ~x5) | (x1 & ~x3 & ~x4 & x5) | (x2 & x3 & ~x4) | (~x1 & x2 & x3 & x4 & ~x5) | (~x1 & x2 & ~x3 & x4) | (~x1 & x2 & ~x3 & ~x4 & x5) | (~x1 & x3 & x4 & x5) | (~x1 & ~x2 & x3 & ~x4 & ~x5) | (~x1 & ~x2 & x4 & ~x5) | (~x1 & ~x2 & ~x3 & x5) | (~x1 & ~x3 & ~x4 & ~x5) | (~x2 & x3 & ~x4 & x5)",
    "x4": "(x1 & x2 & x3 & x4 & x5) | (x1 & x2 & x3 & ~x4) | (x1 & x2 & x4 & ~x5) | (x1 & x2 & ~x3 & x5) | (x1 & x2 & ~x3 & ~x4 & ~x5) | (x1 & ~x2 & ~x3) | (~x1 & x2 & ~x3) | (~x1 & ~x2 & x3)",
    "x5": "(x1 & ~x3)",
}