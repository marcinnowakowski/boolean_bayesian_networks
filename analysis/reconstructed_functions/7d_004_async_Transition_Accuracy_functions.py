# Reconstructed functions for 7d_004
# Mode: async, Best Metric: Transition_Accuracy (Value: 0.23)
# Source File: 7d_004_async_f1_s100_l10_at0.8_scrBDE.bif

reconstructed_functions = {
    "x1": "(x1 & x2) | (x1 & x3) | (~x1 & ~x2 & ~x3)",
    "x2": "(x2 & ~x1) | (x4 & ~x1)",
    "x3": "(x3 & ~x5) | (x3 & ~x6)",
    "x4": "x4 & ~x1",
    "x5": "~x7 | (x5 & ~x3)",
    "x6": "(x3 & ~x1) | (x6 & ~x3)",
    "x7": "x7 | (x1 & x5)",
}
