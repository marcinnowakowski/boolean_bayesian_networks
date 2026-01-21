# Reconstructed functions for 7d_002
# Mode: async, Best Metric: Transition_Accuracy (Value: 0.27)
# Source File: 7d_002_async_f1_s300_l10_at0.8_scrMDL.bif

reconstructed_functions = {
    "x1": "x1 & x3",
    "x2": "(x1 & x2) | (x1 & x3) | (x2 & x3)",
    "x3": "(x3 & x7) | (~x1 & ~x7)",
    "x4": "(x3 & x4) | (x3 & x6) | (x4 & x6)",
    "x5": "(x5 & ~x1) | (x5 & ~x4) | (~x1 & ~x4)",
    "x6": "(x1 & x3) | (x1 & x6) | (x3 & x6)",
    "x7": "x7",
}
