import os
import csv
import itertools
import multiprocessing
from functools import partial

# Importy Twoich modułów
import a01_compile_bool_nets as a01
import a02_transition_nets as a02
import a03_identify_attractors as a03
import a04_alternative as a04_alt
import a05_run_bnfinder as a05
import config


# --- WORKER: Generacja trajektorii ---
def task_generate_trajectories(params, sts, attr, net_nodes, net_name, mode_name):
    """
    Worker wykonujący generowanie puli i zapisywanie plików dla konkretnego
    duetu (freq, length). Zwraca listę logów.
    """
    freq, length = params
    local_stats = []

    # 1. Budujemy pulę dla danej częstotliwości i długości
    pool = a04_alt.generate_trajectory_pool(sts, attr, freq, length, pool_size=config.POOL_SIZE)

    # 2. Tworzymy pliki dla wszystkich kombinacji ratio i size
    for ratio in config.ATTR_RATIO:
        for size in config.SIZES:
            filename = f"{net_name}_{mode_name}_f{freq}_s{size}_l{length}_at{ratio}.txt"
            savepath = os.path.join(config.TRAJECTORIES_DIR, net_name, filename)

            success = a04_alt.save_bnf_from_pool(pool, net_nodes, ratio, config.EPSILON, size, savepath)

            local_stats.append({
                'mode': mode_name,
                'freq': freq,
                'length': length,
                'target_ratio': ratio,
                'size': size,
                'filename': filename,
                'status': 'SUCCESS' if success else 'FAILED'
            })
    return local_stats


# --- WORKER: Uruchomienie BNFindera ---
def task_run_bnf(traj_file_path, output_dir):
    """
    Worker uruchamiający analizę BNFinder dla pojedynczego pliku trajektorii.
    """
    # Wykorzystujemy Twoją istniejącą funkcję z modułu a05
    a05.run_bnfinder_analysis(traj_file_path, output_dir)


# --- GŁÓWNY PIPELINE ---
def main():
    os.makedirs(config.TRAJECTORIES_DIR, exist_ok=True)
    os.makedirs(config.RESULTS_DIR, exist_ok=True)

    for net_name, net_repr in config.BOOL_NETWORKS.items():
        print(f"\n{'=' * 60}\nPRZETWARZANIE SIECI: {net_name}\n{'=' * 60}")

        # a01. Kompilacja sieci
        net_nodes = sorted(net_repr.keys())
        comp_net = a01._prepare_network(net_repr)

        # a02. Tworzenie STS (bez pętli zwrotnych dla przejrzystości grafu)
        sync_sts = a02.get_synchronous_sts(comp_net)
        async_sts = a02.get_asynchronous_sts(comp_net)

        # a03. Identyfikacja atraktorów
        sync_attr = a03.find_attractors(sync_sts)
        async_attr = a03.find_attractors(async_sts)

        # a04. Równoległa generacja trajektorii
        os.makedirs(f"{config.TRAJECTORIES_DIR}/{net_name}", exist_ok=True)
        report_path = os.path.join(config.TRAJECTORIES_DIR, net_name, f"{net_name}_generation_report.csv")

        execution_modes = [
            ('sync', sync_sts, sync_attr),
            ('async', async_sts, async_attr)
        ]

        all_generation_stats = []

        for mode_name, sts, attr in execution_modes:
            print(f"--> Tryb {mode_name}: Rozsyłanie zadań do puli procesów...")

            # Przygotowanie par (freq, length)
            task_combinations = list(itertools.product(config.SAMPLING_FREQS, config.LENGTHS))

            # Uruchomienie multiprocessing dla generacji puli
            with multiprocessing.Pool(processes=config.THREADS) as pool:
                worker_func = partial(task_generate_trajectories,
                                      sts=sts, attr=attr, net_nodes=net_nodes,
                                      net_name=net_name, mode_name=mode_name)

                results = pool.map(worker_func, task_combinations)

                # Spłaszczanie listy wyników
                for batch in results:
                    all_generation_stats.extend(batch)

        # Zapisywanie logu CSV
        with open(report_path, mode='w', newline='') as f:
            writer = csv.DictWriter(f,
                                    fieldnames=['mode', 'freq', 'length', 'target_ratio', 'size', 'filename', 'status'])
            writer.writeheader()
            writer.writerows(all_generation_stats)

        successful_files = sum(1 for log in all_generation_stats if log['status'] == 'SUCCESS')
        print(f"Zakończono generację. Sukcesy: {successful_files}/{len(all_generation_stats)}")

        # a05. Równoległa rekonstrukcja BNFinderem
        print(f"--> Uruchamianie BNFinder2 równolegle na {config.THREADS} rdzeniach...")
        output_folder = os.path.join(config.RESULTS_DIR, net_name)
        os.makedirs(output_folder, exist_ok=True)

        # Lista plików, które faktycznie udało się wygenerować
        valid_files = [
            os.path.join(config.TRAJECTORIES_DIR, net_name, log['filename'])
            for log in all_generation_stats if log['status'] == 'SUCCESS'
        ]

        with multiprocessing.Pool(processes=config.THREADS) as pool:
            bnf_worker = partial(task_run_bnf, output_dir=output_folder)
            pool.map(bnf_worker, valid_files)

    print("\nPROCES ZAKOŃCZONY POMYŚLNIE DLA WSZYSTKICH SIECI.")


if __name__ == "__main__":
    # Niezbędne zabezpieczenie dla multiprocessing w Windows/Linux
    main()