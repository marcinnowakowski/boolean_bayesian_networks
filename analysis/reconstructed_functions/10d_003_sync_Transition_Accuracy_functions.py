# Reconstructed functions for 10d_003
# Mode: sync, Best Metric: Transition_Accuracy (Value: 0.01)
# Source File: 10d_003_sync_f5_s300_l10_at0.7_scrBDE.bif

reconstructed_functions = {
    "x1": "x9 | (x3 & x5) | (~x3 & ~x5)",
    "x2": "~x6 | (x3 & ~x9) | (x9 & ~x3)",
    "x3": "(x6 & ~x9) | (~x3 & ~x6)",
    "x4": "x3 | x8",
    "x5": "~x5 | (x6 & x9) | (~x6 & ~x9)",
    "x6": "x3 | x6",
    "x7": "~x6",
    "x8": "(x10 & x9 & ~x6) | (~x10 & ~x6 & ~x9)",
    "x9": "x3 | (x6 & x9) | (~x6 & ~x9)",
    "x10": "~x3 | (~x5 & ~x7)",
}
