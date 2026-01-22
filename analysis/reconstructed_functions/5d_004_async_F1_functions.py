# Reconstructed functions for 5d_004
# Mode: async, Best Metric: F1 (Value: 0.70)
# Source File: 5d_004_async_f1_s300_l100_at1.0_scrBDE.bif

reconstructed_functions = {
    "x1": "x1 | ~x5",
    "x2": "x2 & x3",
    "x3": "(x2 & x3 & x4) | (x3 & ~x2 & ~x4)",
    "x4": "x4 & ~x1",
    "x5": "x1 & x4 & x5",
}
