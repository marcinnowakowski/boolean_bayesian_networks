import random
import os


def create_trajectory_file(transitions, attractors, nodes, sampling_freq, size, length, attr_ratio, epsilon, filename):
    """
    Tworzy plik trajektorii dla BNFinder2 spełniający określone parametry.

    :param transitions: Słownik przejść (STS)
    :param attractors: Lista list stanów (wynik find_attractors)
    :param nodes: Lista nazw węzłów (dla zachowania kolejności bitów)
    :param sampling_freq: Częstotliwość próbkowania (krok czasowy)
    :param size: Liczba trajektorii w pliku
    :param length: Liczba punktów w każdej SPRÓBKOWANEJ trajektorii
    :param attr_ratio: Docelowa proporcja stanów atraktorowych
    :param epsilon: Tolerancja dla attr_ratio
    :param filename: Nazwa pliku wyjściowego
    """
    attr_states = {s for a in attractors for s in a}
    final_trajectories = []

    # Obliczamy całkowitą długość surowej symulacji potrzebną do uzyskania 'length' próbek
    raw_length_needed = (length - 1) * sampling_freq + 1

    attempts = 0
    while len(final_trajectories) < size and attempts < 10000:
        attempts += 1
        # Startujemy z losowego stanu
        current_state = random.choice(list(transitions.keys()))
        raw_path = [current_state]

        # Symulacja trajektorii
        for _ in range(raw_length_needed - 1):
            next_options = transitions.get(current_state, [])
            if not next_options:  # Punkt stały (brak wyjść w STS bez pętli)
                next_state = current_state
            else:
                next_state = random.choice(next_options)
            raw_path.append(next_state)
            current_state = next_state

        # Próbkowanie (Sampling)
        sampled_path = raw_path[::sampling_freq]

        # Obliczanie rzeczywistego ATTR_RATIO
        attr_count = sum(1 for s in sampled_path if s in attr_states)
        actual_ratio = float(attr_count) / len(sampled_path)

        # Sprawdzenie czy trajektoria mieści się w przedziale tolerancji
        if (attr_ratio - epsilon) <= actual_ratio <= (attr_ratio + epsilon):
            # Konwersja bitstringów na słowniki {węzeł: wartość}
            traj_as_dicts = []
            for state_str in sampled_path:
                state_dict = {nodes[i]: int(state_str[i]) for i in range(len(nodes))}
                traj_as_dicts.append(state_dict)
            final_trajectories.append(traj_as_dicts)

    if len(final_trajectories) < size:
        print(
            f"Warning: Nie udało się wygenerować wszystkich {size} trajektorii. Znaleziono: {len(final_trajectories)}")

    # Zapis do formatu BNFinder2 (wykorzystujemy Twoją funkcję format_for_bnfinder)
    if final_trajectories:
        _format_to_bnf_file(final_trajectories, nodes, filename)
        print(f"Dataset zapisany w: {filename} (Ratio ok. {attr_ratio})")


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