# Reconstructed functions for 7d_004
# Mode: async, Best Metric: F1 (Value: 0.90)
# Source File: 7d_004_async_f1_s300_l50_at0.8_scrMDL.bif

reconstructed_functions = {
    "x1": "(x1 & x2) | (x1 & x3) | (x2 & x3) | (~x1 & ~x2 & ~x3)",
    "x2": "x2",
    "x3": "x3",
    "x4": "x4",
    "x5": "(x3 & ~x7) | (x5 & ~x3)",
    "x6": "(x1 & x6) | (x6 & ~x2)",
    "x7": "x7 | (x1 & x5)",
}
