# Reconstructed functions for 10d_002
# Mode: sync, Best Metric: Transition_Accuracy (Value: 0.01)
# Source File: 10d_002_sync_f5_s100_l10_at0.6_scrMDL.bif

reconstructed_functions = {
    "x1": "Unknown",
    "x2": "x1 | ~x9",
    "x3": "(x1 & ~x10) | (x10 & ~x1)",
    "x4": "(x1 & ~x10) | (~x10 & ~x3)",
    "x5": "(x1 & x3 & x4) | (x1 & ~x3 & ~x4) | (x3 & ~x1 & ~x4)",
    "x6": "(x3 & ~x10) | (x3 & ~x4) | (~x10 & ~x4) | (x10 & x4 & ~x3)",
    "x7": "(x1 & ~x10) | (~x10 & ~x7)",
    "x8": "(x1 & ~x10) | (x10 & x3 & ~x1)",
    "x9": "~x1 & ~x10 & ~x3",
    "x10": "(x4 & ~x1) | (~x1 & ~x3)",
}
