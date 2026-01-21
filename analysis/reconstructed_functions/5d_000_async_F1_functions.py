# Reconstructed functions for 5d_000
# Mode: async, Best Metric: F1 (Value: 0.80)
# Source File: 5d_000_async_f1_s100_l50_at0.9_scrBDE.bif

reconstructed_functions = {
    "x1": "~x4 | (x1 & x5)",
    "x2": "x2",
    "x3": "~x1",
    "x4": "(x1 & x3) | (~x3 & ~x5)",
    "x5": "x5",
}
