def _prepare_network(functions):
    """
    Przygotowuje skompilowane obiekty kodu, usuwając zbędne wcięcia.
    """
    compiled_funcs = {}
    for node, func_str in functions.items():
        # 1. Usuwamy białe znaki z początku i końca (kluczowe!)
        clean_func = func_str.strip()

        # 2. Zamiana operatorów logicznych
        # Dodajemy spacje wokół operatorów, aby uniknąć problemów z przyleganiem
        py_func = clean_func.replace('~', ' not ').replace('&', ' and ').replace('|', ' or ')

        # 3. Opcjonalnie: zamiana wielokrotnych spacji na pojedyncze (dla czytelności)
        py_func = ' '.join(py_func.split())

        try:
            compiled_funcs[node] = compile(py_func, '<string>', 'eval')
        except SyntaxError as e:
            print("Błąd składni w węźle {}: {}".format(node, py_func))
            raise e

    return compiled_funcs


def compile_boolean_library(all_networks):
    """
    Tworzy słownik ze skompilowanymi funkcjami dla wszystkich zdefiniowanych sieci.
    """
    compiled_library = {}

    for net_name, functions in all_networks.items():
        print(f"Kompilowanie sieci: {net_name}...")
        try:
            # Wykorzystujemy Twoją funkcję pomocniczą
            compiled_library[net_name] = _prepare_network(functions)
        except Exception as e:
            print(f"Błąd podczas kompilacji sieci {net_name}: {e}")

    return compiled_library