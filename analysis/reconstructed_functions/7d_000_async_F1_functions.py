# Reconstructed functions for 7d_000
# Mode: async, Best Metric: F1 (Value: 0.83)
# Source File: 7d_000_async_f1_s300_l10_at0.6_scrBDE.bif

reconstructed_functions = {
    "x1": "(x1 & x2 & ~x5) | (x1 & x5 & ~x2)",
    "x2": "(x2 & x5) | (x2 & ~x1)",
    "x3": "x3",
    "x4": "x4",
    "x5": "x5 | (~x1 & ~x7)",
    "x6": "(x6 & ~x4) | (x6 & ~x5) | (x4 & x5 & ~x6)",
    "x7": "(x7 & ~x3) | (x7 & ~x6)",
}
