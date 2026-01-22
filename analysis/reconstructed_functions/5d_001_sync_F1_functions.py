# Reconstructed functions for 5d_001
# Mode: sync, Best Metric: F1 (Value: 1.00)
# Source File: 5d_001_sync_f1_s300_l100_at1.0_scrBDE.bif

reconstructed_functions = {
    "x1": "x2",
    "x2": "(x1 & x4) | (x5 & ~x1) | (~x1 & ~x4)",
    "x3": "~x1 | ~x4",
    "x4": "(x1 & x2) | (x1 & ~x3) | (x2 & ~x3) | (x3 & ~x1 & ~x2)",
    "x5": "x1 & ~x3",
}
