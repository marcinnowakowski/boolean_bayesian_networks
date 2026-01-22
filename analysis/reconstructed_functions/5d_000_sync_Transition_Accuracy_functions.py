# Reconstructed functions for 5d_000
# Mode: sync, Best Metric: Transition_Accuracy (Value: 1.00)
# Source File: 5d_000_sync_f1_s100_l50_at1.0_scrMDL.bif

reconstructed_functions = {
    "x1": "x5 | ~x4",
    "x2": "x5",
    "x3": "~x1",
    "x4": "(x1 & x3) | (~x3 & ~x5)",
    "x5": "x2",
}
