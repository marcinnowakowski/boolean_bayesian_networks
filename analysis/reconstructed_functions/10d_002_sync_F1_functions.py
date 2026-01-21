# Reconstructed functions for 10d_002
# Mode: sync, Best Metric: F1 (Value: 0.44)
# Source File: 10d_002_sync_f1_s100_l10_at0.5_scrMDL.bif

reconstructed_functions = {
    "x1": "0",
    "x2": "~x9 | (x3 & x7)",
    "x3": "x1 | x10",
    "x4": "x7 & ~x1",
    "x5": "(x3 & ~x9) | (~x6 & ~x9)",
    "x6": "~x4 | (x5 & ~x9) | (x9 & ~x5)",
    "x7": "(x2 & x3 & x6) | (~x2 & ~x3) | (~x2 & ~x6) | (~x3 & ~x6)",
    "x8": "(x3 & ~x8) | (~x2 & ~x8)",
    "x9": "(x3 & x4 & ~x10) | (~x10 & ~x3 & ~x4)",
    "x10": "(x2 & ~x3) | (~x3 & ~x5)",
}
