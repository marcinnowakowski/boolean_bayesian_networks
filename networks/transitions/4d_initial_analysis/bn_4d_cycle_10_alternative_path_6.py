# Transitions for a 4D hypercube asynchronous network
# Main 10-cycle:
# 0000→1000→1100→0100→0110→1110→1010→0010→0011→0001→0000
# Plus ONE branch / alternative path using all 6 remaining states:
# 1100→1101→1001→1011→1111→0111→0101→0001

transitions = {
    # main 10-cycle edges
    "0000": ["1000"],
    "1000": ["1100"],
    "1100": ["0100", "1101"], # on 10-cycle, plus start of aternative path
    "0100": ["0110"],  
    "0110": ["1110"],
    "1110": ["1010"],
    "1010": ["0010"],
    "0010": ["0011"],
    "0011": ["0001"],
    "0001": ["0000"],

    # branch through the 6 off-cycle states
    "1101": ["1001"],  
    "1001": ["1011"],
    "1011": ["1111"],
    "1111": ["0111"],
    "0111": ["0101"],
    "0101": ["0001"], # rejoin cycle at 0001
}
