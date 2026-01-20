import csv
import os
import itertools

import a01_compile_bool_nets as a01
import a02_transition_nets as a02
import a03_identify_attractors as a03
import a04_create_trajectory as a04
import a04_alternative as a04_alt
import a05_run_bnfinder as a05

import config

os.makedirs(config.TRAJECTORIES_DIR, exist_ok=True)


for net_name, net_repr in config.BOOL_NETWORKS.items():
    # a01. kompilacja sieci:
    net_dimensions, net_id = net_name.split("_")

    net_nodes = sorted(net_repr.keys())
    comp_net = a01._prepare_network(net_repr)
    
    # a02. tworzenie transition nets:
    sync_sts = a02.get_synchronous_sts(comp_net)
    async_sts = a02.get_asynchronous_sts(comp_net)
    #pprint.pprint(async_sts)
    
    # a03. identyfikacja atraktorów
    sync_attr = a03.find_attractors(sync_sts)
    async_attr = a03.find_attractors(async_sts)
    #pprint.pprint(async_attr)

    #a04. Generacja trajektorii
    # --- a04. Generacja trajektorii z logowaniem ---

    os.makedirs(f"{config.TRAJECTORIES_DIR}/{net_name}", exist_ok=True)
    report_path = os.path.join(config.TRAJECTORIES_DIR, net_name, f"{net_name}_generation_report.csv")

    execution_modes = [
        ('sync', sync_sts, sync_attr),
        ('async', async_sts, async_attr)
    ]

    generation_stats = []  # Tu będziemy zbierać logi

    print(f"--- Rozpoczynam generację dla {net_name} ---")
    cnt = 0
    for mode_name, sts, attr in execution_modes:
        if cnt >1 :break
        cnt += 1
        for freq in config.SAMPLING_FREQS:
            for length in config.LENGTHS:

                # 1. Budujemy pulę raz dla danej długości i częstotliwości
                pool = a04_alt.generate_trajectory_pool(sts, attr, freq, length, pool_size=config.POOL_SIZE)

                for ratio in config.ATTR_RATIO:
                    for size in config.SIZES:
                        filename = f"{net_name}_{mode_name}_f{freq}_s{size}_l{length}_at{ratio}.txt"
                        savepath = os.path.join(config.TRAJECTORIES_DIR, net_name, filename)

                        # Wywołujemy funkcję i sprawdzamy czy zwróciła True (sukces)
                        success = a04_alt.save_bnf_from_pool(pool, net_nodes, ratio, config.EPSILON, size, savepath)

                        # Logujemy dane o tej konkretnej próbie
                        generation_stats.append({
                            'mode': mode_name,
                            'freq': freq,
                            'length': length,
                            'target_ratio': ratio,
                            'size': size,
                            'filename': filename,
                            'status': 'SUCCESS' if success else 'FAILED'
                        })

    # 2. Zapisywanie logu do pliku CSV
    with open(report_path, mode='w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=['mode', 'freq', 'length', 'target_ratio', 'size', 'filename', 'status'])
        writer.writeheader()
        writer.writerows(generation_stats)

    # 3. Wyświetlenie podsumowania w konsoli
    total_files = len(generation_stats)
    successful_files = sum(1 for log in generation_stats if log['status'] == 'SUCCESS')

    print("\n" + "=" * 50)
    print(f"PODSUMOWANIE GENERACJI DLA {net_name}:")
    print(f"  - Wszystkich prób: {total_files}")
    print(f"  - Utworzono plików: {successful_files}")
    print(f"  - Niepowodzenia: {total_files - successful_files}")
    print(f"Pełny raport zapisano w: {report_path}")
    print("=" * 50 + "\n")

    print(f"Zakończono! Wszystkie trajektorie dla {net_name} znajdują się w {config.TRAJECTORIES_DIR}/{net_name}")
    
    # a05. rekonstrukcja sieci bnfinderem
    os.makedirs(f"{config.RESULTS_DIR}/{net_name}", exist_ok=True)
    a05.run_all_bnf_analyses(net_name, config.TRAJECTORIES_DIR, config.RESULTS_DIR)