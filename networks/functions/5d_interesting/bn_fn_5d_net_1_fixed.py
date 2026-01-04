"""
Dependency Structure:
  x1 depends on: x4, x5
  x2 depends on: x5
  x3 depends on: x1
  x4 depends on: x1, x3, x5
  x5 depends on: x2
"""

network_functions = {
    "x1": "~x4 | x5",
    "x2": "x5",
    "x3": "~x1",
    "x4": "(~x3 & ~x5) | (x1 & x3) | (x1 & x3 & x5)",
    "x5": "x2",
}
