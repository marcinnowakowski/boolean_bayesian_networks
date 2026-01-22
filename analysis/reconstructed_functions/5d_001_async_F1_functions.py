# Reconstructed functions for 5d_001
# Mode: async, Best Metric: F1 (Value: 0.72)
# Source File: 5d_001_async_f1_s100_l500_at1.0_scrBDE.bif

reconstructed_functions = {
    "x1": "x2",
    "x2": "x2",
    "x3": "(x3 & ~x1) | (x3 & ~x4)",
    "x4": "x4",
    "x5": "(x1 & x5) | (x1 & ~x3) | (x5 & ~x3)",
}
