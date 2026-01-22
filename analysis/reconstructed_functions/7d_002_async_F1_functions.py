# Reconstructed functions for 7d_002
# Mode: async, Best Metric: F1 (Value: 0.82)
# Source File: 7d_002_async_f1_s100_l10_at0.8_scrBDE.bif

reconstructed_functions = {
    "x1": "x1 & x3",
    "x2": "x1 & x2",
    "x3": "x3 | (~x1 & ~x7)",
    "x4": "(x3 & x4) | (x3 & x6) | (x4 & x6)",
    "x5": "(x5 & ~x1) | (x5 & ~x4) | (~x1 & ~x4)",
    "x6": "(x2 & x3) | (x3 & x6)",
    "x7": "x7",
}
