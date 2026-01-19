import os
import subprocess


def run_all_bnf_analyses(net_name, trajectories_dir, results_base_dir):
    """
    Przechodzi przez wszystkie pliki .txt w folderze sieci i uruchamia BNFinder.
    """
    input_folder = os.path.join(trajectories_dir, net_name)
    output_folder = os.path.join(results_base_dir, net_name)

    if not os.path.exists(input_folder):
        print(f"Błąd: Folder z trajektoriami {input_folder} nie istnieje.")
        return

    # Pobieramy listę wszystkich plików .txt w folderze trajektorii
    trajectory_files = [f for f in os.listdir(input_folder) if f.endswith('.txt')]

    print(f"Znaleziono {len(trajectory_files)} plików do analizy dla sieci {net_name}.")

    for traj_file in sorted(trajectory_files):
        input_path = os.path.join(input_folder, traj_file)
        # Wywołujemy funkcję analizy dla każdego pliku
        run_bnfinder_analysis(input_path, output_folder)


def run_bnfinder_analysis(input_path, output_dir, conda_env="bnf_env"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Ścieżka do Condy
    conda_path = "/home/mateusz-wawrzyniak/miniconda3/bin/conda"

    # Nazwa bazowa pliku (np. 7d_000_sync_f1_s1_l10_at0.3)
    base_name = os.path.splitext(os.path.basename(input_path))[0]

    # Zadanie wymaga przetestowania MDL i BDe
    scoring_criteria = ["MDL", "BDE"]

    for score in scoring_criteria:
        # Formatka nazwy: {base_name}_scr{score}.bif
        output_filename = f"{base_name}_scr{score}.bif"
        output_path = os.path.join(output_dir, output_filename)

        command = [
            conda_path, "run", "-n", conda_env,
            "bnf",
            "-e", input_path,
            "-s", score,  # Poprawiona flaga score
            "-l", "3",  # Poprawiona flaga limitu rodziców
            "-g",  # Pozwolenie na self-loops dla DBN
            "-v",
            "-b", output_path  # Zapis do formatu BIF
        ]

        print(f"--- Przetwarzam: {base_name} | Scoring: {score} ---")
        try:
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            print(f"Sukces! Plik BIF: {output_filename}")
        except subprocess.CalledProcessError as e:
            print(f"Błąd BNFinder2 dla {base_name} ({score}):")
            print(e.stderr)

