# Reconstructed functions for 7d_003
# Mode: sync, Best Metric: F1 (Value: 1.00)
# Source File: 7d_003_sync_f1_s300_l50_at0.9_scrBDE.bif

reconstructed_functions = {
    "x1": "x5 & ~x4",
    "x2": "(x2 & x7) | (x6 & ~x2 & ~x7)",
    "x3": "(x5 & ~x4) | (~x1 & ~x4)",
    "x4": "x5 & ~x6",
    "x5": "(x1 & x5) | (x1 & ~x3) | (x5 & ~x3)",
    "x6": "(x1 & x4) | (x7 & ~x4)",
    "x7": "(x3 & x5) | (x5 & ~x2) | (x2 & ~x3 & ~x5)",
}
