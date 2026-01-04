# Transitions for a 4D hypercube asynchronous network
# Main 10-cycle:
# 0000→1000→1100→0100→0110→1110→1010→0010→0011→0001→0000
# Plus ONE reverse branch using all 6 remaining states:
# 0100→0101→0111→1111→1011→1001→1101→1100

transitions = {
    # main 10-cycle edges
    "0000": ["1000"],
    "1000": ["1100"],
    "1100": ["0100"],
    "0100": ["0110", "0101"],  # on 10-cycle, plus start of branch
    "0110": ["1110"],
    "1110": ["1010"],
    "1010": ["0010"],
    "0010": ["0011"],
    "0011": ["0001"],
    "0001": ["0000"],

    # branch through the 6 off-cycle states
    "0101": ["0111"],
    "0111": ["1111"],
    "1111": ["1011"],
    "1011": ["1001"],
    "1001": ["1101"],
    "1101": ["1100"],  # rejoin cycle at 1100
}
