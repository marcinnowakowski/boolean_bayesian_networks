# Reconstructed functions for 10d_001
# Mode: sync, Best Metric: F1 (Value: 0.35)
# Source File: 10d_001_sync_f5_s100_l10_at0.9_scrBDE.bif

reconstructed_functions = {
    "x1": "(x2 & x7 & ~x9) | (x9 & ~x2 & ~x7)",
    "x2": "x4 | (x5 & ~x7)",
    "x3": "x4 | x7 | ~x5",
    "x4": "x4",
    "x5": "x5 & ~x4 & ~x7",
    "x6": "x7 & ~x4",
    "x7": "(x4 & ~x7) | (x7 & ~x4)",
    "x8": "~x4",
    "x9": "x10 | (x1 & x5) | (~x1 & ~x5)",
    "x10": "(x10 & x7) | (x1 & ~x7)",
}
