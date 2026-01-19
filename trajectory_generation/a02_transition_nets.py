import itertools


def get_synchronous_sts(compiled_net):
    """
    Tworzy synchroniczną sieć przejść bez pętli zwrotnych.
    Jeśli stan następny jest identyczny z obecnym, lista będzie pusta.
    """
    nodes = sorted(compiled_net.keys())
    n = len(nodes)
    transitions = {}

    for state_tuple in itertools.product([0, 1], repeat=n):
        current_state_str = "".join(map(str, state_tuple))
        env = {nodes[j]: state_tuple[j] for j in range(n)}

        next_bits = []
        for node in nodes:
            val = int(eval(compiled_net[node], {"__builtins__": None}, env))
            next_bits.append(str(val))

        next_state_str = "".join(next_bits)

        # Dodajemy tylko jeśli stan się zmienił
        if next_state_str != current_state_str:
            transitions[current_state_str] = [next_state_str]
        else:
            transitions[current_state_str] = []

    return transitions


def get_asynchronous_sts(compiled_net):
    """
    Tworzy asynchroniczną sieć przejść bez pętli zwrotnych.
    Z każdego stanu wychodzą tylko krawędzie prowadzące do NOWYCH stanów.
    """
    nodes = sorted(compiled_net.keys())
    n = len(nodes)
    transitions = {}

    for state_tuple in itertools.product([0, 1], repeat=n):
        current_state_str = "".join(map(str, state_tuple))
        env = {nodes[j]: state_tuple[j] for j in range(n)}

        reachable_states = set()
        for k in range(n):
            node_to_update = nodes[k]
            new_val = int(eval(compiled_net[node_to_update], {"__builtins__": None}, env))

            # Tworzymy potencjalny nowy stan
            new_state_list = list(state_tuple)
            new_state_list[k] = new_val
            new_state_str = "".join(map(str, new_state_list))

            # Filtracja self-loop: dodajemy tylko jeśli stan jest inny niż obecny
            if new_state_str != current_state_str:
                reachable_states.add(new_state_str)

        transitions[current_state_str] = sorted(list(reachable_states))

    return transitions