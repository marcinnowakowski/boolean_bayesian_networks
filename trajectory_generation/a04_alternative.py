import random


def generate_trajectory_pool(transitions, attractors, sampling_freq, length, pool_size):
    """
    Generuje dużą liczbę trajektorii i zwraca je wraz z ich rzeczywistym attr_ratio.
    Zwraca listę krotek: [(trajektoria, ratio), ...]
    """
    attr_states = {s for a in attractors for s in a}
    raw_length_needed = (length - 1) * sampling_freq + 1
    pool = []

    print(f"--- Generowanie puli {pool_size} trajektorii (len={length}, freq={sampling_freq}) ---")

    for _ in range(pool_size):
        current_state = random.choice(list(transitions.keys()))
        raw_path = [current_state]

        # Symulacja
        for _ in range(raw_length_needed - 1):
            next_options = transitions.get(current_state, [])
            next_state = random.choice(next_options) if next_options else current_state
            raw_path.append(next_state)
            current_state = next_state

        sampled_path = raw_path[::sampling_freq]

        # Obliczanie ratio
        attr_count = sum(1 for s in sampled_path if s in attr_states)
        actual_ratio = round(float(attr_count) / len(sampled_path), 4)

        pool.append((sampled_path, actual_ratio))

    return pool

def _format_to_bnf_file(trajectories, nodes, filename):
    """Pomocniczy format zapisujący dane zgodnie z manualem BNFinder2 [cite: 239, 288]"""
    with open(filename, 'w') as f:
        for node in nodes:
            f.write("#discrete {} 0 1\n".format(node))  #

        # Specyfikacja eksperymentu S<id>:<czas> [cite: 288]
        exp_specs = []
        for s_idx, traj in enumerate(trajectories):
            for t_idx in range(len(traj)):
                exp_specs.append("S{}:{}".format(s_idx, t_idx))

        f.write("BNProject {}\n".format(" ".join(exp_specs)))

        # Dane dla każdego węzła [cite: 292]
        for node in nodes:
            vals = []
            for traj in trajectories:
                for state in traj:
                    vals.append(str(state[node]))
            f.write("{} {}\n".format(node, " ".join(vals)))

def save_bnf_from_pool(pool, nodes, target_ratio, epsilon, size, filename):
    """
    Wybiera trajektorie z puli pasujące do target_ratio i zapisuje je do pliku.
    """
    # Filtrowanie puli wg warunku: |actual - target| <= epsilon
    matching_trajectories = [
        traj for traj, ratio in pool
        if abs(ratio - target_ratio) <= epsilon
    ]

    if len(matching_trajectories) < size:
        print(f"    - Brak danych dla {filename} (Znaleziono {len(matching_trajectories)}/{size} pasujących)")
        return False

    # Losujemy 'size' trajektorii z tych, które pasują
    selected_trajs = random.sample(matching_trajectories, size)

    # Konwersja na format słownikowy (taki jak wcześniej)
    final_data = []
    for path in selected_trajs:
        traj_as_dicts = []
        for state_str in path:
            state_dict = {nodes[i]: int(state_str[i]) for i in range(len(nodes))}
            traj_as_dicts.append(state_dict)
        final_data.append(traj_as_dicts)

    _format_to_bnf_file(final_data, nodes, filename)
    print(f"    + Utworzono plik: {filename} (z puli {len(matching_trajectories)} dostępnych)")
    return True