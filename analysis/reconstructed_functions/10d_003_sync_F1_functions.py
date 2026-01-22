# Reconstructed functions for 10d_003
# Mode: sync, Best Metric: F1 (Value: 0.44)
# Source File: 10d_003_sync_f10_s100_l10_at1.0_scrMDL.bif

reconstructed_functions = {
    "x1": "~x2 | ~x7",
    "x2": "(x1 & x10) | (x1 & x2) | (~x1 & ~x10 & ~x2)",
    "x3": "(x3 & ~x9) | (x4 & ~x9)",
    "x4": "(x5 & ~x1) | (x5 & ~x6) | (x1 & x6 & ~x5)",
    "x5": "(x1 & x6) | (x1 & ~x8) | (x8 & ~x1 & ~x6)",
    "x6": "x10 & x2",
    "x7": "(x5 & x7) | (x7 & ~x2) | (x2 & ~x5 & ~x7)",
    "x8": "~x6",
    "x9": "(x3 & ~x9) | (x7 & ~x3) | (x9 & ~x3)",
    "x10": "(x1 & x4 & x7) | (~x4 & ~x7)",
}
