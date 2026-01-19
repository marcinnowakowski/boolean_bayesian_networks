import os
import itertools

import a01_compile_bool_nets as a01
import a02_transition_nets as a02
import a03_identify_attractors as a03
import a04_create_trajectory as a04
import a05_run_bnfinder as a05

import config

os.makedirs(config.TRAJECTORIES_DIR, exist_ok=True)

# a01. kompilacja sieci:
net_dimensions = '7d'
net_id = '000'

net_name = f'{net_dimensions}_{net_id}'
net_functions = config.BOOL_NETWORKS[net_name]
net_nodes = sorted(net_functions.keys())
comp_net = a01._prepare_network(net_functions)

# a02. tworzenie transition nets:
sync_sts = a02.get_synchronous_sts(comp_net)
async_sts = a02.get_asynchronous_sts(comp_net)
#pprint.pprint(async_sts)

# a03. identyfikacja atraktorów
sync_attr = a03.find_attractors(sync_sts)
async_attr = a03.find_attractors(async_sts)
#pprint.pprint(async_attr)

#a04. Generacja trajektorii
os.makedirs(f"{config.TRAJECTORIES_DIR}/{net_name}", exist_ok=True)
execution_modes = [
    ('sync', sync_sts, sync_attr),
    ('async', async_sts, async_attr)
]
print(f"Rozpoczynam generowanie datasetów dla sieci: {net_name}...")
for mode_name, sts, attr in execution_modes:
    # Generujemy iloczyn kartezjański wszystkich hiperparametrów
    param_combinations = itertools.product(
        config.SAMPLING_FREQS,
        config.SIZES,
        config.LENGTHS,
        config.ATTR_RATIO
    )
    for f, s, l, r in param_combinations:
        # Formatka nazwy: {wymiar}_{id}_{mode}_f{freq}_s{size}_l{len}_at{ratio}.txt
        filename = f"{net_name}_{mode_name}_f{f}_s{s}_l{l}_at{r}.txt"
        current_savepath = os.path.join(config.TRAJECTORIES_DIR, net_name, filename)

        # Wywołanie Twojej funkcji generującej
        a04.create_trajectory_file(
            transitions=sts,
            attractors=attr,
            nodes=net_nodes,
            sampling_freq=f,
            size=s,
            length=l,
            attr_ratio=r,
            epsilon=config.EPSILON,
            filename=current_savepath
        )

print(f"Zakończono! Wszystkie trajektorie dla {net_name} znajdują się w {config.TRAJECTORIES_DIR}/{net_name}")

# a05. rekonstrukcja sieci bnfinderem
os.makedirs(f"{config.RESULTS_DIR}/{net_name}", exist_ok=True)
a05.run_all_bnf_analyses(net_name, config.TRAJECTORIES_DIR, config.RESULTS_DIR)