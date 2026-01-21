# Reconstructed functions for 7d_003
# Mode: async, Best Metric: Transition_Accuracy (Value: 0.17)
# Source File: 7d_003_async_f5_s300_l10_at0.7_scrMDL.bif

reconstructed_functions = {
    "x1": "(x5 & x6) | (x1 & ~x5 & ~x6)",
    "x2": "x2 & x7",
    "x3": "(x5 & x6) | (~x1 & ~x5)",
    "x4": "x5 & ~x6",
    "x5": "x1 | (x5 & ~x3)",
    "x6": "x1",
    "x7": "x5",
}
