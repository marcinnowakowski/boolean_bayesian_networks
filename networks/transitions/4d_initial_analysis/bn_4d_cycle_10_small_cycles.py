# Directed transitions on the 4D hypercube
# Original 10-cycle:
# 0000→1000→1100→0100→0110→1110→1010→0010→0011→0001→0000
# plus extra edges using the other 6 states

transitions = {
    "0000": ["1000"],              # on 10-cycle
    "0001": ["0000"],              # on 10-cycle
    "0010": ["0011"],              # on 10-cycle
    "0011": ["0001", "0111"],      # on 10-cycle + branch to 0111
    "0100": ["0110"],              # on 10-cycle
    "0101": ["0111"],              # off-cycle, part of 2-cycle and chord
    "0110": ["1110"],              # on 10-cycle
    "0111": ["0101", "1111"],      # 2-cycle with 0101, link to 1111
    "1000": ["1100", "1001"],      # on 10-cycle + branch to 1001
    "1001": ["0001"],              # off-cycle, closes 4-cycle 0000-1000-1001-0001-0000
    "1010": ["0010"],              # on 10-cycle
    "1011": ["1111"],              # off-cycle, link to 1111
    "1100": ["0100", "1101"],      # on 10-cycle + 2-cycle with 1101
    "1101": ["1100"],              # 2-cycle with 1100
    "1110": ["1010", "1111"],      # on 10-cycle + link to 1111
    "1111": ["1011", "1101"],      # 2-cycle with 1011, chord via 1101
}
