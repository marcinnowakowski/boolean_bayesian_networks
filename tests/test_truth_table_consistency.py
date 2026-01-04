"""
Test consistency between truth tables and function definitions.
"""

import pytest


class TestTruthTableFunctionsConsistency:
    """Test that truth tables are consistent with function definitions."""
    
    def test_truth_table_matches_functions(self):
        """
        Verify that evaluating functions produces the same results as truth table.
        
        For each state in the truth table, evaluate each function and check
        that the result matches what's in the truth table.
        """
        from boolean_networks.truth_tables import load_functions, evaluate_expression
        
        # Load truth table directly
        truth_table_file = "networks/truth_tables/5d_interesting/bn_tt_5d_net_2.py"
        with open(truth_table_file, 'r') as f:
            content = f.read()
        namespace = {}
        exec(content, namespace)
        truth_table = namespace.get('truth_table', {})
        
        # Load functions
        functions_file = "networks/functions/5d_interesting/bn_fn_5d_net_2.py"
        functions = load_functions(functions_file)
        
        num_vars = 5
        var_names = [f"x{i+1}" for i in range(num_vars)]
        
        errors = []
        
        for state_str, next_states in truth_table.items():
            # Convert state string to dict
            state_bits = [int(b) for b in state_str]
            state_dict = {var_names[i]: state_bits[i] for i in range(num_vars)}
            
            for var_idx, var_name in enumerate(var_names):
                # Get expected next state from truth table
                expected_next_state = next_states[var_name]
                expected_val = int(expected_next_state[var_idx])
                
                # Evaluate function
                expr = functions.get(var_name, var_name)
                computed_val = evaluate_expression(expr, state_dict)
                
                if computed_val != expected_val:
                    errors.append(
                        f"State {state_str}, {var_name}: "
                        f"function gives {computed_val}, truth table expects {expected_val}"
                    )
        
        assert len(errors) == 0, f"Mismatches found:\n" + "\n".join(errors[:10])
    
    def test_roundtrip_functions_to_truth_table(self):
        """
        Test that functions -> truth_table -> functions produces equivalent results.
        """
        from boolean_networks.truth_tables import load_functions, generate_truth_table, evaluate_expression
        
        functions_file = "networks/functions/5d_interesting/bn_fn_5d_net_2.py"
        functions = load_functions(functions_file)
        
        # Generate truth table from functions
        truth_table = generate_truth_table(functions)
        
        num_vars = 5
        var_names = [f"x{i+1}" for i in range(num_vars)]
        
        # Verify each entry
        for state_str in truth_table:
            state_bits = [int(b) for b in state_str]
            state_dict = {var_names[i]: state_bits[i] for i in range(num_vars)}
            
            for var_idx, var_name in enumerate(var_names):
                next_state = truth_table[state_str][var_name]
                expected_val = int(next_state[var_idx])
                
                expr = functions.get(var_name, var_name)
                computed_val = evaluate_expression(expr, state_dict)
                
                assert computed_val == expected_val, \
                    f"State {state_str}, {var_name}: got {computed_val}, expected {expected_val}"
