# Reconstructed functions for 7d_000
# Mode: async, Best Metric: Transition_Accuracy (Value: 0.16)
# Source File: 7d_000_async_f10_s300_l10_at0.7_scrBDE.bif

reconstructed_functions = {
    "x1": "0",
    "x2": "x5 | ~x1",
    "x3": "x6 | (x4 & ~x5) | (x5 & ~x4)",
    "x4": "x2 & x4 & x5",
    "x5": "x5 | ~x1",
    "x6": "x6 | (x4 & ~x5)",
    "x7": "(x4 & x6 & ~x5) | (x5 & ~x4 & ~x6)",
}
