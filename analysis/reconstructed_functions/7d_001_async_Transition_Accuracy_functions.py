# Reconstructed functions for 7d_001
# Mode: async, Best Metric: Transition_Accuracy (Value: 0.20)
# Source File: 7d_001_async_f5_s300_l10_at0.6_scrMDL.bif

reconstructed_functions = {
    "x1": "x1 | x6 | ~x2",
    "x2": "x7 | (x6 & ~x4)",
    "x3": "x3 | x6 | ~x2",
    "x4": "~x1 | ~x3",
    "x5": "(x4 & x5 & x6) | (x5 & ~x4 & ~x6) | (x6 & ~x4 & ~x5)",
    "x6": "x6 | ~x4 | ~x7",
    "x7": "x7 | ~x1",
}
