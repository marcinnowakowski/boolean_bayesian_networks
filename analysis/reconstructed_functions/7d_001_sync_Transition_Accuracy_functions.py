# Reconstructed functions for 7d_001
# Mode: sync, Best Metric: Transition_Accuracy (Value: 1.00)
# Source File: 7d_001_sync_f1_s100_l50_at0.9_scrMDL.bif

reconstructed_functions = {
    "x1": "(x2 & x6) | (x7 & ~x2) | (~x2 & ~x6)",
    "x2": "(x6 & ~x2) | (x6 & ~x4) | (~x2 & ~x4) | (x2 & x4 & ~x6)",
    "x3": "x6 | (x2 & ~x7) | (x7 & ~x2)",
    "x4": "~x1 | ~x3",
    "x5": "(x6 & ~x3) | (x6 & ~x5) | (x3 & x5 & ~x6)",
    "x6": "(x2 & x3) | (x1 & ~x3) | (~x1 & ~x2)",
    "x7": "x7 | ~x1",
}
