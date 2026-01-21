# Reconstructed functions for 10d_000
# Mode: sync, Best Metric: Transition_Accuracy (Value: 0.01)
# Source File: 10d_000_sync_f5_s10_l10_at0.8_scrMDL.bif

reconstructed_functions = {
    "x1": "(x4 & ~x7) | (~x7 & ~x8) | (x7 & x8 & ~x4)",
    "x2": "(x10 & x7 & ~x8) | (x7 & x8 & ~x10) | (~x10 & ~x7 & ~x8)",
    "x3": "~x1 | ~x5",
    "x4": "~x9",
    "x5": "(x2 & x7) | (x2 & ~x6) | (x7 & ~x6) | (x6 & ~x2 & ~x7)",
    "x6": "(x4 & ~x7) | (x5 & ~x4) | (x7 & ~x4)",
    "x7": "(x2 & x4) | (x4 & ~x7)",
    "x8": "(x1 & ~x2) | (x1 & ~x8) | (x2 & x8 & ~x1)",
    "x9": "x2 | ~x10",
    "x10": "x8 | ~x5",
}
