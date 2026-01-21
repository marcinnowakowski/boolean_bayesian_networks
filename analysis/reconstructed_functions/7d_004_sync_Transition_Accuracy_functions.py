# Reconstructed functions for 7d_004
# Mode: sync, Best Metric: Transition_Accuracy (Value: 1.00)
# Source File: 7d_004_sync_f1_s100_l10_at0.5_scrMDL.bif

reconstructed_functions = {
    "x1": "(x1 & x2) | (x1 & x3) | (x2 & x3) | (~x1 & ~x2 & ~x3)",
    "x2": "x4 & ~x7",
    "x3": "~x5 | (x3 & ~x6)",
    "x4": "(x2 & x4) | (x4 & ~x1)",
    "x5": "~x7 | (x3 & ~x5) | (x5 & ~x3)",
    "x6": "(x1 & ~x3) | (~x1 & ~x2)",
    "x7": "x1 & x5",
}
