# Reconstructed functions for 7d_002
# Mode: sync, Best Metric: Transition_Accuracy (Value: 1.00)
# Source File: 7d_002_sync_f1_s300_l500_at1.0_scrMDL.bif

reconstructed_functions = {
    "x1": "x3",
    "x2": "x1",
    "x3": "(x1 & x3 & x7) | (~x1 & ~x3 & ~x7)",
    "x4": "x3 & x6",
    "x5": "(x6 & ~x4) | (~x1 & ~x4)",
    "x6": "x2 & x3",
    "x7": "(x1 & x7) | (x7 & ~x3)",
}
