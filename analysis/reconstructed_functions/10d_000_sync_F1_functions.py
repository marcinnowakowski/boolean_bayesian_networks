# Reconstructed functions for 10d_000
# Mode: sync, Best Metric: F1 (Value: 0.47)
# Source File: 10d_000_sync_f5_s300_l500_at1.0_scrBDE.bif

reconstructed_functions = {
    "x1": "(~x3 & ~x7) | (~x7 & ~x8)",
    "x2": "~x3 | (x1 & ~x2) | (x2 & ~x1)",
    "x3": "~x10 | ~x5 | ~x6",
    "x4": "(x3 & ~x7 & ~x9) | (x9 & ~x3 & ~x7)",
    "x5": "x7 | (x2 & ~x6) | (x6 & ~x2)",
    "x6": "(x4 & ~x7) | (x5 & ~x4) | (x7 & ~x4)",
    "x7": "(x2 & x4) | (x2 & ~x7) | (x4 & ~x7)",
    "x8": "(x1 & ~x2) | (x2 & ~x1) | (x2 & ~x8)",
    "x9": "x1 | x2 | x7",
    "x10": "x1 | (x3 & x8)",
}
