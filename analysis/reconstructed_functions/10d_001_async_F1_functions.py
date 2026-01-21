# Reconstructed functions for 10d_001
# Mode: async, Best Metric: F1 (Value: 0.40)
# Source File: 10d_001_async_f5_s100_l500_at1.0_scrBDE.bif

reconstructed_functions = {
    "x1": "x10 & x8",
    "x2": "x2 | x4 | ~x8",
    "x3": "(x4 & ~x9) | (x9 & ~x4) | (x9 & ~x8)",
    "x4": "x4",
    "x5": "~x3 & ~x9",
    "x6": "x6 & x8",
    "x7": "(x6 & x7) | (x7 & ~x4) | (x4 & ~x6 & ~x7)",
    "x8": "~x4 | (x5 & x8)",
    "x9": "x9",
    "x10": "(x1 & x10 & ~x4) | (x10 & x4 & ~x1)",
}
