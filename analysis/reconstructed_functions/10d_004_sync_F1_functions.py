# Reconstructed functions for 10d_004
# Mode: sync, Best Metric: F1 (Value: 0.46)
# Source File: 10d_004_sync_f5_s10_l500_at1.0_scrMDL.bif

reconstructed_functions = {
    "x1": "(x2 & x4 & ~x10) | (x10 & ~x2 & ~x4)",
    "x2": "(x10 & x4 & x9) | (x10 & ~x4 & ~x9) | (x9 & ~x10 & ~x4)",
    "x3": "x6 & ~x7",
    "x4": "(x6 & ~x7) | (x6 & ~x8) | (~x7 & ~x8) | (x7 & x8 & ~x6)",
    "x5": "(x10 & x6) | (~x10 & ~x2)",
    "x6": "(x2 & ~x10) | (x10 & ~x2 & ~x6)",
    "x7": "(x5 & ~x7) | (x7 & ~x5)",
    "x8": "x7 | ~x6",
    "x9": "(x10 & x8 & x9) | (x8 & ~x10 & ~x9)",
    "x10": "(x1 & x3 & x9) | (~x1 & ~x3) | (~x3 & ~x9)",
}
