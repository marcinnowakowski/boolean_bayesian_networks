# Reconstructed functions for 10d_004
# Mode: sync, Best Metric: Transition_Accuracy (Value: 0.02)
# Source File: 10d_004_sync_f10_s100_l10_at0.9_scrMDL.bif

reconstructed_functions = {
    "x1": "(x10 & x4) | (~x10 & ~x3)",
    "x2": "x10 & x7",
    "x3": "0",
    "x4": "(x2 & x3 & ~x5) | (x3 & x5 & ~x2) | (~x2 & ~x3 & ~x5)",
    "x5": "(x10 & x7) | (~x1 & ~x10)",
    "x6": "(x10 & ~x7) | (x1 & x7 & ~x10)",
    "x7": "(x10 & x4) | (x5 & ~x10) | (~x10 & ~x4)",
    "x8": "True",
    "x9": "(x5 & x9) | (~x3 & ~x9) | (~x5 & ~x9)",
    "x10": "(~x5 & ~x9) | (x5 & x9 & ~x3)",
}
