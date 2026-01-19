def find_attractors(transitions):
    """
    Identyfikuje atraktory (terminalne SCC) w sieci przejść.
    Zwraca listę atraktorów, gdzie każdy atraktor to lista stanów (bitstringów).
    """
    visited_time = {}
    low_link = {}
    stack = []
    on_stack = set()
    sccs = []
    timer = [0]

    # 1. Algorytm Tarjana do znalezienia wszystkich SCC
    def dfs(u):
        visited_time[u] = low_link[u] = timer[0]
        timer[0] += 1
        stack.append(u)
        on_stack.add(u)

        for v in transitions.get(u, []):
            if v not in visited_time:
                dfs(v)
                low_link[u] = min(low_link[u], low_link[v])
            elif v in on_stack:
                low_link[u] = min(low_link[u], visited_time[v])

        if low_link[u] == visited_time[u]:
            component = []
            while True:
                node = stack.pop()
                on_stack.remove(node)
                component.append(node)
                if node == u: break
            sccs.append(component)

    for state in transitions:
        if state not in visited_time:
            dfs(state)

    # 2. Identyfikacja, które SCC są terminalne (atraktory)
    attractors = []
    state_to_scc_id = {state: i for i, comp in enumerate(sccs) for state in comp}

    for i, component in enumerate(sccs):
        is_terminal = True
        for u in component:
            for v in transitions.get(u, []):
                # Jeśli istnieje przejście do stanu poza bieżącym SCC, to nie jest atraktor
                if state_to_scc_id[v] != i:
                    is_terminal = False
                    break
            if not is_terminal: break

        if is_terminal:
            attractors.append(component)

    return attractors